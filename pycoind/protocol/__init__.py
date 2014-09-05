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


SERVICE_NODE_NETWORK = (1 << 0)
SERVICE_BLOOM        = (1 << 1)

SERVICES = [SERVICE_NODE_NETWORK, SERVICE_BLOOM]


CCODE_REJECT_MALFORMED        = 0x01
CCODE_REJECT_INVALID          = 0x10
CCODE_REJECT_OBSOLETE         = 0x11
CCODE_REJECT_DUPLICATE        = 0x12
CCODE_REJECT_NONSTANDARD      = 0x40
CCODE_REJECT_DUST             = 0x41
CCODE_REJECT_INSUFFICIENTFEE  = 0x42
CCODE_REJECT_CHECKPOINT       = 0x43

CCODES = [CCODE_REJECT_MALFORMED, CCODE_REJECT_INVALID, CCODE_REJECT_OBSOLETE,
          CCODE_REJECT_DUPLICATE, CCODE_REJECT_NONSTANDARD, CCODE_REJECT_DUST,
          CCODE_REJECT_INSUFFICIENTFEE, CCODE_REJECT_CHECKPOINT]


OBJECT_TYPE_ERROR     = 0
OBJECT_TYPE_MSG_TX    = 1
OBJECT_TYPE_MSG_BLOCK = 2

OBJECT_TYPES = [OBJECT_TYPE_ERROR, OBJECT_TYPE_MSG_TX, OBJECT_TYPE_MSG_BLOCK]


# All message formats and exceptions
from messages import *

# Data typs we pass into messages and exceptions
from format import BlockHeader, InventoryVector, NetworkAddress, OutPoint, ParameterException, Txn, TxnIn, TxnOut
