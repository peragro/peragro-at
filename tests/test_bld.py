import unittest
import os
import tempfile

from mock import Mock, patch

from damn_at import bld


class TestCase(unittest.TestCase):
    """Test Block level dedup"""
    def test_block_hashes_for_file(self):
        digest, hashes = bld.block_hashes_for_file('fakefile')
        self.assertEqual(digest, 'NOT_FOUND(fakefile)')
        self.assertEqual(hashes, [])

    def test_block_hashes_for_file2(self):
        """Test accurate hash generated from file"""
        data = (
            b'QlJBTlQgSVMgU1VQRVIgQVdFU09NRSBDT09MIEFORCBTSElULiBTTFVHUyBBUkUg'
            b'Q1VURQ=='
        )
        expected_digest = '03439afa9d61f99f35d936b01ea8b4982ab247a0'
        expected_hashes = ['03439afa9d61f99f35d936b01ea8b4982ab247a0']
        t = tempfile.NamedTemporaryFile(delete=False)
        t.write(data)
        t.close()
        digest, hashes = bld.block_hashes_for_file(t.name)
        self.assertEqual(digest, expected_digest)
        self.assertEqual(hashes, expected_hashes)

    def test_block_hashes_from_file(self):
        pass

    def test_block_hashes_to_file(self):
        pass

    def test_hash_to_dir(self):
        dir = bld.hash_to_dir('002badb952000339cdcf1b61a3205b221766bf49')
        assert dir == '00/2badb952000339cdcf1b61a3205b221766bf49'

    def test_blocks_for_file(self):
        pass

    def test_filter_existing_block_hashes(self):
        pass

    def test_walk(self):
        pass

def test_suite():
    """Return a list of tests"""
    return unittest.TestLoader().loadTestsFromTestCase(TestCase)

if __name__ == '__main__':
    #unittest.main()
    unittest.TextTestRunner().run(test_suite())
