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

class Potcoin(Litecoin):

    name = "potcoin"

    # All symbols the coin uses and "primary" symbol
    symbols = ["POT"]
    symbol = symbols[0]

    # See: https://github.com/potcoin/potcoin/blob/master/src/net.cpp
    dns_seeds = [
        ("dnsseedz.potcoin.info", 4200),
        ("dns1.potcoin.info", 4200),
    ]

    port = 4200

    genesis_block_hash = 'ec3513ee046dcd52dd41975fcfab4f878f91890a4d17c07a1d7d9c2acbb036de'.decode('hex')
    genesis_merkle_root = '3de5af055300a913c07e178efc107c9184dddcbc9d888aae7eea6ee00686a0d5'.decode('hex')
    genesis_timestamp = 1389688315
    genesis_nonce = 471993

    magic = "\xfb\xc0\xb6\xdb"

    address_version = chr()

    alert_public_key = ''.decode('hex')


