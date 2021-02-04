class CredentialsNotFound(Exception):
    """Credential files not found"""


class MultipleFilesError(Exception):
    """More than one file matching the name given"""


class NotFoundError(Exception):
    """Item not Found"""


class FileExists(Exception):
    """File already exists"""


class FolderExists(Exception):
    """Folder already exists"""
