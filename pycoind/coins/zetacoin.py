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

from .. import util

class Zetacoin(coin.Coin):

    name = "zetacoin"

    # All symbols the coin uses and "primary" symbol;
    # these are only used for UI purposes
    symbols = ['ZET']
    symbol = symbols[0]

    # See: https://en.bitcoin.it/wiki/Satoshi_Client_Node_Discovery
    # Usually in chainparams.cpp or net.cpp
    dns_seeds = [
        ("seed1.zeta-coin.org", 17333),
        ("seed2.zeta-coin.org", 17333),
        ("seed3.zeta-coin.org", 17333),
        ("seed4.zeta-coin.org", 17333),
        ("seed5.zeta-coin.org", 17333),
        ("seed6.zeta-coin.org", 17333),
        ("seed7.zeta-coin.org", 17333),
        ("seed8.zeta-coin.org", 17333),
        ("albs1.zetacoinseed.com", 17333),
        ("albs2.zetacoinseed.com", 17333),
        ("albs3.zetacoinseed.com", 17333),
        ("albs4.zetacoinseed.com", 17333),
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
    port = 17333

    # Genesis block (hashes are little endiand; ie. 0's should be at the end)
    # @TODO: create a utility function to generate new genesis blocks
    genesis_block_hash = 'f4bff286c99d426dc375d17887bb5fdd5844aa02590191dae22baab7ca060000'.decode('hex')
    genesis_merkle_root = 'f9799babc9dacf7d3593adae8a45230d054f479e3d6b65e9bc073d3e8c7b22d0'.decode('hex')
    genesis_timestamp = 1375548986
    genesis_nonce = 2089928209

    # The magic number should be 4-bytes, such that it represents a
    # non-printable string, and not symetric.
    # @TODO: create a utility function to generate safe-ish magic numbers
    # Usually in main.cpp
    magic = "\xfa\xb5\x03\xdf"

    # This value will determine what character your addresses begin with
    # @TODO: create utility function to compute this based on prefix
    # Usually in chainparams.cpp of base58.h under PUBKEY_ADDRESS
    address_version = chr(80)

    # This public key will be used to verify alerts; you can use the
    # pycoind.wallet.Address to generate a public/private key pair
    alert_public_key = '045337216002ca6a71d63edf062895417610a723d453e722bf4728996c58661cdac3d4dec5cecd449b9086e9602b35cc726a9e0163e1a4d40f521fbdaebb674658'.decode('hex')


    block_height_guess = [
        ('zetachain.info', util.fetch_url_json_path_int('http://www.zetachain.info/api/status?q=getInfo', 'info/blocks')),
    ]
