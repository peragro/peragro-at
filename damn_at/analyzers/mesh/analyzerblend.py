"""
Blender file format analyzer.
"""

from damn_at.pluginmanager import IAnalyzer

class BlendAnalyzer(IAnalyzer):
    """Blender file format analyzer."""
    handled_types = ["application/x-blender"]
    
    def __init__(self):
        IAnalyzer.__init__(self)
      
    def activate(self):
        raise Exception('rr')

    def analyze(self, an_uri):
        raise Exception("'analyze' must be reimplemented by %s" % self) 




















