"""DAMN Service server"""
# Standard
import os
import sys
import logging

# 3rd Party
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

# Damn
from damn_at.serialization.generated.damn import DamnService
from damn_at.analyzer import Analyzer
from damn_at.serialization.generated.damn_types.ttypes import (
    TargetMimetype,
    TargetMimetypeOption
)

sys.path.append(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'generated'
))
LOG = logging.getLogger(__name__)


class DamnServiceHandler:
    """DAMN Service Implementation"""
    def __init__(self):
        self.log = {}

    def ping(self):
        """Implementation"""
        LOG.debug("ping()")

    def get_supported_mimetypes(self):
        """Implementation"""
        return Analyzer().get_supported_mimetypes()

    def get_target_mimetypes(self):
        """Implementation"""
        mimetypes = {}

        for source in Analyzer().get_supported_mimetypes():
            option = TargetMimetypeOption(
                name='',
                description='',
                type='',
                constraint='',
                default_value=''
            )
            target = TargetMimetype(
                mimetype='target//' + source,
                description='',
                template='/x/x/'
            )
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
    # server = TServer.TThreadedServer(processor, transport, tfactory, pfactory)
    # server = TServer.TThreadPoolServer(
    #     processor,
    #     transport,
    #     tfactory,
    #     pfactory
    # )

    LOG.info('Starting the server...')
    server.serve()
    LOG.info('Done.')


if __name__ == '__main__':
    main()
