"""
Generic Image analyzer.
"""
import os


from damn_at import logger
from damn_at.analyzer import AnalyzerException
from damn_at.thrift.generated.damn_types.ttypes import FileId, FileReference

from damn_at.pluginmanager import IAnalyzer
from damn_at.utilities import script_path, run_blender

class GenericImageAnalyzer(IAnalyzer):
    """Generic Image analyzer."""
    handled_types = ["image/jpeg"]
    
    def __init__(self):
        IAnalyzer.__init__(self)
      
    def activate(self):
        pass

    def analyze(self, an_uri):
    	fileid = FileId(filename = os.path.abspath(an_uri))
        fileref = FileReference(file = fileid)
        
        return fileref
        
        














