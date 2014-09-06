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


import os
import sqlite3

from .. import coins, util

KEY_VERSION = 1

class DatabaseException(Exception): pass

class Database(object):

    # subclasses should set these;
    # Columns is a list of (column_name, column_type, should_index) tuples
    Columns = []
    Name = 'table_name'

    # if non-backwards-compatible changes are made, change this and opening
    # obsolete databases will raise an exception
    Version = 1

    def __init__(self, data_dir = None, coin = coins.Bitcoin):

        if data_dir is None:
            data_dir = util.default_data_directory()
        self.__data_dir = data_dir
        self.__coin = coin

        self.sql_select = 'select %s from %s' % (','.join(n for (n, t, i) in self.Columns), self.Name)

        offset = 0
        if len(self.Columns) and self.Columns[0][0] == 'id':
            offset = 1

        self.sql_insert = 'insert into %s (%s) values (%s)' % (
            self.Name,
            ','.join(n for (n, t, i) in self.Columns[offset:]),
            ','.join('?' for c in self.Columns[offset:])
        )


    data_dir = property(lambda s: s.__data_dir)
    coin = property(lambda s: s.__coin)

    def get_filename(self, extra = ''):
        return os.path.join(self.data_dir, '%s-%s%s.sqlite' % (self.coin.name, self.Name, extra))

    def get_connection(self, extra = ''):
        filename = self.get_filename(extra)
        connection = sqlite3.connect(filename, timeout = 30)
        connection.row_factory = sqlite3.Row
        self.initialize_database(connection)
        return connection

    def initialize_database(self, connection):
        cursor = connection.cursor()

        try:

            # create a metadata table to track version and custom keys/values
            sql = 'create table metadata (key integer primary key, value integer, value_bin blob)'
            cursor.execute(sql)

            # set the database version
            sql = 'insert into metadata (key, value, value_bin) values (?, ?, ?)'
            cursor.execute(sql, (KEY_VERSION, self.Version, None))

            # create table statement
            column_defs = ','.join("%s %s" % (n, t) for (n, t, i) in self.Columns)
            sql = 'create table %s (%s)' % (self.Name, column_defs)
            cursor.execute(sql)

            # add each index
            for (n, t, i) in self.Columns:
                if not i: continue

                sql = "create index index_%s on %s (%s)" % (n, self.Name, n)
                cursor.execute(sql)

            # let subclasses pre-populate the database
            self.populate_database(cursor)

            connection.commit()

        # this will happen every time except the first time
        except sqlite3.OperationalError, e:
            if e.message != ('table metadata already exists'):
                raise e

            # check the version is compatible
            version = self.get_metadata(cursor, KEY_VERSION)
            if version != self.Version:
                raise DatabaseException('incompatible database version: %d (expected %d)' % (version, self.Version))

    def set_metadata(self, cursor, key, value):
        '''Set metadata for this database; the caller must commit. The value may
           be either an integer or a string.'''

        if key == KEY_VERSION:
            raise ValueError('cannot change version')

        sql = 'insert or replace into metadata (key, value, value_bin) values (?, ?, ?)'

        if isinstance(value, int):
            cursor.execute(sql, (key, value, None))

        elif isinstance(value, str):
            cursor.execute(sql, (key, 0, buffer(value)))

        else:
            raise ValueError('value must be integer or string')

    def get_metadata(self, cursor, key, default = None):
        sql = 'select value, value_bin from metadata where key = ?'
        cursor.execute(sql, (key, ))
        row = cursor.fetchone()
        if row:
            if row[1] is not None:
                return str(row[1])
            return row[0]

        return default

    def populate_database(self, cursor):
        pass

