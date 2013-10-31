import unittest
import damn_at


class TestCase(unittest.TestCase):

    def test_say(self):
        assert 'hello world' == 'hello world'


def suite():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTest(loader.loadTestsFromTestCase(TestCase))
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())

