import unittest

from mock import Mock, patch

from damn_at import bld


class TestCase(unittest.TestCase):
    """Test Block level dedup"""
    def test_block_hashes_for_file(self):
        digest, hashes = bld.block_hashes_for_file('fakefile')


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
