"""
The MetaDataStore handler.
"""
import os
from git import Repo

from damn_at.pluginmanager import IRepository

from damn_at import MetaDataType, MetaDataValue


class Repository(IRepository):
    """
    A GIT Repository.
    """
    def __init__(self, path):
        self.path = path
        self.repo = Repo(path)
        
    def get_meta_data(self, an_uri, file_descr):
        """
        """
        commit = self.repo.heads.master.commit
        path = os.path.relpath(an_uri, self.path)
        blob = commit.tree/path

        file_descr.metadata['git.author.name'] = MetaDataValue(type=MetaDataType.STRING, string_value=commit.author.name)
        file_descr.metadata['git.author.email'] = MetaDataValue(type=MetaDataType.STRING, string_value=commit.author.email)
        file_descr.metadata['git.message'] = MetaDataValue(type=MetaDataType.STRING, string_value=commit.message)
        file_descr.metadata['git.committer.name'] = MetaDataValue(type=MetaDataType.STRING, string_value=commit.committer.name)
        file_descr.metadata['git.committer.email'] = MetaDataValue(type=MetaDataType.STRING, string_value=commit.committer.email)
        file_descr.metadata['git.name_rev'] = MetaDataValue(type=MetaDataType.STRING, string_value=commit.name_rev)
        
        file_descr.metadata['git.remotes.origin.url'] = MetaDataValue(type=MetaDataType.STRING, string_value=self.repo.remotes.origin.config_reader.get('url'))
        
        return file_descr


if __name__ == '__main__':

    repo = Repo("/home/sueastside/dev/DAMN/damn-test-files")
    
    print(dir(repo))
    print(dir(repo.remotes[0]))
    print(repo.remotes[0].name)
    
    origin = repo.remotes.origin
    print(dir(origin))
    print(origin.refs[0].name)
    print(origin.refs[0].path)
    print(origin.refs[0].remote_name)
    print(origin.config_reader.get('url'))

    commit = repo.heads.master.commit

    path = 'mesh/blender/cube1.blend'

    commits = [commit]
    commits.extend(commit.iter_parents(path))

    for c in commits:
        print('-'*70)
        blob = (c.tree/path)
        print blob, blob.data_stream.read(4)
        #print dir(c)
        print c.author, c.authored_date, c.committed_date, c.committer, c.message, c.name_rev, c.summary
