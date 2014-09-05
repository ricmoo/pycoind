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

from .. import util

__all__ = ['Coin', 'satoshi_per_coin']


satoshi_per_coin = 100000000

class Coin(object):
    name = None

    @staticmethod
    def proof_of_work(block_header):
        return util.sha256d(block_header[:80])

    # see: https://en.bitcoin.it/wiki/Protocol_rules
    @staticmethod
    def block_creation_fee(block):
        return (50 * 100000000) >> (block.height // 210000)

    symbols = [ ]
    symbol = None

    protocol_version = 70002
    dns_seeds = [ ]

    port = 0

    genesis_version = 1
    genesis_block_hash = chr(0) * 32
    genesis_merkle_root = chr(0) * 32
    genesis_timestamp = 0
    genesis_bits = 504365040    # 0x1e0ffff0
    genesis_nonce = 0

    magic = chr(0) * 4

    address_version = chr(0)

    alert_public_key = None

    checkpoint_public_key = None

    def __hash__(self):
        return hash(self.symbol)

    def __cmp__(self, other):
        return cmp(self.name, other.name)

    def __str__(self):
        return '<%s>' % self.name.capitalize()





