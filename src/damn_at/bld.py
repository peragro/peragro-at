"""
Block-level deplucation utility functions.
"""
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
import os
import subprocess
import glob
import hashlib

from damn_at.utilities import calculate_hash_for_file
from io import open


BLOCK_SIZE = 2048

def block_hashes_for_file(an_uri):
    """
    Calculate the hash for each block in the given file
    as well as the hash for the entire file and return it.
    :param an_uri: the URI pointing to the file
    :rtype: string, list<string>
    """
    try:
        hashes = []
        chksum = hashlib.sha1()
        with open(an_uri, 'rb') as filehandle:
            while True:
                buf = filehandle.read(BLOCK_SIZE)
                if not buf:
                    break
                chksum.update(buf)
                blockhash = hashlib.sha1()
                blockhash.update(buf)
                hashes.append(blockhash.hexdigest())
        return chksum.hexdigest(), hashes
    except IOError:
        return 'NOT_FOUND(%s)' % an_uri, []


def block_hashes_from_file(an_uri):
    """
    Deserialize the saved block hashes from the given file.
    :param an_uri: the URI pointing to the file
    :rtype: list<string>
    """
    with open(an_uri, 'rb') as filehandle:
        for line in filehandle.readlines()[1:]:
            yield line.strip()


def block_hashes_to_file(file_hash, block_hashes, an_uri):
    """
    Serialize the given block hashes to the given uri destination.
    :param file_hash: the complete file's hash
    :param block_hashes: a list of block hashes to serialize
    :param an_uri: the file path which to save to
    :rtype: list<string>
    """
    if not os.path.exists(os.path.dirname(an_uri)):
        os.makedirs(os.path.dirname(an_uri))
    with open(an_uri, 'wb') as filehandle:
        filehandle.write('%s %d\n'%(file_hash, len(block_hashes)))
        for hash in block_hashes:
            filehandle.write(hash+'\n')


def hash_to_dir(hash):
    """
    Transforms a given hash to a relative path and filename
    ex: '002badb952000339cdcf1b61a3205b221766bf49' -> '00/2badb952000339cdcf1b61a3205b221766bf49'
    :param hash: the hash to split
    :rtype: string
    """
    return hash[:2]+'/'+hash[2:]


def blocks_for_file(an_uri, destination):
    """
    Write all blocks for the given file to the destination.
    :param an_uri: the URI pointing to the file to split
    :param destination: the destination directory for the block files
    :rtype: list<string> the paths to the written blocks
    """
    try:
        paths = []
        with open(an_uri, 'rb') as filehandle:
            while True:
                buf = filehandle.read(BLOCK_SIZE)
                if not buf:
                    break
                blockhash = hashlib.sha1()
                blockhash.update(buf)
                hash = blockhash.hexdigest()
                path = os.path.join(destination, hash_to_dir(hash))
                paths.append(path)
                if os.path.exists(path):
                    #print 'Block exists'
                    continue

                if not os.path.exists(os.path.dirname(path)):
                    os.makedirs(os.path.dirname(path))
                with open(path, 'wb') as block:
                    block.write(buf)
        return paths
    except IOError:
        return 'NOT_FOUND(%s)' % an_uri


def blocks_to_file(an_uri, block_hashes, destination):
    """
    Combine the referenced blocks into a given destination file.
    :param an_uri: the directory containing the blocks
    :param block_hashes: a list of block hashes
    :param destination: the destination file path
    """
    if not os.path.exists(os.path.dirname(destination)):
        os.makedirs(os.path.dirname(destination))
    with open(destination, 'wb') as filehandle:
        for block_hash in block_hashes:
            with open(os.path.join(an_uri, hash_to_dir(block_hash)), 'rb') as block:
                filehandle.write(block.read())


def filter_existing_block_hashes(an_uri, block_hashes):
    """
    Check the given uri if it contains the given blocks and filter out the existing.
    :param an_uri: the directory containing the blocks
    :param block_hashes: the list of block hashes to check for existence
    :rtype: list<string> a list of block hashes that do not exist
    """
    new_block_hashes = set([])
    dirs = os.listdir(an_uri)
    cache = {}
    for bloc_hash in block_hashes:
        prefix = bloc_hash[:2]
        if prefix not in dirs:
            new_block_hashes.add(bloc_hash)
        else:
            if prefix not in cache:
                cache[prefix] = os.listdir(os.path.join(an_uri, prefix))
            else:
                print(('from cache', bloc_hash))
            if bloc_hash[2:] not in cache[prefix]:
                new_block_hashes.add(bloc_hash)
    return new_block_hashes


def walk(uri):
    for root, dirs, files in os.walk(uri):
        if '.git' in dirs:
            dirs.remove('.git')
        for file_name in files:
            if file_name.startswith('.git'):
                files.remove(file_name)
                continue
            path = os.path.join(root, file_name)
            yield path


def statistics(uri):
    blocks = {}
    block_count = 0
    for path in walk(uri):
        for block_hash in block_hashes_from_file(path):
            if block_hash in blocks:
                blocks[block_hash].append(path)
                #print '  duplicate', file_hash, block_hash, path
            else:
                blocks[block_hash] = [path]
            block_count += 1

    print(('%d unique blocks with %d references'%(len(blocks), block_count)))
    saved = ((block_count-len(blocks))*BLOCK_SIZE) // 1024
    total = (block_count*BLOCK_SIZE) // 1024
    print(('saving %.2f KB on a total of %.2f KB'%(saved, total)))
    reuse = {}
    for block_hash, paths in blocks.items():
        if len(paths) in reuse:
            reuse[len(paths)] += 1
        else:
            reuse[len(paths)] = 1
    for paths, count in reuse.items():
        print(('%d files with %d reused blocks'%(count, paths)))


def verify(uri):
    for path in walk(uri):
        file_hash = os.path.basename(os.path.dirname(path)) + os.path.basename(path)
        new_file_hash = calculate_hash_for_file(path)
        print(('Verification %s %s'%(path, 'OK' if file_hash == new_file_hash else 'FAIL')))


if __name__ == '__main__':
    test_files_dir = os.path.join(os.path.dirname(__file__), '../../../peragro-test-files')
    for path in walk(test_files_dir):
        file_hash, block_hashes = block_hashes_for_file(path)
        block_hashes_to_file(file_hash, block_hashes, '/tmp/files/'+hash_to_dir(file_hash))
        blocks_for_file(path, '/tmp/blocks')


    statistics('/tmp/files/')

    for path in walk(test_files_dir):
        file_hash = calculate_hash_for_file(path)
        block_hashes = block_hashes_from_file('/tmp/files/'+hash_to_dir(file_hash))
        new_path = '/tmp/out/'+os.path.basename(path)
        blocks_to_file('/tmp/blocks', block_hashes, new_path)

        new_file_hash = calculate_hash_for_file(new_path)
        print(('Verification %s'%('OK' if file_hash == new_file_hash else 'FAIL')))

    verify('/tmp/blocks')

    block_hashes = ['b499ca988473a4abc0461717cc8d4ce8753aa6d9', #exists
    'b497ca988473a4abc0461717cc8d4ce8753aa6d9',
    'b497ca988473a4abc0461717cc8d4ce8753aa6d9',
    'b48e1faa27b06f8a6fabfd32c719d685accfccf4', #exists
    'b48e1faa27b06f8a6fabfd32c719d685accfccf4']

    print((filter_existing_block_hashes('/tmp/blocks', block_hashes)))
