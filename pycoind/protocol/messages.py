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


import hashlib
import os
import struct

import format

from .. import util

__all__ = ['MessageFormatException', 'Message', 'UnknownMessageException',

           'Address', 'Alert', 'Block', 'GetAddress', 'GetBlocks', 'GetData',
           'GetHeaders', 'Headers', 'Inventory', 'MemoryPool', 'NotFound',
           'Ping', 'Pong', 'Reject', 'Transaction', 'Version', 'VersionAck']


def _debug(obj, params):
    message = ['<%s' % obj.__class__.__name__]
    for (k, v) in params:
        if isinstance(v, (list, tuple)):
            message.append(('len(%s)=%d' % (k, len(v))))
            if len(v):
                k = '%s[0]' % k
                v = v[0]

        if v:
            if isinstance(v, format.NetworkAddress):
                text = '%s:%d' % (v.address, v.port)
            elif isinstance(v, format.InventoryVector):
                obj_type = 'unknown'
                if v.object_type <= 2:
                    obj_type = ['error', 'tx', 'block'][v.object_type]
                text = '%s:%s' % (obj_type, v.hash.encode('hex'))
            elif isinstance(v, format.Txn):
                text = v.hash.encode('hex')
            elif isinstance(v, format.BlockHeader):
                text = v.hash.encode('hex')
            else:
                text = str(v)
            message.append(('%s=%s' % (k, text)))

    return " ".join(message) + '>'


# Raised if the message command is not registered
class UnknownMessageException(Exception): pass


# Raised if there was a problem with the header
class MessageFormatException(Exception): pass


class Message(format.CompoundType):
    '''A message object. This base class is responsible for serializing and
       deserializing binary network payloads.

       Each message sub-class should specify an array of (name, FormatType)
       tuples named properties. See below for examples.

       Message subclasses will automatically be registered, unless they set
       do_not_register = True.

       Messages are rigorously type checked for the properties that are given
       to ensure the bytes over the wire will be what was expected.'''

    command = None

    do_not_register = False

    properties = []

    # Only parsed messages will have a magic number
    _magic = None
    magic = property(lambda s: s._magic)

    def binary(self, magic):
        'Returns the binary representation of the message.'

        payload = format.CompoundType.binary(self)

        checksum = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]

        # pad the command
        command = self.command + (chr(0) * (12 - len(self.command)))

        # header + payload
        return magic + command + struct.pack('<I', len(payload)) + checksum + payload


    MessageTypes = dict()

    @staticmethod
    def register(message_type):
        'Register a new message type.'

        Message.MessageTypes[message_type.command] = message_type


    @staticmethod
    def first_message_length(data):
        '''Returns the length of the first message with beginning bytes of
           data, or None if the length cannot be determined (yet).'''

        # not enough to even determine payload size
        if len(data) < 20:
            return None

        return struct.unpack('<I', data[16:20])[0] + 24


    @classmethod
    def parse(cls, data, magic):

        # check magic number
        if data[0:4] != magic:
            raise MessageFormatException('bad magic number')

        # get binary payload
        (length, ) = struct.unpack('<I', data[16:20])
        payload = data[24:24 + length]

        # check the checksum
        checksum = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
        if data[20:24] != checksum:
            raise MessageFormatException('bad checksum')

        # get the correct class for this message's command
        command = data[4:16].strip(chr(0))
        message_type = cls.MessageTypes.get(command)

        if message_type is None:
            raise UnknownMessageException('command: %r (%r)' % (command, data))

        # parse the properties using the correct class's parse
        (vl, message) = super(Message, message_type).parse(payload)
        message._magic = magic

        return message


    @property
    def name(self):
        '''Should be overridden in sub-classes whose name differs from its
        command. For example, the "addr" command's name is "address".

        The name determines which command_* will be called on a node.'''

        return self.command


    def _debug(self):
         return _debug(self, [])


class Version(Message):
    command = "version"

    properties = [
        ('version', format.FormatTypeNumber('i')),
        ('services', format.FormatTypeNumber('Q')),
        ('timestamp', format.FormatTypeNumber('q', allow_float = True)),
        ('addr_recv', format.FormatTypeNetworkAddressWithoutTimestamp()),
        ('addr_from', format.FormatTypeNetworkAddressWithoutTimestamp()),
        ('nonce', format.FormatTypeBytes(8)),
        ('user_agent', format.FormatTypeVarString()),
        ('start_height', format.FormatTypeNumber('i')),
        ('relay', format.FormatTypeOptional(format.FormatTypeNumber('B'), True)),
    ]

    def _debug(self):
        return _debug(self,[
            ('v', self.version),
            ('s', self.services),
            ('ua', self.user_agent),
            ('sh', self.start_height),
        ])

class VersionAck(Message):
    command = 'verack'
    name = "version_ack"


class Address(Message):
    command = 'addr'
    name = "address"

    properties = [
        ('addr_list', format.FormatTypeArray(format.FormatTypeNetworkAddress(), max_length = 1000)),
    ]

    def _debug(self):
        return _debug(self, [('a', self.addr_list)])



class Inventory(Message):
    command = 'inv'
    name = "inventory"

    properties = [
        ('inventory', format.FormatTypeArray(format.FormatTypeInventoryVector(), max_length = 50000)),
    ]

    def _debug(self):
        return _debug(self, [('i', self.inventory)])


class GetData(Inventory):
    command = "getdata"
    name = "get_data"


class NotFound(Inventory):
    command = "notfound"
    name = "not_found"


class GetBlocks(Message):
    command = "getblocks"
    name = "get_blocks"

    properties = [
        ('version', format.FormatTypeNumber('I')),
        ('block_locator_hashes', format.FormatTypeArray(format.FormatTypeBytes(32), 1)),
        ('hash_stop', format.FormatTypeBytes(32)),
    ]

    def _debug(self):
        return _debug(self, [('blh', [h.encode('hex') for h in self.block_locator_hashes])])


class GetHeaders(GetBlocks):
    command = "getheaders"
    name = "get_headers"


class Transaction(Message):
    command = "tx"
    name = "transaction"

    properties = [
        ('version', format.FormatTypeNumber('I')),
        ('tx_in', format.FormatTypeArray(format.FormatTypeTxnIn(), 1)),
        ('tx_out', format.FormatTypeArray(format.FormatTypeTxnOut(), 1)),
        ('lock_time', format.FormatTypeNumber('I')),
    ]

    def _debug(self):
        return _debug(self, [('in', self.tx_in), ('out', self.tx_out)])

class Block(Message):
    command = "block"

    properties = [
        ('version', format.FormatTypeNumber('I')),
        ('prev_block', format.FormatTypeBytes(32)),
        ('merkle_root', format.FormatTypeBytes(32)),
        ('timestamp', format.FormatTypeNumber('I', allow_float = True)),
        ('bits', format.FormatTypeNumber('I')),
        ('nonce', format.FormatTypeNumber('I')),
        ('txns', format.FormatTypeArray(format.FormatTypeTxn())),
    ]

    @staticmethod
    def from_block(block):
        return Block(block.version, block.previous_block_hash,
                     block.merkle_root, block.timestamp, block.bits,
                     block.nonce, block.transactions)

    def _debug(self):
        block_hash = util.get_block_header(self.version,
                                           self.prev_block,
                                           self.merkle_root,
                                           self.timestamp,
                                           self.bits,
                                           self.nonce)
        return _debug(self, [('h', block_hash.encode('hex')), ('t', self.txns)])

class Headers(Message):
    command = "headers"

    properties = [
      ('headers', format.FormatTypeArray(format.FormatTypeBlockHeader())),
    ]

    def _debug(self):
        return _debug(self, [('h', self.headers)])


class GetAddress(VersionAck):
    command = "getaddr"
    name = "get_address"


class MemoryPool(VersionAck):
    command = "mempool"
    name = "memory_pool"


class Ping(Message):
    command = 'ping'

    properties = [
      ('nonce', format.FormatTypeBytes(8)),
    ]

    def _debug(self):
        return _debug(self, [('n', self.nonce.encode('hex'))])


class Pong(Ping):
    command = "pong"


class Reject(Message):
    command = "reject"

    properties = [
      ('message', format.FormatTypeVarString()),
      ('ccode', format.FormatTypeNumber('B')),
      ('reason', format.FormatTypeVarString()),
    ]

    def _debug(self):
        return _debug(self, [('m', self.message), ('r', self.reason)])

class FilterLoad(Message):
    command = "filterload"
    name = "filter_load"

    do_not_register = True

    properties = [
        ('filter', format.FormatTypeArray(format.FormatTypeNumber('B'))),
        ('n_hashes_func', format.FormatTypeNumber('I')),
        ('n_tweak', format.FormatTypeNumber('I')),
        ('n_flags', format.FormatTypeNumber('B')),
    ]


class FilterLoad(Message):
    command = "filteradd"
    name = "filter_add"

    do_not_register = True

    properties = [
        ('data', format.FormatTypeVarString()),
    ]


class FilterClear(VersionAck):
    command = "filterclear"
    name = "filter_clear"

    do_not_register = True


class MerkleBlock(Message):
    command = "merkleblock"
    name = "merkle_block"

    do_not_register = True

    properties = [
        ('version', format.FormatTypeNumber('I')),
        ('prev_block', format.FormatTypeBytes(32)),
        ('merkle_root', format.FormatTypeBytes(32)),
        ('timestamp', format.FormatTypeNumber('I', allow_float = True)),
        ('bits', format.FormatTypeNumber('I')),
        ('nonce', format.FormatTypeNumber('I')),
        ('total_transactions', format.FormatTypeNumber('I')),
        ('hashes', format.FormatTypeArray(format.FormatTypeBytes(32))),
        ('flags', format.FormatTypeArray(format.FormatTypeNumber('b'))),
    ]


class Alert(Message):
    command = "alert"

    properties = [
        ('payload', format.FormatTypeVarString()),
        ('signature', format.FormatTypeVarString())
    ]

    payload_properties = [
        'version', 'relay_until', 'expiration', 'id', 'cancel', 'set_cancel',
        'min_ver', 'max_ver', 'set_sub_ver', 'priority', 'comment',
        'status_bar', 'reserved'
    ]

    # Alert is a special... The binary packed format contains additional info
    # See: https://en.bitcoin.it/wiki/Protocol_specification#alert
    version = property(lambda s: s._parse_and_get('version'))
    relay_until = property(lambda s: s._parse_and_get('relay_until'))
    expiration = property(lambda s: s._parse_and_get('expiration'))
    id = property(lambda s: s._parse_and_get('id'))
    cancel = property(lambda s: s._parse_and_get('cancel'))
    set_cancel = property(lambda s: s._parse_and_get('set_cancel'))
    min_ver = property(lambda s: s._parse_and_get('min_ver'))
    max_ver = property(lambda s: s._parse_and_get('max_ver'))
    set_sub_ver = property(lambda s: s._parse_and_get('set_sub_ver'))
    priority = property(lambda s: s._parse_and_get('priority'))
    comment = property(lambda s: s._parse_and_get('comment'))
    status_bar = property(lambda s: s._parse_and_get('status_bar'))
    reserved = property(lambda s: s._parse_and_get('reserved'))

    # The above properties will use this method to extract and cache everything
    def _parse_and_get(self, name):

        if not hasattr(self, '_data'):
            self._data = dict()

        if not self._data:
            data = self.payload

            self._data = dict()

            offset = 0

            # extract version, relay_until, expiration, id and cancel
            (v, r, e, i, c) = struct.unpack('<iqqii', data[offset:offset + 28])
            self._data['version'] = v
            self._data['relay_until'] = r
            self._data['expiration'] = e
            self._data['id'] = i
            self._data['cancel'] = c
            offset += 28

            # extract the set of alerts this alert cancels
            (vl, s) = format.parse_variable_set(data[offset:], format.FormatTypeNumber('i'))
            self._data['set_cancel'] = s
            offset += vl

            # extract minimum and maximum versions affecte by this alert
            (minver, maxver) = struct.unpack('<ii', data[offset:offset + 8])
            self._data['min_ver'] = minver
            self._data['max_ver'] = maxver
            offset += 8

            # extract the set of sub-versions affected by this alert
            (vl, s) = format.parse_variable_set(data[offset:], format.FormatTypeVarString())
            self._data['set_sub_ver'] = s
            offset += vl

            # extract priority
            (p, ) = struct.unpack('<i', data[offset:offset + 4])
            self._data['priority'] = p
            offset += 4

            # extract comment (no need to display)
            (vl, c) = format.FormatTypeVarString.parse(data[offset:])
            self._data['comment'] = c
            offset += vl

            # extract status bar message (should be shown in the UI)
            (vl, s) = format.FormatTypeVarString.parse(data[offset:])
            self._data['status_bar'] = s
            offset += vl

            # just incase *this* is an old version and the new format includes
            # extra stuff, we can still view it
            (vl, r) = format.FormatTypeVarString.parse(data[offset:])
            self._data['reserved'] = r
            offset += vl

        return self._data[name]

    def verify(self, public_key):
        return util.ecc.verify(self.payload, public_key, self.signature)

    def __str__(self):
        return '<message.Alert version=%d relay_until=%d expiration=%d id=%d cancel=%d cancel_set=[%s] min_ver=%d maxver=%d set_sub_ver=[%s] priority=%s comment=%r status_bar=%r reserverd=%r>' % (self.version, self.relay_until, self.expiration, self.id, self.cancel, ", ".join(str(i) for i in self.set_cancel), self.min_ver, self.max_ver, ", ".join(self.set_sub_ver), self.priority, self.comment, self.status_bar, self.reserved)


    def _debug(self):
        return _debug(self, [('s', self.status_bar)])
