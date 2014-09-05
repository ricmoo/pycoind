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

# https://github.com/realcoinyecoin/coinyecoin

__all__ = ['Coinyecoin']

class Coinyecoin(Litecoin):

    name = "coinyecoin"

    @staticmethod
    def block_creation_fee(block):
        return (666666 * 100000000) >> (block.height // 100000)

    symbols = ["COYE"]
    symbol = symbols[0]

    dns_seeds = [
        ("seed1.coinyeco.in", 41338),
        ("seed2.coinyeco.in", 41338),
        ("seed3.coinyeco.in", 41338),
        ("seed4.coinyeco.in", 41338),
        ("seed5.coinyeco.in", 41338),
    ]

    port = 41338
    rpc_port = 41337

    # Genesis block (hashes are little endiand; ie. 0's should be at the end)
    genesis_block_hash = ('3fca9bb899bf64824aba73b2c1dbe6343556bfcca537d596b9efb45bf8933333').decode('hex')
    genesis_merkle_root = ('6ee5b04be0981f246b045c38595b904e08db50f653d89bd166341272d91981ad').decode('hex')
    genesis_timestamp = 1369199888
    genesis_nonce = 11288888

    magic = "\xf9\xf7\xc0\xe8"

    address_version = chr(11)

    script_address = chr(22)   #??

    alert_public_key = '040184710fa689ad5023690c80f3a49c8f13f8d45b8c857fbcbc8bc4a8e4d3eb4b10f4d4604fa08dce601aaf0f470216fe1b51850b4acf21b179c45070ac7b03a9'.decode('hex')


class _CoinyecoinTest(Coinyecoin):
    magic = "\xfa\xf8\xc1\xe9"

    address_version = chr(113)

    script_address = chr(196)

