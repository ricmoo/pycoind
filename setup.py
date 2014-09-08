#!/usr/bin/env python

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


LONG_DESCRIPTION = '''A simple, pure-Python easy-to-setup-and-use, full-node for bitcoin and any [most] altcoins based on the original bitcoind.'''


import os
import sys

# get the version of pycoind we are working with
import pycoind
version = '.'.join(str(n) for n in pycoind.VERSION)


# the base path of this script
BASE_PATH = os.path.split(__file__)[0]


# All scripts in the script directory
Scripts = [('scripts/%s' % fn) for fn in os.listdir(os.path.join(BASE_PATH, 'scripts'))]


from distutils.core import Command, setup
import distutils.log as log

class Tests(Command):
    description = "Run test case suite."

    user_options = [('test=', None, 'which test to run (without "test-" prefix and ".py" extension)')]

    def initialize_options(self):
        self.test = None

    def finalize_options(self):
        self.path = os.path.join(BASE_PATH, 'tests')

    def run_test(self, filename):
        path = os.path.join(self.path, filename)
        self.announce("Running %s..." % filename, log.INFO)
        try:
            execfile(path)
        except Exception, e:
            self.announce('Test case failed: %s (%r)' % (filename, e), log.FATAL)
            raise e

    def run(self):
        self.announce("Running Test Suite (version %s)" % version, log.INFO)
        if self.test:
            filename = 'test-%s.py' % self.test
            self.run_test(filename)
        else:
            for filename in os.listdir(self.path):
                if filename.startswith('test-') and filename.endswith('.py'):
                    self.run_test(filename)


setup(name = 'pycoind',
      version = version,
      description = 'Pure-Python full node for bitcoin and related altcoins.',
      long_description = LONG_DESCRIPTION,
      author = 'Richard Moore',
      author_email = 'ricmoo@pycoind.org',
      url = 'http://www.pycoind.org',
      packages = [
          'pycoind',
          'pycoind.blockchain',
          'pycoind.coins',
          'pycoind.node',
          'pycoind.protocol',
          'pycoind.script',
          'pycoind.util',
          'pycoind.util.ecdsa',
          'pycoind.util.pyaes',
          'pycoind.util.pyscrypt',
          'pycoind.wallet',
      ],
      scripts = Scripts,
      classifiers = [
          'Topic :: Security :: Cryptography',
          'License :: OSI Approved :: MIT License',
      ],
      license = "License :: OSI Approved :: MIT License",
      cmdclass = dict(test = Tests),
     )
