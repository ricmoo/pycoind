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


import coin

from .litecoin import Litecoin

from .. import util

class Flappycoin(Litecoin):

    name = "flappycoin"

    # All symbols the coin uses and "primary" symbol;
    # these are only used for UI purposes
    symbols = ['FLAP']
    symbol = symbols[0]

    # See: https://en.bitcoin.it/wiki/Satoshi_Client_Node_Discovery
    # Usually in chainparams.cpp or net.cpp
    dns_seeds = [
        ("dnsseed.flap.so", 11556),
    ]

    # This function returns the block creation fee based on a block
    # Usually the chainparams.cpp or main.cpp has a method GetBlockValue
    # or uses a subsidy block halving interval
    #@staticmethod
    #def block_creation_fee(block):
    #     return (50 * 100000000) >> (block.height // 210000)

    # The default port this coin listens on; should not be on an otherwise
    # well-known port and not in the OS' ephemeral port range (>= 49152)
    # Usually in chainparams.cpp or protocol.h
    port = 11556

    protocol_version = 70003

    # Genesis block (hashes are little endiand; ie. 0's should be at the end)
    # @TODO: create a utility function to generate new genesis blocks
    genesis_block_hash = '64b0e6b2a85682d82499efb52038ea053cdd97b8890e472a3e33ab8cc4228801'.decode('hex')
    genesis_merkle_root = '318868cf8a975f003ab0c2e89f21c3d39f004f74685a729a0b03cd71acb000d6'.decode('hex')
    genesis_timestamp = 1392281929
    genesis_nonce = 265310

    # The magic number should be 4-bytes, such that it represents a
    # non-printable string, and not symetric.
    # @TODO: create a utility function to generate safe-ish magic numbers
    # Usually in main.cpp
    magic = "\xc1\xc1\xc1\xc1"

    # This value will determine what character your addresses begin with
    # @TODO: create utility function to compute this based on prefix
    # Usually in chainparams.cpp of base58.h under PUBKEY_ADDRESS
    address_version = chr(35)

    script_address = chr(5)

    # This public key will be used to verify alerts; you can use the
    # pycoind.wallet.Address to generate a public/private key pair
    alert_public_key = '040184710fa689ad5023690c80f3a49c8f13f8d45b8c857fbcbc8bc4a8e4d3eb4b10f4d4604fa08dce601aaf0f470216fe1b51850b4acf21b179c45070ac7b03a9'.decode('hex')


    block_height_guess = [
        ('flappyapi.com', util.fetch_url_int('http://flappyapi.com/currentblock')),
    ]
