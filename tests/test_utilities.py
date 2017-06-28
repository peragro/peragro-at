"""
Utilities Tests
---------------
UnitTests for the utilities module
"""
import unittest
import tempfile
import os
from damn_at import utilities as utils


class UtilTests(unittest.TestCase):

    def test_is_existing_file_a(self):
        """Test returns false when given a bad path"""

        ret = utils.is_existing_file('/foo/monkey/slug/shit')
        self.assertFalse(ret)

    def test_is_existing_file_b(self):
        """Test returns true when given a valid path"""

        f = tempfile.NamedTemporaryFile(delete=False)
        f.close()
        ret = utils.is_existing_file(f.name)
        self.assertTrue(ret)

    def test_calculate_hash(self):
        """Test accurate hash generated from file"""

        data = (
            b'QlJBTlQgSVMgU1VQRVIgQVdFU09NRSBDT09MIEFORCBTSElULiBTTFVHUyBBUkUg'
            b'Q1VURQ=='
        )
        expected_hash = '03439afa9d61f99f35d936b01ea8b4982ab247a0'
        t = tempfile.NamedTemporaryFile(delete=False)
        t.write(data)
        t.close()
        ret = utils.calculate_hash_for_file(t.name)
        self.assertEqual(ret, expected_hash)

    def test_unique_asset_id_reference_from_fields(self):
        """Make sure uuid generator produces accurate strings"""

        ret = utils.unique_asset_id_reference_from_fields(
            'OHIAMAHASH',
            'SNAILJUICE',
            'text/rtf'
        )
        self.assertEqual(ret, 'OHIAMAHASHSNAILJUICEtext__rtf')


def test_suite():
    """Return a list of tests"""
    return unittest.TestLoader().loadTestsFromTestCase(UtilTests)

if __name__ == '__main__':
    # unittest.main()
    unittest.TextTestRunner().run(test_suite())
