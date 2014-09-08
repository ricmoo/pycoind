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

class Novacoin(Litecoin):

    name = "novacoin"

    # All symbols the coin uses and "primary" symbol;
    # these are only used for UI purposes
    symbols = [NVC]
    symbol = symbols[0]

    # See: https://en.bitcoin.it/wiki/Satoshi_Client_Node_Discovery
    # Usually in chainparams.cpp or net.cpp
    dns_seeds = [
        ("dnsseed.novacoin.su", 7777),
        ("dnsseed.novacoin.ru", 7777),
        ("dnsseed.novacoin.in", 7777),
    ]

    # The default port this coin listens on; should not be on an otherwise
    # well-known port and not in the OS' ephemeral port range (>= 49152)
    # Usually in chainparams.cpp or protocol.h
    port = 7777

    # Genesis block (hashes are little endiand; ie. 0's should be at the end)
    # (if you use util.hex_to_bin, 0's should be at the start)
    # @TODO: create a utility function to generate new genesis blocks
    genesis_block_hash = util.hex_to_bin('00000a060336cbb72fe969666d337b87198b1add2abaa59cca226820b32933a4')
    genesis_merkle_root = util.hex_to_bin('4cb33b3b6a861dcbc685d3e614a9cafb945738d6833f182855679f2fad02057b')
    genesis_timestamp = 1360105017
    genesis_nonce = 1575379

    # The magic number should be 4-bytes, such that it represents a
    # non-printable string, and not symetric.
    # @TODO: create a utility function to generate safe-ish magic numbers
    # Usually in main.cpp
    magic = "\xe4\xe8\xe9\xe5"

    # This value will determine what character your addresses begin with
    # @TODO: create utility function to compute this based on prefix
    # Usually in chainparams.cpp of base58.h under PUBKEY_ADDRESS
    address_version = chr(8)

    script_address = chr(20)

    # This public key will be used to verify alerts; you can use the
    # pycoind.wallet.Address to generate a public/private key pair
    # Usually in alert.cpp
    alert_public_key = '043fa441fd4203d03f5df2b75ea14e36f20d39f43e7a61aa7552ab9bcd7ecb0e77a3be4585b13fcdaa22ef6e51f1ff6f2929bec2494385b086fb86610e33193195'.decode('hex')

    block_height_guess = []

class NovacoinTest(Novacoin):

    port = 17777
    magic = "\xcd\xf2\xc0\xef"
    address_version = chr(111)
    script_address = chr(196)
