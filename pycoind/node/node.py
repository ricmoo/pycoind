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


import random
import time
import sys

from .basenode import BaseNode

from .. import blockchain
from .. import coins
from .. import protocol

class Node(BaseNode):

    # maximum number of pending getdata requests for a peer to have in-flight
    MAX_INCOMPLETE_INFLIGHT = 10000

    # maximum number of incomplete blocks to track at a time (ish)
    MAX_INCOMPLETE_BLOCKS = 50000

    # maximum query limit for incomplete blocks
    MAX_INCOMPLETE_FETCH = 10000

    def __init__(self, data_dir = None, address = None, seek_peers = 16, max_peers = 125, bootstrap = True, log = sys.stdout, coin = coins.Bitcoin):
        BaseNode.__init__(self, data_dir, address, seek_peers, max_peers, bootstrap, log, coin)

        # blockchain database
        self._blocks = blockchain.block.Database(self.data_dir, self._coin)
        self._txns = self._blocks._txns

        # memory pool; circular buffer of 30,000 most recent seen transactions
        self._mempool_index = 0
        self._mempool = []
        self._prime_mempool()

        # how long since we last asked for headers or blocks
        self._last_get_headers = 0

        # maps blockhash to last request time
        self._incomplete_blocks = dict()
        self._last_incomplete_block = None

        # how many in-flight block requests per peer
        self._inflight_blocks = dict()


    @property
    def blockchain_height(self):
        return self._blocks[-1].height


    def _prime_mempool(self):
        # @TODO: on start-up pull in last couple of blocks' transactions
        pass

    def _add_mempool(self, txn):
        if len(self._mempool) > 30000:
            self._mempool[self._mempool_index] = txn
            self._mempool_index = (self._mempool_index + 1) % 30000
        else:
            self._mempool.append(txn)

    def _search_mempool(self, txid):
         txns = [t for t in self._mempool if t.hash == txid]
         if txns:
             return txns[0]
         return None


    def command_block(self, peer, version, prev_block, merkle_root, timestamp, bits, nonce, txns):

        try:
            # get the block
            header = protocol.BlockHeader(version, prev_block, merkle_root,
                                          timestamp, bits, nonce, 0)
            block = self._blocks.get(header.hash)
            if not block:
                raise blockchain.block.InvalidBlockException('block header not found')

            # add the transactions
            self._txns.add(block, txns)

            # update the memory pool
            for txn in txns:
                self._add_mempool(txn)

            # it is no longer incomplete
            if block.hash in self._incomplete_blocks:
                del self._incomplete_blocks[block.hash]

        except blockchain.block.InvalidBlockException, e:
            self.punish_peer(peer, str(e))

        # give the peer more room to request blocks
        if peer in self._inflight_blocks:
            self._inflight_blocks[peer] -= 1
            if self._inflight_blocks[peer] < 0:
                self._inflight_blocks[peer] = 0


    def command_get_blocks(self, peer, version, block_locator_hashes, hash_stop):
        blocks = self._blocks.locate_blocks(block_locator_hashes, 500, hash_stop)

        # we found their place on the blockchain
        if blocks:
            inv = [protocol.InventoryVector(protocol.OBJECT_TYPE_MSG_BLOCK, b.hash) for b in blocks]
            self.send_message(protocol.Inventory(inv))

        # we didn't find anything that matched their locator... What to do? not_found?
        else:
            self.send_message(protocol.NotFound(block_locator_hashes))


    def command_get_data(self, peer, inventory):

        # look up each block and transaction requested
        notfound = [ ]
        for iv in inventory:

            if iv.type == protocol.OBJECT_TYPE_MSG_BLOCK:

                # search the database
                block = self._blocks.get(iv.hash)

                # if we found one, return it
                if block:
                    peer.send_message(protocol.Block(block.block_message()))
                else:
                    notfound.append(iv)

            elif iv.type == protocol.OBJECT_TYPE_MSG_TX:

                # search the memory pool and database
                txn = self._search_mempool(iv.hash)
                if not txn:
                    tx = self._txns.get(iv.hash)
                    if tx: txn = tx.txn

                # if we found one, return it
                if txn:
                    peer.send_message(txn)
                else:
                    notfound.append(iv)

        # anything not found?
        if notfound:
            peer.send_message(protocol.NotFound(notfound))


    def command_get_headers(self, peer, version, block_locator_hashes, hash_stop):
        # Send the list of headers
        blocks = self._blocks.locate_blocks(block_locator_hashes, 2000, hash_stop)
        peer.send_message(protocol.Headers([protocol.BlockHeader.from_block(b) for b in blocks]))


    def command_headers(self, peer, headers):
        if len(headers) == 0: return

        # Add the headers to the database (we fill in the transactions later)
        new_headers = False
        for header in headers:
            try:
                added = self._blocks.add_header(header)
                if added:
                    new_headers = True
            except blockchain.block.InvalidBlockException, e:
                self.punish_peer(peer, str(e))


        # we got some headers, so we can request the next batch now
        self.sync_blockchain_headers(new_headers = new_headers)


    def command_inventory(self, peer, inventory):
        pass

        # look for new blocks being advertised by peers
        #def useful_block(iv):
        #    if iv.object_type != protocol.OBJECT_TYPE_MSG_BLOCK:
        #        return False
        #    if self._blockchain.get(iv.hash):
        #        return False
        #    return True

        #block_inventory = [iv for iv in inventory if useful_block(iv)]

        # @TODO: 
        # new block
        #if block_inventory:
        #    peer.send_message(protocol.GetData(block_inventory))


    def command_memory_pool(self, peer):
        inv = [protocol.InventoryVector(protocol.OBJECT_TYPE_MSG_TX, t.hash) for t in self._mempool]
        per.send_message(inv)


    def command_not_found(self, peer, inventory):

        # the peer did not have the blocks we were looking for, so we can send more
        block_count = len(b for b in inventory if b.object_type == protocol.OBJECT_TYPE_MSG_BLOCK)
        if peer in self._inflight_blocks:
            self._inflight_blocks[peer] -= block_count
            if self._inflight_blocks[peer] < 0:
                self._inflight_blocks[peer] = 0

    def command_version_ack(self, peer):
        BaseNode.command_version_ack(self, peer)

        # might be the first peer, see if we can sync some blockchain
        self.sync_blockchain_headers()
        self.sync_blockchain_blocks()

    def disconnected(self, peer):
        'Called by a peer after it has been closed.'

        BaseNode.disconnected(self, peer)

        if peer in self._inflight_blocks:
            del self._inflight_blocks[peer]

    def heartbeat(self):
        BaseNode.heartbeat(self)

        # if we have peers, poke them to sync the blockchain
        if self.peers:
            self.sync_blockchain_headers()
            self.sync_blockchain_blocks()

    def close(self):
        self._blocks.close()
        BaseNode.close(self)

    def sync_blockchain_headers(self, new_headers = False):

        # give getheaders at least 30 seconds to respond (new_headers means
        # it already did and we are ready to ask for more)
        if not new_headers and time.time() - self._last_get_headers < 30:
            return
        self._last_get_headers = time.time()

        # pick a peer that's ready
        peers = [p for p in self.peers if p.verack]
        if not peers: return
        peer = random.choice(peers)

        # request the next block headers (if any)
        locator = self._blocks.block_locator_hashes()
        getheaders = protocol.GetHeaders(self.coin.protocol_version, locator, chr(0) * 32)
        peer.send_message(getheaders)


    def sync_blockchain_blocks(self):

        # we can handle more incomplete blocks
        if len(self._incomplete_blocks) < self.MAX_INCOMPLETE_BLOCKS:
            incomplete = self._blocks.incomplete_blocks(from_block = self._last_incomplete_block, max_count = self.MAX_INCOMPLETE_FETCH)
            if incomplete:
                for block in incomplete:
                    if block.hash in self._incomplete_blocks: continue
                    self._incomplete_blocks[block.hash] = 0
                self._last_incomplete_block = incomplete[-1]

        # we have incomplete blocks, so request data from our peers
        if self._incomplete_blocks:
            now = time.time()

            peers = [p for p in self.peers if p.verack]
            random.shuffle(peers)
            for peer in peers:

                # this peer is already full
                inflight = self._inflight_blocks.get(peer, 0)
                if inflight >= self.MAX_INCOMPLETE_INFLIGHT:
                    continue

                # find some not-recently-requested blocks (over 5 minutes ago)
                getdata = []
                for hash in self._incomplete_blocks:
                    if now - self._incomplete_blocks[hash] < 300:
                        continue
                    self._incomplete_blocks[hash] = now

                    getdata.append(protocol.InventoryVector(protocol.OBJECT_TYPE_MSG_BLOCK, hash))
                    if len(getdata) + inflight >= self.MAX_INCOMPLETE_INFLIGHT:
                        break

                # nothing to request
                if not getdata:
                    break

                # ask the peer
                peer.send_message(protocol.GetData(getdata))

                # track how many inflight block requests this peer has
                if peer not in self._inflight_blocks:
                    self._inflight_blocks[peer] = 0
                self._inflight_blocks[peer] += len(getdata)

