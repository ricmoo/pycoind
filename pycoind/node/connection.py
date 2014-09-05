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
import os
import socket
import sys
import time
import traceback

from .. import protocol
from .. import util


BLOCK_SIZE = 8192


class Connection(asyncore.dispatcher):
    '''A connection to a remote peer node.

       Handles buffering input and output into messages and call the
       corresponding command_* handler in daemon.'''

    SERVICES = protocol.SERVICE_NODE_NETWORK


    def __init__(self, node, address, sock = None):

        # this is also available as self._map from dispatcher
        self._node = node

        # send and receive buffers
        self._send_buffer = ""
        self._recv_buffer = ""

        # total byte count we have sent and received
        self._tx_bytes = 0
        self._rx_bytes = 0

        # last time we sent and receieved data
        self._last_tx_time = 0
        self._last_ping_time = 0
        self._last_rx_time = 0

        # remote node details
        self._address = address
        self._external_ip_address = None
        self._services = None
        self._start_height = None
        self._user_agent = None
        self._version = None
        self._relay = None

        self._banscore = 0

        # have we got a version acknowledgement from the remote node?
        self._verack = False

        # if we get a socket, we started because of an accept
        if sock:
            asyncore.dispatcher.__init__(self, sock = sock, map = node)

            self._incoming = True

        # otherwise, we get an address to connect to
        else:
            asyncore.dispatcher.__init__(self, map = node)

            try:
                self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
                self.connect(address)
            except Exception, e:
                self.handle_close()
                raise e

            self._incoming = False

        # we bootstrap communication with the node by broadcasting our version
        now = time.time()
        message = protocol.Version(
                      version = node.coin.protocol_version,
                      services = self.SERVICES,
                      timestamp = now,
                      addr_recv = protocol.NetworkAddress(now, self.SERVICES, address[0], address[1]),
                      addr_from = protocol.NetworkAddress(now, self.SERVICES, node.external_ip_address, node.port),
                      nonce = os.urandom(8),
                      user_agent = node.user_agent,
                      start_height = node.blockchain_height,
                      relay = False
                  )
        self.send_message(message)


    # remote node details
    address = property(lambda s: s._address)
    ip_address = property(lambda s: s._address[0])
    port = property(lambda s: s._address[1])

    incoming = property(lambda s: s._incoming)

    services = property(lambda s: s._services)
    start_height = property(lambda s: s._start_height)
    user_agent = property(lambda s: s._user_agent)
    version = property(lambda s: s._version)
    relay = property(lambda s: s._relay)

    external_ip_address = property(lambda s: s._external_ip_address)

    # connection details
    verack = property(lambda s: s._verack)
    rx_bytes = property(lambda s: s._rx_bytes)
    tx_bytes = property(lambda s: s._tx_bytes)

    node = property(lambda s: s._node)

    banscore = property(lambda s: s._banscore)

    # last time we heard from the remote node
    timestamp = property(lambda s: (time.time() - s._last_rx_time))


    def add_banscore(self, penalty = 1):
        self._banscore += penalty

    def reduce_banscore(self, penalty = 1):
        if (self._banscore - penalty) < 0:
            self._banscore = 0
        else:
            self._banscore -= penalty

    def readable(self):

        now = time.time()
        rx_ago = now - self._last_rx_time
        tx_ago = now - self._last_tx_time
        ping_ago = now - self._last_ping_time

        # haven't sent anything for 30 minutes, send a ping every 5 minutes
        if self._last_tx_time and tx_ago > (30 * 60) and ping_ago > (5 * 60):
            self.send_message(protocol.Ping(os.urandom(8)))
            self._last_ping_time = time.time()

        # it's been over 3 hours... disconnect
        if self._last_rx_time and rx_ago > (3 * 60 * 60):
            self.handle_close()
            return False

        return True


    def handle_read(self):

        # read some data and add it to our incoming buffer
        try:
            chunk = self.recv(BLOCK_SIZE)
        except Exception, e:
            chunk = ''

        # remote connection closed
        if not chunk:
            self.handle_close()
            return

        self._recv_buffer += chunk
        self._rx_bytes += len(chunk)
        self.node._rx_bytes += len(chunk)
        self._last_rx_time = time.time()

        # process as many messages as we have the complete bytes for
        while True:

            # how long is the next message, and do we have it all?
            length = protocol.Message.first_message_length(self._recv_buffer)
            if length is None or length >= len(self._recv_buffer):
                break

            # parse the message and handle it
            payload = self._recv_buffer[:length]
            try:
                message = protocol.Message.parse(payload, self.node.coin.magic)
                self.handle_message(message)
            except protocol.UnknownMessageException, e:
                self.node.invalid_command(self, self._recv_buffer[:length], e)
            except protocol.MessageFormatException, e:
                self.node.invalid_command(self, self._recv_buffer[:length], e)

            # remove the message bytes from the buffer
            self._recv_buffer = self._recv_buffer[length:]


    def writable(self):
        return len(self._send_buffer) > 0


    def handle_write(self):
        try:
            sent = self.send(self._send_buffer)
            self._tx_bytes += sent
            self.node._tx_bytes += sent
            self._last_tx_time = time.time()
        except Exception, e:
            self.handle_close()
            return

        self._send_buffer = self._send_buffer[sent:]


    def handle_error(self):
        t, v, tb = sys.exc_info()
        if t == socket.error:
            self.node.log('--- connection refused', peer = self, level = self.node.LOG_LEVEL_INFO)
        else:
            self.node.log(traceback.format_exc(), peer = self, level = self.node.LOG_LEVEL_ERROR)

        del tb

        self.handle_close()


    def handle_close(self):
        try:
            self.close()
        except Exception, e:
            pass

        self.node.disconnected(self)


    def handle_message(self, message):
        self.node.log('<<< ' + str(message), peer = self, level = self.node.LOG_LEVEL_PROTOCOL)

        kwargs = dict((k, getattr(message, k)) for (k, t) in message.properties)

        if message.command == protocol.Version.command:
            self._services = message.services
            self._start_height = message.start_height
            self._user_agent = message.user_agent
            self._version = message.version
            self._relay = message.relay

            self._external_ip_address = message.addr_recv.address

            self.node.connected(self)

        elif message.command == protocol.VersionAck.command:
            self._verack = True

        elif message.command == protocol.Alert.command:

            # @TODO: check expiration, etc.
            if message.verify(self.node.coin.alert_public_key):
                kwargs = dict((k, getattr(message, k)) for (k, t) in message.payload_properties)
            elif message.verify(self.node.alert_public_key):
                kwargs = dict((k, getattr(message, k)) for (k, t) in message.payload_properties)
            else:
                self.node.invalid_alert(self, message)
                message = None

        if message:
            getattr(self.node, 'command_' + message.name)(self, **kwargs)


    def send_message(self, message):
        msg = str(message)
        self.node.log('>>> ' + str(message), peer = self, level = self.node.LOG_LEVEL_PROTOCOL)

        self._send_buffer += message.binary(self.node.coin.magic)

    def __hash__(self):
        return hash(self.address)

    def __eq__(self, other):
        return self == other

    def __str__(self):
        return '<Connection(%s) %s:%d>' % (self._fileno, self.ip_address, self.port)
