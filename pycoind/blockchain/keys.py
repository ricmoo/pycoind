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

def get_txck(blockid, txn_index):
    'Generate a composite key for transactions.'

    if (blockid & 0x7fffff) != blockid:
        raise ValueError('blockid is out of range')
    if (txn_index & 0xfffff) != txn_index:
        raise ValueError('index is out of range')

    return (blockid << 20) | txn_index


def get_txck_blockid(txck):
    'Get the blockid from a transaction composite key.'

    return txck >> 20


def get_txck_index(txck):
    'Get the index from a transaction composite key.'

    return txck & 0xfffff


def get_hint(data):
    'Generate a 6-byte hint.'

    return struct.unpack('>Q', data[:8])[0] & 0x7fffffffffff

def get_uock(txck, output_index):
    'Generate a composite key for unspend outputs.'

    if (txck & 0x7ffffffffff) != txck:
        raise ValueError('txck is out of range')
    if (output_index & 0xfffff) != output_index:
        raise ValueError('output index is out of range')

    return (txck << 20) | output_index


def get_uock_txck(uock):
    'Get the transaction composite key from a utxo composite key.'

    return uock >> 20


def get_uock_index(uock):
    'Get the output index from a utxo composite key.'

    return uock & 0xfffff


def get_address_hint(address):
    'Generate a 6-byte hint for an address with kind field.'

    if address is None:
        return 0
    bytes = util.base58.decode_check(address)
    hint = get_hint(bytes[1:])
    return (hint & 0x7ffffffffffe) | 0x01

