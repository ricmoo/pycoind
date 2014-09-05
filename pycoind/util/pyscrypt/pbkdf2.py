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


import struct

from .util import block_xor

def pbkdf2(password, salt, count, key_length, prf):
    '''Returns the result of the Password-Based Key Derivation Function 2.
      prf - a psuedorandom function

       See http://en.wikipedia.org/wiki/PBKDF2
    '''

    def f(block_number):
        '''The function "f".'''

        U = prf(password, salt + struct.pack('>L', block_number))

        if count > 1:
            U = [ c for c in U ]
            for i in xrange(2, 1 + count):
                block_xor(prf(password, ''.join(U)), 0, U, 0, len(U))
        U = ''.join(U)

        return U

    size = 0

    block_number = 0
    blocks = [ ]

    # The iterations
    while size < key_length:
        block_number += 1
        block = f(block_number)

        blocks.append(block)
        size += len(block)

    return ''.join(blocks)[:key_length]

