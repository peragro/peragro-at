"""
The MetaDataStore handler.
"""
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
        super(Repository, self).__init__()

    def get_meta_data(self, an_uri, file_descr):
        """
        Get git commit metadata for the specified file.
        """
        commit = self.repo.heads.master.commit
        #path = os.path.relpath(an_uri, self.path)
        #blob = commit.tree/path

        file_descr.metadata['git.author.name'] = MetaDataValue(type=MetaDataType.STRING, string_value=commit.author.name)
        file_descr.metadata['git.author.email'] = MetaDataValue(type=MetaDataType.STRING, string_value=commit.author.email)
        file_descr.metadata['git.message'] = MetaDataValue(type=MetaDataType.STRING, string_value=commit.message)
        file_descr.metadata['git.committer.name'] = MetaDataValue(type=MetaDataType.STRING, string_value=commit.committer.name)
        file_descr.metadata['git.committer.email'] = MetaDataValue(type=MetaDataType.STRING, string_value=commit.committer.email)
        file_descr.metadata['git.name_rev'] = MetaDataValue(type=MetaDataType.STRING, string_value=commit.name_rev)

        file_descr.metadata['git.remotes.origin.url'] = MetaDataValue(type=MetaDataType.STRING, string_value=self.repo.remotes.origin.config_reader.get('url'))

        return file_descr
