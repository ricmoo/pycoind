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

# https://github.com/dogecoin/dogecoin

__all__ = ['Dogecoin']

class Dogecoin(Litecoin):
    name = "dogecoin"

    dns_seeds = [
        ("seed.dogecoin.com", 22556),
        ("seed.mophides.com", 22556),
        ("seed.dglibrary.org", 22556),
        ("seed.dogechain.info", 22556),
    ]

    symbols = ['DOGE']
    symbol = symbols[0]

    port = 22556
    rpc_port = 22555

    genesis_version = 1
    genesis_block_hash = '9156352c1818b32e90c9e792efd6a11a82fe7956a630f03bbee236cedae3911a'.decode('hex')
    genesis_merkle_root = '696ad20e2dd4365c7459b4a4a5af743d5e92c6da3229e6532cd605f6533f2a5b'.decode('hex')
    genesis_timestamp = 1386325540
    genesis_bits = 504365040
    genesis_nonce = 99943

    magic = '\xc0\xc0\xc0\xc0'

    address_version = chr(30)
