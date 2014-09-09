pycoind
=======

A simple, pure-Python easy-to-setup-and-use full-node (soon) for bitcoin and any [most] altcoins based on the original bitcoind.


Features
--------

* A **full** network node (soon)
* Single code base for multiple coins
* Downloads the entire blockchain
* Allow other peers to connect and download the blockchain
* Zero dependencies beyond standard Python installation (see scrypt performance below)
* 100% MIT/BSD licensed
* Full BIP38 encrypted address and wallet
* Separation of *data directory* and *wallet*

Currently Supported Coins
-------------------------

* bitcoin
* coinyecoin (dead?)
* dogecoin
* feathercoin
* flappycoin
* litecoin
* mooncoin (dead?)
* potcoin
* zetacoin

To Do (coming soon...)
----------------------

There are lots of things left to do. Expect the API to change frequently for now. Also, as each altcoin has slightly different and random "things" changed from the reference implementation, which means more functions will be added to the individual `pycoind.coin` classes to accomodate a wider selection of altcoins.

* Full wallet API with Deterministic BIP32
* Wallet UI
* Checkpoints
* UTXO database (requires checkpoints)
* Become a fullnode; ie. support relaying (once checkpoints and UTXO databse is complete)
* Full legacy command line support
* Full legacy RPC support (use the original bitcoind rpc client with pycoind, or pycoind legacy_cli with the original bitcoind)
* Bloom filters
* Lots more coins (namecoin is highest on the list)
* X11 based coins
* Adaptive-N scrypt coins
* Python 3 support
* UI for sending transactions
* ipv6 has been "implemented" but is untested... I need to set up a ipv6 network to test on.
* more test cases (integrate all bitcoind test cases too)

### Why is it not yet a full node?

A full node (should) verify all transactions before relaying them to peers. To verify transactions, each transaction input spends several *unspent outputs* (utxo), which must be verified. This requires storing a master database of all the UTXO's. While the database is implemented and seems to work, it is slow. Incredibly slow. So, first I wish to get checkpoints implemented, which will allow the UTXO database to populate much faster.

So, in short, the missing functionality is relay transactions to peers.


Motivation
----------

I was quite interested in all that makes bitcoin tick, but the C++ [bitcoind source code](https://github.com/bitcoin/bitcoin) was a bit intimidating, having not used C++ since university; even in my best days of C++, it was not my go-to language for learning a new algorithm or protocol.

Of course, I first installed bitcoind to whet my appetite (after settling macport's tantrums with boost)... Then litecoind... dogecoind... Lather, rinse, repeat.

It was more work than I thought necessary, tweaking Makefiles, building, setting up and managing a completely separate code bases for a dozen coins, that were nearly identical except for a handful bytes.

So, I finally started pycoind, to bring all my full nodes into a single cohesive (ish) code base.


Application and Scripts
=======================

Several useful scipts are included that demonstrate this library, and should suffice for most users' needs.


Address Manipulation *(pycoind-address)*
----------------------------------------

This tool allows you to perform common functions to addresses, such as:
* generate new private keys and addresses
* dump all information about a private or public key
* compress and decompress addresses' private keys and addresses
* encrypt and decrypt private keys
* generate printable BIP38 intermediate codes
* generate BIP38 EC-multiply printed private keys from an intermediate code and confirm their confirmation codes
* available in human readable or JSON output
* supports all available coins

In general, passing in a `passphrase` or `key` on the command line is **not secure**. Leaving it blank will provide a secure (non-echoing) prompt for you to enter your `passphrase` or `key`.

Care should also be taken when displaying unencrypted private keys (ie. `--show-private`), as your terminal may have a scrollback buffer which would leave the keys visible long after using the utility. On *OS X*, `alt-command-K` will clear your scrollback.

```bash
usage: pycoind-address [--coin COINNAME] [--generate | --key [KEY]]
                       [--compress | --decompress] [--decrypt [PASSWORD]]
                       [--encrypt [PASSWORD]] [--intermediate [PASSWORD]]
                       [--lot LOT] [--sequence SEQUENCE]
                       [--generate-printed INTERMEDIATE_CODE]
                       [--confirm CONFIRM_CODE [PASSWORD]] [-h] [-v]
                       [--show-private] [--json]

Address Manipulation Tool

Address Options:
  --coin COINNAME       specify coin (default: bitcoin)
  --generate            generate a new address
  --key [KEY]           hex public key or wif private key *

Compression:
  --compress            compress the key
  --decompress          decompress the key

Encryption:
  --decrypt [PASSWORD]  use passsphrase to decrypt key *
  --encrypt [PASSWORD]  use passphrase to encrypt key *

Printed Addresses:
  --intermediate [PASSWORD]
                        generate an intermediate code for a passphrase *
  --lot LOT             set printed address lot number
  --sequence SEQUENCE   set printed address sequence number
  --generate-printed INTERMEDIATE_CODE
                        generate a printed address
  --confirm CONFIRM_CODE [PASSWORD]
                        confirm a printed address *

Output Formatting:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  --show-private        show unencrypted private keys *
  --json                output in JSON

* Most terminals use a scrollback buffer, which can leave contents (such as
private keys and passphrases) visible long after using this utility. Make sure
you clear your scrollback and use the secure passphrase and key input when
possible, by omitting the passphrase or key from the command line.
```

### Example: generate new addresses

Generate a compressed address:

```
/home/ricmoo> pycoind-address --generate --show-private
Address:     1AqGV68GPQVAZLtpRBkgRD5bC5V1xYavkD
Public Key:  03d24230984c42a2d733da5535abb6ac989ad709f0a231259207c5b90278983093
Compressed:  True
Private Key: L3PizuKXn5r8SVxhgXx5L5jKUa1uxC67e6ekUYhFDP8Xy7NJTzFX
```

Generate a decompressed address:

```
/home/ricmoo> pycoind-address --generate --show-private --decompress
Address:     137BJruaWcvS5YLGvX8ptTK1jRXVewzGHr
Public Key:  046fe1b3d42a5d73e0bc53d5d559f18bfe0a49193d19fdb4f50fdc8dc7f15344a5141b3a45e68b1a5f0284a76ff8bd6c30df21cbad1fb82cadd19e240836197f67
Compressed:  False
Private Key: 5KEBWFpYiZrb1sYZYTNvhHcVtfJ3nTA8XQzfb6SPVTmhfGBZ3Yi
```

Or, more securely, do not display the private key, instead encrypt it:

```
/home/ricmoo> pycoind-address --generate --encrypt
Passphrase: [typed foo]
Compressed:  True
Private Key: 6PYKQkjEsozH4JHnV4GQYTsAr3nt2ZVq3djWmY1MhewD8aK2gmtdEMNfRx
```

### Example: compressed addresses

Decompress an address:

```
/home/ricmoo> pycoind-address --key L1e4vSqvTfFhc4NNDXr5gm4MmtMgZSDLGoz6rwBGtBSNSbkFBSMW --show-private --decompress
Address:     1MCwNzTdFX3dTCXY6MzryR8XtmQkStmxzo
Public Key:  043fd52cf96f079ef4520f989f7f6273cde1f18992967a7a0d72ac156e8f2baf1879b7f9d48ff27b04ddc8ca5d954319f5bfde9023c1ba7f178c29a42bb23b1590
Compressed:  False
Private Key: 5JpNHBqhCvyoMdZUv8tuGMQRC5PMk9RzqSbgqvWWt21JzwZBdZw
```

Compress an address:

```
/home/ricmoo> pycoind-address --key 5JpNHBqhCvyoMdZUv8tuGMQRC5PMk9RzqSbgqvWWt21JzwZBdZw --show-private --compress
Address:     1FhTqT8eFTk3uUoSKfevB7BKBTQdieMMVE
Public Key:  023fd52cf96f079ef4520f989f7f6273cde1f18992967a7a0d72ac156e8f2baf18
Compressed:  True
Private Key: L1e4vSqvTfFhc4NNDXr5gm4MmtMgZSDLGoz6rwBGtBSNSbkFBSMW
```

### Example: change password from "foo" to "bar"

```
/home/ricmoo> pycoind-address --key 6PYMn7XkUgLhAmARM4BeayeyfycbZAyv7Lpwjk6jsNpLZNc7oRwnqd49H9 --decrypt foo --encrypt bar
Compressed:  True
Private Key: 6PYMn7XkTrBCRXEhwtnTEKGrHPRQiGdq4qS6tMMyAmfdZhcBCVmNVpnYf9
```

**Or, Using secure input:** (note that what you type will not be echoed to the terminal)

```bash
/home/ricmoo> pycoind-address --key --decrypt --encrypt 
Key: [typed 6PYMn7XkUgLhAmARM4BeayeyfycbZAyv7Lpwjk6jsNpLZNc7oRwnqd49H9]
Passphrase: [typed foo]
Passphrase: [typed bar]
Compressed:  True
Private Key: 6PYMn7XkTrBCRXEhwtnTEKGrHPRQiGdq4qS6tMMyAmfdZhcBCVmNVpnYf9
```


Node Management *(pycoind-node)*
--------------------------------

This tool starts a pycoind full node, which will connect to other nodes to synchronize and maintain a local copy of the blockchain.

```
/home/ricmoo> pycoind-node --help
usage: pycoind-node [--coin COINNAME] [--data-dir DIRECTORY] [--no-init]
                    [--background] [--bind ADDRESS] [--port PORT]
                    [--no-listen] [--max-peers COUNT] [--seek-peers COUNT]
                    [--connect ADDRESS[:PORT] [ADDRESS[:PORT] ...]]
                    [--no-dns-lookup] [--no-bootstrap] [-h] [--version]
                    [--debug]

Node Management Tool

Node Options:
  --coin COINNAME       specify coin (default: bitcoin)
  --data-dir DIRECTORY  database directory (default: ~/.pycoind/data)
  --no-init             do not create data-dir if missing
  --background          run the node in the background

Network:
  --bind ADDRESS        Use specific interface (default: 127.0.0.1)
  --port PORT           port to connect on (default: coin specific)
  --no-listen           do not accept incoming connections

Peer Discovery:
  --max-peers COUNT     maximum connections to allow (default: 125)
  --seek-peers COUNT    number of peers to seek out (default: 16)
  --connect ADDRESS[:PORT] [ADDRESS[:PORT] ...]
                        specify peer addresses
  --no-dns-lookup       do not attempt to resolve DNS names for connect
  --no-bootstrap        do not use DNS seeds to bootstrap

Other Options:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --debug               display debug logs
```

**Note:** The `--background` feature is not recommended at this time as there is no way (eg. RPC) to communitcate with the node.

### Example: run bitcoin full-node

```
/home/ricmoo> pycoind-node
```

### Example: clone a litecoin blockchain on localhost

The `--seek-peers 0` will prevent the node from adding any new peers beyond the explicitly added `--connect` peers.

```
/home/ricmoo> pycoind-node --coin litecoin --connect 127.0.0.1 --seek-peers 0 --data-dir /tmp/litecoin
```

Blockchain Explorer (pycoind-blockchain)
----------------------------------------

This tool is useful for exploring the blockchain from the command line. It can only examine a local blockchain, so you must have had node sync (or currently syncing) the blockchain from the network.

```bash
usage: pycoind-blockchain [--coin COINNAME] [--data-dir DIRECTORY] [--no-init]
                          [--block BLOCK_HASH | --height HEIGHT | --txid TXID]
                          [--big-endian | --little-endian] [--txns] [--inputs]
                          [--outputs] [--strict] [-h] [-v] [--json]

Blockchain Management Tool

Blockchain Options:
  --coin COINNAME       specify coin (default: bitcoin)
  --data-dir DIRECTORY  database directory (default: ~/.pycoind/data)
  --no-init             do not create data-dir if missing

Block Explorer:
  --block BLOCK_HASH    dump a block by its block hash
  --height HEIGHT       dump a block by its height
  --txid TXID           dump a transaction by its txid
  --big-endian          display values as big-endian
  --little-endian       display values as little-endian
  --txns                include transactions for blocks
  --inputs              include inputs for transactions
  --outputs             include outputs transactions
  --strict              search using only the display endianess

Output:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  --json                output in JSON
```

### Example: Examine blocks

Blocks can be located by their **block hash**:

```
/home/ricmoo> pycoind-blockchain --block 00000000000000001bb82a7f5973618cfd3185ba1ded04dd852a653f92a27c45
Height:        314159
Hash:          00000000000000001bb82a7f5973618cfd3185ba1ded04dd852a653f92a27c45
Previous Hash: 00000000000000003021634037ebf164433fa819aac82d4dac8852e14a1a6952
Merkle Root:   85d96247cb71e427b250e01b2b0e55a404976f49bc557a5ab3dd2e585ff7af2c
Next Hash:     00000000000000002700a33cb08fb90741b5f58f58b1a12ccd6238156095b36a
Timestamp:     1407292005
Version:       2
Bits:          406498978
Difficulty:    18736441558.3
Nonce:         474785672
Txn Count:     779

```

or by their **height** in the blockchain:

```
/home/ricmoo> pycoind-blockchain --height 314159
Height:        314159
Hash:          00000000000000001bb82a7f5973618cfd3185ba1ded04dd852a653f92a27c45
Previous Hash: 00000000000000003021634037ebf164433fa819aac82d4dac8852e14a1a6952
Merkle Root:   85d96247cb71e427b250e01b2b0e55a404976f49bc557a5ab3dd2e585ff7af2c
Next Hash:     00000000000000002700a33cb08fb90741b5f58f58b1a12ccd6238156095b36a
Timestamp:     1407292005
Version:       2
Bits:          406498978
Difficulty:    18736441558.3
Nonce:         474785672
Txn Count:     779
```

### Example: Examine the newest block

Block heights may also be specified as negative numbers to search form the top. To examine the top block in the blockchain:

```
/home/ricmoo> pycoind-blockchain --height -1
Height:        318962
Hash:          00000000000000000105e684173d5262bc7b46206f9efa2283e47272fe868255
Previous Hash: 00000000000000000bfd40deddbc1c1e919a7e923fd283bba05cab59bde9b4b5
Merkle Root:   bde3bb92633b519b365c97da17be96177ecc041e631f71c77a40764cbaf1b39d
Next Hash:     None
Timestamp:     1409775099
Version:       2
Bits:          405280238
Difficulty:    27428630902.3
Nonce:         3973936217
Txn Count:     253
```

### Example: Examine block transactions

The `--txns` will list all transactions (instead of merely the number of transactions):

```
/home/ricmoo> pycoind-blockchain --height 0 --txns
Height:        0
Hash:          000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f
Previous Hash: 0000000000000000000000000000000000000000000000000000000000000000
Merkle Root:   4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b
Next Hash:     00000000839a8e6886ab5951d76f411475428afc90947ee320161bbf18eb6048
Timestamp:     1231006505
Version:       1
Bits:          486604799
Difficulty:    1.0
Nonce:         2083236893
Txn Count:     1
Transactions:
    4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b
```

Using a *txid*, the transaction can then be examined:

```
/home/ricmoo> pycoind-blockchain --txid 4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b
Txid:         4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b
Block:        000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f
Index:        0
Version:      1
Lock Time:    0
Input Count:  1
Output Count: 1
```

### Example: Examine transaction inputs and outputs

The inputs and outputs can be examined as well by using `--inputs` and `--outputs` respectively.

```
/home/ricmoo> pycoind-blockchain --txid 4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b --inputs --outputs
Txid:         4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b
Block:        000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f
Index:        0
Version:      1
Lock Time:    0
Input Count:  1
Output Count: 1
Inputs:
    Input #0
    Previous Output Hash:   0000000000000000000000000000000000000000000000000000000000000000
    Previous Output Index:  4294967295
    Signature Script (Hex): 04ffff001d0104455468652054696d65732030332f4a616e2f32303039204368616e63656c6c6f72206f6e206272696e6b206f66207365636f6e64206261696c6f757420666f722062616e6b73
    Signature Script:       ffff001d 04 5468652054696d65732030332f4a616e2f32303039204368616e63656c6c6f72206f6e206272696e6b206f66207365636f6e64206261696c6f757420666f722062616e6b73
    Sequence:               4294967295

Outputs:
    Output #0
    Value:                   5000000000
    Public Key Script (Hex): 4104678afdb0fe5548271967f1a67130b7105cd6a828e03909a67962e0ea1f61deb649f6bc3f4cef38c4f35504e51ec112de5c384df7ba0b8d578a4c702b6bf11d5fac
    Public Key Script:       04678afdb0fe5548271967f1a67130b7105cd6a828e03909a67962e0ea1f61deb649f6bc3f4cef38c4f35504e51ec112de5c384df7ba0b8d578a4c702b6bf11d5f OP_CHECKSIG
```

### Example: JSON output

Using `--json` the output will provide the output in a machine-readable JSON container.

```
/home/ricmoo> pycoind-blockchain --height 0 --txns --json
{
    "nonce": 2083236893, 
    "next_hash": "00000000839a8e6886ab5951d76f411475428afc90947ee320161bbf18eb6048", 
    "hash": "000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f", 
    "txn_count": 1, 
    "timestamp": 1231006505, 
    "merkle_root": "4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b", 
    "transactions": [
        "4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b"
    ], 
    "height": 0, 
    "difficulty": 1.0, 
    "version": 1, 
    "previous_hash": "0000000000000000000000000000000000000000000000000000000000000000", 
    "bits": 486604799
}
```
```
/home/ricmoo> pycoind-blockchain --txid 4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b --inputs --outputs --json
{
    "index": 0, 
    "lock_time": 0, 
    "inputs": [
        {
            "signature_script": "04ffff001d0104455468652054696d65732030332f4a616e2f32303039204368616e63656c6c6f72206f6e206272696e6b206f66207365636f6e64206261696c6f757420666f722062616e6b73", 
            "previous_output": {
                "index": 4294967295, 
                "hash": "0000000000000000000000000000000000000000000000000000000000000000"
            }, 
            "sequence": 4294967295
        }
    ], 
    "outputs": [
        {
            "pk_script": "4104678afdb0fe5548271967f1a67130b7105cd6a828e03909a67962e0ea1f61deb649f6bc3f4cef38c4f35504e51ec112de5c384df7ba0b8d578a4c702b6bf11d5fac", 
            "value": 5000000000
        }
    ], 
    "output_count": 1, 
    "txid": "4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b", 
    "version": 1, 
    "input_count": 1, 
    "block": "000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f"
}
```

Library Overview
================

This library is broken up into the following packages. (see API below)

* `pycoind.blockchain` - manages the databases of blocks, transactions and unspent transaction outputs (utxo)
* `pycoind.coins` - coin specific parameters
* `pycoind.node` - connects to the peer-to-peer network and manages peer connections
* `pycoind.protocol` - serializes and deserializes the network protocol messages
* `pycoind.script` - script language for processing transactions
* `pycoind.util` - various of useful bits and pieces
* `pycoind.wallet` - wallet and address management


Performance Note: scrypt
------------------------

Some parts of the protocol (ie. BIP38 wallets) use an intentionally CPU and memory intensive algorithm called *scrypt*, which performs *very* poorly in pure-Python. There are a few options to improve performance:

* **Python Bindings:** a Python wrapper for the C implmentation of scrypt. [Download from pypi](https://pypi.python.org/pypi/scrypt/) or use pip, `pip install scrypt`
* **Pypy:** a JIT-compiler and runtime for Python that can run pycoind about 600x times faster. [Download from pypy.org](http://pypy.org/download.html). It can be installed locally without root permissions.


API
===

Blockchain
----------

This demonstrates the simplified blockchain API for deailing with read-only access to a pycoind blockchain database. This should suffice for most people's needs.

Write-access will not be covered here, but interested parties should look at the `pycoind.blockchain.block.Database` and `pycoind.blockchain.transaction.Database`.

### Blocks

```python
>>> import pycoind

>>> # Open up a blockchian database (defaults to bitcoin)
>>> blockchain = pycoind.Blockchain()

>>> # Get a block by its blockhash
>>> block_hash = '9a22db7fd25e719abf9e8ccf869fbbc1e22fa71822a37efae054c17b00000000'.decode('hex')
>>> print blockchain.get_block(block_hash)
<Block 9a22db7fd25e719abf9e8ccf869fbbc1e22fa71822a37efae054c17b00000000>

>>> # The blockchain's total height
>>> len(blockchain)
305128

>>> # Get a block by its height (0 is the genesis)
>>> block = blockchain[100]
>>> print block
<Block 9a22db7fd25e719abf9e8ccf869fbbc1e22fa71822a37efae054c17b00000000>

>>> # Getting the next and previous block of a block...
>>> print block.next_block
<Block 84999d1fa0ae9b7eb8b75fa8ad765c6d467a6117015860dce4d89bb600000000>
>>> block.previous_block
<Block 95194b8567fe2e8bbda931afd01a7acd399b9325cb54683e64129bcd00000000>

>>> # The most recent block (negative indices look from the top)
>>> block = blockchain[-1]
>>> print block
<Block a97c1c20f983e06e286e73317e0ef4d60bc9d128d26de8100000000000000000>

>>> # The various attributes on a block...
>>> block.hash.encode('hex')
'a97c1c20f983e06e286e73317e0ef4d60bc9d128d26de8100000000000000000'
>>> block.version
2
>>> block.previous_hash
'cda8ccb789212be51f77927f8ad709337deb88f37e5ade330000000000000000'
>>> block.merkle_root.encode('hex')
'49b74a21aa97781ed70bb48ea7bf2ffd9790d3ac8ad1a56a8f082155d90df7b8'
>>> block.timestamp
1402411608
>>> block.bits
408782234
>>> block.nonce
1267643715
>>> block.height
305127
>>> block.txn_count
328

>>> # See below for more with transactions
>>> block.transactions
(<pycoind.blockchain.transaction.Transaction object at 0x102dd7ad0>, ... )
```

### Transactions

```python
>>> # Get a transaction
>>> txid = '370b0e8298cf00b47a61ebac3381d38f38f62b065ef5d8dd3cfd243e4b6e9137'.decode('hex')
>>> txn = blockchain.get_transaction(txid)
>>> print txn
<Transaction hash=0x370b0e8298cf00b47a61ebac3381d38f38f62b065ef5d8dd3cfd243e4b6e9137>

>>> # Get the block for a transaction
>>> blockchain.get_transaction_block(txn)
<Block a97c1c20f983e06e286e73317e0ef4d60bc9d128d26de8100000000000000000>

>>> # The various attributes on a transactio...
>>> txn.version
1
>>> txn.inputs
(<pycoind.protocol.format.TxnIn object at 0x1025d6950>,)
>>> txn.outputs
(<pycoind.protocol.format.TxnOut object at 0x1025e82d0>,
  <pycoind.protocol.format.TxnOut object at 0x1025e8390>)
>>> txn.lock_time
0
>>> txn.hash.encode('hex')
'370b0e8298cf00b47a61ebac3381d38f38f62b065ef5d8dd3cfd243e4b6e9137'
>>> txn.index
1

>>> # The raw transaction object from the network
>>> txn.txn
<pycoind.protocol.format.Txn object at 0x1025d68d0>

>>> # The raw bytes from the network
>>> txn.txn_binary.encode('hex')
'''0100000001430e1bc96057b9465b0e53111f260679222b0bb283
   75c7e3cf5bb15ccb0dc2f9000000008b483045022058ba932ffa
   927aa9a478310fd1112abb0df69e4e5f286b3a5ec2c6ae00912c
   b7022100b0c3bb6bd80440ae7427c3ea03128a99c6f3348aa677
   15f5760648512e00992e0141044d226629ff5244f2194505fa4b
   a911564137dad160a3b8831f682d14e194dea1a6bdc8962132c2
   c07ff85076ad9e49051513e1ba2cf3d69ac3c333d4da576e02ff
   ffffff0240c06503000000001976a914d64b71729a504d23d948
   88d3f712d55753d5d62288ac1c5e1300000000001976a914e1cd
   18b90a5db94b58dd643e706a462b75e512a588ac00000000'''
```

### Unspent Transaction Outputs (utxo)

*Coming soon...*

Verifying the blockchain is slow, which must be done first. Then Checkpointing will be implemented and finally the UTXO database will be turned on.

It is currently available in `pycoind.blockchain.unspent`, just turned off (and likely buggy).


Node
----

I will add more to this later.

```python
>>> import pycoind

>>> node = pycoind.Node(coin = pycoind.coins.Litecoin)
>>> node.add_peer(('127.0.0.1', node.coin.port))
>>> node.serve_forever()
```

Script
------

The script library can be used for a lot more, but for now, the main purpose most people will wish to use it is to display a script.

```python
>>> import pycoind

>>> # txid: 370b0e8298cf00b47a61ebac3381d38f38f62b065ef5d8dd3cfd243e4b6e9137 (input# 0)
>>> pk_script = 'v\xa9\x14\xd6Kqr\x9aPM#\xd9H\x88\xd3\xf7\x12\xd5WS\xd5\xd6"\x88\xac'
>>> print pycoind.Tokenizer(pk_script)
OP_DUP OP_HASH160 d64b71729a504d23d94888d3f712d55753d5d622 OP_EQUALVERIFY OP_CHECKSIG
```

Wallet/Address
--------------

Wallets are not yet implemented beyond a stub, however the `Address` API is quite useful.

```python
>>> import pycoind

>>> # Generate a new address
>>> address = pycoind.Address.generate(compressed = True)
>>> print address
<Address address=1PdrvpMr37oii5Wir2zsWxDHbG2n6z7sMu
  public_key=033adac21649eace0570478eea3af918e191af33430d9b5bb5168eecc61a541861
  private_key=**redacted**>

>>> address.address
'1PdrvpMr37oii5Wir2zsWxDHbG2n6z7sMu'
>>> address.public_key.encode('hex')
'033adac21649eace0570478eea3af918e191af33430d9b5bb5168eecc61a541861'
>>> address.compressed
True
>>> address.private_key
'KyBxUHBq7L6GvxwiX9Dd5t13HtGF3WbW3JsZviVSuLUWeX3mMJxS'

>>> # Return a decompressed instance
>>> decompressed = address.decompress()
>>> print decompressed
<Address address=1Joh7VqCXJzN8UCMdrCQTYvVA8mmmkCH3v
  public_key=043adac21649eace0570478eea3af918e191af33430d9b5bb5168eecc61a541861
             be0fd196952b92c1b3a9eb4b2c4cde86f23fa2a9a0113afbf7032dc7a415f41b
  private_key=**redacted**>

>>> # Return a compressed instance
>>> print decompressed.compress()
<Address address=1PdrvpMr37oii5Wir2zsWxDHbG2n6z7sMu
  public_key=033adac21649eace0570478eea3af918e191af33430d9b5bb5168eecc61a541861
  private_key=**redacted**>

>>> # Return an encrypted instance
>>> encrypted = address.encrypt('foo')
>>> print encrypted
<EncryptedAddress private_key=6PYN7vxDNYgNn7cBVfB8KErNWWBKTKFRA9yB9DoQnukhX1iJzj6mkPgHvj>

>>> # Decrypt with an incorrect password
>>> print encrypted.decrypt('bar')
None

>>> print encrypted.decrypt('foo')
<Address address=1PdrvpMr37oii5Wir2zsWxDHbG2n6z7sMu
  public_key=033adac21649eace0570478eea3af918e191af33430d9b5bb5168eecc61a541861
  private_key=**redacted**>

>>> # Generate a brain wallet a la https://brainwallet.github.io
>>> passphrase = 'foobar'
>>> bytes = pycoind.util.hash.sha256('foobar')
>>> print pycoind.Address.from_binary(bytes, compressed = False)
<Address address=15cN6CmsrERdrkTWU5VsDBfQv1bTqsAGh1 
  public_key=0481f098ee628abc173d50d1641485d58a659c79ded5acb4d889545f3ca07ada10
             b75bbab5c65f0a1769774ff4411ebfbf047b4f537e97450730a9afd2ec167ac6 
  private_key=**redacted**>
```

Cookbook
========

How to start your own coin
--------------------------

This is generally not a grand idea, as there are [already so many out there](https://www.altcoincalendar.info/calendar), but if you believe you have a novel idea to experiment with, who am I to stand in your way. Let's assume you are creating a new coin called a Kriegerand.

1. Copy the pycoind/coins/template.py to pycoind/coins/kriegerand.py
2. Edit the file, filling in the blanks
3. Add the coin to pycoind/coins/\_\_init\_\_.py (import it and add it to the `Coins` array)
4. pycoind-node --coin kriegerand
5. Done. Now you can start mining. (@TODO: explain how to set up mining...)

Analyze the blockchain
----------------------

There are so many things possible, but for example, let's say you wish to figure out what percentage of all outputs ever generated, are currently unspent.

**This is old and wrong... I will update this to use the new API soon.**

```python
import pycoind

blockchain = pycoind.BlockChain()

last_count = -100000
spent = 0
unspent = set()

# for each block...
for block in blockchain:

    # give some feedback once and a while as this could take a LONG time
    if spent - last_spent > 1000:
        print "spent: %d, unspent: %d" % (spent, len(unspent))
        last_spent = spent

    # transactions could be None if the block is not downloaded yet
    txns = b.transactions
    if not txns: continue

    # for each transaction...
    for txn in txns:

        # track all the outputs as unspent
        for (i, tx_out) in enumerate(txn.tx_out):
            unspent.add((txn.hash, i))
            count += 1

        # each input has spent an unspent
        for tx_in in txn.tx_in:

            prev_output = tx_in.previous_output.hash

            # this means the input was generated
            if prev_output == chr(0) * 32: continue

            # remove the spent from unspent
            prev_output = (prev_output, tx_in.previous_output.index)
            if prev_output in unspent:
                unspent.remove(prev_output)
                spent += 1

            else:
                print "possibly double-spend: %r" % prev_output

# The final answer
print len(unspent) / (len(unspent) + spent)
```

Bandwidth Capped Node
---------------------

Perhaps you have a hosting company which restricts your monthly bandwidth and you would like to run a full node, but not at the risk of going over your cap.

This is a very basic solution, as you would probably want to track bandwidth across restarts (using a file or database) and group it by month; such extras are left as an exercise to the reader.

```python
import pycoind

class CappedNode(pycoind.node.Node):

    # 1GB
    BANDWIDTH_CAP = (1 << 30)
    
    def begin_loop(self):
        '''Begin loop is called at the start of each event loop. Subclasses
           do not need to call the parent's begin_loop.'''

        if (self.rx_bytes + self.tx_bytes) > self.BANDWIDTH_CAP:
            raise pycoind.node.StopNode()

node = CappedNode()
node.serve_forever()
```

Vanity Address
--------------

This will be slow. VERY slow. It is just provided as an example. If you really want a vanity address with any complexity, check out [vanitygen](https://github.com/samr7/vanitygen).

```python
>>> import pycoind

>>> while True:
...    address = pycoind.wallet.Address.generate()
...    if address.address.startswith('1Moo'):
...        break

>>> address.address
'1MooEooyXNVTfGDh86Er1CGgzpXdYMZefm'

>>> address.private_key
'5HwhzLizMNEzGpKvtbkdFo3AuMg8PRp4rxFfSEufau8syue5vLS'
```

Piecewise Vanity Address
------------------------

Compatible with [vanitygen](https://github.com/samr7/vanitygen), this method allows an untrusted source to generate private keys for you, while only being able to compute the public key and address that would result.

You create a public/private key pair A on a host you trust:

### Trusted Host

```python
>>> import pycoind

>>> address = pycoind.wallet.Address.generate()

>>> pubkeyA = address.get_public_key(compressed = False)
>>> pubkeyA.encode('hex')
'''044715c46005a73ae7b87ef22ffeec67380ea15838b3bd8f71995066847b
   76cc14e037397542f5dbc11ac8453316d22757c9750edc532e6469fcb2f1
   c55194507f'''

>>> privkeyA = address.private_key
>>> privkeyA
'5JT2oBFsHwBu3xedw5kGiUCZvujiS7HzErmumETJYEnmcGXZkUW'
```

(this is the same as using *vanitygen*, `keyconv -G`)


### Untrusted Host

The public key `pubkeyA` may now be given to a [vanity pool](https://vanitypool.appspot.com) or you could run vanitygen on a host you don't trust (maybe on some sketchy compute cloud).

This allows a host you do not trust to search for a private key B, that when combined with the above private key A (which you keep secret) will yield the desired address, without the untrusted host ever knowing the final private key.

```python
>>> from pycoind.util.piecewise import get_address

>>> while True:
...     address = pycoind.wallet.Address.generate()
...     result = get_address(pubkeyA, address.private_key)
...     if result.startswith("1Moo"):
...         break

>>> address.address
'1MooifZYH39f4AFULunTRZ1iCBNzD1cQQL'

>>> privkeyB = address.private_key
>>> privkeyB
'5HuEjrhpN9fhVVd9sVAwqsQu9M7o9PVEHSPm7aTpo2STZpJjjNk'
```

(this is the same as using *vanitygen*, `vanitygen -P pubkeyA 1Moo`)


### Trusted Host (again)

With the result from the untrusted source, you can now combine the two keys:

```python
>>> from pycoind.util.piecewise import combine_private_keys

>>> privkey = combine_private_keys(privkeyA, privkeyB)
>>> privkey
'5JXyxMWbadHcHStWmNUKUHsLrf2bNMv8oV6tedsP6PNb1PwvqsZ'

>>> address = pycoind.wallet.Address(private_key = privkey)
>>> address.address
'1MooifZYH39f4AFULunTRZ1iCBNzD1cQQL'
```

(this is the same as using *vanitygen*, `keyconv -c privkeyA privkeyB`)


Security
========

This needs to be a thing...


FAQ
===


### Why so much SQLite?

The standard Python library leaves much to be desired in the area of reliable, cross-platform file-locking.

SQLite is the most portable way to handle the delicate issues with having multiple threads and processes accessing the same file, although it still has it's issues. See SQLite's [things that can go wrong](http://www.sqlite.org/atomiccommit.html#sect_9_0) for more details, but for the most part you should be safe so long as you **NEVER** delete a journal file and **avoid** network based file-systems (eg. NFS).


### Why are the database files capped at 1.75 GB?

They are capped at approximately 1.75 GB, for people that wish to keep the blockchain on a FAT32 formatted USB, which has a 2GB file size limit.


Donations?
==========

* **Bitcoin** - 1PycoindXg8zWjn82tRSzGwy953FxrGNfB
* **Dogecoin** - DPycoindsmBiWvo5gcdNNGLDYwzDkU5fFX
* **Litecoin** - LPycoindHX4VmQLeJE7LbWUfJG5TfRDhtx
