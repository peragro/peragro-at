# PYTHON_ARGCOMPLETE_OK
# Add  eval "$(register-python-argcomplete pt)"   to ~/.basrc or so.
"""
Peragro commandline tool
"""
from __future__ import absolute_import
import os
import sys
import json
import logging
import argparse
import argcomplete
from argcomplete.completers import (
    ChoicesCompleter,
    FilesCompleter,
    # _wrapcall
)
import pkg_resources
from six.moves import map

LOG = logging.getLogger(__name__)


def serialize_file_description(file_descr, format='print'):
    from .utilities import pretty_print_file_description
    from damn_at.serialization import SerializeThriftMsg
    from thrift.protocol.TJSONProtocol import TSimpleJSONProtocol

    try:
        from cStringIO import StringIO
    except ImportError:
        from io import StringIO
    if format == 'print':
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        pretty_print_file_description(file_descr)
        data = sys.stdout.getvalue()
        sys.stdout.close()
        sys.stdout = old_stdout
    elif format == 'json':
        data = SerializeThriftMsg(file_descr, TSimpleJSONProtocol)
    elif format == 'json-pretty':
        data = SerializeThriftMsg(file_descr, TSimpleJSONProtocol)
        data = json.loads(data)
        data = json.dumps(data, indent=4)
    elif format == 'binary':
        data = SerializeThriftMsg(file_descr)
    else:
        raise Exception('Unknown format %s', format)
    return data


def create_argparse_analyze(subparsers):
    subparse = subparsers.add_parser(
        "a",  # aliases=("analyze",),
        help="Analyze a given file",
    )
    subparse.add_argument(
        dest="path", type=str,
        help="Path to checkout on the server",
    ).completer = FilesCompleter(directories=False)

    group = subparse.add_mutually_exclusive_group()
    group.add_argument(
        "-o", "--output", dest="output", type=str,
        help="The file to write the binary output to",
    )
    group.add_argument(
        "-f", "--format", dest="format", type=str,
        help="The format to output",
    ).completer = ChoicesCompleter(['print', 'binary', 'json', 'json-pretty'])
    group.add_argument(
        "-s", "--store", dest="store", type=str,
        help="The store to write the binary output to",
    ).completer = FilesCompleter(['ignore'])

    def analyze(path, output, format_type, store):
        from .analyzer import Analyzer
        from .metadatastore import MetaDataStore
        from damn_at.serialization import SerializeThriftMsg
        from .utilities import calculate_hash_for_file

        analyzer = Analyzer()
        descr = analyzer.analyze_file(path)
        descr.file.hash = calculate_hash_for_file(path)
        if not format_type and not output and not store:
            LOG.info(serialize_file_description(descr, 'print'))
            # print(serialize_file_description(descr, 'print'))
        elif not output and not store:
            LOG.info(serialize_file_description(descr, format_type))
            # print(serialize_file_description(descr, format_type))
        elif output:
            with open(output, 'wb') as file:
                data = SerializeThriftMsg(descr)
                file.write(data)
        elif store:
            store = MetaDataStore(store)
            hash = descr.file.hash
            store.write_metadata('', hash, descr)
        else:
            assert False  # Error in logic

    subparse.set_defaults(func=lambda args: analyze(
        args.path,
        args.output,
        args.format,
        args.store
    ),)


def assetname_completer(prefix, parsed_args, **kwargs):
    if parsed_args.fd:
        from damn_at import FileDescription
        from damn_at.serialization import DeserializeThriftMsg
        with open(parsed_args.fd, 'rb') as f:
            file_descr = DeserializeThriftMsg(FileDescription(), f.read())
            data = ['{0.subname}({0.mimetype})'.format(asset.asset) for
                    asset in file_descr.assets]
            return data


def split_assetname(assetname):
    import re
    regexp = re.compile(r'^(.+?)(\((.+?)\))?$')
    match = regexp.match(assetname)
    asset_subname = match.group(1)
    asset_mimetype = match.group(3)
    return asset_subname, asset_mimetype


def target_mimetype_completer(prefix, parsed_args, **kwargs):
    from .transcoder import Transcoder

    asset_subname, asset_mimetype = split_assetname(parsed_args.assetname)

    t = Transcoder('/tmp/transcoded/')

    targets = [x.mimetype for x in t.get_target_mimetypes()[asset_mimetype]]
    return targets


def create_argparse_transcode(parser, subparsers):
    subparse = subparsers.add_parser(
        "t",  # aliases=("transcode",),
        help="Transcode a given file",
    )
    subparse.add_argument(
        dest="path",
        type=str,
        help="Path to file to transcode",
    ).completer = FilesCompleter(directories=False)
    subparse.add_argument(
        'assetname',
        help='The subname of the asset to transcoder'
    ).completer = assetname_completer
    subparse.add_argument(
        'mimetype',
        help='The destination mimetype'
    ).completer = target_mimetype_completer
    subparse.add_argument(
        "-fd",
        "--file-description",
        dest="fd",
        type=str,
        help="Path to the cached FileDescription",
    ).completer = FilesCompleter(directories=False)
    subparse.add_argument(
        "-o", "--output",
        dest="output",
        type=str,
        help="The output directory to write the transcoded files to",
    ).completer = FilesCompleter(['ignore'])

    try:
        args, options_args = parser.parse_known_args()
        #TODO
        if args.assetname and args.mimetype:
            from .transcoder import Transcoder
            t = Transcoder('/tmp/transcoded/')
            asset_subname, asset_mimetype = split_assetname(args.assetname)
            target_mimetype = t.get_target_mimetype(
                asset_mimetype,
                args.mimetype
            )
            for option in target_mimetype.options:
                subparse.add_argument(
                    "--" + option.name,
                    dest=option.name,
                    default=option.default_value,
                    help='%s (%s) [default: %s] (%s)' % (
                        option.description,
                        option.constraint,
                        option.default_value,
                        option.type
                    )
                )
    except:
        pass

    def transcode(args):
        LOG.info('Transcoding...')
        from .transcoder import Transcoder
        t = Transcoder('/tmp/transcoded/')
        asset_subname, asset_mimetype = split_assetname(args.assetname)
        target_mimetype = t.get_target_mimetype(asset_mimetype, args.mimetype)
        if target_mimetype is None:
            parser.print_help()
        # TODO
        LOG.info("Options:\n%s" % "\n".join(map(str, target_mimetype.options)))
        
        options = t.parse_options(asset_mimetype, target_mimetype, **vars(args))
        
        if not args.fd:
            from .analyzer import Analyzer
            analyzer = Analyzer()
            descr = analyzer.analyze_file(args.path)
            
        from .utilities import find_asset_id_in_file_descr    
        asset_id = find_asset_id_in_file_descr(descr, asset_subname, asset_mimetype)
        if asset_id is None:
            parser.print_help()
        print (t.transcode(descr, asset_id, target_mimetype, **options))

    subparse.set_defaults(func=lambda args: transcode(args),)


def file_or_hash_completer(prefix, parsed_args, **kwargs):
    if not parsed_args.store:
        return FilesCompleter(directories=False)
    path = os.path.join(parsed_args.store, prefix[:2])
    if os.path.isdir(path):
        res = [prefix[:2]+x for x in os.listdir(path)]
    else:
        res = os.listdir(parsed_args.store)

    return res


def create_argparse_inspect(parser, subparsers):
    subparse = subparsers.add_parser(
        "i",  # aliases=("inspect",),
        help="Inspect a given file or hash in store",
    )
    subparse.add_argument(
        dest="path",
        type=str,
        help="Path to file to transcode",
    ).completer = file_or_hash_completer
    subparse.add_argument(
        "-s",
        "--store",
        dest="store",
        type=str,
        help="The store to write the binary output to",
    ).completer = FilesCompleter(['ignore'])
    subparse.add_argument(
        "-f",
        "--format",
        dest="format",
        type=str,
        help="The format to output",
        default='print'
    ).completer = ChoicesCompleter(['print', 'binary', 'json', 'json-pretty'])

    def inspect(args):
        from .metadatastore import MetaDataStore
        if args.store:
            m = MetaDataStore(args.store)
            descr = m.get_metadata('', args.path)
        else:
            from damn_at import FileDescription
            from damn_at.serialization import DeserializeThriftMsg
            with open(args.path, 'rb') as f:
                descr = DeserializeThriftMsg(FileDescription(), f.read())

        LOG.info(serialize_file_description(descr, args.format))
        # print(serialize_file_description(descr, args.format))

    subparse.set_defaults(func=lambda args: inspect(args),)


def create_argparse():
    usage_text = ("Platinumial\n" + __doc__)

    parser = argparse.ArgumentParser(
        prog="pt",
        description=usage_text,
    )

    parser.add_argument(
        '-v',
        '--verbose',
        help='Be verbose',
        action="store_const",
        dest="loglevel",
        const=logging.DEBUG,
        default=logging.INFO
    )
    parser.add_argument(
        '-q',
        '--quiet',
        help='Hide most output',
        action="store_const",
        dest="loglevel",
        const=logging.ERROR
    )

    subparsers = parser.add_subparsers(
        title='subcommands',
        description='valid subcommands',
        help='additional help',
    )

    create_argparse_analyze(subparsers)
    create_argparse_inspect(parser, subparsers)

    group = 'peragro.commandline.hooks'
    for entrypoint in pkg_resources.iter_entry_points(group=group):
        plugin = entrypoint.load(require=False)
        plugin(parser, subparsers)

    #Do this last as it does a parse_know_args
    create_argparse_transcode(parser, subparsers)

    return parser


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    parser = create_argparse()
    argcomplete.autocomplete(parser)
    args = parser.parse_args(argv)

    # Setup basic logging
    logging.basicConfig(
        level=args.loglevel,
        format='%(levelname)7s:%(name)s: %(message)s',
        handlers=[logging.StreamHandler()]
    )

    # logging.basicConfig(format='%(levelname)s:%(message)s',
    #                     level=args.loglevel)

    # call subparser callback
    if not hasattr(args, "func"):
        parser.print_help()
        return

    args.func(args)


if __name__ == "__main__":
    main()
