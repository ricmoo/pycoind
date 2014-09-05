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

class Blackcoin(coin.Coin):

    name = "blackcoin"

    symbols = ['BC']
    symbol = symbols[0]

    # See: https://github.com/rat4/blackcoin/blob/6225d1c1119e8cb446815992a96ce32e15805ede/src/net.cpp#L1141
    dns_seeds = [
        ("seed.blackcoin.co", 15714),
        ("seed2.blackcoin.co", 15714),
    ]

    protocol_version = 60013

    port = 15714

    genesis_block_hash = '63451e9101b1a50b3d262f23bf83c1f21d6242626e90cffbc4de25effa010000'.decode('hex')
    genesis_merkle_root = '90dc08aaa21e939141d461fc706c9e8cb95fda4d59c2c887b2247fa9160d6312'.decode('hex')
    genesis_timestamp = 1393221600
    genesis_nonce = 164482

    magic = "\x70\x35\x22\x05"

    address_version = chr(0)

    alert_public_key = '0486bce1bac0d543f104cbff2bd23680056a3b9ea05e1137d2ff90eeb5e08472eb500322593a2cb06fbf8297d7beb6cd30cb90f98153b5b7cce1493749e41e0284'.decode('hex')
    checkpoint_public_key = '04a18357665ed7a802dcf252ef528d3dc786da38653b51d1ab8e9f4820b55aca807892a056781967315908ac205940ec9d6f2fd0a85941966971eac7e475a27826'.decode('hex')

class BlackcoinTestnet(Blackcoin):
    magic = "\xcd\xf2\xc0\xef"
    port = 25714
