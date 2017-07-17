"""DAMN Service client"""
# Standard
import sys
import socket
import logging

# 3rd Party
from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

# Damn
from damn_at.serialization.generated.damn import DamnService

sys.path.append('generated')
LOG = logging.getLogger(__name__)


class DamnServiceClient(object):
    """DamnServiceClient"""
    def __init__(self):
        self.host = 'localhost'
        self.port = 9090
        self._socket = None
        self._client = None
        self._transport = None
        self.connected = False

    def _connect(self):
        # Make socket
        self._socket = TSocket.TSocket(self.host, self.port)

        # Buffering is critical. Raw sockets are very slow
        self._transport = TTransport.TBufferedTransport(self._socket)

        # Wrap in a protocol
        protocol = TBinaryProtocol.TBinaryProtocol(self._transport)

        # Create a client to use the protocol encoder
        self._client = DamnService.Client(protocol)

        # Connect!
        self._transport.open()

        self.connected = True

    def __del__(self):
        self._transport.close()

    def __getattr__(self, name):
        try:
            if not self.connected:
                self._connect()
            return getattr(self._client, name)
        except TTransport.TTransportException as tte:
            self.connected = False
            raise tte
        except socket.error as serr:
            self.connected = False
            raise serr


if __name__ == '__main__':
    client = DamnServiceClient()
    while True:
        try:
            # client.ping()
            LOG.debug(client.get_target_mimetypes())
        except Thrift.TApplicationException as tae:
            LOG.error('while TApplicationException: %s' % str(tae))
        except TTransport.TTransportException as wtte:
            # import traceback
            # traceback.print_exc()
            LOG.debug('while TTransport: %s' % str(wtte))
        except socket.error as wserr:
            # import traceback
            # traceback.print_exc()
            LOG.debug('while socket: %s' % str(wserr))
            client = DamnServiceClient()
