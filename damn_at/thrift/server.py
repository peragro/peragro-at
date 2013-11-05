#!/usr/bin/env python
"""DAMN Service server"""
 
import os
import sys
directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'generated')
sys.path.append(directory)
 
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

from damn_at.thrift.generated.damn import DamnService

from damn_at.analyzer import Analyzer

from damn_at.thrift.generated.damn_types.ttypes import TargetMimetype, TargetMimetypeOption
 
class DamnServiceHandler:
    """DAMN Service Implementation"""
    def __init__(self):
        self.log = {}

    def ping(self, ):
        """Implementation"""
        print "ping()"

    def get_supported_mimetypes(self, ):
        """Implementation"""
        return Analyzer().get_supported_mimetypes()
    
    def get_target_mimetypes(self, ):
        """Implementation"""
        mimetypes = {}
        
        for source in Analyzer().get_supported_mimetypes():
            option = TargetMimetypeOption(name='', description='', type='', constraint='', default_value='')
            target = TargetMimetype(mimetype='target//'+source, description='', template='/x/x/')
            target.options = [option]
            mimetypes[source] = target
        
        return mimetypes
        
    def analyze(self, a_file):
        """
        Parameters:
         - file
        """
        pass


def main(): 
    """Start the server"""
    handler = DamnServiceHandler()
    processor = DamnService.Processor(handler)
    transport = TSocket.TServerSocket(port=9090)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()

    server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)

    # You could do one of these for a multithreaded server
    #server = TServer.TThreadedServer(processor, transport, tfactory, pfactory)
    #server = TServer.TThreadPoolServer(processor, transport, tfactory, pfactory)

    print 'Starting the server...'
    server.serve()
    print 'done.'


if __name__ == '__main__': 
    main()
