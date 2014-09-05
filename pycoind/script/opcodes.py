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


__all__ = ['DISABLED', 'OPCODE_NAMES', 'OP_0', 'OP_0NOTEQUAL', 'OP_1', 'OP_10',
           'OP_11', 'OP_12', 'OP_13', 'OP_14', 'OP_15', 'OP_16', 'OP_1ADD',
           'OP_1NEGATE', 'OP_1SUB', 'OP_2', 'OP_2DIV', 'OP_2DROP', 'OP_2DUP',
           'OP_2MUL', 'OP_2OVER', 'OP_2ROT', 'OP_2SWAP', 'OP_3', 'OP_3DUP',
           'OP_4', 'OP_5', 'OP_6', 'OP_7', 'OP_8', 'OP_9', 'OP_ABS', 'OP_ADD',
           'OP_AND', 'OP_BOOLAND', 'OP_BOOLOR', 'OP_CAT', 'OP_CHECKMULTISIG',
           'OP_CHECKMULTISIGVERIFY', 'OP_CHECKSIG', 'OP_CHECKSIGVERIFY',
           'OP_CODESEPARATOR', 'OP_DEPTH', 'OP_DIV', 'OP_DROP', 'OP_DUP',
           'OP_ELSE', 'OP_ENDIF', 'OP_EQUAL', 'OP_EQUALVERIFY', 'OP_FALSE',
           'OP_FROMALTSTACK', 'OP_GREATERTHAN', 'OP_GREATERTHANOREQUAL',
           'OP_HASH160', 'OP_HASH256', 'OP_IF', 'OP_IFDUP', 'OP_INVALIDOPCODE',
           'OP_INVERT', 'OP_LEFT', 'OP_LESSTHAN', 'OP_LESSTHANOREQUAL',
           'OP_LSHIFT', 'OP_MAX', 'OP_MIN', 'OP_MOD', 'OP_MUL', 'OP_NEGATE',
           'OP_NIP', 'OP_NOP', 'OP_NOP1', 'OP_NOP10', 'OP_NOP2', 'OP_NOP3',
           'OP_NOP4', 'OP_NOP5', 'OP_NOP6', 'OP_NOP7', 'OP_NOP8', 'OP_NOP9',
           'OP_NOT', 'OP_NOTIF', 'OP_NUMEQUAL', 'OP_NUMEQUALVERIFY',
           'OP_NUMNOTEQUAL', 'OP_OR', 'OP_OVER', 'OP_PICK', 'OP_PUBKEY',
           'OP_PUBKEYHASH', 'OP_PUSHDATA1', 'OP_PUSHDATA2', 'OP_PUSHDATA4',
           'OP_RESERVED', 'OP_RESERVED1', 'OP_RESERVED2', 'OP_RETURN',
           'OP_RIGHT', 'OP_RIPEMD160', 'OP_ROLL', 'OP_ROT', 'OP_RSHIFT',
           'OP_SHA1', 'OP_SHA256', 'OP_SIZE', 'OP_SUB', 'OP_SUBSTR', 'OP_SWAP',
           'OP_TOALTSTACK', 'OP_TRUE', 'OP_TUCK', 'OP_VER', 'OP_VERIF',
           'OP_VERIFY', 'OP_VERNOTIF', 'OP_WITHIN', 'OP_XOR', 'RESERVED',
           'get_opcode_name', 'is_disabled', 'is_reserved']

###################
# Constants

# An empty array of bytes is pushed onto the stack. (This is not a no-op: an
# item is added to the stack.)
OP_0                     = 0x00
OP_FALSE                 = 0x00

# The next opcode bytes is data to be pushed onto the stack
#N/A                      = 0x01-0x4b

# The next byte contains the number of bytes to be pushed onto the stack.
OP_PUSHDATA1             = 0x4c

# The next two bytes contain the number of bytes to be pushed onto the stack.
OP_PUSHDATA2             = 0x4d

# The next four bytes contain the number of bytes to be pushed onto the stack.
OP_PUSHDATA4             = 0x4e

# The number -1 is pushed onto the stack.
OP_1NEGATE               = 0x4f

# The number 1 is pushed onto the stack.
OP_1                     = 0x51
OP_TRUE                  = 0x51

# The number in the word name (2-16) is pushed onto the stack.
OP_2                     = 0x52
OP_3                     = 0x53
OP_4                     = 0x54
OP_5                     = 0x55
OP_6                     = 0x56
OP_7                     = 0x57
OP_8                     = 0x58
OP_9                     = 0x59
OP_10                    = 0x5a
OP_11                    = 0x5b
OP_12                    = 0x5c
OP_13                    = 0x5d
OP_14                    = 0x5e
OP_15                    = 0x5f
OP_16                    = 0x60


###################
# Flow Control

# Does nothing.
OP_NOP                   = 0x61

# If the top stack value is not 0, the statements are executed. The top
# stack value is removed.
OP_IF                    = 0x63

# If the top stack value is 0, the statements are executed. The top stack
# value is removed.
OP_NOTIF                 = 0x64

# If the preceding OP_IF or OP_NOTIF or OP_ELSE was not executed then these
# statements are and if the preceding OP_IF or OP_NOTIF or OP_ELSE was
# executed then these statements are not.
OP_ELSE                  = 0x67

# Ends an if/else block.
OP_ENDIF                 = 0x68

# Marks transaction as invalid if top stack value is not true. True is
# removed, but false is not.
OP_VERIFY                = 0x69

# Marks transaction as invalid.
OP_RETURN                = 0x6a


###################
# Stack

# Puts the input onto the top of the alt stack. Removes it from the main stack.
OP_TOALTSTACK            = 0x6b

# Puts the input onto the top of the main stack. Removes it from the alt stack.
OP_FROMALTSTACK          = 0x6c

# If the top stack value is not 0, duplicate it.
OP_IFDUP                 = 0x73

# Puts the number of stack items onto the stack.
OP_DEPTH                 = 0x74

# Removes the top stack item.
OP_DROP                  = 0x75

# Duplicates the top stack item.
OP_DUP                   = 0x76

# Removes the second-to-top stack item.
OP_NIP                   = 0x77

# Copies the second-to-top stack item to the top.
OP_OVER                  = 0x78

# The item ''n'' back in the stack is copied to the top.
OP_PICK                  = 0x79

# The item ''n'' back in the stack is moved to the top.
OP_ROLL                  = 0x7a

# The top three items on the stack are rotated to the left.
OP_ROT                   = 0x7b

# The top two items on the stack are swapped.
OP_SWAP                  = 0x7c

# The item at the top of the stack is copied and inserted before the
# second-to-top item.
OP_TUCK                  = 0x7d

# Removes the top two stack items.
OP_2DROP                 = 0x6d

# Duplicates the top two stack items.
OP_2DUP                  = 0x6e

# Duplicates the top three stack items.
OP_3DUP                  = 0x6f

# Copies the pair of items two spaces back in the stack to the front.
OP_2OVER                 = 0x70

# The fifth and sixth items back are moved to the top of the stack.
OP_2ROT                  = 0x71

# Swaps the top two pairs of items.
OP_2SWAP                 = 0x72


###################
# Splice

# Concatenates two strings.
OP_CAT                   = 0x7e

# Returns a section of a string.
OP_SUBSTR                = 0x7f

# Keeps only characters left of the specified point in a string.
OP_LEFT                  = 0x80

# Keeps only characters right of the specified point in a string.
OP_RIGHT                 = 0x81

# Pushes the string length of the top element of the stack (without popping it).
OP_SIZE                  = 0x82


###################
# Bitwise Logic

# Flips all of the bits in the input.
OP_INVERT                = 0x83

# Boolean ''and'' between each bit in the inputs.
OP_AND                   = 0x84

# Boolean ''or'' between each bit in the inputs.
OP_OR                    = 0x85

# Boolean ''exclusive or'' between each bit in the inputs.
OP_XOR                   = 0x86

# Returns 1 if the inputs are exactly equal, 0 otherwise.
OP_EQUAL                 = 0x87

# Same as OP_EQUAL, but runs OP_VERIFY afterward.
OP_EQUALVERIFY           = 0x88


###################
# Arithmetic

# 1 is added to the input.
OP_1ADD                  = 0x8b

# 1 is subtracted from the input.
OP_1SUB                  = 0x8c

# The input is multiplied by 2.
OP_2MUL                  = 0x8d

# The input is divided by 2.
OP_2DIV                  = 0x8e

# The sign of the input is flipped.
OP_NEGATE                = 0x8f

# The input is made positive.
OP_ABS                   = 0x90

# If the input is 0 or 1, it is flipped. Otherwise the output will be 0.
OP_NOT                   = 0x91

# Returns 0 if the input is 0. 1 otherwise.
OP_0NOTEQUAL             = 0x92

# a is added to b.
OP_ADD                   = 0x93

# b is subtracted from a.
OP_SUB                   = 0x94

# a is multiplied by b.
OP_MUL                   = 0x95

# a is divided by b.
OP_DIV                   = 0x96

# Returns the remainder after dividing a by b.
OP_MOD                   = 0x97

# Shifts a left b bits, preserving sign.
OP_LSHIFT                = 0x98

# Shifts a right b bits, preserving sign.
OP_RSHIFT                = 0x99

# If both a and b are not 0, the output is 1. Otherwise 0.
OP_BOOLAND               = 0x9a

# If a or b is not 0, the output is 1. Otherwise 0.
OP_BOOLOR                = 0x9b

# Returns 1 if the numbers are equal, 0 otherwise.
OP_NUMEQUAL              = 0x9c

# Same as OP_NUMEQUAL, but runs OP_VERIFY afterward.
OP_NUMEQUALVERIFY        = 0x9d

# Returns 1 if the numbers are not equal, 0 otherwise.
OP_NUMNOTEQUAL           = 0x9e

# Returns 1 if a is less than b, 0 otherwise.
OP_LESSTHAN              = 0x9f

# Returns 1 if a is greater than b, 0 otherwise.
OP_GREATERTHAN           = 0xa0

# Returns 1 if a is less than or equal to b, 0 otherwise.
OP_LESSTHANOREQUAL       = 0xa1

# Returns 1 if a is greater than or equal to b, 0 otherwise.
OP_GREATERTHANOREQUAL    = 0xa2

# Returns the smaller of a and b.
OP_MIN                   = 0xa3

# Returns the larger of a and b.
OP_MAX                   = 0xa4

# Returns 1 if x is within the specified range (left-inclusive), 0 otherwise.
OP_WITHIN                = 0xa5


###################
# Crypto

# The input is hashed using RIPEMD-160.
OP_RIPEMD160             = 0xa6

# The input is hashed using SHA-1.
OP_SHA1                  = 0xa7

# The input is hashed using SHA-256.
OP_SHA256                = 0xa8

# The input is hashed twice: first with SHA-256 and then with RIPEMD-160.
OP_HASH160               = 0xa9

# The input is hashed two times with SHA-256.
OP_HASH256               = 0xaa

# All of the signature checking words will only match signatures to the data
# after the most recently-executed OP_CODESEPARATOR.
OP_CODESEPARATOR         = 0xab

# The entire transaction's outputs, inputs, and script (from the most
# recently-executed OP_CODESEPARATOR to the end) are hashed. The signature
# used by OP_CHECKSIG must be a valid signature for this hash and public
# key. If it is, 1 is returned, 0 otherwise.
OP_CHECKSIG              = 0xac

# Same as OP_CHECKSIG, but OP_VERIFY is executed afterward.
OP_CHECKSIGVERIFY        = 0xad

# For each signature and public key pair, OP_CHECKSIG is executed. If more
# public keys than signatures are listed, some key/sig pairs can fail. All
# signatures need to match a public key. If all signatures are valid, 1 is
# returned, 0 otherwise. Due to a bug, one extra unused value is removed
# from the stack.
OP_CHECKMULTISIG         = 0xae

# Same as OP_CHECKMULTISIG, but OP_VERIFY is executed afterward.
OP_CHECKMULTISIGVERIFY   = 0xaf


###################
# Pseudo-words

# Represents a public key hashed with OP_HASH160.
OP_PUBKEYHASH            = 0xfd

# Represents a public key compatible with OP_CHECKSIG.
OP_PUBKEY                = 0xfe

# Matches any opcode that is not yet assigned.
OP_INVALIDOPCODE         = 0xff


###################
# Reserved words

# Transaction is invalid unless occuring in an unexecuted OP_IF branch
OP_RESERVED              = 0x50

# Transaction is invalid unless occuring in an unexecuted OP_IF branch
OP_VER                   = 0x62

# Transaction is invalid even when occuring in an unexecuted OP_IF branch
OP_VERIF                 = 0x65

# Transaction is invalid even when occuring in an unexecuted OP_IF branch
OP_VERNOTIF              = 0x66

# Transaction is invalid unless occuring in an unexecuted OP_IF branch
OP_RESERVED1             = 0x89

# Transaction is invalid unless occuring in an unexecuted OP_IF branch
OP_RESERVED2             = 0x8a

# The word is ignored.
OP_NOP1                  = 0xb0
OP_NOP2                  = 0xb1
OP_NOP3                  = 0xb2
OP_NOP4                  = 0xb3
OP_NOP5                  = 0xb4
OP_NOP6                  = 0xb5
OP_NOP7                  = 0xb6
OP_NOP8                  = 0xb7
OP_NOP9                  = 0xb8
OP_NOP10                 = 0xb9

DISABLED = frozenset([OP_CAT, OP_SUBSTR, OP_LEFT, OP_RIGHT, OP_INVERT, OP_AND,
                      OP_OR, OP_XOR, OP_2MUL, OP_2DIV, OP_MUL, OP_DIV, OP_MOD,
                      OP_LSHIFT, OP_RSHIFT])

RESERVED = frozenset([OP_RESERVED, OP_VER, OP_VERIF, OP_VERNOTIF, OP_RESERVED1,
                      OP_RESERVED2, OP_NOP1, OP_NOP2, OP_NOP3, OP_NOP4,
                      OP_NOP5, OP_NOP6, OP_NOP7, OP_NOP8, OP_NOP9, OP_NOP10])

OPCODE_NAMES = ['OP_FALSE', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A',
                'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A',
                'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A',
                'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A',
                'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A',
                'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A',
                'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A',
                'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A',
                'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A',
                'N/A', 'N/A', 'N/A', 'N/A', 'OP_PUSHDATA1', 'OP_PUSHDATA2',
                'OP_PUSHDATA4', 'OP_1NEGATE', 'OP_RESERVED', 'OP_TRUE',
                'OP_2', 'OP_3', 'OP_4', 'OP_5', 'OP_6', 'OP_7', 'OP_8',
                'OP_9', 'OP_10', 'OP_11', 'OP_12', 'OP_13', 'OP_14', 'OP_15',
                'OP_16', 'OP_NOP', 'OP_VER', 'OP_IF', 'OP_NOTIF', 'OP_VERIF',
                'OP_VERNOTIF', 'OP_ELSE', 'OP_ENDIF', 'OP_VERIFY',
                'OP_RETURN', 'OP_TOALTSTACK', 'OP_FROMALTSTACK', 'OP_2DROP',
                'OP_2DUP', 'OP_3DUP', 'OP_2OVER', 'OP_2ROT', 'OP_2SWAP',
                'OP_IFDUP', 'OP_DEPTH', 'OP_DROP', 'OP_DUP', 'OP_NIP',
                'OP_OVER', 'OP_PICK', 'OP_ROLL', 'OP_ROT', 'OP_SWAP',
                'OP_TUCK', 'OP_CAT', 'OP_SUBSTR', 'OP_LEFT', 'OP_RIGHT',
                'OP_SIZE', 'OP_INVERT', 'OP_AND', 'OP_OR', 'OP_XOR',
                'OP_EQUAL', 'OP_EQUALVERIFY', 'OP_RESERVED1', 'OP_RESERVED2',
                'OP_1ADD', 'OP_1SUB', 'OP_2MUL', 'OP_2DIV', 'OP_NEGATE',
                'OP_ABS', 'OP_NOT', 'OP_0NOTEQUAL', 'OP_ADD', 'OP_SUB',
                'OP_MUL', 'OP_DIV', 'OP_MOD', 'OP_LSHIFT', 'OP_RSHIFT',
                'OP_BOOLAND', 'OP_BOOLOR', 'OP_NUMEQUAL', 'OP_NUMEQUALVERIFY',
                'OP_NUMNOTEQUAL', 'OP_LESSTHAN', 'OP_GREATERTHAN',
                'OP_LESSTHANOREQUAL', 'OP_GREATERTHANOREQUAL', 'OP_MIN',
                'OP_MAX', 'OP_WITHIN', 'OP_RIPEMD160', 'OP_SHA1', 'OP_SHA256',
                'OP_HASH160', 'OP_HASH256', 'OP_CODESEPARATOR', 'OP_CHECKSIG',
                'OP_CHECKSIGVERIFY', 'OP_CHECKMULTISIG',
                'OP_CHECKMULTISIGVERIFY', 'OP_NOP1', 'OP_NOP2', 'OP_NOP3',
                'OP_NOP4', 'OP_NOP5', 'OP_NOP6', 'OP_NOP7', 'OP_NOP8',
                'OP_NOP9', 'OP_NOP10', None, None, None, None, None, None,
                None, None, None, None, None, None, None, None, None, None,
                None, None, None, None, None, None, None, None, None, None,
                None, None, None, None, None, None, None, None, None, None,
                None, None, None, None, None, None, None, None, None, None,
                None, None, None, None, None, None, None, None, None, None,
                None, None, None, None, None, None, None, None, None, None,
                None, 'OP_PUBKEYHASH', 'OP_PUBKEY', 'OP_INVALIDOPCODE']

def get_opcode_name(opcode):
    if opcode < 0 or opcode > 255:
        raise ValueError('opcode must be 1 byte')

    name = OPCODE_NAMES[opcode]
    if name is None: return OPCODE_NAMES[0xff]
    return name

def get_opcode(opcode_name):
    return OPCODE_NAMES.index(opcode_name)

def is_disabled(opcode):
    return opcode in DISABLES

def is_reserved(opcode):
    return opcode in RESERVED
