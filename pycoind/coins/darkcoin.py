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
import util

class Darkcoin(coin.Coin):
    name = 'darkcoin'

    symbols = [ 'DRK' ]
    symbol = symbols[0]

    # https://github.com/darkcoinproject/darkcoin/blob/master/src/net.cpp#L1195
    dns_seeds = [
        ("23.23.186.131", 9333),
        ("162.252.83.46", 9333),
        ("107.155.71.72", 9333),
        ("50.16.206.102", 9333),
        ("50.19.116.123", 9333),
        ("98.165.130.67", 9333),
        ("23.23.186.131", 9333),
        ("50.16.206.102", 9333),
        ("50.19.116.123", 9333),
        ("50.19.116.123", 9333),
        ("23.21.204.34", 9333),
        ("188.142.39.105", 9333),
        ("50.16.206.102", 9333),
        ("23.23.186.131", 9333),
        ("50.19.116.123", 9333),
        ("54.248.227.151", 9333),
        ("42.121.58.91", 9333),
        ("50.81.192.39", 9333),
        ("54.193.124.32", 9333),
        ("62.141.39.175", 9333),
        ("5.254.96.3", 9333),
        ("175.115.201.44", 9333),
        ("208.53.191.2", 9333),
        ("162.243.33.16", 9333),
    ]

    port = 9333

    genesis_version = 2
    genesis_block_hash = util.hex_to_bin('00000ffd590b1485b3caadc19b22e6379c733355108f107a430458cdf3407ab6')
    genesis_merkle_root = util.hex_to_bin('e0028eb9648db56b1ac77cf090b99048a8007e2bb64b68f092c03c7f56a662c7')
    genesis_timestamp = 1390103681
    genesis_nonce = 128987

    # https://github.com/darkcoinproject/darkcoin/blob/master/src/protocol.cpp#L26
    magic = "\xbf\x0c\x6b\xbd"

    address_version = chr(76)

class DarkcoinTest(Darkcoin):
    dns_seeds = [
        ("23.23.186.131", 19333),
    ]

    port = 19333
