"""
Blender file format analyzer.
"""
import binascii

from thrift.protocol import TBinaryProtocol

from damn_at import logger
from damn_at.analyzer import AnalyzerException
from damn_at import FileDescription
from damn_at.serialization import DeserializeThriftMsg

from damn_at.pluginmanager import IAnalyzer
from damn_at.utilities import script_path, run_blender

class BlendAnalyzer(IAnalyzer):
    """Blender file format analyzer."""
    handled_types = ["application/x-blender"]
    
    def __init__(self):
        IAnalyzer.__init__(self)
      
    def activate(self):
        pass

    def analyze(self, an_uri):
        stdoutdata, stderrdata, returncode = run_blender(an_uri, script_path(__file__))
        
        if returncode != 0: 
            raise AnalyzerException('BlendAnalyzer failed with %s'%(returncode))
        
        logger.debug(stdoutdata)
        logger.debug(stderrdata)
        
        data = str(stdoutdata).split('-**-')[1].replace('\n', '').replace('\r', '').replace("b'", '').replace("'", '')
        data = binascii.unhexlify(data)
        
        file_descr = DeserializeThriftMsg(FileDescription(), data, TBinaryProtocol.TBinaryProtocol)
        
        return file_descr
