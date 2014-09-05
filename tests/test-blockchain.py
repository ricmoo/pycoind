import sys
sys.path.append('.')

import unittest

import pycoind

class TestBlockchain(unittest.TestCase):

    # Block whose hash does not meet the required target
    block_1_invalid_target = '01000000000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26fd4e1732e44abdc5199c755a22eaf95b32c27af28396b7066e8e5db6352c3ae8d61bc6649ffff001d2a00000000'

    # Mainchain
    block_0 = '0100000000000000000000000000000000000000000000000000000000000000000000003ba3edfd7a7b12b27ac72c3e67768f617fc81bc3888a51323a9fb8aa4b1e5e4a29ab5f49ffff001d1dac2b7c01'
    block_1 = '010000006fe28c0ab6f1b372c1a6a246ae63f74f931e8365e15a089c68d6190000000000982051fd1e4ba744bbbe680e1fee14677ba1a3c3540bf7b1cdb606e857233e0e61bc6649ffff001d01e3629901'
    block_2 = '010000004860eb18bf1b1620e37e9490fc8a427514416fd75159ab86688e9a8300000000d5fdcc541e25de1c7a5addedf24858b8bb665c9f36ef744ee42c316022c90f9bb0bc6649ffff001d08d2bd6101'
    block_3 = '01000000bddd99ccfda39da1b108ce1a5d70038d0a967bacb68b6b63065f626a0000000044f672226090d85db9a9f2fbfe5f0f9609b387af7be5b7fbb7a1767c831c9e995dbe6649ffff001d05e0ed6d01'
    block_4 = '010000004944469562ae1c2c74d9a535e00b6f3e40ffbad4f2fda3895501b582000000007a06ea98cd40ba2e3288262b28638cec5337c1456aaf5eedc8e9e5a20f062bdf8cc16649ffff001d2bfee0a901'
    block_5 = '0100000085144a84488ea88d221c8bd6c059da090e88f8a2c99690ee55dbba4e00000000e11c48fecdd9e72510ca84f023370c9a38bf91ac5cae88019bee94d24528526344c36649ffff001d1d03e47701'
    block_6 = '01000000fc33f596f822a0a1951ffdbf2a897b095636ad871707bf5d3162729b00000000379dfb96a5ea8c81700ea4ac6b97ae9a9312b2d4301a29580e924ee6761a2520adc46649ffff001d189c4c9701'
    block_7 = '010000008d778fdc15a2d3fb76b7122a3b5582bea4f21f5a0c693537e7a03130000000003f674005103b42f984169c7d008370967e91920a6a5d64fd51282f75bc73a68af1c66649ffff001d39a59c8601'
    block_8 = '010000004494c8cf4154bdcc0720cd4a59d9c9b285e4b146d45f061d2b6c967100000000e3855ed886605b6d4a99d5fa2ef2e9b0b164e63df3c4136bebf2d0dac0f1f7a667c86649ffff001d1c4b566601'
    block_9 = '01000000c60ddef1b7618ca2348a46e868afc26e3efc68226c78aa47f8488c4000000000c997a5e56e104102fa209c6a852dd90660a20b2d9c352423edce25857fcd37047fca6649ffff001d28404f5301'

    # Forks Naming Convention
    #
    #   block_HEIGHT_PATH
    #
    # For example, block_1_a is the parent of both block_1_aa and block_1_ab.
    # and the parent of block_3_acc is block_2_ac.
    #

    block_1_a = '010000006fe28c0ab6f1b372c1a6a246ae63f74f931e8365e15a089c68d61900000000000090b6fe0de6d49a30fe6efb003c5ca82cf91c8515c5fa7f46526566eed0f4bbb2026749ffff001d8f316be500'
    block_1_b = '010000006fe28c0ab6f1b372c1a6a246ae63f74f931e8365e15a089c68d6190000000000378b0b16de3eaeab264ab3376c265d2d6c9efb6ff3650ac64edcda94b3198216d1026749ffff001d5df6dd2600'

    block_2_aa = '01000000541366d25ac71b75f218615d003f882909a9463c976162965ea0f92600000000eb48f9bc278e2f682116a878be4acaeba88dd895e1ad90b5ed3ca6bbce769dd009056749ffff001d4ad59e9200'
    block_2_ab = '01000000541366d25ac71b75f218615d003f882909a9463c976162965ea0f926000000009913ed436f51accd234711843247d0151d2d0cec0e04ce95b7cb85c814ec33b009056749ffff001d4cbabc2f00'
    block_2_ac = '01000000541366d25ac71b75f218615d003f882909a9463c976162965ea0f92600000000e1aad8a8612021f14b767a85caf84e1f5f2421f5e8d48dbc699723e31cbb82e80d056749ffff001d5182898100'
    block_2_ba = '010000000320b30417371c73aab13e0adfd8154097d2bf1bb0fb58bbdfe5665f00000000516a747c302d320ebab1ba97ef18b02d61490e2fe2c28b71580f05cf6dac21e621056749ffff001d15f186a300'
    block_2_bb = '010000000320b30417371c73aab13e0adfd8154097d2bf1bb0fb58bbdfe5665f0000000069991198c73b2a696989be65eaea94f5cbe1694fb2b3f95494ba96ee1bc1abed2d056749ffff001d0d94fabd00'

    block_3_aaa = '01000000dbc4e7fc50f53ef3a80c5c4ac9119b83cb53b6a0a4e8da7084c4f320000000001084640903ca51050fe8902fb323fade18c417116c42e1a6c45d531d7b7403ef6d076749ffff001d816aa6b700'
    block_3_aab = '01000000dbc4e7fc50f53ef3a80c5c4ac9119b83cb53b6a0a4e8da7084c4f32000000000d5daa3efd7e1f2c5e9bd8330ac35fa08ea45579d7045054d1623498183cdf67f74076749ffff001d4b58eecc00'
    block_3_aac = '01000000dbc4e7fc50f53ef3a80c5c4ac9119b83cb53b6a0a4e8da7084c4f320000000007c8c9fdb7867668711314705da16fd3ef48a858af160438e73d3849786d01da978076749ffff001d285ceed800'
    block_3_aba = '01000000f9160116faba4b380d01bd112dd628fe8a10f4bae83495633bd5140c000000007c8c9fdb7867668711314705da16fd3ef48a858af160438e73d3849786d01da97c076749ffff001dcea0efb900'
    block_3_abb = '01000000f9160116faba4b380d01bd112dd628fe8a10f4bae83495633bd5140c000000009d3143df7eb099e67385fdb4a4a8ddd4539d88d320acd54df011000ced474fce8a076749ffff001d8b07cc7000'
    block_3_abc = '01000000f9160116faba4b380d01bd112dd628fe8a10f4bae83495633bd5140c000000009532498c861e8aa87cfc2b39b9e17451eaa6bb0120a439dcb33c3ac7dc13f42591076749ffff001d3517b99400'
    block_3_aca = '0100000093286d1a16d9baaca6f9792ab72f83cc58d7b22e5c43312a717b0b6e0000000088be51901eb1815e645ca600d0c03c5c5c1342cc3891104e82bb0607adf5200a6e076749ffff001d0a51cd3700'
    block_3_acb = '0100000093286d1a16d9baaca6f9792ab72f83cc58d7b22e5c43312a717b0b6e00000000c0b3ddbd2fbb1ba0d7e07c68e846f690d42f4365a451a4c103a3c474539d560b6f076749ffff001d14f9e00e00'
    block_3_acc = '0100000093286d1a16d9baaca6f9792ab72f83cc58d7b22e5c43312a717b0b6e000000001dcd9172f4938fd96b9cdd84af0ac5a3f4cb5730b391975ec046546e2105fc6985076749ffff001d01b8965d00'
    block_3_baa = '01000000a8d1c5535465f9a26c55cf9b4c4033d7c19464681f024a1bb31a869b00000000e1aad8a8612021f14b767a85caf84e1f5f2421f5e8d48dbc699723e31cbb82e871076749ffff001d681d5bd500'
    block_3_bab = '01000000a8d1c5535465f9a26c55cf9b4c4033d7c19464681f024a1bb31a869b00000000fe4c606d64d08d00c9bf77da1df13f40b74e8a91c920f304e787c0f6c9052d9e76076749ffff001db15c33da00'
    block_3_bac = '01000000a8d1c5535465f9a26c55cf9b4c4033d7c19464681f024a1bb31a869b000000003505dbbfe3c55c501f3169315c5e23dc5f4e8a04d3db4170d9423607da1269b881076749ffff001d8f34f32a00'
    block_3_bba = '0100000059b3445d1781983b00c48e63a10cb5ef8e6219d84a1dec14749d40f800000000397a5f0c18de0d3ec20f057d39341e4a48336d51c924c34e61a490b0a6b1068874076749ffff001d421d86a400'
    block_3_bbb = '0100000059b3445d1781983b00c48e63a10cb5ef8e6219d84a1dec14749d40f80000000037a4124f3fb2fc97158add9d0ad45b79020479df5539a57bc81fa146fd0e83f393076749ffff001d7ed4b95800'
    block_3_bbc = '0100000059b3445d1781983b00c48e63a10cb5ef8e6219d84a1dec14749d40f8000000005a8720b79f5ae35e96f98c82f309587b03c6116988dfc8369bb4ea0018746a7d99076749ffff001d37af4f3100'

    block_4_aaaa = '0100000015e08e6fd14f70fc63e002863a54bc31370e054b2e82854ab126ece40000000056db6ea6b70b637c40c5ae289df4b99e009e9c3eb9ebc89dfc9ba1debb499177eb096749ffff001d3a5e830500'

    block_5_aaaaa = '010000005af95ad58d2cd9492385996159d0cf4b0d9e450b48ff85465cb3ae6000000000c479338d2750a2cd4256577afed6f137786b85425b74ec5e4b36d16838ac16882b0c6749ffff001d1085371800'

    # Block connectivity
    Chains = {
        block_0: {
            block_1: {
                block_2: {
                    block_3: {
                        block_4: {
                            block_5: {
                                block_6: {
                                    block_7: {
                                        block_8: {
                                            block_9: {
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
            block_1_a: {
                block_2_aa: {
                    block_3_aaa: {
                        block_4_aaaa: {
                            block_5_aaaaa: {
                            },
                        },
                    },
                    block_3_aab: {
                    },
                    block_3_aac: {
                    },
                },
                block_2_ab: {
                    block_3_aba: {
                    },
                    block_3_abb: {
                    },
                    block_3_abc: {
                    },
                },
                block_2_ac: {
                    block_3_aca: {
                    },
                    block_3_acb: {
                    },
                    block_3_acc: {
                    },
                },
            },
            block_1_b: {
                block_2_ba: {
                    block_3_baa: {
                    },
                    block_3_bab: {
                    },
                    block_3_bac: {
                    },
               },
                block_2_bb: {
                    block_3_bba: {
                    },
                    block_3_bbb: {
                    },
                    block_3_bbc: {
                    },
                },
            },
        },
    }


    def setUp(self):
        pass


    def get_header(self, block):
        (l, header) = pycoind.protocol.BlockHeader.parse(block.decode('hex') + "\0\0")
        return header


    def run_on_new_database(self, func):
        import shutil
        import tempfile

        # get temp directory for storing a database
        data_dir = tempfile.mkdtemp('-test-fork')
        #print "Using temporary directory %s..." % data_dir

        try:
            # create new database
            database = pycoind.blockchain.block.Database(data_dir)

            # run the function
            func(database)

        finally:
            # remove the temp directory
            #print "Removing directory %s..." % data_dir
            shutil.rmtree(data_dir)


    def do_header_test(self, chain, top_block, chain_height, message = ''):

        # make all that binary data into nice block headers
        headers = [self.get_header(b) for b in chain]
        top_header = self.get_header(top_block)

        def test(database):

            # make sure we are starting with the genesis block
            self.assertTrue(chain[0] == self.block_0, 'first block not genesis')

            # add blocks (excluding the genesis block which is prepopulated)
            for header in headers[1:]:
                result = database.add_header(header)
                self.assertTrue(result, 'a block header failed to get added to the blockchain (%s)' % message)

            # build a map that maps each block hash to whether it is mainchain or not
            cursor = database._cursor()
            cursor.execute('select hash, mainchain from blocks where height >= 0')
            mainchain = dict((str(h), v) for (h, v) in cursor.fetchall())

            # check longest (or first, for ties) chain blocks are mainchain
            height = 0
            cur_header = top_header
            while cur_header:
                self.assertTrue(mainchain[cur_header.hash], 'a block that is in the mainchain thinks it is not [%s] (%s)' % (cur_header.hash.encode('hex'), message))
                del mainchain[cur_header.hash]
                height += 1

                # find the block whose hash is the current prev_hash
                for header in headers:
                    if header.hash == cur_header.prev_block:
                        break
                else:
                    header = None
                cur_header = header

            # check all other blocks are not
            for block_hash in mainchain:
                self.assertFalse(mainchain[block_hash], 'a block that is not in the mainchain thinks it is [%s] (%s)' % (block_hash.encode('hex'), message))

            # check that the chain was the correct height
            self.assertTrue(height == chain_height, 'the chain height was incorrect [expected %d, got %d] (%s)' % (chain_height, height, message))

        self.run_on_new_database(test)


    def test_duplicate(self):
        def test(database):
            result = database.add_header(self.get_header(self.block_1_a))
            self.assertTrue(result, 'A block header failed to get added to the blockchain')
            result = database.add_header(self.get_header(self.block_1_a))
            self.assertFalse(result, 'A duplicate block header was added')

        self.run_on_new_database(test)


    def test_invalid_target(self):
        def test(database):
            try:
                database.add_header(self.get_header(self.block_1_invalid_target))
                self.fail('An block header with no parent was added')
            except pycoind.blockchain.block.InvalidBlockException, e:
                assert(e.message == 'block proof-of-work is greater than target')

        self.run_on_new_database(test)


    def test_no_parent(self):
        def test(database):
            try:
                database.add_header(self.get_header(self.block_2_aa))
                self.fail('An block header with no parent was added')
            except pycoind.blockchain.block.InvalidBlockException, e:
                assert(e.message == 'previous block does not exist')

        self.run_on_new_database(test)


    def test_forking(self):

        # maps blockhash => set(blockhashes...)
        edgemap = dict()
        def populate_edgemap(tree):
            for child in tree:
                if child not in edgemap:
                    edgemap[child] = set()
                edgemap[child].update(tree[child].keys())
                populate_edgemap(tree[child])
        populate_edgemap(self.Chains)

        # generates all possible, valid incoming block orders
        def constructions(complete, incomplete):
            if not incomplete: return [complete]
            ret = []
            for inc in incomplete:
                for com in complete:
                    if inc in edgemap[com]:
                        ret.extend(constructions(complete + [inc], [i for i in incomplete if i != inc]))
            return ret


        # Test genesis-only blockchain
        chain = [
            self.block_0,
        ]
        self.do_header_test(chain, self.block_0, 1, 'genesis only')


        # Test straight mainchain blockchain
        chain = [
            self.block_0,
            self.block_1,
            self.block_2,
            self.block_3,
            self.block_4,
            self.block_5,
        ]
        self.do_header_test(chain, self.block_5, 6, 'mainchain straight')


        # Test fork mainchain blockchain, mainchain wins b/c first
        chain = [
            self.block_0,
            self.block_1,
            self.block_1_a,
        ]
        self.do_header_test(chain, self.block_1, 2, 'fork mainchain first')


        # Test fork mainchain blockchain, mainchain loses b/c last
        chain = [
            self.block_0,
            self.block_1_a,
            self.block_1,
        ]
        self.do_header_test(chain, self.block_1_a, 2, 'fork mainchain late')

        # Test long re-fork
        chain = [
            self.block_0,
            self.block_1_a,
            self.block_2_aa,
            self.block_3_aaa,
            self.block_4_aaaa,
            self.block_5_aaaaa,
            self.block_1,
            self.block_2,
            self.block_3,
            self.block_4,
            self.block_5,
            self.block_6,
        ]
        self.do_header_test(chain, self.block_6, 7, 'long re-fork')

        # Test fork mainchain blockchain, mainchain loses b/c shorter
        blocks = [
            self.block_0,
            self.block_1,
            self.block_1_a,
            self.block_2_aa,
        ]
        for chain in constructions([blocks[0]], blocks[1:]):
            self.do_header_test(chain, self.block_2_aa, 3, 'short mainchain')


        # Test double fork mainchain blockchain, mainchain and b lose b/c shorter
        blocks = [
            self.block_0,
            self.block_1,
            self.block_1_a,
            self.block_1_b,
            self.block_2_aa,
            self.block_2_ba,
            self.block_3_aaa
        ]
        for chain in constructions([blocks[0]], blocks[1:]):
            self.do_header_test(chain, self.block_3_aaa, 4, 'double-fork')

suite = unittest.TestLoader().loadTestsFromTestCase(TestBlockchain)
unittest.TextTestRunner(verbosity = 2).run(suite)

