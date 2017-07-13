import unittest
import os
from mock import Mock, patch
from damn_at.analyzers.text.plain import analyzertext
from damn_at import utilities


class TestCase(unittest.TestCase):
    def test_analyze_plain_text(self):
        dic = {'charset': "us-ascii",
               'lines': '6'}

        uri = os.path.join(os.path.dirname(__file__),
                           '../../peragro-test-files/text/plain/test.txt')
        analyzer = analyzertext.GenericTextAnalyzer()
        file_descr = analyzer.analyze(uri)
        assert file_descr, "something went wrong while analysing test.test"
        # print(file_descr)
        metadata_dic = {}
        for asset in file_descr.assets:
            for key, value in asset.metadata.items():
                ty, val = utilities.get_metadatavalue_type(value)
                metadata_dic[key] = val
        assert metadata_dic == dic, \
            "Analyzed values are not equal to the expected ones"


def test_suite():
    """Return a list of tests"""
    return unittest.TestLoader().loadTestsFromTestCase(TestCase)

if __name__ == '__main__':
    # unittest.main()
    unittest.TextTestRunner().run(test_suite())
