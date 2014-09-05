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


import struct

from .. import util

def parse_variable_set(data, kind):
    '''Reads a set of Parsable objects prefixed with a VarInteger.

       Any object can be used that supports parse(data), which returns
       a tuple of (bytes_consumed, value).'''

    (offset, count) = FormatTypeVarInteger.parse(data)

    result = [ ]
    index = 0

    while index < count:
        (item_length, item_obj) = kind.parse(data[offset:])
        result.append(item_obj)
        index += 1
        offset += item_length

    return (offset, result)


class ParameterException(Exception):
    def __init__(self, name, value, kind = None):
        if kind is None: kind = type(value)
        Exception.__init__(self, "Bad Parameter: %s = %r (%s)" % (name, value, kind))
        self._name = name
        self._value = value
        self._kind = kind

    name = property(lambda s: s._name)
    value = property(lambda s: s._value)
    kind = property(lambda s: s._kind)


# This metaclass will convert all the (name, kind) pairs in properties into
# class properties and if the base class has a register(cls) method, call it.
class _AutoPopulateAndRegister(type):

    def __init__(cls, name, bases, dct):
        super(_AutoPopulateAndRegister, cls).__init__(name, bases, dct)

        for (key, vt) in cls.properties:
            def get_parameter(k):
                return property(lambda s: s._properties[k])
            setattr(cls, key, get_parameter(key))

        cls._name = name

        for base in bases:
            if hasattr(base, 'register'):
                if hasattr(base, 'do_not_register') and not base.do_not_register:
                    base.register(cls)
                break

#import time
#profile = dict(count = 0)

class CompoundType(object):
    properties = []

    def __init__(self, *args, **kw):
        keys = [k for (k, t) in self.properties]

        # convert the positional arguments into keywords
        params = dict(zip(keys, args))

        # did we specify a parameter both positionally and as a keyword?
        for k in kw:
            if k in params:
                raise TypeError('got multiple values for keyword argument %r' % k)

        # do we have any unknown keywords?
        keys = set(keys)
        for k in kw:
            if k not in keys:
                raise TypeError('got an unexpected keyword argument %r' % k)

        # add in the keyword arguments
        params.update(kw)

        # check for the correct number of properties
        if len(params) != len(keys):
            suffix = ''
            if suffix != 1: suffix = 's'
            raise TypeError("takes exactly %d argument%s (%d given)" % (len(keys), suffix, len(params)))

        # verify all properties and convert to immutable types.
        for (key, vt) in self.properties:
            value = vt.validate(params[key])
            if value is None:
                 raise ParameterException(key, params[key])
            params[key] = value

        self._properties = params


    __metaclass__ = _AutoPopulateAndRegister

    def binary(self):
        'Returns the binary representation of the message.'
        return "".join(vt.binary(self._properties[key]) for (key, vt) in self.properties)


    @classmethod
    def parse(cls, data):
        #t0 = time.time()

        kw = dict()
        offset = 0
        for (key, vt) in cls.properties:
            try:
                (length, kw[key]) = vt.parse(data[offset:])
                offset += length
            except Exception, e:
                raise ParameterException(key, data[offset:], vt)

        #dt = time.time() - t0
        #if cls not in profile: profile[cls] = [0.0, 0]
        #profile[cls][0] += dt
        #profile[cls][1] += 1
        #profile['count'] += 1
        #if profile['count'] % 100000 == 0:
        #    print "PROFILE"
        #    for key in profile:
        #        if key == 'count': continue
        #        (t, c) = profile[key]
        #        print '  %s: %f ms/call (%d calls, %f total time)' % (key.__name__, 1000 * t / c, c, t)

        # create without __init__ (would unnecessarily verify the parameters)
        self = cls.__new__(cls)
        self._properties = kw
        return (offset, self)


    def __str__(self):
        output = [self._name]
        for (key, vt) in self.properties:
            output.append('%s=%s' % (key, vt.str(self._properties[key])))

        return '<%s>' % " ".join(output)


class FormatType(object):

    def validate(self, obj):
        '''Returns the object to store if obj is valid for this type, otherwise
           None. The type returned should be immutable.'''

        raise NotImplemented()

    def binary(self, obj):
        'Returns the binary form for this type.'

        raise NotImplemented()

    def parse(self, data):
        '''Returns a (length, value) tuple where length is the amount of
         data that was consumed.'''

        raise NotImplemented()

    def str(self, obj):
        return str(obj)

    def __str__(self):
        cls = str(self.__class__).split('.')[-1].strip(">'")
        return '<%s>' % cls


class FormatTypeCompoundType(object):
    expected_type = None

    @classmethod
    def validate(cls, obj):
        if isinstance(obj, cls.expected_type):
            return obj
        return None

    @staticmethod
    def binary(obj):
        return obj.binary()

    @classmethod
    def parse(cls, data):
        return cls.expected_type.parse(data)

    @classmethod
    def str(cls, obj):
        return str(obj)


class FormatTypeOptional(FormatType):
    def __init__(self, child, default):
        self._child = child
        self._default = default

    def validate(self, obj):
        try:
            value = self._child.validate(obj)
            if value is not None:
                return value
        except Exception, e:
            print e

        return self._default

    def binary(self, obj):
        return self._child.binary(obj)

    def parse(self, data):
        try:
            return self._child.parse(data)
        except Exception, e:
            pass
        return (0, self._default)

    def __str__(self):
        return '<FormatTypeOptional child=%s default=%s>' % (self._child, self._default)

    def str(self, obj):
        return self._child.str(obj)

# Simple formats (don't use any CompoundTypes nor FormatTypes)

class FormatTypeNumber(FormatType):
    '''Number format.

       Allows the object type to be the expected_type (default: int) using
       the endian and format to pack the value (default: little endian, signed
       4-byte integer).

       A tuple can be passed in for expected_type to accept multiple types.

       Possible Formats:
           b, B - signed, unsigned 1-byte char
           i, I - signed, unsigned 4-byte integer
           q, Q - signed, unsigned 8-byte integer'''


    def __init__(self, format = 'i', big_endian = False, allow_float = False):
        if format not in self._ranges:
            raise ValueError('invalid format type: %s' % format)
        self._format = {True: '>', False: '<'}[big_endian] + format
        self._allow_float = allow_float

    _ranges = dict(
        b = (-128, 128),
        B = (0, 256),
        h = (-32768, 32768),
        H = (0, 65536),
        i = (-2147483648, 2147483648),
        I = (0, 4294967296),
        q = (-9223372036854775808L, 9223372036854775808L),
        Q = (0, 18446744073709551616L)
    )

    def validate(self, obj):

        # check type
        if not (self._allow_float and isinstance(obj, float)):
            if self._format[1] in 'qQ':
                if not isinstance(obj, (int, long)):
                    return None
            elif not isinstance(obj, int):
                return None

        # check valid range
        (min_value, max_value) = self._ranges[self._format[1]]
        if min_value <= obj < max_value:
            return obj

        return None

    def binary(self, obj):
        return struct.pack(self._format, int(obj))

    def parse(self, data):
        length = dict(b = 1, h = 2, i = 4, q = 8)[self._format.lower()[-1]]
        return (length, struct.unpack(self._format, data[:length])[0])

    def __str__(self):
        return '<FormatTypeNumber format=%s>' % (self._format, self._expected_type)


class FormatTypeVarInteger(FormatType):

    @staticmethod
    def validate(obj):
        if isinstance(obj, int):
            return obj
        return None

    @staticmethod
    def binary(obj):
        if obj < 0xfd:
            return struct.pack('<B', obj)
        elif obj < 0xffff:
            return chr(0xfd) + struct.pack('<H', obj)
        elif obj < 0xffffffff:
            return chr(0xfe) + struct.pack('<I', obj)
        return chr(0xff) + struct.pack('<Q', obj)

    @staticmethod
    def parse(data):
        value = ord(data[0])
        if value == 0xfd:
            return (3, struct.unpack('<H', data[1:3])[0])
        elif value == 0xfe:
            return (5, struct.unpack('<I', data[1:5])[0])
        elif value == 0xfd:
            return (9, struct.unpack('<Q', data[1:9])[0])
        return (1, value)

    def str(self, obj):
        return str(obj)


# @TODO: test ipv6...
class FormatTypeIPAddress(FormatType):

    @staticmethod
    def _ipv4_groups(obj):

        # convert each group to its value
        try:
            groups = map(int, obj.split('.'))
        except ValueError, e:
            return None

        # too many or not enough groups
        if len(groups) != 4:
            return None

        # is each group in the correct range?
        for group in groups:
            if not (0x00 <= group <= 0xff):
                return None

        return groups

    @staticmethod
    def _ipv6_groups(obj):

        # multiple double-colons or more than 8 groups; bad address
        objs = obj.split(':')
        if objs.count('') > 1 or len(objs) > 8:
            return None

        # calculate each group's value
        groups = [ ]
        for group in objs:
            if group == '':
                groups.extend([ 0 ] * (8 - len(objs)))
            else:
                groups.append(int(group, 16))

        # is each group in the correct range?
        for group in groups:
            if not (0x0000 <= group <= 0xffff):
                return None

        return groups

    @staticmethod
    def validate(obj):
        if not isinstance(obj, str):
            return None

        if FormatTypeIPAddress._ipv4_groups(obj) is not None:
            return obj

        if FormatTypeIPAddress._ipv6_groups(obj) is not None:
            return obj

        return None

    @staticmethod
    def parse(data):
        if data[0:10] == (chr(0) * 10) and data[10:12] == (chr(255) * 2):
            return (16, '.'.join(str(i) for i in struct.unpack('>BBBB', data[12:16])))
        return (16, ':'.join(("%x" % i) for i in struct.unpack('>HHHHHHHH', data[:16])))

    def binary(self, obj):

        groups = self._ipv4_groups(obj)
        if groups is not None:
            return (chr(0) * 10) + (chr(255) * 2) + struct.pack('>BBBB', * groups)

        groups = self._ipv6_groups(obj)
        if groups is not None:
            return struct.pack('>HHHHHHHH', *groups)

        raise Exception('should not be able to reach here')


class FormatTypeBytes(FormatType):
    '''String format.

       Allows the object to be a fixed length string.'''


    def __init__(self, length):
        self._length = length

    def validate(self, obj):
        if isinstance(obj, str) and len(obj) == self._length:
            return obj
        return None

    def binary(self, obj):
        return obj

    def parse(self, data):
        return (self._length, data[:self._length])

    def str(self, obj):
        return '0x' + obj.encode('hex')

    def __str__(self):
        return '<FormatTypeBytes length=%d>' % self._length


class FormatTypeVarString(FormatType):
    '''VarString format.

       The parameter must be a string, but may have variable length.'''

    @staticmethod
    def validate(obj):
        if isinstance(obj, str):
            return obj
        return None

    @staticmethod
    def binary(obj):
        return FormatTypeVarInteger.binary(len(obj)) + obj

    @staticmethod
    def parse(data):
        (vl, length) = FormatTypeVarInteger.parse(data)
        obj = data[vl:vl + length]
        return (vl + len(obj), obj)

    def str(self, obj):
        return repr(obj)


class FormatTypeArray(FormatType):
    '''Array format.

       The properties must be an array of objects, each of child_type. If
       min_length is specified, the array must contain at least that many
       children.

       A tuple is returned to ensure the structure is immutable.'''

    def __init__(self, child_type, min_length = None, max_length = None):
        self._child_type = child_type
        self._min_length = min_length
        self._max_length = max_length

    def validate(self, obj):
        if not isinstance(obj, (list, tuple)):
            return None

        if self._min_length and len(obj) < self._min_length:
            return None

        if self._max_length and len(obj) > self._max_length:
            return None

        obj = [self._child_type.validate(o) for o in obj]

        if None in obj:
            return None

        return tuple(obj)

    def binary(self, obj):
        return (FormatTypeVarInteger.binary(len(obj)) +
                "".join(self._child_type.binary(o) for o in obj))

    def parse(self, data):
        return parse_variable_set(data, self._child_type)

    def str(self, obj):
        return "[%s]" % ", ".join(self._child_type.str(o) for o in obj)

    def __str__(self):
        return '<FormatTypeArray child=%s length=[%s, %s]>' % (self._child_type, self._min_length, self._max_length)


#class FormatTypeRemaining(FormatType):
#    def validate(self, obj):
#        if isinstance(obj, str):
#            return obj
#        return None
#
#    def binary(self, obj):
#        return obj
#
#    def parse(self, data):
#        return (len(data), data)
#
#    def str(self, obj):
#        return '0x' + obj.encode('hex')


# Network Address types and format

class NetworkAddress(CompoundType):

    properties = [
        ('timestamp', FormatTypeNumber('I', allow_float = True)),
        ('services', FormatTypeNumber('Q')),
        ('address', FormatTypeIPAddress()),
        ('port', FormatTypeNumber('H', big_endian = True)),
    ]


class FormatTypeNetworkAddress(FormatTypeCompoundType):
    '''NetowrkAddress format.

       The properties must be a NetworkAddress.'''

    expected_type = NetworkAddress


class FormatTypeNetworkAddressWithoutTimestamp(FormatTypeNetworkAddress):
    '''NetowrkAddress format.

       The properties must be a NetworkAddress. The timestamp will be zero
       when deserialized and will be ommitted when serialized'''

    @classmethod
    def parse(cls, data):
        (vl, obj) = FormatTypeNetworkAddress.parse((chr(0) * 4) + data)
        return (vl - 4, obj)

    def binary(self, obj):
        return FormatTypeNetworkAddress.binary(obj)[4:]


# Inventory Vectors type and format

class InventoryVector(CompoundType):
    properties = [
        ('object_type', FormatTypeNumber('I')),
        ('hash', FormatTypeBytes(32)),
    ]


class FormatTypeInventoryVector(FormatTypeCompoundType):
    '''InventoryVector format.

       The properties must be an InventoryVector.'''

    expected_type = InventoryVector


# Txn types and formats

class OutPoint(CompoundType):
    properties = [
        ('hash', FormatTypeBytes(32)),
        ('index', FormatTypeNumber('I')),
    ]

    def __hash__(self):
        return hash((self.hash, self.index))

    def __eq__(self, other):
        if not isinstance(other, OutPoint):
            return False
        return (self.hash == other.hash) and (self.index == otehr.index)


class FormatTypeOutPoint(FormatTypeInventoryVector):
    expected_type = OutPoint


class TxnIn(CompoundType):
    properties = [
        ('previous_output', FormatTypeOutPoint()),
        ('signature_script', FormatTypeVarString()),
        ('sequence', FormatTypeNumber('I')),
    ]


class FormatTypeTxnIn(FormatTypeCompoundType):
    '''TxnIn format.

       The properties must be a TxnIn.'''

    expected_type = TxnIn


class TxnOut(CompoundType):
    properties = [
        ('value', FormatTypeNumber('q')),
        ('pk_script', FormatTypeVarString()),
    ]


class FormatTypeTxnOut(FormatTypeCompoundType):
    '''TxnOut format.

       The properties must be a TxnOut.'''

    expected_type = TxnOut


class Txn(CompoundType):
    properties = [
        ('version', FormatTypeNumber('I')),
        ('tx_in', FormatTypeArray(FormatTypeTxnIn, 1)),
        ('tx_out', FormatTypeArray(FormatTypeTxnOut, 1)),
        ('lock_time', FormatTypeNumber('I')),
    ]

    @property
    def hash(self):
        if '__hash' not in self._properties:
            self._properties['__hash'] = util.sha256d(self.binary())
        return self._properties['__hash']


class FormatTypeTxn(FormatTypeInventoryVector):
    '''Txn format.

       The properties must be a Txn.'''

    expected_type = Txn




# Block Header type and format

class BlockHeader(CompoundType):
    properties = [
        ('version', FormatTypeNumber('I')),
        ('prev_block', FormatTypeBytes(32)),
        ('merkle_root', FormatTypeBytes(32)),
        ('timestamp', FormatTypeNumber('I', allow_float = True)),
        ('bits', FormatTypeNumber('I')),
        ('nonce', FormatTypeNumber('I')),
        ('txn_count', FormatTypeVarInteger()),
    ]

    @staticmethod
    def from_block(block):
        return BlockHeader(block.version, block.previous_hash,
                           block.merkle_root, block.timestamp,
                           block.bits, block.nonce,
                           len(block.transactions))

    @property
    def hash(self):
        if '__hash' not in self._properties:
            self._properties['__hash'] = util.sha256d(self.binary()[:80])
        return self._properties['__hash']


class FormatTypeBlockHeader(FormatTypeInventoryVector):
    '''BlockHeader format.

       The properties must be a BlockHeader.'''

    expected_type = BlockHeader



