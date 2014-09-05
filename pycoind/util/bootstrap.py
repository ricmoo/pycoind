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
import socket
import threading

class DNSSeeder(object):

    def __init__(self, dns_seeds):
        self._dns_seeds = dns_seeds
        self._lock = threading.Lock()
        self._found = []
        self._start()

    def __len__(self):
        with self._lock:
            return len(self._found)

    def pop(self):
        with self._lock:
            address = random.choice(self._found)
            self._found.remove(address)
            return address

    def _start(self):
        def try_address(address):
            try:
                (ip_address, port) = address

                index = 0
                for info in socket.getaddrinfo(ip_address, port, socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP):
                    try:
                        with self._lock:
                            self._found.append((info[4][0], info[4][1]))
                    except Exception, e:
                        pass

                    # snooze for some time, so each dns_seed has a chance
                    # to add nodes, and get addresses from those nodes
                    #snooze = -1 + 1.3 ** index
                    #if snooze > 600: snooze = 600 + random.randint(0, 120)
                    #index += 1
                    #time.sleep(snooze)

            except Exception, e:
                pass

        for address in self._dns_seeds:
            thread = threading.Thread(target = try_address, args = (address, ))
            thread.daemon = True
            thread.start()

