"""Test DAMN services"""
import unittest

from thrift.protocol import TJSONProtocol, TBinaryProtocol

from damn_at.thrift.serialization import SerializeThriftMsg, DeserializeThriftMsg

from damn_at.thrift.generated.damn_types.ttypes import FileId, AssetId, AssetReference

class DAMNServiceTest(unittest.TestCase):
    """DAMNServiceTest"""   

    def test_something(self): # pylint: disable=C0103
        """test_something"""
        self.assertEqual(True, True)

def test_suite():
    """Suits"""
    return unittest.TestLoader().loadTestsFromTestCase(DAMNServiceTest)

if __name__ == '__main__':
    #unittest.main()
    unittest.TextTestRunner().run(test_suite())
