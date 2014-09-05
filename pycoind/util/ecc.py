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

import binascii

from . import ecdsa

from .ecdsa import der, ellipticcurve
from .ecdsa import SECP256k1 as curve
from .ecdsa.six import b

from .hash import sha256d

from .key import decompress_public_key, privkey_from_wif

__all__ = ['sign', 'verify']

# http://stackoverflow.com/questions/1604464/twos-complement-in-python
def twos_comp(val, bits):
    "Compute the 2's compliment of val with the width bits."

    if (val & (1 << (bits - 1))):
        val = val - (1 << bits)
    return val

def remove_integer(string):
    if not string.startswith(b("\x02")):
        n = string[0] if isinstance(string[0], der.integer_types) else ord(string[0])
        raise UnexpectedDER("wanted integer (0x02), got 0x%02x" % n)
    length, llen = der.read_length(string[1:])
    numberbytes = string[1+llen:1+llen+length]
    rest = string[1+llen+length:]
    #nbytes = numberbytes[0] if isinstance(numberbytes[0], der.integer_types) else ord(numberbytes[0])
    value = int(binascii.hexlify(numberbytes), 16)
    return (value, rest)
    #return (twos_comp(value, len(numberbytes) * 8), rest)


def sigdecode_der(sig_der, order):
    '''We use a slightly more liberal der decoder because sometimes signatures
       seem to have trailing 0 bytes. (see block bitcoin@135106)'''

    rs_strings, empty = der.remove_sequence(sig_der)
    #if empty != b("") and empty.strip(chr(0)):
    #    raise der.UnexpectedDER("trailing junk after DER sig: %s" %
    #                             binascii.hexlify(empty))
    r, rest = remove_integer(rs_strings)
    s, empty = remove_integer(rest)
    #if empty != b("") and empty.strip(chr(0)):
    #    raise der.UnexpectedDER("trailing junk after DER numbers: %s" %
    #                  binascii.hexlify(empty))
    #if s < 0:
    #    s = s % order
    return r, s


def sign(data, private_key):
    key = ecdsa.SigningKey.from_string(private_key, ecdsa.SECP256k1)
    return key.sign_digest(sha256d(data), sigencode = ecdsa.util.sigencode_der)


def verify(data, public_key, signature):
    try:
        public_key = decompress_public_key(public_key)
    except ValueError:
        return False

    key = ecdsa.VerifyingKey.from_string(public_key[1:], ecdsa.SECP256k1)
    try:
        return key.verify_digest(signature, sha256d(data), sigdecode = sigdecode_der)
    except ecdsa.BadSignatureError, e:
        return False

from .ecdsa.util import number_to_string, string_to_number
def shared_secret(public_key, private_key):
    public_key = decompress_public_key(public_key)

    x = string_to_number(public_key[1:33])
    y = string_to_number(public_key[33:])
    public_point = ellipticcurve.Point(ecdsa.SECP256k1.curve, x, y)

    privkey = privkey_from_wif(private_key)
    secexp = string_to_number(privkey)

    shared_point = public_point * secexp
    shared_key = number_to_string(shared_point.x(), curve.order)

    return shared_key

def point(x, y):
    return ellipticcurve.Point(ecdsa.SECP256k1.curve, x, y)


