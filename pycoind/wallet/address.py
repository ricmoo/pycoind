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

import os
import struct
import unicodedata

from .. import coins
from .. import util

from ..util.ecdsa import SECP256k1 as curve
from ..util.ecdsa.util import string_to_number, number_to_string, randrange
from ..util.pyaes.aes import AES

__all__ = ['Address', 'EncryptedAddress', 'get_address', 'PrintedAddress']

class BaseAddress(object):
    def __init__(self, private_key, coin = coins.Bitcoin):
        self._private_key = private_key
        self._coin = coin

    coin = property(lambda s: s._coin)

    private_key = property(lambda s: s._private_key)

    @property
    def _privkey(self):
        'The binary representation of a private key.'

        if self.private_key is None:
            return None
        return util.key.privkey_from_wif(self.private_key)



class Address(BaseAddress):
    '''Wallet Address.

       Provide exactly one of:
         private_key    WIF encoded private key (compressed or uncompressed)
         public_key     binary public key (compressed or uncompressed)'''

    def __init__(self, public_key = None, private_key = None, coin = coins.Bitcoin):
        BaseAddress.__init__(self, private_key, coin)

        self._compressed = False

        if private_key:
            if public_key is not None:
                raise ValueError('cannot specify public_key and private_key')

            self._private_key = private_key

            # this is a compressed private key
            if private_key.startswith('L') or private_key.startswith('K'):
                self._compressed = True
            elif not private_key.startswith('5'):
                raise ValueError('unknown private key type: %r' % private_key[0])

            # determine the public key (internally, we only store uncompressed)
            secexp = string_to_number(util.key.privkey_from_wif(self._private_key))
            point = curve.generator * secexp
            public_key = _key_from_point(point, False)

        else:
            self._private_key = None

        if public_key:

            # we store the public key decompressed
            if public_key[0] == chr(0x04):
                if len(public_key) != 65:
                    raise ValueError('invalid uncomprssed public key')
            elif public_key[0] in (chr(0x02), chr(0x03)):
                public_key = util.key.decompress_public_key(public_key)
                self._compressed = True
            else:
                raise ValueError('invalid public key')

            self._public_key = public_key

        # we got no parameters
        else:
            raise ValueError('no address parameters')

        # determine the address
        self._address = util.key.publickey_to_address(self.public_key, version = coin.address_version)

    @property
    def public_key(self):
        'The public key, compressed if the address is compressed.'
        if self._compressed:
            return util.key.compress_public_key(self._public_key)
        return self._public_key

    address = property(lambda s: s._address)

    compressed = property(lambda s: s._compressed)

    @staticmethod
    def generate(compressed = True, coin = coins.Bitcoin):
        'Generate a new random address.'

        secexp = randrange(curve.order)
        key = number_to_string(secexp, curve.order)
        if compressed:
            key = key + chr(0x01)
        return Address(private_key = util.key.privkey_to_wif(key), coin = coin)

    @staticmethod
    def from_binary(binary_key, compressed = True):
        '''Returns a key associated with a 32-byte key. This is useful for
           brain wallets or wallets generated from other sources of entropy.'''

        if len(binary_key) == 32:
            key = string_to_number(binary_key)
            if 1 <= key < curve.order:
                if compressed:
                    binary_key += chr(0x01)
                private_key = util.key.privkey_to_wif(binary_key)
                return Address(private_key = private_key)

        raise ValueError('invalid binary key')

    def decompress(self):
        'Returns the decompressed address.'

        if not self.compressed: return self

        if self.private_key:
            return Address(private_key = util.key.privkey_to_wif(self._privkey), coin = self.coin)

        if address.public_key:
            return Address(public_key = util.key.decompress_public_key(self.public_key), coin = self.coin)

        raise ValueError('address cannot be decompressed')

    def compress(self):
        'Returns the compressed address.'

        if self.compressed: return self

        if self.private_key:
            return Address(private_key = util.key.privkey_to_wif(self._privkey + chr(0x01)), coin = self.coin)

        if address.public_key:
            return Address(public_key = util.key.compress_public_key(self.public_key), coin = self.coin)

        raise ValueError('address cannot be compressed')

    def encrypt(self, passphrase):
        'Return an encrypted address using  passphrase.'

        if self.private_key is None:
            raise ValueError('cannot encrypt address without private key')

        return _encrypt_private_key(self.private_key, passphrase, self.coin)

    def sign(self, data):
        "Signs data with this address' private key."

        if self.private_key is None: raise Exception()
        pk = util.key.privkey_from_wif(self.private_key, self.coin.address_version)
        return util.ecc.sign(data, pk)

    def verify(self, data, signature):
        "Verifies the data and signature with this address' public key."

        if self.public_key is None: raise Exception()
        return util.ecc.verify(data, self._public_key, signature)

    def __str__(self):
        private_key = 'None'
        if self.private_key: private_key = '**redacted**'
        return '<Address address=%s public_key=%s private_key=%s>' % (self.address, self.public_key.encode('hex'), private_key)


# See: https://github.com/bitcoin/bips/blob/master/bip-0038.mediawiki
class EncryptedAddress(BaseAddress):

    def __init__(self, private_key, coin = coins.Bitcoin):
        BaseAddress.__init__(self, private_key, coin)

        privkey = self._privkey
        if len(privkey) != 39 or privkey[0:2] not in ('\x01\x42', '\x01\x43'):
            raise ValueError('unsupported encrypted address')

        self._compressed = bool(ord(privkey[2]) & 0x20)

    # encrypted addresses don't use the standard wif prefix
    _privkey = property(lambda s: util.base58.decode_check(s.private_key))

    compressed = property(lambda s: s._compressed)

    @staticmethod
    def generate(passphrase, compressed = True, coin = coins.Bitcoin):
        'Generate a new random address encrypted with passphrase.'

        address = Address.generate(compressed, coin)
        return EncryptedAddress.encrypt_address(address, passphrase, compressed)

    def decrypt(self, passphrase):
        'Return a decrypted address of this address, using passphrase.'

        # what function do we use to decrypt?
        if self._privkey[1] == chr(0x42):
            decrypt = _decrypt_private_key
        else:
            decrypt = _decrypt_printed_private_key

        return decrypt(self.private_key, passphrase, self.coin)

    def __str__(self):
        return '<EncryptedAddress private_key=%s>' % self.private_key


class PrintedAddress(Address):
    """This should not be instantiated directly. Use:

          EncryptedAddress(printed_private_key).decrypt(passphrase)

       If Alice wishes Bob to create private keys for her, she can come up with
       a secure passphrase, which she uses to generate an intermediate code
       (EncryptedAddress.generate_intermediate_code) which can be given to Bob.
       Bob is no able to create new EncryptedPrintedAddresses, for which he can
       determine the address and public key, but is unable to determine the
       decrypted private key. He then provides Alice the encrypted private key,
       which Alice can then decrypt using her passphrase, to get the decrypted
       private key."""

    def __init__(self):
        raise ValueError('cannot instantiate a PrintedAddress')

    lot = property(lambda s: s._lot)
    sequence = property(lambda s: s._sequence)

    @staticmethod
    def generate_intermediate_code(passphrase, lot = None, sequence = None):
        '''Generates an intermediate code for generated printed addresses
           using passphrase and optional lot and sequence.'''

        return _generate_intermediate_code(passphrase, lot, sequence)

    @staticmethod
    def generate(intermediate_code, coin = coins.Bitcoin):
        'Generate a new random printed address for the intermediate_code.'

        return _generate_printed_address(intermediate_code, coin)

    @staticmethod
    def confirm(confirmation_code, passphrase, coin = coins.Bitcoin):
        "Confirm a passphrase decrypts a printed address' confirmation_code."

        return _check_confirmation_code(confirmation_code, passphrase, coin)


class EncryptedPrintedAddress(EncryptedAddress):
    """This should not be instantiated directly. Use:

          code = PrintedAddress.generate_intermediate_code(passphrase)
          PrintedAddress.generate(code)"""

    def __init__(self):
        raise ValueError('cannot instantiate an EncryptedPrintedAddress')

    public_key = property(lambda s: s._public_key)
    address = property(lambda s: s._address)

    confirmation_code = property(lambda s: s._confirmation_code)

    lot = property(lambda s: s._lot)
    sequence = property(lambda s: s._sequence)


class Confirmation(object):
    """This should not be instantiated directly. Use:

          PrintedAddress.confirm(confimation_code, passphrase)"""

    def __init__(self):
        raise ValueError('cannot instantiate a Confirmation')

    coin = property(lambda s: s._coin)

    address = property(lambda s: s._address)

    public_key = property(lambda s: s._public_key)
    compressed = property(lambda s: s._compressed)

    lot = property(lambda s: s._lot)
    sequence = property(lambda s: s._sequence)

    def __str__(self):
        return '<Confirmation address=%s lot=%s sequence=%s>' % (self.address, self.lot, self.sequence)


def _normalize_utf(text):
    'Returns text encoded in UTF-8 using "Normalization Form C".'

    return unicodedata.normalize('NFC', unicode(text)).encode('utf8')

def _encrypt_xor(a, b, aes):
    'Returns encrypt(a ^ b).'

    block = [(ord(a) ^ ord(b)) for (a, b) in zip(a, b)]
    return "".join(chr(c) for c in aes.encrypt(block))

def _decrypt_xor(a, b, aes):
    'Returns decrypt(a) ^ b)'

    a = [ord(c) for c in a]
    block = [(a ^ ord(b)) for (a, b) in zip(aes.decrypt(a), b)]
    return "".join(chr(c) for c in block)

def _encrypt_private_key(private_key, passphrase, coin = coins.Bitcoin):
    'Encrypts a private key.'

    # compute the flags
    flagbyte = 0xc0
    if private_key.startswith('L') or private_key.startswith('K'):
        flagbyte |= 0x20
    elif not private_key.startswith('5'):
        raise ValueError('unknown private key type')

    # compute the address, which is used for the salt
    address = Address(private_key = private_key, coin = coin)
    salt = util.sha256d(address.address)[:4]

    # compute the key
    derived_key = util.scrypt(_normalize_utf(passphrase), salt, 16384, 8, 8, 64)
    (derived_half1, derived_half2) = (derived_key[:32], derived_key[32:])

    aes = AES(derived_half2)

    # encrypt the private key
    privkey  = address._privkey
    encrypted_half1 = _encrypt_xor(privkey[:16], derived_half1[:16], aes)
    encrypted_half2 = _encrypt_xor(privkey[16:], derived_half1[16:], aes)

    # encode it
    payload = (chr(0x01) + chr(0x42) + chr(flagbyte) + salt +
               encrypted_half1 + encrypted_half2)

    return EncryptedAddress(util.base58.encode_check(payload), coin)


def _decrypt_private_key(private_key, passphrase, coin = coins.Bitcoin):
    'Decrypts a private key.'

    payload = util.base58.decode_check(private_key)
    if len(payload) != 39 or payload[:2] != "\x01\x42":
        return None

    # decode the flags
    flagbyte = ord(payload[2])
    compressed = bool(flagbyte & 0x20)

    salt = payload[3:7]
    encrypted = payload[7:39]

    # compute the key
    derived_key = util.scrypt(_normalize_utf(passphrase), salt, 16384, 8, 8, 64)
    (derived_half1, derived_half2) = (derived_key[0:32], derived_key[32:])

    aes = AES(derived_half2)

    # decrypt the payload
    decrypted_half1 = _decrypt_xor(encrypted[:16], derived_half1[:16], aes)
    decrypted_half2 = _decrypt_xor(encrypted[16:], derived_half1[16:], aes)

    # set the private key compressed bit if needed
    privkey = decrypted_half1 + decrypted_half2
    if compressed:
        privkey += chr(0x01)

    # check the decrypted private key is correct (otherwise, wrong password)
    address = Address(private_key = util.key.privkey_to_wif(privkey), coin = coin)
    if util.sha256d(address.address)[:4] != salt:
        return None

    return Address(private_key = address.private_key, coin = coin)

def _key_from_point(point, compressed):
    'Converts a point into a key.'

    key = (chr(0x04) +
           number_to_string(point.x(), curve.order) +
           number_to_string(point.y(), curve.order))

    if compressed:
        key = util.key.compress_public_key(key)

    return key

def _key_to_point(key):
    'Converts a key to an EC Point.'

    key = util.key.decompress_public_key(key)
    x = string_to_number(key[1:33])
    y = string_to_number(key[33:65])
    return util.ecc.point(x, y)

def _generate_intermediate_code(passphrase, lot = None, sequence = None):
    'Generates a new intermediate code for passphrase.'

    if (lot is None) ^ (sequence is None):
        raise ValueError('must specify both or neither of lot and sequence')

    if lot and not (0 <= lot <= 0xfffff):
        raise ValueError('lot is out of range')

    if sequence and not (0 <= sequence <= 0xfff):
        raise ValueError('lot is out of range')

    # compute owner salt and entropy
    if lot is None:
        owner_salt = os.urandom(8)
        owner_entropy = owner_salt
    else:
        owner_salt = os.urandom(4)
        lot_sequence = struct.pack('>I', (lot << 12) | sequence)
        owner_entropy = owner_salt + lot_sequence

    prefactor = util.scrypt(_normalize_utf(passphrase), owner_salt, 16384, 8, 8, 32)
    if lot is None:
        pass_factor = string_to_number(prefactor)
    else:
        pass_factor = string_to_number(util.hash.sha256d(prefactor + owner_entropy))

    # compute the public point
    point = curve.generator * pass_factor
    pass_point = _key_from_point(point, True)

    prefix = '\x2c\xe9\xb3\xe1\xff\x39\xe2'
    if lot is None:
        prefix += chr(0x53)
    else:
        prefix += chr(0x51)

    # make a nice human readable string, beginning with "passphrase"
    return util.base58.encode_check(prefix + owner_entropy + pass_point)


def _generate_printed_address(intermediate_code, compressed, coin = coins.Bitcoin):

    payload = util.base58.decode_check(intermediate_code)

    if len(payload) != 49:
        raise ValueError('invalid intermediate code')

    if payload[0:7] != '\x2c\xe9\xb3\xe1\xff\x39\xe2':
        raise ValueError('invalid intermediate code prefix')

    # de-searialize the payload
    magic_suffix = ord(payload[7])
    owner_entropy = payload[8:16]
    pass_point = payload[16:49]

    # prepare the flags
    flagbyte = 0
    if compressed:
        flagbyte |= 0x20

    # if we have a lot and sequence, determine them and set the flags
    lot = None
    sequence = None
    if magic_suffix == 0x51:
        flagbyte |= 0x04
        lot_sequence = struct.unpack('>I', owner_entropy[4:8])[0]
        lot = lot_sequence >> 12
        sequence = lot_sequence & 0xfff
    elif magic_suffix != 0x53:
        raise ValueError('invalid intermediate code prefix')

    # generate the random seedb
    seedb = os.urandom(24)
    factorb = string_to_number(util.sha256d(seedb))

    # compute the public point (and address)
    point = _key_to_point(pass_point) * factorb
    public_key = _key_from_point(point, compressed)

    address = util.key.publickey_to_address(public_key, coin.address_version)

    address_hash = util.sha256d(address)[:4]

    # key for encrypting the seedb (from the public point)
    salt = address_hash + owner_entropy
    derived_key = util.scrypt(pass_point, salt, 1024, 1, 1, 64)
    (derived_half1, derived_half2) = (derived_key[:32], derived_key[32:])

    aes = AES(derived_half2)

    # encrypt the seedb; it's only 24 bytes, so we can nest to save space
    encrypted_half1 = _encrypt_xor(seedb[:16], derived_half1[:16], aes)
    encrypted_half2 = _encrypt_xor(encrypted_half1[8:16] + seedb[16:24],
                                   derived_half1[16:], aes)

    # final binary private key
    payload = ('\x01\x43' + chr(flagbyte) + address_hash + owner_entropy +
               encrypted_half1[0:8] + encrypted_half2)
    private_key = util.base58.encode_check(payload)

    # generate the confirmation code point
    point = curve.generator * factorb
    pointb = _key_from_point(point, True)

    # encrypt the confirmation code point
    pointb_prefix = chr(ord(pointb[0]) ^ (ord(derived_half2[31]) & 0x01))
    pointbx1 = _encrypt_xor(pointb[1:17], derived_half1[:16], aes)
    pointbx2 = _encrypt_xor(pointb[17:], derived_half1[16:], aes)
    encrypted_pointb = pointb_prefix + pointbx1 + pointbx2

    # make a nice human readable string, beginning with "cfrm"
    prefix = "\x64\x3b\xf6\xa8\x9a"
    payload = (prefix + chr(flagbyte) + address_hash + owner_entropy +
               encrypted_pointb)
    confirmation_code = util.base58.encode_check(payload)

    # wrap it up in a nice object
    self = EncryptedPrintedAddress.__new__(EncryptedPrintedAddress)
    BaseAddress.__init__(self, private_key = private_key, coin = coin)

    self._public_key = public_key
    self._address = address

    self._lot = lot
    self._sequence = sequence

    self._confirmation_code = confirmation_code

    return self


def _check_confirmation_code(confirmation_code, passphrase, coin = coins.Bitcoin):
    '''Verifies a confirmation code with passphrase and returns a
       Confirmation object.'''

    payload = util.base58.decode_check(confirmation_code)
    if payload[:5] != '\x64\x3b\xf6\xa8\x9a':
        raise ValueError('invalid confirmation code prefix')

    # de-serialize the payload
    flagbyte = ord(payload[5])

    address_hash = payload[6:10]
    owner_entropy = payload[10:18]
    encrypted_pointb = payload[18:]

    # check for compressed flag
    compressed = False
    if flagbyte & 0x20:
        compressed = True

    # check for a lot and sequence
    lot = None
    sequence = None
    owner_salt = owner_entropy
    if flagbyte & 0x04:
        lot_sequence = struct.unpack('>I', owner_entropy[4:8])[0]
        lot = lot_sequence >> 12
        sequence = lot_sequence & 0xfff
        owner_salt = owner_entropy[:4]

    prefactor = util.scrypt(_normalize_utf(passphrase), owner_salt, 16384, 8, 8, 32)
    if lot is None:
        pass_factor = string_to_number(prefactor)
    else:
        pass_factor = string_to_number(util.hash.sha256d(prefactor + owner_entropy))

    # determine the passpoint
    point = curve.generator * pass_factor
    pass_point = _key_from_point(point, True)

    # derive the key that was used to encrypt the pointb
    salt = address_hash + owner_entropy
    derived_key = util.scrypt(pass_point, salt, 1024, 1, 1, 64)
    (derived_half1, derived_half2) = (derived_key[:32], derived_key[32:])

    aes = AES(derived_half2)

    # decrypt the pointb
    pointb_prefix = ord(encrypted_pointb[0]) ^ (ord(derived_half2[31]) & 0x01)
    pointbx1 = _decrypt_xor(encrypted_pointb[1:17], derived_half1[:16], aes)
    pointbx2 = _decrypt_xor(encrypted_pointb[17:], derived_half1[16:], aes)
    pointb = chr(pointb_prefix) + pointbx1 + pointbx2

    # compute the public key (and address)
    point = _key_to_point(pointb) * pass_factor
    public_key = _key_from_point(point, compressed)

    address = util.key.publickey_to_address(public_key, coin.address_version)

    # verify the checksum
    if util.sha256d(address)[:4] != address_hash:
        raise ValueError('invalid passphrase')

    # wrap it up in a nice object
    self = Confirmation.__new__(Confirmation)

    self._public_key = public_key
    self._address = address
    self._compressed = compressed

    self._lot = lot
    self._sequence = sequence

    self._coin = coin

    return self


def _decrypt_printed_private_key(private_key, passphrase, coin = coins.Bitcoin):
    'Decrypts a printed private key returning an instance of PrintedAddress.'

    payload = util.base58.decode_check(private_key)

    if payload[0:2] != '\x01\x43':
        raise ValueError('invalid printed address private key prefix')

    if len(payload) != 39:
        raise ValueError('invalid printed address private key length')

    # de-serialize the payload
    flagbyte = ord(payload[2])

    address_hash = payload[3:7]
    owner_entropy = payload[7:15]

    encrypted_quarter1 = payload[15:23]
    encrypted_half2 = payload[23:39]

    # check for compressed flag
    compressed = False
    if flagbyte & 0x20:
        compressed = True

    # check for lot and sequence
    (lot, sequence) = (None, None)
    owner_salt = owner_entropy
    if flagbyte & 0x04:
        lot_sequence = struct.unpack('>I', owner_entropy[4:8])[0]
        lot = lot_sequence >> 12
        sequence = lot_sequence & 0xfff
        owner_salt = owner_entropy[0:4]

    prefactor = util.scrypt(_normalize_utf(passphrase), owner_salt, 16384, 8, 8, 32)
    if lot is None:
        pass_factor = string_to_number(prefactor)
    else:
        pass_factor = string_to_number(util.hash.sha256d(prefactor + owner_entropy))

    # compute the public point
    point = curve.generator * pass_factor
    pass_point = _key_from_point(point, True)

    # derive the key that was used to encrypt the seedb; based on the public point
    derived_key = util.scrypt(pass_point, address_hash + owner_entropy, 1024, 1, 1, 64)
    (derived_half1, derived_half2) = (derived_key[:32], derived_key[32:])

    aes = AES(derived_half2)

    # decrypt the seedb (it was nested, so we work backward)
    decrypted_half2 = _decrypt_xor(encrypted_half2, derived_half1[16:], aes)
    encrypted_half1 = encrypted_quarter1 + decrypted_half2[:8]
    decrypted_half1 = _decrypt_xor(encrypted_half1, derived_half1[:16], aes)

    # compute the seedb
    seedb = decrypted_half1 + decrypted_half2[8:16]
    factorb = string_to_number(util.sha256d(seedb))

    # compute the secret exponent
    secexp = (factorb * pass_factor) % curve.order

    # convert it to a private key
    private_key = number_to_string(secexp, curve.order)
    if compressed:
        private_key += chr(0x01)

    # wrap it up in a nice object
    self = PrintedAddress.__new__(PrintedAddress)
    Address.__init__(self, private_key = util.key.privkey_to_wif(private_key), coin = coin)

    self._lot = lot
    self._sequence = sequence

    # verify the checksum
    if address_hash != util.sha256d(self.address)[:4]:
        raise ValueError('incorrect passphrase')

    return self

#def requires_passphrase(private_key):
#    return private_key.startswith('6P')

def get_address(private_key, passphrase = None, coin = coins.Bitcoin):
    '''Detects the type of private key uses the correct class to instantiate
       an Address, optionally decrypting it with passphrase.'''

    # unencrypted
    if private_key[0] in ('5', 'L', 'K'):
        return Address(private_key = private_key, coin = coin)

    # encrypted
    if private_key.startswith('6P'):
        address = EncryptedAddress(private_key = private_key, coin = coin)

        # decrypt it if we have a passphrase
        if passphrase:
            address = address.decrypt(passphrase)

        return address

    return None


