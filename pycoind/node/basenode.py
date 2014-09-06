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


import asyncore
import random
import socket
import sys
import time

from . import connection
from .. import coins, protocol, util

from ..util.bootstrap import DNSSeeder

__all__ = [
    'AddressInUseException', 'DEV_PUBLIC_KEY', 'Node', 'StopNode',
]

PUBLIC_KEY = '045e4dd6dab7e1db2c2754053adf610c02819f93b4fa79d2f3ba19964521b798096c9629226801994c2141a48d00b826973b7028cad5bbd1f219ac91c3a3e00ee5'.decode('hex')

# Maximum number of address we will store in memory
MAX_ADDRESSES = 2500

# Maximum recent messages a peer can ask to be relayed
MAX_RELAY_COUNT = 100

# How many messages per second we forget from each peer
RELAY_COUNT_DECAY = 10

class AddressInUseException(Exception): pass

class StopNode(Exception): pass

VERSION = [0, 0, 2]

class BaseNode(asyncore.dispatcher, object):

    alert_public_key = PUBLIC_KEY

    LOG_LEVEL_PROTOCOL = 0
    LOG_LEVEL_DEBUG    = 1
    LOG_LEVEL_INFO     = 2
    LOG_LEVEL_ERROR    = 3
    LOG_LEVEL_FATAL    = 4

    def __init__(self, data_dir = None, address = None, seek_peers = 16, max_peers = 125, bootstrap = True, log = sys.stdout, coin = coins.Bitcoin):
        asyncore.dispatcher.__init__(self, map = self)

        if data_dir is None:
            data_dir = util.default_data_directory()

        self._data_dir = data_dir

        # set up the default listen address
        self._listen = True  # @TODO: remove _listen and ideally set up no listen socket
        if address is None:
            address = ('127.0.0.1', 0)
            self._listen = False

        self._address = address

        self._seek_peers = seek_peers
        self._max_peers = max_peers

        self._bootstrap = None
        if bootstrap:
            self._bootstrap = DNSSeeder(coin.dns_seeds)

        self._log = log
        self._log_level = self.LOG_LEVEL_ERROR

        self._coin = coin

        # our external IP address (see _check_external_ip_address)
        self._guessed_external_ip_address = address[0]
        self._external_ip_address = None

        # total bytes we have sent and received
        self._tx_bytes = 0
        self._rx_bytes = 0

        self._banned = dict()

        self._alerts = dict()

        self._user_agent = '/pycoind:%s(%s)/' % ('.'.join(str(i) for i in VERSION), coin.name)

        # heartbeat every 10s for maintenance
        self._last_heartbeat = 0

        # the map we emulate a map on top of to pass self into asyncore as map
        self._peers = dict()

        # map of (address, port) tuples to (timestamp, service) tuples
        self._addresses = dict()

        # relay_count maps peer to number of messages sent recently so we can
        # throttle peers that seem *too* chatty
        self._relay_count = dict()
        self._last_relay_decay = time.time()

        # Create a listening socket; when we get an incoming connection
        # handle_accept will spawn a new peer.
        try:
            self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
            self.set_reuse_addr()
            self.bind(address)
            self.listen(5)

            # we bound to a random port, keep track of that
            if address[1] == 0:
                self._address = self.getsockname()

        # port in use... Maybe already running.
        except socket.error, e:
            if e.errno == 48:
                raise AddressInUseException()
            raise e


    data_dir = property(lambda s: s._data_dir)

    # When connecting to a peer, the current blockchain height is included.
    # Sub-classes should override this or keep it updated.
    blockchain_height = 0

    # the address as an (ip_address, port) tuple
    address = property(lambda s: s._address)

    ip_address = property(lambda s: s._address[0])
    port = property(lambda s: s._address[1])

    def _get_external_ip_address(self):
        if self._external_ip_address:
            return self._external_ip_address
        return self._guessed_external_ip_address
    def _set_external_ip_address(self, address):
        self._external_ip_address = address
    external_ip_address = property(_get_external_ip_address, _set_external_ip_address)

    rx_bytes = property(lambda s: s._rx_bytes)
    tx_bytes = property(lambda s: s._tx_bytes)

    coin = property(lambda s: s._coin)

    def _get_user_agent(self):
        return self._user_agent
    def _set_user_agent(self, user_agent):
        self._user_agent = user_agent
    user_agent = property(_get_user_agent, _set_user_agent)

    def _get_log_level(self):
        return self._log_level
    def _set_log_level(self, log_level):
        self._log_level = log_level
    log_level = property(_get_log_level, _set_log_level)


    def log(self, message, peer = None, level = LOG_LEVEL_INFO):
        if self._log is None or level < self._log_level: return
        if peer:
            source = peer.address[0]
        else:
            source = 'node'
        message = '(%s) %s' % (source, message)

        #if message.find('Traceback') == -1:
        #    message = message[:100]

        print >>self._log, message

    # Relaying
    # @TODO: not implemented yet and won't be made available until
    # checkpointing is implemented which won't be available until
    # my code has validated the entire blockchain (currently at 222K/317K)

    def relay(self, message, peer):
        "Relay a message for a peer, providing it has not reached its quota."

        # relaying will not be implemented until checkpoints are
        return

        # quota reached for this peer
        if self._relay_count.get(peer, 0) > MAX_RELAY_COUNT:
            return

        # track this relay request
        if peer not in self._relay_count: self._relay_count[peer] = 0
        self._relay_count[peer] += 1

        # relay to every peer except the sender
        for n in self.peers:
            if n == peer: continue
            peer.send(message)


    def _decay_relay(self):
        'Apply aging policy for throttling relaying per peer.'

        # relaying will not be implemented until checkpoints are
        return

        dt = time.time() - self._last_relay_decay
        for peer in list(self._relay_count):
            count = self._relay_count[peer]
            count -= dt * RELAY_COUNT_DECAY
            if count <= 0.0:
                del self._relay_count[peer]
            else:
                self._relay_cound[peer] = count

        self._last_relay_decay = time.time()


    # peer state management

    def serve_forever(self):
        'Block and begin accepting connections.'

        try:
            asyncore.loop(5, map = self)
        except StopNode, e:
            pass
        finally:
            self.handle_close()

    def close(self):
        asyncore.dispatcher.close(self)


    # Node management

    def add_peer(self, address, force = True):
        '''Connect a new peer peer.

           If force is False, and we already have max_peers, then the
           peer is not connected.'''

        # already have enough peers
        if not force and len(self) >= self._max_peers: return False

        # already a peer
        if address in [n.address for n in self.values()]:
            return False

        try:
            # asyncore keeps a reference in the map (ie. node = self)
            connection.Connection(address = address, node = self)
        except Exception, e:
            self.log(str(e))
            return False

        return True


    def remove_peer(self, address):
        'Remove a peer node.'

        for peer in self.peers:
            if peer.address == address:
                peer.handle_close()
                break


    @property
    def peers(self):
        'List of connected peer nodes.'

        return [n for n in self.values() if isinstance(n, connection.Connection)]


    # Alert management

    def alerts(self):
        def alert_sort(a, b):
            return cmp(self._alerts[a], self._alerts[b])
        return [a for a in sorted(self._alerts, alert_sort)]

    def clear_alerts(self):
        alerts = [ ]


    # Node callbacks for connections (subclasses can override these)

    def command_address(self, peer, addr_list):
        for address in addr_list:
            if len(self._addresses) > MAX_ADDRESSES: return
            self._addresses[(address.address, address.port)] = (address.timestamp, address.services)


    def command_alert(self, peer, version, relay_until, expiration, id, cancel, set_cancel, min_ver, max_ver, set_sub_ver, priority, comment, status_bar, reserved):
        self._alerts[status_bar] = time.time()


    def command_block(self, peer, version, prev_block, merkle_root, timestamp, bits, nonce, txns):
        pass


    def command_get_address(self, peer):
        addresses = [ ]

        # sorts addresses by timestamp
        def sort_address(a, b):
            return cmp(self._addresses[b][0], self._addresses[a][0])

        # add the most recent peers
        for address in sorted(self._addresses, sort_address):
            (timestamp, services) = self._addresses[address]
            if services is None: continue

            (ip_address, port) = address

            addresses.append(protocol.NetworkAddress(timestamp, services, ip_address, port))

            if len(address) >= 1000: break

        # Send the remote peer our list of addresses
        peer.send_message(message.Address(addresses))


    def command_get_blocks(self, peer, version, block_locator_hashes, hash_stop):
        self.send_message(protocol.NotFound(block_locator_hashes))


    def command_get_data(self, peer, inventory):
        for iv in inventory:
            peer.send_message(protocol.NotFound(iv))


    def command_get_headers(self, peer, version, block_locator_hashes, hash_stop):
        peer.send_message(protocol.Headers([]))


    def command_headers(self, peer, headers):
        pass


    def command_inventory(self, peer, inventory):
        pass


    def command_memory_pool(self, peer):
        pass


    def command_not_found(self, peer, inventory):
        pass


    def command_ping(self, peer, nonce):
        peer.send_message(protocol.Pong(nonce))


    def command_pong(self, peer, nonce):
        pass


    def command_reject(self, peer, message, ccode, reason):
        pass


    def command_transaction(self, peer, version, tx_in, tx_out, lock_time):
        pass


    def command_version(self, peer, version, services, timestamp, addr_recv, addr_from, nonce, user_agent, start_height, relay):
        peer.send_message(protocol.VersionAck())


    def command_version_ack(self, peer):

        # a peer acknowledged us, lets as for some addresses
        if len(self._addresses) < MAX_ADDRESSES:
            self._addresses[peer.address] = (peer.timestamp, peer.services)


    def invalid_command(self, peer, payload, exception):
        self.log("Invalid Command: %r (%s)" % (payload, exception))


    def invalid_alert(self, peer, alert):
        '''Called by a peer when an alert is invalid.

           An alert is invalid if the signature is incorrect, the alert has
           expired or the alert does not apply to this protocol version.'''

        self.log("Ignored alert: %s" % alert)


    def connected(self, peer):
        'Called by a peer once we know its capabilites (ie. Version message).'

        self._check_external_ip_address()


    def disconnected(self, peer):
        'Called by a peer after it has been closed.'

        if peer.address in self._addresses:
            del self._addresses[peer.address]


    # maintenance

    def punish_peer(self, peer, reason = None):
        peer.add_banscore()
        if peer.banscore > 5:
            self._banned[peer.ip_address] = time.time()
            peer.handle_close()

    def _check_external_ip_address(self):
        '''We rely on the peers we have connected to to tell us our IP address.

           Until we have connected peers though, this means we tell a white
           lie; we give our bound network ip address (usually 127.0.0.1).

           We ask all our peers what our address is, and take the majority
           answer. Even if we are lied to by dishonest/insane peers, the
           only problem is that we lie a bit more to our peers, which they
           likely ignore anyways, since they can determine it themselves more
           accurately from the tcp packets (like we do in handle_accept).'''

        tally = dict()
        for peer in self.peers:
            address = peer.external_ip_address
            if address is None: continue
            if address not in tally: tally[address] = 0
            tally[address] += 1

        if tally:
            tally = [(tally[a], a) for a in tally]
            tally.sort()

            self._guessed_external_ip_address = tally[-1][1]

    def add_any_peer(self):

        # if we don't have any addresses (and randomly, just sometimes) use a dns seed
        if not self._addresses or random.randint(0, 5) == 1:
            # use the DNS seeds to find some peers
            if self._bootstrap:
                self.add_peer(self._bootstrap.pop(), False)

        else:
            peers = self.peers

            # we have some addresses, add one
            active_addresses = [n.address for n in peers]
            for address in self._addresses:

                # don't use addresses we are already connected to
                if address in active_addresses: continue

                self.add_peer(address)
                break



    def heartbeat(self):
        'Called about every 10 seconds to perform maintenance tasks.'

        peers = self.peers

        # if we need more peer connections, attempt to add some (up to 5 at a time)
        for i in xrange(0, min(self._seek_peers - len(peers), 5)):
            self.add_any_peer()

        # if we don't have many addresses ask any peer for some more
        if peers and len(self._addresses) < 50:
            peer = random.choice(peers)
            peer.send_message(protocol.GetAddress())

        # Give a little back to peers that were bad but seem to be good now
        for peer in peers:
            peer.reduce_banscore()

        # Give all the peers a little more room for relaying
        self._decay_relay()

    # asyncore operations

    def begin_loop(self):
        'Sub-classes can override this to handle the start of the event loop.'

        pass

    def handle_accept(self):
        'Incoming connection, connect it if we have avaialble connections.'

        pair = self.accept()
        if not pair: return

        (sock, address) = pair

        # we banned this address less than an hour ago
        if address in self._banned:
            if time.time() - self._banned[address] < 3600:
                sock.close()
                return
            del self._banned[address]

        # we are not accepting incoming connections; drop it
        if not self._listen:
            sock.close()
            return

        # asyncore keeps a reference to us in the map (ie. node = self)
        connection.Connection(node = self, sock = sock, address = address)


    def readable(self):
        return True



    # emulate a dictionary so we an pass in the Node as the asyncode map

    def items(self):

        # map.items() gets called at the top of the asyncore loop

        self.begin_loop()

        # how long since we called heartbeat?
        now = time.time()
        if now - self._last_heartbeat > 10:
            self._last_heartbeat = now;
            self.heartbeat()

        return self._peers.items()

    def values(self):
        return self._peers.values()

    def keys(self):
        return self._peers.keys()

    def get(self, name, default = None):
        return self._peers.get(name, default)

    def __nonzero__(self):
        return True

    def __len__(self):
        return len(self._peers)

    def __getitem__(self, name):
        return self._peers[name]

    def __setitem__(self, name, value):
        self._peers[name] = value

    def __delitem__(self, name):
        del self._peers[name]

    def __iter__(self):
        return iter(self._peers)

    def __contains__(self, name):
        return name in self._peers


