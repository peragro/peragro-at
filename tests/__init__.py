import unittest

import test_damn_at

def suite():
    import unittest
    suite = unittest.TestSuite()
    suite.addTests(test_damn_at.suite())
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
