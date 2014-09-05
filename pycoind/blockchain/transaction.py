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


# Transaction Database
#
#   txck      - transaction composite key (see below)
#   txid_hint - hash integer, provides pruning to likely txid
#   txn       - the binary blob of the transaction
#
# The database is broken up into files about 1.75GB each (so file systems like
# FAT32 work). The database filename contains two numbers, a number of
# partitions (N) and an index (i) which is in the range [0, N). These files
# will be denoted as file(N, i)
#
# When inserting, we insert into the highest N. Given an id, we insert into
# file(N, get_q(txid) % N). The function get_q hash bytes into an integer
#
# When searching, we must check each partition level, so to search for id, we
# start at the highest N, and check:
#    1. file(N, get_q(txid) % N)
#    2. file(N / 2, get_q(txid) % (N / 2))
#    3. file(N / 4, get_q(txid) % (N / 4))
# and so on, until we reach a k, such that (N / (2 ** k)) < 4.
#
# We can also, over time migrate values into higher levels. This is a future
# todo, if performance becomes an issue.

# Composite Keys
#
# We use composite keys so we can optimize space with the 8-byte rowid we get
# by default in a sqlite database as well as the speed gain as they are the
# keys in the B-Tree. (see: http://www.sqlite.org/lang_createtable.html#rowid)
#
#   txck (transaction-composite-key: 43 bits)
#     - (block-id:23 bits) (txn-index:20 bits)
#
# With these keys, we can support up to 8 million blocks, each block with up
# to 1 million transactions.

# Hints
#
# A hint (hash integer) the integer value of a byte string to quickly prune
# any obviously non-matching elements. The remaining elements must then be
# compared against confirmed values, since the hash may yield false positives.


import os
import random
import sqlite3
import struct

from . import database
from . import keys

from .. import coins
from .. import protocol
from .. import script
from .. import util

__all__ = ['Database']


def get_q(txid):
    'Compute the index q from a txid.'

    return struct.unpack('>I', txid[:4])[0]


_KEY_DUP = 'PRIMARY KEY must be unique'

_0 = chr(0) * 32

class Transaction(object):

    def __init__(self, database, row, _transaction = None):
        keys = [n for (n, t, i) in database.Columns]

        self._database = database
        self._data = dict(zip(keys, row))

        # cache for previous outputs' transactions, since it hits the database
        self._po_cache = dict()

        self._transaction = _transaction

    version = property(lambda s: s.txn.version)

    inputs = property(lambda s: s.txn.tx_in)
    outputs = property(lambda s: s.txn.tx_out)

    lock_time = property(lambda s: s.txn.lock_time)

    hash = property(lambda s: s.txn.hash)

    index = property(lambda s: keys.get_txck_index(s._txck))

    def __getstate__(self):
        return (self._po_cache, dict(txn = str(self._data['txn']), txck = self._data['txck']))

    def __setstate__(self, state):
        self._database = None

        (self._po_cache, self._data) = state

        self._transaction = None

    def cache_previous_outputs(self):
        for i in xrange(0, len(self.inputs)):
            self.previous_transaction(i)

    def previous_transaction(self, index):
        "Returns the previous output's transaction for the input at index."

        # coinbase transaction
        if self.index == 0 and index == 0:
            return None

        # look up the previous output's transaction and cache it
        if index not in self._po_cache:
            po_hash = self.inputs[index].previous_output.hash

            previous_txn = self._database.get(po_hash)
            if previous_txn is None:
                raise KeyError('missing transaction: %s' % po_hash)

            self._po_cache[index] = previous_txn

        # return the cache value
        return self._po_cache[index]

    def previous_output(self, index):
        'Returns the previous output for the input at index.'

        previous_txn = self.previous_transaction(index)
        if previous_txn is None: return None

        po = self.inputs[index].previous_output
        return previous_txn.outputs[po.index]

    def __str__(self):
        return "<Transaction hash=0x%s>" % self.hash.encode('hex')

    # transaction composite key and database block id; internal use
    _txck = property(lambda s: s._data['txck'])
    _blockid = property(lambda s: keys.get_txck_blockid(s._txck))

    def _previous_uock(self, index):

        previous_txn = self.previous_transaction(index)
        if previous_txn is None: return None

        po = self.inputs[index].previous_output
        return keys.get_uock(previous_txn._txck, po.index)

    @property
    def txn(self):
        'The raw transaction object.'

        if self._transaction is None:
            (vl, self._transaction) = protocol.Txn.parse(self.txn_binary)
        return self._transaction

    txn_binary = property(lambda s: str(s._data['txn']))


class Database(database.Database):

    MINIMUM_N = 4

    TARGET_SIZE = (1 << 30) * 7 // 4     # 1.75GB

    Columns = [
        ('txck', 'integer primary key', False),
        ('txid_hint', 'integer', True),
        ('txn', 'blob', False),
    ]

    Name = 'txns'

    def __init__(self, data_dir = None, coin = coins.Bitcoin):
        database.Database.__init__(self, data_dir, coin)

        # maps (n, i % n) tuples to sqlite connection
        self._connections = dict()

        # the largest N level on disk
        self._N = self.load_n()

        # loading/creating a connection loads/creates the entire level
        n = self._N
        while n >= self.MINIMUM_N:
            self.get_connection(n, 0, True)
            n //= 2

        #self._unspent = unspent.Database(self.data_dir, coin)

    def load_n(self):
        'Determine the highest N for a database directory.'

        n = self.MINIMUM_N
        while True:
            if not os.path.isfile(self.get_filename(self.get_suffix(n * 2, 0))):
                break
            n *= 2
        return n


    def get_suffix(self, n, q):
        return '-%03d-%03d' % (n, q % n)


    def get_connection(self, n, q, allow_create = False):
        '''Get a connection for the database file at (n, q % n). First a
           connection cache is searched. Then the disk is checked for new
           files, in which case every file at level n is loaded.

           If allow_create and the database file does not exist, all
           partitions at the level n are created.'''

        # the location we want
        loc = (n, q % n)
        if loc not in self._connections:

            locs = [(n, i) for i in xrange(0, n)]

            # doesn't exist; create the files backward
            if not os.path.isfile(self.get_filename(self.get_suffix(n, 0))):
                if not allow_create: return None
                locs.reverse()

            for l in locs:
                suffix = self.get_suffix(l[0], l[1])
                self._connections[l] = database.Database.get_connection(self, suffix)

        return self._connections[loc]


    def check_size(self):
        'Checks the sizes of the database level, increasing the size as needed.'

        # if any (statistically selected) database is full, increase our size
        suffix = self.get_suffix(self._N, random.randint(0, self._N - 1))
        filename = self.get_filename(suffix)
        if os.path.getsize(filename) > self.TARGET_SIZE:
            self._N *= 2
            self.get_connection(self._N, 0, True)


    def add(self, block, transactions):
        'Add transactions to the database.'

        # expand the database if necessary
        self.check_size()

        # check the merkle root of the transactions against the block
        block._check_merkle_root(util.get_merkle_root(transactions))

        # for each transaction...
        connections = dict()
        block_txns = [ ]
        for (txn_index, txn) in enumerate(transactions):

            # ...get the database to save to
            txid = txn.hash
            q = get_q(txid)
            connection = self.get_connection(self._N, q)
            connections[(self._N, q % self._N)] = connection

            # ...insert
            cursor = connection.cursor()
            txck = keys.get_txck(block._blockid, txn_index)
            row = (txck, keys.get_hint(txid), buffer(txn.binary()))
            try:
                cursor.execute(self.sql_insert, row)

            # (duplicates don't matter)
            except sqlite3.IntegrityError, e:
                if e.message != _KEY_DUP:
                    raise e

            # wrap up the transaction for the returned block
            block_txns.append(Transaction(self, row, txn))

        # commit the transactions to the databases
        for connection in connections.values():
            connection.commit()

        # update the block with the transactions
        block._update_transactions(block_txns)

        # return the now updated block
        return block

    # @TODO optimization: store in each txn db a max_blockid so we can prune
    def _get(self, txck):
        ''

        for connection in self._connections.values():
            cursor = connection.cursor()
            cursor.execute(self.sql_select + ' where txck = ?', (txck, ))
            row = cursor.fetchone()
            if row:
                return Transaction(self, row)

        return None

    def _get_transactions(self, blockid):
        "Find all transactions for a block, ordered by transaction index. Internal use."

        # the range that this block's composite keys can have [lo, hi)
        lo = keys.get_txck(blockid, 0)
        hi = keys.get_txck(blockid + 1, 0)

        # find all transactions across all databases within this range
        txns = [ ]
        for connection in self._connections.values():
            cursor = connection.cursor()
            cursor.execute(self.sql_select + ' where txck >= ? and txck < ?', (lo, hi))
            txns.extend((r[0], r) for r in cursor.fetchall())

        # sort by index (actually (blockid, index), but all have same blockid)
        txns.sort()

        # wrap it up in a helpful wrapper
        return [Transaction(self, row) for (txck, row) in txns]


    def get(self, txid, default = None):
        'Get a transaction by its txid.'

        # the hint we index by for faster lookup
        txid_hint = keys.get_hint(txid)

        # search each level (n, n // 2, n // 4, etc)
        n = self._N
        q = get_q(txid)
        while n >= self.MINIMUM_N:
            connection = self.get_connection(n, q)

            cursor = connection.cursor()
            cursor.execute(self.sql_select + ' where txid_hint = ?', (txid_hint, ))
            for row in cursor.fetchall():
                (vl, txn) = protocol.Txn.parse(row[2])
                if txn.hash == txid:
                    return Transaction(self, row, txn)

            n //= 2

        # maybe another process grew us, and we didn't know? Try again.
        new_n = self.load_n()
        if new_n != self._N:
            self._N = new_n
            return self._get(txid)

        return default


    #def __getitem__(self, name):
    #    'Get a transaction by its txid.'
    #
    #    txn = self.get(name)
    #    if txn is not None:
    #        return txn
    #    raise KeyError(name)

    # Useful? Should it return a blockhain.transaction.Transaction or protocol.Txn?
    #def __iter__(self):
    #    'Iterate over every transaction. There is no meaningful order.'
    #
    #    for connection in self._connections.values():
    #        cursor = connection.cursor()
    #        cursor.execute(self.sql_select)
    #        while True:
    #            rows = cursor.fetchmany()
    #            if not rows: break
    #            for row in rows:
    #                #yield Transaction(self, row)
    #                (vl, txn) = protocol.Txn.parse(row[2])[1]
    #                yield txn
