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


# Do not use this directly, it is meant as a template for adding new coins


import coin

from .litecoin import Litecoin

from .. import util

class Mooncoin(Litecoin):

    name = "mooncoin"

    # All symbols the coin uses and "primary" symbol;
    # these are only used for UI purposes
    symbols = ['MOON']
    symbol = symbols[0]

    # See: https://en.bitcoin.it/wiki/Satoshi_Client_Node_Discovery
    # Usually in chainparams.cpp or net.cpp
    dns_seeds = [
        ("seed.mooncoin.info", 44664),
    ]

    protocol_version = 70003

    # This function returns the block creation fee based on a block
    # Usually the chainparams.cpp or main.cpp has a method GetBlockValue
    # or uses a subsidy block halving interval
    #@staticmethod
    #def block_creation_fee(block):
    #     return (50 * 100000000) >> (block.height // 210000)

    # The default port this coin listens on; should not be on an otherwise
    # well-known port and not in the OS' ephemeral port range (>= 49152)
    # Usually in chainparams.cpp or protocol.h
    port = 44664

    # Genesis block (hashes are little endiand; ie. 0's should be at the end)
    # @TODO: create a utility function to generate new genesis blocks
    genesis_block_hash = 'e9aec56aa60b81d3ebb33556b05d765de36c1a2efd1d4b4d724248acbb7c68bd'.decode('hex')
    genesis_merkle_root = '6632e9c6d07adfb85c364542de24ebf81de0def5a5ff8f1294055d56d7aeaab3'.decode('hex')
    genesis_timestamp = 1388158603
    genesis_nonce = 1767251

    # The magic number should be 4-bytes, such that it represents a
    # non-printable string, and not symetric.
    # @TODO: create a utility function to generate safe-ish magic numbers
    # Usually in main.cpp
    magic = "\xf9\xf7\xc0\xe8"

    # This value will determine what character your addresses begin with
    # @TODO: create utility function to compute this based on prefix
    # Usually in chainparams.cpp of base58.h under PUBKEY_ADDRESS
    address_version = chr(3)

    script_address = chr(22)

    # This public key will be used to verify alerts; you can use the
    # pycoind.wallet.Address to generate a public/private key pair
    alert_public_key = '04d4da7a5dae4db797d9b0644d57a5cd50e05a70f36091cd62e2fc41c98ded06340be5a43a35e185690cd9cde5d72da8f6d065b499b06f51dcfba14aad859f443a'.decode('hex')


    block_height_guess = [
        ('www.moonchain.net', util.fetch_url_int('http://www.moonchain.net/chain/Mooncoin/q/getblockcount'))
    ]
