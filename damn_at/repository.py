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
        
    def get_meta_data(self, an_uri, file_ref):
        """
        """
        commit = self.repo.heads.master.commit
        path = os.path.relpath(an_uri, self.path)
        blob = commit.tree/path
        print('==>', dir(commit.author))
        file_ref.metadata['git.author.name'] = MetaDataValue(type=MetaDataType.STRING, string_value=commit.author.name)
        file_ref.metadata['git.author.email'] = MetaDataValue(type=MetaDataType.STRING, string_value=commit.author.email)
        file_ref.metadata['git.message'] = MetaDataValue(type=MetaDataType.STRING, string_value=commit.message)
        file_ref.metadata['git.committer.name'] = MetaDataValue(type=MetaDataType.STRING, string_value=commit.committer.name)
        file_ref.metadata['git.committer.email'] = MetaDataValue(type=MetaDataType.STRING, string_value=commit.committer.email)
        file_ref.metadata['git.name_rev'] = MetaDataValue(type=MetaDataType.STRING, string_value=commit.name_rev)
        
        return file_ref


if __name__ == '__main__':

    repo = Repo("/home/sueastside/dev/DAMN/damn-test-files")

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
