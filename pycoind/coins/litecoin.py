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

from ..util import scrypt

__all__ = ['Litecoin']

class Litecoin(coin.Coin):
    name = "litecoin"

    # https://github.com/litecoin-project/litecoin/blob/master-0.8/src/main.cpp#L1085
    @staticmethod
    def block_creation_fee(block):
        return (50 * 100000000) >> (block.height // 840000)

    @staticmethod
    def proof_of_work(block_header):
        block_header = block_header[:80]
        return scrypt(block_header, block_header, 1024, 1, 1, 32)

    symbols = [ 'LTC' ]
    symbol = symbols[0]

    # See: https://github.com/litecoin-project/litecoin/blob/master-0.8/src/net.cpp#L1194
    dns_seeds = [
        ("dnsseed.litecointools.com", 9333),
        ("dnsseed.litecoinpool.org", 9333),
        ("dnsseed.ltc.xurious.com", 9333),
        ("dnsseed.koin-project.com", 9333),
        ("dnsseed.weminemnc.com", 9333),
    ]

    port = 9333
    rpc_port = 9332

    genesis_version = 1
    genesis_block_hash = 'e2bf047e7e5a191aa4ef34d314979dc9986e0f19251edaba5940fd1fe365a712'.decode('hex')
    genesis_merkle_root = 'd9ced4ed1130f7b7faad9be25323ffafa33232a17c3edf6cfd97bee6bafbdd97'.decode('hex')
    genesis_timestamp = 1317972665
    genesis_bits = 504365040
    genesis_nonce = 2084524493

    # https://github.com/litecoin-project/litecoin/blob/master-0.8/src/main.cpp#L3082
    magic = '\xfb\xc0\xb6\xdb'

    alert_public_key = '040184710fa689ad5023690c80f3a49c8f13f8d45b8c857fbcbc8bc4a8e4d3eb4b10f4d4604fa08dce601aaf0f470216fe1b51850b4acf21b179c45070ac7b03a9'.decode('hex')
    address_version = chr(48)

class LitecoinTestnet(Litecoin):

    port = 19333
    rpc_port = 19332

    magic = '\xfc\xc1\xb7\xdc'

    alert_public_key = '04302390343f91cc401d56d68b123028bf52e5fca1939df127f63c6467cdf9c8e2c14b61104cf817d0b780da337893ecc4aaff1309e536162dabbdb45200ca2b0a'.decode('hex')
