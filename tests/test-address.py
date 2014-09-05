#import sys
#sys.path.append('../pycoind')

# These are known correct values generated using vanitygen (https://github.com/samr7/vanitygen)

Tests = [
    ('1testbXQ43Kpdnxnn3M2pPGb25K3hctMD',
     '5J9YULLVqfJvcSfGKX2ACas48YgH34BhrQFBpidVbrvVoTp6NbH'),
    ('1test2DuCNdPEhkyxa27Y9jZjNcETHYFL',
     '5JpyLYVkANv94ufoUwp5GPdj47MpeEMax6gyQw6pmKPVqm2nVPq'),
    ('1testahNKiaynVnXAzSVUpFScJDL1F5ch',
    '5J8APFb8WxLQLGt83dgazfRAY4NW6qD6PjRTJddNBLj9iBYtThS'),
    ('1Q1pE5vPGEEMqRcVRMbtBK842Y6Pzo6nK9',
     'KwntMbt59tTsj8xqpqYqRRWufyjGunvhSyeMo3NTYpFYzZbXJ5Hp')
]

TestsEncrypted = [
    ('TestingOneTwoThree',
     '6PRVWUbkzzsbcVac2qwfssoUJAN1Xhrg6bNk8J7Nzm5H7kxEbn2Nh2ZoGg',
     '5KN7MzqK5wt2TP1fQCYyHBtDrXdJuXbUzm4A9rKAteGu3Qi5CVR'),

    ('Satoshi',
     '6PRNFFkZc2NZ6dJqFfhRoFNMR9Lnyj7dYGrzdgXXVMXcxoKTePPX1dWByq',
     '5HtasZ6ofTHP6HCwTqTkLDuLQisYPah7aUnSKfC7h4hMUVw2gi5'),

    (u'\u03D2\u0301\u0000\U00010400\U0001F4A9',
     '6PRW5o9FLp4gJDDVqJQKJFTpMvdsSGJxMYHtHaQBF3ooa8mwD69bapcDQn',
     '5Jajm8eQ22H3pGWLEVCXyvND8dQZhiQhoLJNKjYXk9roUFTMSZ4'),

    ('TestingOneTwoThree',
     '6PYNKZ1EAgYgmQfmNVamxyXVWHzK5s6DGhwP4J5o44cvXdoY7sRzhtpUeo',
     'L44B5gGEpqEDRS9vVPz7QT35jcBG2r3CZwSwQ4fCewXAhAhqGVpP'),

    ('Satoshi',
     '6PYLtMnXvfG3oJde97zRyLYFZCYizPU5T3LwgdYJz1fRhh16bU7u6PPmY7',
     'KwYgW8gcxj1JWJXhPSu4Fqwzfhp5Yfi42mdYmMa4XqK7NJxXUSK7'),
]

TestsPrinted = [
    ('TestingOneTwoThree',
     'passphrasepxFy57B9v8HtUsszJYKReoNDV6VHjUSGt8EVJmux9n1J3Ltf1gRxyDGXqnf9qm',
     None,
     '6PfQu77ygVyJLZjfvMLyhLMQbYnu5uguoJJ4kMCLqWwPEdfpwANVS76gTX',
     '5K4caxezwjGCGfnoPTZ8tMcJBLB7Jvyjv4xxeacadhq8nLisLR2',
     '1PE6TQi6HTVNz5DLwB1LcpMBALubfuN2z2',
     None, None),
    ('Satoshi',
     'passphraseoRDGAXTWzbp72eVbtUDdn1rwpgPUGjNZEc6CGBo8i5EC1FPW8wcnLdq4ThKzAS',
     None,
     '6PfLGnQs6VZnrNpmVKfjotbnQuaJK4KZoPFrAjx1JMJUa1Ft8gnf5WxfKd',
     '5KJ51SgxWaAYR13zd9ReMhJpwrcX47xTJh2D3fGPG9CM8vkv5sH',
     '1CqzrtZC6mXSAhoxtFwVjz8LtwLJjDYU3V',
     None, None),
    ('MOLON LABE',
     'passphraseaB8feaLQDENqCgr4gKZpmf4VoaT6qdjJNJiv7fsKvjqavcJxvuR1hy25aTu5sX',
     'cfrm38V8aXBn7JWA1ESmFMUn6erxeBGZGAxJPY4e36S9QWkzZKtaVqLNMgnifETYw7BPwWC9aPD',
     '6PgNBNNzDkKdhkT6uJntUXwwzQV8Rr2tZcbkDcuC9DZRsS6AtHts4Ypo1j',
     '5JLdxTtcTHcfYcmJsNVy1v2PMDx432JPoYcBTVVRHpPaxUrdtf8',
     '1Jscj8ALrYu2y9TD8NrpvDBugPedmbj4Yh',
     263183, 1),
]

import pycoind

for (address, private_key) in Tests:

    # test address hashes
    a = pycoind.wallet.Address(private_key = private_key)
    if a.address != address:
        raise Exception('address hashed incorectly')

    # test address compression
    a = pycoind.wallet.Address(private_key = private_key)
    c = a.compress()
    d = c.decompress()
    c = a.compress()
    d = c.decompress()
    if a.compressed and (c.private_key != private_key):
        raise Exception('address compression broken')
    if not a.compressed and (d.private_key != private_key):
        raise Exception('address compression broken')

for (passphrase, encrypted, decrypted) in TestsEncrypted:

    # test encrypted addresses against test vectors
    a = pycoind.wallet.EncryptedAddress(encrypted)
    d = a.decrypt(passphrase)
    if d.private_key != decrypted:
        raise Exception('test case failed')

    # test random address decrypts and encrypts properly (uncompressed)
    a = pycoind.wallet.Address.generate(compressed = False)
    e = a.encrypt(passphrase)
    d = e.decrypt(passphrase)
    if a.private_key != d.private_key:
        raise Exception('encrypted then decrypted private key fail')

for (passphrase, code, confirm, encrypted, decrypted, address, lot, sequence) in TestsPrinted:

    # test confirmation code
    if confirm:
        c = pycoind.wallet.PrintedAddress.confirm(confirm, passphrase)
        if c.address != address or c.lot != lot or c.sequence != sequence:
            raise Exception('confrimation code did not validate address')

    # decrypt the address
    a = pycoind.wallet.EncryptedAddress(encrypted)
    d = a.decrypt(passphrase)
    if d.address != address:
        raise Exception('EC-multiply addresses do not match')
    if d.private_key != decrypted:
        raise Exception('EC-multiply private keys do not match')
    if d.lot != lot or d.sequence != sequence:
        raise Exception('EC-multiply private key sequence or lot wrong')

    # generate a new address with the intermediate code (uncompressed)
    p = pycoind.wallet.PrintedAddress.generate(code, False)
    c = pycoind.wallet.PrintedAddress.confirm(p.confirmation_code, passphrase)
    if c.address != p.address or c.lot != lot or c.sequence != sequence:
        raise Exception('confrimation code did not validate address')
    d = p.decrypt(passphrase)
    if d.address != p.address:
        raise Exception('EC-multiply intermediate address does not match decrypted address')
    if d.lot != lot or d.sequence != sequence:
        raise Exception('EC-multiply private key sequence or lot wrong')

    # generate a new address with the intermediate code (compressed)
    p = pycoind.wallet.PrintedAddress.generate(code, True)
    c = pycoind.wallet.PrintedAddress.confirm(p.confirmation_code, passphrase)
    if c.address != p.address or c.lot != lot or c.sequence != sequence:
        raise Exception('confrimation code did not validate address')
    d = p.decrypt(passphrase)
    if d.address != p.address:
        raise Exception('EC-multiply intermediate address does not match decrypted address')
    if d.lot != lot or d.sequence != sequence:
        raise Exception('EC-multiply private key sequence or lot wrong')

    # generate an intermediate code and use it to generate an address
    code = pycoind.wallet.PrintedAddress.generate_intermediate_code(passphrase, lot = lot, sequence = sequence)
    p = pycoind.wallet.PrintedAddress.generate(code, False)
    c = pycoind.wallet.PrintedAddress.confirm(p.confirmation_code, passphrase)
    if c.address != p.address or c.lot != lot or c.sequence != sequence:
        raise Exception('confrimation code did not validate address')
    d = p.decrypt(passphrase)
    if d.address != p.address:
        raise Exception('EC-multiply intermediate code created unmatched address')
    if d.lot != lot or d.sequence != sequence:
        raise Exception('EC-multiply private key sequence or lot wrong')


