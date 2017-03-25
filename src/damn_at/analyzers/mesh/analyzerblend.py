"""
Blender file format analyzer.
"""
# Standard
import binascii
import logging

# 3rd Party
from thrift.protocol import TBinaryProtocol

# Damn
from damn_at import FileDescription
from damn_at.serialization import DeserializeThriftMsg
from damn_at.pluginmanager import IAnalyzer
from damn_at.utilities import (
    script_path,
    run_blender
)
from damn_at.analyzer import AnalyzerException

LOG = logging.getLogger(__name__)


class BlendAnalyzer(IAnalyzer):
    """Blender file format analyzer."""
    handled_types = ["application/x-blender"]

    def __init__(self):
        IAnalyzer.__init__(self)

    def activate(self):
        pass

    def analyze(self, an_uri):
        stdoutdata, stderrdata, returncode = run_blender(
            an_uri,
            script_path(__file__)
        )

        if returncode != 0:
            raise AnalyzerException('BlendAnalyzer failed with returncode "%s"'
                                    % returncode)

        LOG.debug(stdoutdata)
        LOG.debug(stderrdata)

        data = str(stdoutdata).split('-**-')[1]
        for old, replace in [('\\r\\n', ''), ('\n', ''), ('\r', ''), ("b'", ''), ("'", '')]:
            data = data.replace(old, replace)      
        data = binascii.unhexlify(data)

        file_descr = DeserializeThriftMsg(
            FileDescription(),
            data,
            TBinaryProtocol.TBinaryProtocol
        )

        return file_descr
