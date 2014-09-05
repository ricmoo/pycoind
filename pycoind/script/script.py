# The MIT License (MIT)
#
# Copyright (c) 2014 Richard Moore
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


import inspect
import struct


from .bytevector import ByteVector
from . import opcodes

from .. import coins
from .. import protocol
from .. import util

from ..protocol import format

__all__ = ['Script', 'Tokenizer']

# Convenient constants
Zero = ByteVector.from_value(0)
One = ByteVector.from_value(1)

def _is_pubkey(opcode, bytes, data):
    if opcode != Tokenizer.OP_LITERAL:
        return False
    if len(data) != 65 or data[0] != chr(0x04):
        return False
    return True

def _is_hash160(opcode, bytes, data):
    if opcode != Tokenizer.OP_LITERAL:
        return False
    if len(data) != 20:
        return False
    return True

def _is_hash256(opcode, bytes, data):
    if opcode != Tokenizer.OP_LITERAL:
        return False
    if len(data) != 32:
        return False
    return True

def _too_long(opcode, bytes, data):
    return False

SCRIPT_FORM_NON_STANDARD               = 'non-standard'
SCRIPT_FORM_PAY_TO_PUBKEY_HASH         = 'pay-to-pubkey-hash'
SCRIPT_FORM_PAY_TO_PUBKEY              = 'pay-to-pubkey'
SCRIPT_FORM_UNSPENDABLE                = 'unspendable'
SCRIPT_FORM_ANYONE_CAN_SPEND           = 'anyone-can-spend'
SCRIPT_FORM_TRANSACTION_PUZZLE_HASH256 = 'transaction-puzzle-hash256'

STANDARD_SCRIPT_FORMS = [
    SCRIPT_FORM_PAY_TO_PUBKEY_HASH,
    SCRIPT_FORM_PAY_TO_PUBKEY
]

# @TODO: outdated documentation
# Templates are (name, template) tuples. Each template is a tuple of
# (callable, item1, item2, ...) where callable is called on the entrie
# tokenized script; itemN can be either an opcode or a callable which
# accepts (opcode, bytes, value).

TEMPLATE_PAY_TO_PUBKEY_HASH = (lambda t: len(t) == 5, opcodes.OP_DUP,
    opcodes.OP_HASH160, _is_hash160, opcodes.OP_EQUALVERIFY,
    opcodes.OP_CHECKSIG)

TEMPLATE_PAY_TO_PUBKEY = (lambda t: len(t) == 2, _is_pubkey,
    opcodes.OP_CHECKSIG)

Templates = [

    (SCRIPT_FORM_PAY_TO_PUBKEY_HASH, TEMPLATE_PAY_TO_PUBKEY_HASH),

    (SCRIPT_FORM_PAY_TO_PUBKEY, TEMPLATE_PAY_TO_PUBKEY),

#    (SCRIPT_FORM_UNSPENDABLE,
#     (lambda t: True,
#      opcodes.OP_RETURN, )),

#    (SCRIPT_FORM_ANYONE_CAN_SPEND,
#     (lambda t: len(t) == 0, )),

#    (SCRIPT_FORM_TRANSACTION_PUZZLE_HASH256,
#     (lambda t: len(t) == 3,
#      opcodes.OP_HASH256, _is_hash256, opcodes.OP_EQUAL)),
]

def _stack_op(stack, func):
    '''Replaces the top N items from the stack with the items in the list
       returned by the callable func; N is func's argument count.

       The result must return a list.

       False is returned on error, otherwise True.'''

    # not enough arguments
    count = len(inspect.getargspec(func).args)
    if len(stack) < count: return False
    args = stack[-count:]
    stack[-count:] = []

    # add each returned item onto the stack
    for item in func(*args):
        stack.append(item)

    return True


def _math_op(stack, func, check_overflow = True):
    '''Replaces the top N items from the stack with the result of the callable
       func; N is func's argument count.

       A boolean result will push either a 0 or 1 on the stack. None will push
       nothing. Otherwise, the result must be a ByteVector.

       False is returned on error, otherwise True.'''

    # not enough arguments
    count = len(inspect.getargspec(func).args)
    if len(stack) < count: return False
    args = stack[-count:]
    stack[-count:] = []

    # check for overflow
    if check_overflow:
        for arg in args:
            if len(arg) > 4: return False

    # compute the result
    result = func(*args)

    # convert booleans to One or Zero
    if result == True:
        result = One
    elif result == False:
        result = Zero

    if result is not None:
        stack.append(result)

    return True


def _hash_op(stack, func):
    '''Replaces the top of the stack with the result of the callable func.

       The result must be a ByteVector.

       False is returned on error, otherwise True.'''

    # not enough arguments
    if len(stack) < 1: return False

    # hash and push
    value = func(stack.pop().vector)
    stack.append(ByteVector(value))

    return True


def check_signature(signature, public_key, hash_type, subscript, transaction, input_index):

    # figure out the hash_type and adjust the signature
    if hash_type == 0:
        hash_type = ord(signature[-1])
    if hash_type != ord(signature[-1]):
        raise Exception('@todo: should I check for this?')
    signature = signature[:-1]

    #print hash_type

    # SIGHASH_ALL
    if (hash_type & 0x1f) == 0x01 or hash_type == 0:
        #print "ALL"
        tx_ins = [ ]
        for (index, tx_in) in enumerate(transaction.inputs):
            script = ''
            if index == input_index:
                script = subscript

            tx_in = protocol.TxnIn(tx_in.previous_output, script, tx_in.sequence)
            tx_ins.append(tx_in)

        tx_outs = transaction.outputs

    # SIGHASH_NONE (other tx_in.sequence = 0, tx_out = [ ])
    elif (hash_type & 0x1f) == 0x02:
        #print "NONE"
        tx_ins = [ ]
        index = 0
        for tx_in in transaction.inputs:
            script = ''
            sequence = 0
            if index == input_index:
                script = subscript
                sequence = tx_in.sequence
            index += 1

            tx_in = protocol.TxnIn(tx_in.previous_output, script, sequence)
            tx_ins.append(tx_in)

        tx_outs = [ ]

    # SIGHASH_SINGLE (len(tx_out) = input_index + 1, other outputs = (-1, ''), other tx_in.sequence = 0)
    elif (hash_type & 0x1f) == 0x03:
        #print "SINGLE"
        tx_ins = [ ]
        index = 0
        for tx_in in transaction.inputs:
            script = ''
            sequence = 0
            if index == input_index:
                script = subscript
                sequence = tx_in.sequence
            index += 1

            tx_in = protocol.TxnIn(tx_in.previous_output, script, sequence)
            tx_ins.append(tx_in)

        tx_outs = [ ]
        index = 0
        for tx_out in transaction.outputs:
            if len(tx_outs) > input_index: break
            if index != input_index:
                tx_out = protocol.TxnOut(-1, '')
            tx_outs.append(tx_out)
            index += 1

    else:
        raise Exception('unknown hash type: %d' % hash_type)

    # SIGHASH_ANYONECANPAY
    if (hash_type & 0x80) == 0x80:
        #print "ANYONE"
        tx_in = transaction.inputs[input_index]
        tx_ins = [protocol.TxnIn(tx_in.previous_output, subscript, tx_in.sequence)]

        tx_outs = transaction.outputs

    tx_copy = FlexTxn(transaction.version, tx_ins, tx_outs, transaction.lock_time)

    # compute the data to verify
    sig_hash = struct.pack('<I', hash_type)
    payload = tx_copy.binary() + sig_hash

    # verify the data
    #print "PK", public_key.encode('hex')
    #print "S", signature.encode('hex'), input_index
    #print "T", transaction
    #print "I", input_index
    return util.ecc.verify(payload, public_key, signature)


# identical to protocol.Txn except it allows zero tx_out for SIGHASH_NONE
class FlexTxn(protocol.Txn):
    properties = [
        ('version', format.FormatTypeNumber('I')),
        ('tx_in', format.FormatTypeArray(format.FormatTypeTxnIn, 1)),
        ('tx_out', format.FormatTypeArray(format.FormatTypeTxnOut)),
        ('lock_time', format.FormatTypeNumber('I')),
    ]


class Tokenizer(object):
    '''Tokenizes a script into tokens.

       Literals can be accessed with get_value and have the opcode 0x1ff.

       The *VERIFY opcodes are expanded into the two equivalent opcodes.'''

    OP_LITERAL = 0x1ff

    def __init__(self, script, expand_verify = False):
        self._script = script
        self._expand_verify = expand_verify
        self._tokens = [ ]
        self._process(script)

    def append(self, script):
        self._script += script
        self._process(script)

    def get_subscript(self, start_index = 0, filter = None):
        '''Rebuild the script from token start_index, using the callable
           removing tokens that return False for filter(opcode, bytes, value)
           where bytes is the original bytes and value is any literal value.'''

        output = ''
        for (opcode, bytes, value) in self._tokens[start_index:]:
            if filter and not filter(opcode, bytes, value):
                continue
            output += bytes
        return output

    def match_template(self, template):
        'Given a template, return True if this script matches.'

        if not template[0](self):
            return False

        # ((opcode, bytes, value), template_target)
        for ((o, b, v), t) in zip(self._tokens, template[1:]):

            # callable, check the value
            if callable(t):
                if not t(o, b, v):
                    return False

            # otherwise, compare opcode
            elif t != o:
                return False

        return True

    _Verify = {
        opcodes.OP_EQUALVERIFY: opcodes.OP_EQUAL,
        opcodes.OP_NUMEQUALVERIFY: opcodes.OP_NUMEQUAL,
        opcodes.OP_CHECKSIGVERIFY: opcodes.OP_CHECKSIG,
        opcodes.OP_CHECKMULTISIGVERIFY: opcodes.OP_CHECKMULTISIG,
    }

    def _process(self, script):
        'Parse the script into tokens. Internal use only.'

        while script:
            opcode = ord(script[0])
            bytes = script[0]
            script = script[1:]
            value = None

            verify = False

            if opcode == opcodes.OP_0:
                value = Zero
                opcode = Tokenizer.OP_LITERAL

            elif 1 <= opcode <= 78:
                length = opcode

                if opcodes.OP_PUSHDATA1 <= opcode <= opcodes.OP_PUSHDATA4:
                    op_length = [1, 2, 4][opcode - opcodes.OP_PUSHDATA1]
                    format = ['<B', '<H', '<I'][opcode - opcodes.OP_PUSHDATA1]
                    length = struct.unpack(format, script[:op_length])[0]
                    bytes += script[:op_length]
                    script = script[op_length:]

                value = ByteVector(vector = script[:length])
                bytes += script[:length]
                script = script[length:]
                if len(value) != length:
                    raise Exception('not enought script for literal')
                opcode = Tokenizer.OP_LITERAL

            elif opcode == opcodes.OP_1NEGATE:
                opcode = Tokenizer.OP_LITERAL
                value = ByteVector.from_value(-1)

            elif opcode == opcodes.OP_TRUE:
                opcode = Tokenizer.OP_LITERAL
                value = ByteVector.from_value(1)

            elif opcodes.OP_1 <= opcode <= opcodes.OP_16:
                value = ByteVector.from_value(opcode - opcodes.OP_1 + 1)
                opcode = Tokenizer.OP_LITERAL

            elif self._expand_verify and opcode in self._Verify:
                opcode = self._Verify[opcode]
                verify = True

            self._tokens.append((opcode, bytes, value))

            if verify:
                self._tokens.append((opcodes.OP_VERIFY, '', None))

    def get_bytes(self, index):
        'Get the original bytes used for the opcode and value'

        return self._tokens[index][1]


    def get_value(self, index):
        'Get the value for a literal.'

        return self._tokens[index][2]

    def __len__(self):
        return len(self._tokens)

    def __getitem__(self, name):
        return self._tokens[name][0]

    def __iter__(self):
        for (opcode, bytes, value) in self._tokens:
            yield opcode

    def __str__(self):
        output = [ ]
        for (opcode, bytes, value) in self._tokens:
            if opcode == Tokenizer.OP_LITERAL:
                output.append(value.vector.encode('hex'))
            else:
                if bytes:
                    output.append(opcodes.get_opcode_name(ord(bytes[0])))

        return " ".join(output)


class Script(object):
    def __init__(self, transaction, coin = coins.Bitcoin):
        self._transaction = transaction
        self._coin = coin

    @property
    def output_count(self):
        return len(self._transaction.outputs)

    def output_address(self, output_index):
        pk_script = self._transaction.outputs[output_index].pk_script
        tokens = Tokenizer(pk_script)

        if tokens.match_template(TEMPLATE_PAY_TO_PUBKEY_HASH):
            pubkeyhash = tokens.get_value(2).vector
            return util.key.pubkeyhash_to_address(pubkeyhash, self._coin.address_version)

        if tokens.match_template(TEMPLATE_PAY_TO_PUBKEY):
            pubkey = tokens.get_value(0).vector
            return util.key.publickey_to_address(pubkey, self._coin.address_version)

        return None

    #def previous_output(self, index):
    #    po = self._transaction.tx_in[index].previous_output
    #    return (po.hash, po.index)

    def script_form(self, output_index):
        pk_script = self._transaction.outputs[output_index].pk_script
        tokens = Tokenizer(pk_script)
        for (sf, template) in Templates:
            if tokens.match_template(template):
                return sf
        return SCRIPT_FORM_NON_STANDARD

    def is_standard_script(self, output_index):
        pk_script = self._transaction.outputs[output_index]
        tokens = Tokenize(pk_script, expand_verify = False)
        for sf in STANDARD_SCRIPT_FORMS:
            if tokens.match_template(Templates[sf]):
                return True
        return False

    @property
    def input_count(self):
        return len(self._transaction.inputs)

    def verify_input(self, input_index, pk_script):
        input = self._transaction.inputs[input_index]
        return self.process(input.signature_script, pk_script, self._transaction, input_index)

    def verify(self):
        '''Return True if all transaction inputs can be verified against their
           previous output.'''

        for i in xrange(0, len(self._transaction.inputs)):

            # ignore coinbase (generation transaction input)
            if self._transaction.index == 0 and i == 0: continue

            # verify the input with its previous output
            input = self._transaction.inputs[i]
            previous_output = self._transaction.previous_output(i)
            if not self.verify_input(i, previous_output.pk_script):
                #print "INVALID:", self._transaction.hash.encode('hex'), i
                return False

        return True

    @staticmethod
    def process(signature_script, pk_script, transaction, input_index, hash_type = 0):

        # tokenize (placing the last code separator after the signature script)
        tokens = Tokenizer(signature_script, expand_verify = True)
        signature_length = len(tokens)
        tokens.append(pk_script)
        last_codeseparator = signature_length

        #print str(tokens)

        # check for VERY forbidden opcodes (see "reserved Words" on the wiki)
        for token in tokens:
            if token in (opcodes.OP_VERIF, opcodes.OP_VERNOTIF):
                return False

        # stack of entered if statments' condition values
        ifstack = []

        # operating stacks
        stack = []
        altstack = []

        for pc in xrange(0, len(tokens)):
            opcode = tokens[pc]

            #print "STACK:", (opcodes.OPCODE_NAMES[min(opcode, 255)], repr(tokens.get_value(pc)))
            #print "  " + "\n  ".join("%s (%d)" % (i.vector.encode('hex'), i.value) for i in stack)
            #print

            # handle if before anything else
            if opcode == opcodes.OP_IF:
                ifstack.append(stack.pop().value != 0)

            elif opcode == opcodes.OP_NOTIF:
                ifstack.append(stack.pop().value == 0)

            elif opcode == opcodes.OP_ELSE:
                if len(ifstack) == 0: return False
                ifstack.push(not ifstack.pop())

            elif opcode == opcodes.OP_ENDIF:
                if len(ifstack) == 0: return False
                ifstack.pop()

            # we are in a branch with a false condition
            if False in ifstack: continue

            ### Literals

            if opcode == Tokenizer.OP_LITERAL:
                stack.append(tokens.get_value(pc))

            ### Flow Control (OP_IF and kin are above)

            elif opcode == opcodes.OP_NOP:
                pass

            elif opcode == opcodes.OP_VERIFY:
                if len(stack) < 1: return False
                if bool(stack[-1]):
                    stack.pop()
                else:
                    return False

            elif opcode == opcodes.OP_RETURN:
                return False

            ### Stack Operations

            elif opcode == opcodes.OP_TOALTSTACK:
                if len(stack) < 1: return False
                altstack.append(stack.pop())

            elif opcode == opcodes.OP_FROMALTSTACK:
                if len(altstack) < 1: return False
                stack.append(altstack.pop())

            elif opcode == opcodes.OP_IFDUP:
                if len(stack) < 1: return False
                if bool(stack[-1]):
                    stack.append(stack[-1])

            elif opcode == opcodes.OP_DEPTH:
                stack.append(ByteVector.from_value(len(stack)))

            elif opcode == opcodes.OP_DROP:
                if not _stack_op(stack, lambda x: [ ]):
                    return False

            elif opcode == opcodes.OP_DUP:
                if not _stack_op(stack, lambda x: [x, x]):
                    return False

            elif opcode == opcodes.OP_NIP:
                if not _stack_op(stack, lambda x1, x2: [x2]):
                    return False

            elif opcode == opcodes.OP_OVER:
                if not _stack_op(stack, lambda x1, x2: [x1, x2, x1]):
                    return False

            elif opcode == opcodes.OP_PICK:
                if len(stack) < 2: return False
                n = stack.pop().value + 1
                if not (0 <= n <= len(stack)): return False
                stack.append(stack[-n])

            elif opcode == opcodes.OP_ROLL:
                if len(stack) < 2: return False
                n = stack.pop().value + 1
                if not (0 <= n <= len(stack)): return False
                stack.append(stack.pop(-n))

            elif opcode == opcodes.OP_ROT:
                if not _stack_op(stack, lambda x1, x2, x3: [x2, x3, x1]):
                    return False

            elif opcode == opcodes.OP_SWAP:
                if not _stack_op(stack, lambda x1, x2: [x2, x1]):
                    return False

            elif opcode == opcodes.OP_TUCK:
                if not _stack_op(stack, lambda x1, x2: [x2, x1, x2]):
                    return False

            elif opcode == opcodes.OP_2DROP:
                if not _stack_op(stack, lambda x1, x2: []):
                    return False

            elif opcode == opcodes.OP_2DUP:
                if not _stack_op(stack, lambda x1, x2: [x1, x2, x1, x2]):
                    return False

            elif opcode == opcodes.OP_3DUP:
                if not _stack_op(stack, lambda x1, x2, x3: [x1, x2, x3, x1, x2, x3]):
                    return False

            elif opcode == opcodes.OP_2OVER:
                if not _stack_op(stack, lambda x1, x2, x3, x4: [x1, x2, x3, x4, x1, x2]):
                    return False

            elif opcode == opcodes.OP_2ROT:
                if not _stack_op(stack, lambda x1, x2, x3, x4, x5, x6: [x3, x4, x5, x6, x1, x2]):
                    return False

            elif opcode == opcodes.OP_2SWAP:
                if not _stack_op(stack, lambda x1, x2, x3, x4: [x3, x4, x1, x2]):
                    return False

            ### Splice Operations

            elif opcode == opcodes.OP_SIZE:
                if len(stack) < 1: return False
                stack.append(ByteVector.from_value(len(stack[-1])))

            ### Bitwise Logic Operations

            elif opcode == opcodes.OP_EQUAL:
                if not _math_op(stack, lambda x1, x2: bool(x1 == x2), False):
                    return False

            ### Arithmetic Operations

            elif opcode == opcodes.OP_1ADD:
                if not _math_op(stack, lambda a: a + One):
                    return False

            elif opcode == opcodes.OP_1SUB:
                if not _math_op(stack, lambda a: a - One):
                    return False

            elif opcode == opcodes.OP_NEGATE:
                if not _math_op(stack, lambda a: -a):
                    return False

            elif opcode == opcodes.OP_ABS:
                if not _math_op(stack, lambda a: abs(a)):
                    return False

            elif opcode == opcodes.OP_NOT:
                if not _math_op(stack, lambda a: bool(a == 0)):
                    return False

            elif opcode == opcodes.OP_0NOTEQUAL:
                if not _math_op(stack, lambda a: bool(a != 0)):
                    return False

            elif opcode == opcodes.OP_ADD:
                if not _math_op(stack, lambda a, b: a + b):
                    return False

            elif opcode == opcodes.OP_SUB:
                if not _math_op(stack, lambda a, b: a - b):
                    return False

            elif opcode == opcodes.OP_BOOLAND:
                if not _math_op(stack, lambda a, b: bool(a and b)):
                    return False

            elif opcode == opcodes.OP_BOOLOR:
                if not _math_op(stack, lambda a, b: bool(a or b)):
                    return False

            elif opcode == opcodes.OP_NUMEQUAL:
                if not _math_op(stack, lambda a, b: bool(a == b)):
                    return False

            elif opcode == opcodes.OP_NUMNOTEQUAL:
                if not _math_op(stack, lambda a, b: bool(a != b)):
                    return False

            elif opcode == opcodes.OP_LESSTHAN:
                if not _math_op(stack, lambda a, b: bool(a < b)):
                    return False

            elif opcode == opcodes.OP_GREATERTHAN:
                if not _math_op(stack, lambda a, b: bool(a > b)):
                    return False

            elif opcode == opcodes.OP_LESSTHANOREQUAL:
                if not _math_op(stack, lambda a, b: bool(a <= b)):
                    return False

            elif opcode == opcodes.OP_GREATERTHANOREQUAL:
                if not _math_op(stack, lambda a, b: bool(a >= b)):
                    return False

            elif opcode == opcodes.OP_MIN:
                if not _math_op(stack, lambda a, b: min(a, b)):
                    return False

            elif opcode == opcodes.OP_MAX:
                if not _math_op(stack, lambda a, b: max(a, b)):
                    return False

            elif opcode == opcodes.OP_WITHIN:
                if not _math_op(stack, lambda x, omin, omax: bool(omin <= x < omax)):
                    return False

            ### Crypto Operations

            elif opcode == opcodes.OP_RIPEMD160:
                if not _hash_op(stack, util.ripemd160):
                    return False

            elif opcode == opcodes.OP_SHA1:
                if not _hash_op(stack, util.sha1):
                    return False

            elif opcode == opcodes.OP_SHA256:
                if not _hash_op(stack, util.sha256):
                    return False

            elif opcode == opcodes.OP_HASH160:
                if not _hash_op(stack, util.hash160):
                    return False

            elif opcode == opcodes.OP_HASH256:
                if not _hash_op(stack, util.sha256d):
                    return False

            elif opcode == opcodes.OP_CODESEPARATOR:
                if pc > last_codeseparator:
                    last_codeseparator = pc

            # see: https://en.bitcoin.it/wiki/OP_CHECKSIG
            elif opcode == opcodes.OP_CHECKSIG:
                if len(stack) < 2: return False

                # remove the signature and code separators for subscript
                def filter(opcode, bytes, value):
                    if opcode == opcodes.OP_CODESEPARATOR:
                        return False
                    if opcode == Tokenizer.OP_LITERAL and isinstance(value, str) and value == signature:
                        return False
                    return True
                subscript = tokens.get_subscript(last_codeseparator, filter)

                public_key = stack.pop().vector
                signature = stack.pop().vector
                valid = check_signature(signature, public_key, hash_type, subscript, transaction, input_index)

                if valid:
                    stack.append(One)
                else:
                    #print "PK", public_key.encode('hex')
                    #print "S", signature.encode('hex'), input_index
                    stack.append(Zero)

            elif opcode == opcodes.OP_CHECKMULTISIG:
                if len(stack) < 2: return False

                # get all the public keys
                count = stack.pop().value
                if len(stack) < count: return False
                public_keys = [stack.pop() for i in xrange(count)]

                if len(stack) < 1: return False

                # get all the signautres
                count = stack.pop().value
                if len(stack) < count: return False
                signatures = [stack.pop() for i in xrange(count)]

                # due to a bug in the original client, discard an extra operand
                if len(stack) < 1: return False
                stack.pop()

                # remove the signature and code separators for subscript
                def filter(opcode, bytes, value):
                    if opcode == opcodes.OP_CODESEPARATOR:
                        return False
                    if opcode == Tokenizer.OP_LITERAL and isinstance(value, str) and value in signatures:
                        return False
                    return True
                subscript = tokens.get_subscript(last_codeseparator, filter)

                matched = dict()
                for signature in signatures:

                    # do any remaining public keys work?
                    for public_key in public_keys:
                        if check_signature(signature, public_key, hash_type, subscript, transaction, input_index):
                            break
                    else:
                        public_key is None

                    # record which public key and remove from future canidate
                    if public_key is not None:
                        matched[signature] = public_key
                        public_keys.remove(public_key)

                # did each signature have a matching public key?
                if len(matched) == len(signatures):
                    stack.append(One)
                else:
                    #print "MULTISIG"
                    #print "PK", public_key.encode('hex')
                    #print "S", signature.encode('hex'), input_index
                    stack.append(Zero)

            elif opcode == opcodes.OP_RESERVED:
                return False

            elif opcode == opcodes.OP_VER:
                return False

            elif opcode == opcodes.OP_RESERVED1:
                return False

            elif opcode == opcodes.OP_RESERVED2:
                return False

            elif opcodes.OP_NOP1 <= opcode <= opcodes.OP_NOP10:
                pass

            else:
                #print "UNKNOWN OPCODE: %d" % opcode
                return False

        #print "STACK:"
        #print "  " + "\n  ".join(str(i) for i in stack)
        if len(stack) and bool(stack[-1]):
            return True

        return False

