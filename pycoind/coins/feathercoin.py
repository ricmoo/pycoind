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

# https://github.com/FeatherCoin/Feathercoin

__all__ = ['Feathercoin']


class Feathercoin(Litecoin):
    name = "feathercoin"

    # see: https://github.com/FeatherCoin/Feathercoin/blob/master-0.8/src/main.cpp#L1075
    @staticmethod
    def block_creation_fee(block):
        subsidy = 200
        if block.height >= 204639:    # nForkThree = 204639
            subsidy = 80
        return (subsidy * 100000000) >> ((block.height + 306960) // 210000)

    symbols = ['FTC']
    symbol = symbols[0]

    dns_seeds = [
        ("dnsseed.feathercoin.com", 9336),
        ("dnsseed.alltheco.in", 9336),
        ("dnsseed.btcltcftc.com", 9336),
        ("dnsseed.fc.altcointech.net", 9336),
    ]

    port = 9336
    rpc_port = 9337

    genesis_version = 1
    genesis_block_hash = 'e2bf047e7e5a191aa4ef34d314979dc9986e0f19251edaba5940fd1fe365a712'.decode('hex')
    genesis_merkle_root = 'd9ced4ed1130f7b7faad9be25323ffafa33232a17c3edf6cfd97bee6bafbdd97'.decode('hex')
    genesis_timestamp = 1317972665
    genesis_bits = 504365040
    genesis_nonce = 2084524493

    magic = '\xfb\xc0\xb6\xdb'

    addrss_version = chr(14)

    block_height_guess = [
        ('explorer.feathercoin.com', util.fetch_url_int('http://explorer.feathercoin.com/chain/Feathercoin/q/getblockcount')),
    ]
