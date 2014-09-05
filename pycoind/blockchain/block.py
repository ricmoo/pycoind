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


import math
import struct
import time

from . import database
from . import transaction

from .. import coins
from .. import util

__all__ = ['Database', 'InvalidBlockException']

# A buffer of 32 chr(0) bytes
_0 = buffer(chr(0) * 32)

class InvalidBlockException(Exception): pass

class Block(object):

    def __init__(self, database, row):
        keys = [n for (n, t, i) in database.Columns]

        self.__database = database
        self.__data = dict(zip(keys, row))

    coin = property(lambda s: s.__database.coin)

    hash = property(lambda s: str(s.__data['hash']))

    version = property(lambda s: s.__data['version'])
    merkle_root = property(lambda s: str(s.__data['merkle_root']))
    timestamp = property(lambda s: s.__data['timestamp'])
    bits = property(lambda s: s.__data['bits'])
    nonce = property(lambda s: s.__data['nonce'])

    height = property(lambda s: s.__data['height'])
    txn_count = property(lambda s: s.__data['txn_count'])

    mainchain = property(lambda s: s.__data['mainchain'])

    @property
    def transactions(self):
        if self.txn_count == 0:
            return None

        if 'txns' not in self.__data:
            txns = tuple(self.__database._txns._get_transactions(self._blockid))
            self.__data['txns'] = txns

        return self.__data['txns']

    @property
    def previous_hash(self):
        block = self.previous_block
        if block:
            return block.hash
        return None

    @property
    def previous_block(self):
        cursor = self.__database._cursor()
        cursor.execute(self.__database.sql_select + ' where id = ?', (self._previous_blockid, ))
        row = cursor.fetchone()
        if row:
            return Block(self.__database, row)
        return None

    @property
    def next_block(self):
        cursor = self.__database._cursor()
        cursor.execute(self.__database.sql_select + ' where previous_id = ?', (self._blockid, ))
        row = cursor.fetchone()
        if row:
            return Block(self.__database, row)
        return None

    def __str__(self):
        return '<Block %s>' % (self.hash.encode('hex'), )


    # mostly just for internal use... mostly.
    _blockid = property(lambda s: s.__data['id'])
    _previous_blockid = property(lambda s: s.__data['previous_id'])

    def _check_merkle_root(self, merkle_root):
        'Checks the merkle_root is correct. Internal use.'

        if merkle_root != self.merkle_root:
            raise InvalidBlockException('invalid merkle root')

    def _update_transactions(self, transactions):
        '''Update the database with the transaction count and attaches the
           transactions to this Block instance. INTERNAL USE ONLY!!'''

        cursor = self.__database._cursor()
        cursor.execute('update blocks set txn_count = ? where id = ?', (len(transactions), self._blockid))
        self.__database._connection.commit()

        self.__data['txns'] = transactions
        self.__data['txn_count'] = len(transactions)


class Database(database.Database):

    Columns = [
        ('id', 'integer primary key', False),
        ('previous_id', 'integer not null', True),

        ('hash', 'blob unique not null', True),
        ('version', 'integer not null', False),
        ('merkle_root', 'blob not null', False),
        ('timestamp', 'integer not null', False),
        ('bits', 'integer not null', False),
        ('nonce', 'integer not null', False),

        ('height', 'integer not null', True),
        ('txn_count', 'integer not null', True),
        ('mainchain', 'boolean not null', False),
    ]

    Name = 'blocks'

    def __init__(self, data_dir = None, coin = coins.Bitcoin):
        database.Database.__init__(self, data_dir, coin)

        # connect to the block database
        self._connection = self.get_connection()

        # transaction database (used by Block to for .transactions)
        self._txns = transaction.Database(self.data_dir, coin)


    def populate_database(self, cursor):

        # add an entry for the block previous to the genesis block
        pregenesis = [-1, _0, 1, _0, 0, 0, 0, -1, -1, 1]
        cursor.execute(self.sql_insert, pregenesis)

        # add the genesis block
        genesis = [
            cursor.lastrowid,                          # previous_id
            buffer(self.coin.genesis_block_hash),
            self.coin.genesis_version,
            buffer(self.coin.genesis_merkle_root),
            self.coin.genesis_timestamp,
            self.coin.genesis_bits,
            self.coin.genesis_nonce,
            0,                                         # height
            0,                                         # txn_count
            1,                                         # mainchain
        ]
        cursor.execute(self.sql_insert, genesis)


    def _cursor(self):
        return self._connection.cursor()


    def add_header(self, header):
        '''Adds a block to the database (if not present) and returns it.

           If a block's transactions is None, it means that only the block
           header is present in the database.'''

        # Calculate the block hash
        binary_header = header.binary()[:80]

        block_hash = util.sha256d(binary_header)

        # Already exists and nothing new
        existing = self.get(block_hash)
        if existing:
            return False
            #return existing

        # verify the block hits the target
        if not util.verify_target(self.coin, header):
            raise InvalidBlockException('block proof-of-work is greater than target')

        # find the previous block
        previous_block = self.get(header.prev_block, orphans = True)
        if not previous_block:
            raise InvalidBlockException('previous block does not exist')

        cursor = self._cursor()
        cursor.execute('begin immediate transaction')

        # find the top block
        cursor.execute(self.sql_select + ' where mainchain = 1 order by height desc limit 1')
        top_block = Block(self, cursor.fetchone())

        height = previous_block.height + 1

        mainchain = bool(height > top_block.height)

        # we building off of a sidechain that will become the mainchain?
        if mainchain and not previous_block.mainchain:

            # update all blocks from previous_block to the fork as mainchain
            cur = previous_block
            while not cur.mainchain:
                cursor.execute('update blocks set mainchain = 1 where id = ?', (cur._blockid, ))
                cur = cur.previous_block

            forked_at = cur.hash

            # update all blocks from the old top (now orphan) to the fork as not mainchain
            cur = top_block
            while cur.hash != forked_at:
                cursor.execute('update blocks set mainchain = 0 where id = ?', (cur._blockid, ))
                cur = cur.previous_block

        # add the block to the database
        cursor = self._cursor()
        row = (previous_block._blockid, buffer(block_hash), header.version,
               buffer(header.merkle_root), header.timestamp, header.bits,
               header.nonce, height, 0, mainchain)
        cursor.execute(self.sql_insert, row)
        #lastrowid = cursor.lastrowid
        self._connection.commit()

        return True
        #return Block(self, (lastrowid, ) + row)


    def _get(self, blockid):
        'Return a block for a blockid. Internal use only.'

        cursor = self._cursor()
        cursor.execute(self.sql_select + ' where id = ?', (blockid, ))
        row = cursor.fetchone()
        if row:
            return Block(self, row)

        return None


    def get(self, blockhash, default = None, orphans = False):
        'Return the block with the hash, or None if not in the block chain.'

        sql = ' where hash = ?'
        if not orphans:
            sql += ' and mainchain = 1'

        cursor = self._cursor()
        cursor.execute(self.sql_select + sql, (buffer(blockhash), ))
        row = cursor.fetchone()
        if row:
            return Block(self, row)

        return default


    def block_locator_hashes(self):
        'Return a list of hashes suitable as a block locator hash.'

        # Find the height of the block chain
        hashes = [ ]

        # First 10...
        offset = 0
        cursor = self._cursor()
        cursor.execute('select hash, height from blocks where mainchain = 1 and height > 0 order by height desc limit 10')
        rows = cursor.fetchall()
        hashes.extend([str(hash) for (hash, offset) in rows])
        offset -= 1

        # ...then step down by twice the previous step...
        if offset > 0:
            for i in xrange(1, int(math.log(2 * offset, 2))):
                if offset <= 1: break
                cursor.execute('select hash from blocks where mainchain = 1 and height = ?', (offset, ))
                hashes.append(str(cursor.fetchone()[0]))
                offset -= (1 << i)

        # ...finally the genesis hash
        hashes.append(self.coin.genesis_block_hash)

        return hashes


    def locate_blocks(locator, count = 500, hash_stop = None):

        # Find the first block that matches
        block = None
        for hash in locator:
            block = self.get_block(hash)
            if block: break

        # no matching block... :'(
        if block is None:
            return None

        # Select the next count rows
        cursor = self._cursor()
        sql = ' where mainchain = 1 and height > ? order by height limit %d' % count
        cursor.execute(self._SELECT + sql, (block.height, ))

        # Wrap the row in the Block object
        blocks = [ ]
        for row in cursor.fetchall():
            block = Block(self, row)
            blocks.append(block)
            if hash_stop == block.hash: break

        return blocks


    def __getitem__(self, name):

        row = None

        # negative height, search from the top
        if name < 0:

            # get the highest block
            cursor = self._cursor()
            cursor.execute(self.sql_select + ' where mainchain = 1 order by height desc limit 1')
            row = cursor.fetchone()

            # row is currently the top (ie. -1); otherwise use the below search
            if name != -1:
                row = None
                name += highest.height + 1

        # find the block
        if name >= 0 and row is None:
            cursor = self._cursor()
            cursor.execute(self.sql_select + ' where mainchain = 1 and height = ?', (name, ))
            row = cursor.fetchone()

        # wrap it up and return it
        if row:
            return Block(self, row)

        # nothing found
        raise IndexError()


    def __len__(self):
        highest = self[-1]
        return highest.height + 1


    def incomplete_blocks(self, from_block = None, max_count = 1000):
        cursor = self._cursor()

        sql = ' where txn_count = 0 and mainchain = 1'
        if from_block:
            sql += (' and id > %d' % from_block._blockid)

        sql += ' order by id asc'

        if max_count:
            sql += (' limit %d' % max_count)

        cursor.execute(self.sql_select + sql)

        return [Block(self, r) for r in cursor.fetchall()]


    def incomplete_block_count(self):
        cursor = self._cursor()
        cursor.execute('select count(*) from blocks where txn_count = 0 and mainchain = 1')
        return cursor.fetchone()[0]


    def _TODO_generate_checkpoint_list(self):
        '''Build a list of hashes that make good checkpoints.

           What makes a good checkoint?
           - all nearby blocks have monotonic timestamps
           - contains no "strange" transactions

           See: https://github.com/bitcoin/bitcoin/blob/master/src/checkpoints.cpp'''

        pass


    def close(self):
        self._connection.close()


    def __iter__(self):
        cursor = self._cursor()
        cursor.execute(self.sql_select + ' where mainchain = 1 order by height asc')

        # skip the pre-genesis block
        cursor.fetchone()

        while True:
            rows = cursor.fetchmany()
            if not rows: raise StopIteration()
            for row in rows:
                yield Block(self, row)


