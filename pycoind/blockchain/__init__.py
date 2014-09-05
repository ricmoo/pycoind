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


import threading

from . import block
from . import keys
from . import transaction
from . import unspent

from .. import coins
from .. import script
from .. import util

__all__ = ['BlockChain']

_0 = chr(0) * 32


class BlockChain(object):

    def __init__(self, data_dir = None, coin = coins.Bitcoin):
        if data_dir is None:
            data_dir = util.default_data_directory()
        self._data_dir = data_dir
        self._coin = coin

        # a block database also holds a reference to a transaction database
        self._blocks = block.Database(data_dir, coin)

        self._unspent = unspent.Database(data_dir, coin, processes = 1)

    data_dir = property(lambda s: s._data_dir)
    coin = property(lambda s: s._coin)


    def get_block(self, blockhash):
        'Return a block by its blockhash.'

        return self._blocks.get(blockhash)


    def get_transaction(self, txid):
        'Return a transaction by its txid.'

        return self._blocks._txns.get(txid)


    def get_transaction_block(self, transaction):
        'Return the block for a transaction.'

        return self._blocks._get(transaction._blockid)


    def get_unspent_outputs(self, address):
        'Return the list of unspent transaction outputs (utxo) for an address.'

        raise NotImplementedError('coming soon...')

        outputs = []
        for uock in self._unspent._list_unspent(address):

            # get the transaction for this utxo
            txck = keys.get_uock_txck(uock)
            txn = self._blocks._txns._get(txck)

            output_index = keys.get_uock_index(uock)

            # remove false positives (since the database only stores a hint)
            txio = script.Script(txn)
            if txio.output_address(output_index) == address:
                outputs.append(txn.outputs[output_index])

        return outputs


    def get_balance(self, address):
        'Return the current balance for an address.'

        raise NotImplementedError('coming soon...')

        return sum(o.value for o in self.get_unspent_outputs(address)) / 100000000.0


    def __getitem__(self, name):
        return self._blocks[name]

    def __len__(self):
        return len(self._blocks)

    def __iter__(self):
        for block in self._blocks:
            yield block

