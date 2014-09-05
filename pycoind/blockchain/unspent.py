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


# Unspent Transaction Output (utxo) Database
#
#   uock         - unspent output composite key (see below)
#   address_hint - hash integer, provides pruning to likely address
#

# Composite Keys
#
# We use composite keys so we can optimize space with the 8-byte rowid we get
# by default in a sqlite database as well as the speed gain as they are the
# keys in the B-Tree. (see: http://www.sqlite.org/lang_createtable.html#rowid)
#
#   uock (unspent-output-composite-key: 63 bits)
#     - (txck: 43 bits) (output-index: 20 bits)
#
# With this composite key, we can store up to 1 million outputs per
# transaction.

# Hints
#
# A hint (hash integer) the integer value of a byte string to quickly prune
# any obviously non-matching elements. The remaining elements must then be
# compared against confirmed values, since the hash may yield false positives.


import sqlite3
import multiprocessing
import signal
import time

from . import database
from . import keys

from .. import coins
from .. import script
from .. import util

__all__ = ['Database']


KEY_LAST_VALID_BLOCK = 2


_KEY_DUP = 'PRIMARY KEY must be unique'
_0 = chr(0) * 32


class InvalidTransactionException(Exception): pass


def init_worker():
    "Initialize a process to ignore keyboard interrupts."

    signal.signal(signal.SIGINT, signal.SIG_IGN)


def po_value(transaction, index):
    po = transaction.previous_output(index)
    if po:
        return po.value
    return 0


def verify(transaction):
    "Veryify a transaction's inputs and outputs."
    try:
        # do the inputs afford the outputs? (coinbase is an exception)
        fees = 0
        if transaction.index != 0:
            sum_in = sum(po_value(transaction, i) for i in xrange(0, len(transaction.inputs)))
            sum_out = sum(o.value for o in transaction.outputs)
            fees = sum_in - sum_out
            if fees < 0:
                print sum_in, sum_out
                print "FAIL(sum_in < sum_out)", transaction
                return (False, [], 0)

        # are all inputs valid against their previous output?
        txio = script.Script(transaction)
        valid = txio.verify()
        addresses = [txio.output_address(o) for o in xrange(0, txio.output_count)]

        if not valid:
            print transaction

        return (valid, addresses, fees)
    except Exception, e:
        print transaction, e
        import traceback
        traceback.print_exc()
        raise e


class Database(database.Database):
    Columns = [
        ('uock', 'integer primary key', False),
        ('address_hint', 'integer', True),
    ]
    Name = 'unspent'

    def __init__(self, data_dir, coin = coins.Bitcoin, processes = None):
        database.Database.__init__(self, data_dir, coin)

        self.sql_delete = 'delete from unspent where uock = ?'

        self._connection = self.get_connection()

        if processes is None or processes != 1:
            self._pool = multiprocessing.Pool(processes = processes, initializer = init_worker)
            print "Spawning %d processes" % self._pool._processes
        else:
            self._pool = None

    def populate_database(self, cursor):
        self.set_metadata(cursor, KEY_LAST_VALID_BLOCK, 1)

    @property
    def last_valid_block(self):
        cursor = self._connection.cursor()
        return self.get_metadata(cursor, KEY_LAST_VALID_BLOCK)

    def _todo_rollback(self, block):
        'Undo all unspent transactions for a block. Must be the latest valid block.'

        # this would break our data model (but shouldn't be possible anyways)
        if block._blockid <= 1:
            raise ValueError('cannot remove pre-genesis block')

        # get the base uock for this block (ie. txn_index == output_index == 0)
        txck = keys.get_txck(block._blockid, 0)
        uock = keys.get_uock(txck, 0)

        # begin a transaction, locking out other updates
        cursor = self._connection.cursor()
        cursor.execute('begin immediate transaction')

        # make sure we are removing a block we have already added
        last_valid_block = self.get_metadata(cursor, KEY_LAST_VALID_BLOCK)
        if last_valid_block != block._blockid:
            raise ValueError('can only rollback last valid block')

        # remove all outputs
        raise NotImplemented()

        # re-add all inputs' outputs
        raise NotImplemented()

        # the most recent block is now the previous block
        self.set_metadata(cursor, KEY_LAST_VALID_BLOCK, block._previous_blockid)

        self._connection.commit()


    def update(self, block):
        '''Updates the unspent transaction output (utxo) database with the
           transactions from a block.'''

        t0 = time.time()

        txns = block.transactions
        for txn in txns:
            txn.cache_previous_outputs()

        t1 = time.time()

        if self._pool is None:
            results = map(verify, txns)
        else:
            results = self._pool.map(verify, txns)

        # make sure the coinbase's output doesn't exceed its permitted fees
        fees = sum(r[2] for r in results)
        fees += self.coin.block_creation_fee(block)
        sum_out = sum(o.value for o in txns[0].outputs)
        if fees < sum_out:
            raise InvalidTransactionException('invalid coinbase fee')

        t2 = time.time()

        # update the database
        self._update(block, [(t, r[0], r[1]) for (t, r) in zip(txns, results)])

        t3 = time.time()

        print "Processed %d transaction (cache=%fs, compute=%fs, update=%fs)" % (len(txns), t1 - t0, t2 - t1, t3 - t2)


    def _update(self, block, results):

        # lock the database
        cursor = self._connection.cursor()
        cursor.execute('begin immediate transaction')

        # make sure we are adding the next block (haven't skipped any)
        last_valid_block = self.get_metadata(cursor, KEY_LAST_VALID_BLOCK)
        if last_valid_block != block._previous_blockid:
            raise InvalidTransactionException('must add consequetive block')

        for (txn, valid, addresses) in results:

            # invalid transaction
            if not valid:
                raise InvalidTransactionException('temporary')
                print "invalid", txn
                continue

            # remove each input's previous outputs
            for i in xrange(0, len(txn.inputs)):
                uock = txn._previous_uock(i)
                if uock is None: continue

                txck = keys.get_uock_txck(uock)
                #print '-', keys.get_txck_blockid(txck), keys.get_txck_index(txck), keys.get_uock_index(uock), txn.previous_output(i).value

                cursor.execute(self.sql_delete, (uock, ))
                if cursor.rowcount != 1:
                    raise Exception('bad state: failed to delete a utxo')

            # add new outputs (with a hint of the address)
            for (o, address) in enumerate(addresses):
                uock = keys.get_uock(txn._txck, o)

                #print '+', keys.get_txck_blockid(txn._txck), keys.get_txck_index(txn._txck), o, txn.outputs[o].value

                address_hint = keys.get_address_hint(address)
                try:
                    cursor.execute(self.sql_insert, (uock, address_hint))

                # (duplicates don't matter)
                except sqlite3.IntegrityError, e:
                    if e.message != _KEY_DUP:
                        raise e

        # update last valid block
        self.set_metadata(cursor, KEY_LAST_VALID_BLOCK, block._blockid)

        self._connection.commit()



    def _list_unspent(self, address):
        address_hint = keys.get_address_hint(address)
        cursor = self._connection.cursor()
        cursor.execute('select uock from unspent where address_hint = ?', (address_hint, ))

        return [r[0] for r in cursor.fetchall()]
        #for row in cursor.fetchall():
        #    uock = row[0]
        #    txck = keys.get_uock_txck(uock)
        #    output_index = keys.get_uock_index(uock)
        #    blockid = keys.get_txck_blockid(txck)
        #    txn_index = keys.get_txck_index(txck)
        #    txn = self._txndb._get_transactions(blockid)[txn_index]
        #    outputs.append(txn.tx_out[output_index])

        #return outputs
