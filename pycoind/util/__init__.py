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
import math
import os
import struct

from . import base58
from . import bootstrap
from . import ecc
from . import key
from . import piecewise

from .hash import sha1, sha256, sha256d, ripemd160, hash160

__all__ = [
    'base58', 'ecc', 'key', 'piecewise',
    'sha1', 'sha256', 'sha256d', 'ripemd160', 'hash160',
    'scrypt',
    'hex_to_bin', 'bin_to_hex',
    'get_version', 'make_version',
    'default_data_directory'
    # TODO: add others for import *
]

# Try finding a fast implementation of scrypt, fallback onto pyscrpyt
try:
    import scrypt
    _scrypt = scrypt.hash
except Exception, e:
    import pyscrypt
    _scrypt = pyscrypt.hash


# Hashing Algorithms


def scrypt(data, salt, N, r, p, dk_length):
    return _scrypt(data, salt, N, r, p, dk_length)

def x11(data):
    raise NotImplemented()


# Formatting Helpers

def commify(value):
    return "{:,d}".format(value)


# Block Header Helpers

def get_block_header(version, prev_block, merkle_root, timestamp, bits, nonce):
    return struct.pack('<I32s32sIII', version, prev_block, merkle_root, timestamp, bits, nonce)

def verify_target(coin, block_header):
    binary_header = block_header.binary()[:80]
    pow = coin.proof_of_work(binary_header)[::-1]
    return pow <= get_target(block_header.bits)

def get_target(bits):
    target = ((bits & 0x7fffff) * 2 ** (8 * ((bits >> 24) - 3)))
    return ("%064x" % target).decode('hex')


DifficultyOneTarget = 26959535291011309493156476344723991336010898738574164086137773096960.0
def get_difficulty(bits):
    return DifficultyOneTarget / ((bits & 0x7fffff) * 2 ** (8 * ((bits >> 24) - 3)))

# https://en.bitcoin.it/wiki/Protocol_specification#Merkle_Trees
def get_merkle_root(transactions):
    branches = [t.hash for t in transactions]

    while len(branches) > 1:
        if (len(branches) % 2) == 1:
            branches.append(branches[-1])

        branches = [sha256d(a + b) for (a, b) in zip(branches[0::2], branches[1::2])]

    return branches[0]


# Hexlify Helpers

def hex_to_bin(data):
    return data.decode('hex')[::-1]


def bin_to_hex(data):
    return data[::-1].encode('hex')


# Protocl Version Helpers

def get_version(version):
     major = version // 1000000
     minor = (version // 10000) % 100
     revision = (version // 100) % 100
     build = version % 100
     return (major, minor, revision, build)

def make_version(major, minor, revision, build):
    if not ((0 <= minor < 100) and (0 <= revision < 100) and (0 <= build < 100)):
        raise ValueError('minor, revision and build must be in the range [0, 99]')
    return (major * 1000000) + (minor * 10000) + (revision * 100) + build


# File Helpers

def default_data_directory():
    return os.path.expanduser('~/.pycoind/data')

# QR Code
#def qrcode(data, box_size = 10, border = 4, lmqh = 'M'):
#    import cStringIO as StringIO
#    ec = dict(L = 1, M = 0, Q = 3, H = 2)
#    qr = QRCode(box_size = box_size, border = border)
#    qr.add_data(data)
#    qr.make(fit = True, image_factory = PymagingImage)
#    img = make_img()
#    print img
#    return 'foo'


