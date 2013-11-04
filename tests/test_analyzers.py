"""
Does some stuff
"""
import os
import unittest

#import logging
#logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

from damn_at.pluginmanager import DAMNPluginManagerSingleton
from damn_at.analyzer import Analyzer
from damn_at import registry

def pretty_print(fileref):
    """Pretty print the fileref"""
    print(fileref.file.filename)
    if fileref.assets:
        for asset in fileref.assets:
            print('', asset.asset.subname, asset.asset.mimetype, asset.asset.file.filename)
            if asset.dependencies:
                for dep in asset.dependencies:
                    print('  ', dep.subname, dep.mimetype, dep.file.filename)


class TestCase(unittest.TestCase):
    """Test case"""
    def rtest_say(self):
        """Test say"""
        # Build the manager
        simple_plugin_mgr = DAMNPluginManagerSingleton.get()
        print(simple_plugin_mgr.getAllPlugins())

        # Activate all loaded plugins
        for plugin_info in simple_plugin_mgr.getAllPlugins():
            print('Activating', plugin_info.name)
        for plugin_info in simple_plugin_mgr.getPluginsOfCategory('Failed'):
            print('E: ', plugin_info.name, plugin_info.error)
        assert True
        
    def test_analyze(self):
        """Test say"""
        ref = Analyzer().analyze_file('/home/sueastside/dev/blenderassets/cube1.blend')
        pretty_print(ref)
        assert True
        
    def test_registry(self):
        """Test say"""
        print(registry.get('damn_at.analyzer.number_of_analyzers').value())
        assert True

def test_suite():
    """Return a list of tests"""
    return unittest.TestLoader().loadTestsFromTestCase(TestCase)

if __name__ == '__main__':
    #unittest.main()
    unittest.TextTestRunner().run(test_suite())
