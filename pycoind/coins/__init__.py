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


from bitcoin import Bitcoin
from coinyecoin import Coinyecoin
from dogecoin import Dogecoin
from feathercoin import Feathercoin
from flappycoin import Flappycoin
from litecoin import Litecoin
from mooncoin import Mooncoin
from potcoin import Potcoin
from zetacoin import Zetacoin

from coin import satoshi_per_coin

__all__ = [
    'Bitcoin', 'Coinyecoin', 'Dogecoin', 'Feathercoin', 'Flappycoin',
    'Litecoin', 'Mooncoin', 'Potcoin', 'Zetacoin',
    'Coins', 'get_coin',
    'satoshi_per_coin'
]

Coins = [
    Bitcoin,
    Coinyecoin,
    Dogecoin,
    Feathercoin,
    Flappycoin,
    Litecoin,
    Mooncoin,
    Potcoin,
    Zetacoin,
]


def get_coin(name = None, symbol = None):

    if name is None: name = ''
    if symbol is None: symbol = ''

    for coin in Coins:
        if name and name.lower() == coin.name or symbol.upper() in coin.symbols:
            return coin

    return None
