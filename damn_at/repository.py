"""
The MetaDataStore handler.
"""
from git import Repo

from damn_at.pluginmanager import IRepository


class Repository(IRepository):
    """
    A GIT Repository.
    """
    def __init__(self, path):
        self.path = path
        self.repo = Repo(path)
        
    def get_meta_data(self, an_uri, a_file_ref):
        """
        """
        commit = repo.heads.master.commit
        path = an_uri.replace(self.path, '')
        blob = c.tree/path
        
        raise NotImplementedError("'get_meta_data' must be reimplemented by %s" % self)


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
