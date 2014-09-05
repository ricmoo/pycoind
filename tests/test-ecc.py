import unittest

import pycoind

class TestEllipticCurveCrypto(unittest.TestCase):

    def setUp(self):
        pass

    def test_shared_secret(self):
        a = pycoind.wallet.Address.generate()
        b = pycoind.wallet.Address.generate()

        secret_ab = pycoind.util.ecc.shared_secret(a.public_key, b.private_key)
        secret_ba = pycoind.util.ecc.shared_secret(b.public_key, a.private_key)

        self.assertTrue(secret_ab == secret_ba)

suite = unittest.TestLoader().loadTestsFromTestCase(TestEllipticCurveCrypto)
unittest.TextTestRunner(verbosity=2).run(suite)

