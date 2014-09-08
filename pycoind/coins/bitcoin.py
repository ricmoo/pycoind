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

import coin

# https://github.com/bitcoin/bitcoin

__all__ = ['Bitcoin']

class Bitcoin(coin.Coin):

    name = "bitcoin"

    # All symbols the coin uses and "primary" symbol
    symbols = ['BTC', 'XBT']
    symbol = symbols[0]

    # See: https://en.bitcoin.it/wiki/Satoshi_Client_Node_Discovery
    #      https://github.com/bitcoin/bitcoin/blob/master/src/chainparams.cpp#L143
    dns_seeds = [
        ("seed.bitcoin.sipa.be", 8333),
        ("dnsseed.bluematt.me", 8333),
        ("dnsseed.bitcoin.dashjr.org", 8333),
        ("seed.bitcoinstats.com", 8333),
        ("seed.bitnodes.io", 8333),
        ("bitseed.xf2.org", 8333),
    ]

    port = 8333
    rpc_port = 8332

    genesis_version = 1
    genesis_block_hash = '6fe28c0ab6f1b372c1a6a246ae63f74f931e8365e15a089c68d6190000000000'.decode('hex')
    genesis_merkle_root = '3ba3edfd7a7b12b27ac72c3e67768f617fc81bc3888a51323a9fb8aa4b1e5e4a'.decode('hex')
    genesis_timestamp = 1231006505
    genesis_bits = 486604799
    genesis_nonce = 2083236893

    magic = '\xf9\xbe\xb4\xd9'

    address_version = chr(0)

    alert_public_key = '04fc9702847840aaf195de8442ebecedf5b095cdbb9bc716bda9110971b28a49e0ead8564ff0db22209e0374782c093bb899692d524e9d6a6956e7c5ecbcd68284'.decode('hex')

    # Not sure if these will be needed later... from chainparams
    secret_key = chr(239)
    ext_public_key = "".join(chr(i) for i in (0x04, 0x35, 0x87, 0xCF))
    ext_secret_key = "".join(chr(i) for i in (0x04, 0x35, 0x83, 0x94))

    script_address = chr(5)

    block_height_guess = [
        ('blockchain.info', util.fetch_url_json_path_int('https://blockchain.info/latestblock', 'height')),
        ('blockexplorer.com', util.fetch_url_int('https://blockexplorer.com/q/getblockcount')),
        ('blockr.io', util.fetch_url_json_path_int('http://btc.blockr.io/api/v1/coin/info', 'data/last_block/nb')),
        ('chain.so', util.fetch_url_json_path_int('https://chain.so/api/v2/get_info/BTC', 'data/blocks')),
    ]


#class BitcoinTestnet(Bitcoin):
#    name = "bitcoin-testnet"
#    address_version = chr(111)
#    magic = "\xfa\xbf\xb5\xda"

#class BitcoinTestnet3(Bitcoin):
#    name = "bitcoin-testnet3"
#    port = 18333
#    magic = "\x0b\x11\x09\x07"
#    alert_public_key = '04302390343f91cc401d56d68b123028bf52e5fca1939df127f63c6467cdf9c8e2c14b61104cf817d0b780da337893ecc4aaff1309e536162dabbdb45200ca2b0a'.decode('hex')
