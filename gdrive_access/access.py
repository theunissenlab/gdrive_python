import enum
import hashlib
import logging
import glob
import os
import time

from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from pydrive2.files import GoogleDriveFile

from .display import *
from .errors import CredentialsNotFound, FileExists, FolderExists, MultipleFilesError, NotFoundError


def get_auth(settings_file="settings.yaml", webauth=False):
    gauth = GoogleAuth(settings_file=settings_file)
    if webauth:
        gauth.LocalWebserverAuth()
    else:
        gauth.CommandLineAuth()
    return gauth


def _md5(file_):
    with open(file_, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


logger = logging.getLogger()
logging.basicConfig()


class RootDrive(GoogleDriveFile):
    """A dummy object representing the root directory location"""
    _dict = {
        "id": "root",
        "mimeType": None,
    }

    def __getitem__(self, key):
        if key not in self._dict:
            raise RuntimeError("Can only access {} of the RootDrive dummy object".format(list(self._dict.keys())))
        else:
            return self._dict[key]


class GDriveCommands(object):
    """
    Access google drive with methods

    Setup
    =====
    # Initialize the object and authenticate
    g = GDriveCommands()

    Get root directory (not necessary)
    ==================================
    g.ls_root() -> list of GDRIVE_FILES
    root = g.get_root(ROOTDIR) -> GDRIVE_DIRECTORY

    Access Files
    ============
    # These functions can all optionally start with a google drive directory object
    # (GoogleDriveFile with mimeType=application/vnd.google-apps.folder). They start
    # from the root otherwise.
    g.find(GDRIVE_DIRECTORY, *path_elements) -> GDRIVE_FILE/GDRIVE_DIRECTORY
    g.find(*path_elements) -> GDRIVE_FILE/GDRIVE_DIRECTORY
    g.ls(GDRIVE_DIRECTORY, *path_elements) -> list of GDRIVE_FILEs
    g.ls(*path_elements) -> list of GDRIVE_FILEs
    g.exists(GDRIVE_DIRECTORY, *path_elements) -> bool
    g.exists(*path_elements) -> bool

    Download Files
    ==============
    g.download_file(GDRIVE_FILE, local_path, overwrite=g.Overwrite.NEVER)
    g.download_files([GDRIVE_FILE1, GDRIVE_FILE2, ...], local_folder_path, overwrite=g.Overwrite.NEVER)
    g.download_folder(GDRIVE_DIRECTORY, local_folder_path)

    Overwrite Modes
    ===============
    g.Overwrite.NEVER
    g.Overwrite.ALWAYS
    g.Overwrite.ON_FILESIZE_CHANGE
    g.Overwrite.ON_MD5_CHECKSUM_CHANGE

    Upload Files/Create Folders
    ===========================
    g.create_folder(GDRIVE_DIRECTORY, folder_name)
    g.upload_file(local_file_path, GDRIVE_DIRECTORY)
    """
    class Overwrite(enum.Enum):
        NEVER = 0
        ALWAYS = 1
        ON_FILESIZE_CHANGE = 2
        ON_MD5_CHECKSUM_CHANGE = 3

    def __init__(self, settings_file="settings.yaml", log_level=logging.INFO):
        self.drive = GoogleDrive(self._get_auth(settings_file))

        self.logger = logging.getLogger("gdrive_access.access.GDriveCommands")
        self.logger.setLevel(log_level)

    def _split_root_and_path(self, *path):
        """Split a list of path elements into the root and string path

        Returns a tuple of (root: GoogleDriveFile, path: List[str])
        """
        if not len (path) or isinstance(path[0], str):
            return RootDrive(), path

        if not isinstance(path[0], GoogleDriveFile):
            raise ValueError("The path must either be all strings or start with a GoogleDriveFile")

        return path[0], path[1:]

    def get_root(self, folder_name: str, shared: bool=False):
        """Get the root directory to start queries from

        Params
        ======
        folder_name: Name of folder to search for
        shared (default=False): If true, only searches for folders in "Shared with Me"

        Returns:
            pydrive.GoogleDriveFile object of the root location
        """
        if shared is False:
            result_list = PyDriveListWrapper(self.drive.ListFile({
                "q": "title = '{}'".format(folder_name)
            }).GetList())
        else:
            result_list = PyDriveListWrapper(self.drive.ListFile({
                "q": "title = '{}' and sharedWithMe".format(folder_name)
            }).GetList())

        if len(result_list) > 1:
            logger.warning("Located {} files by name {}. Selecting the first one".format(
                len(result_list), folder_name
            ))
        elif len(result_list) == 0:
            raise NotFoundError("{}older '{}' not found. Use ls() or "
                "ls_root() to see potential top level folders".format("Shared f" if shared else "F", folder_name))

        return result_list[0]

    def _get_auth(self, settings_file="settings.yaml"):
        if not os.path.exists(settings_file):
            raise CredentialsNotFound("Settings file {} was not found.\n"
                    "Please fix the path to the settings.yaml file or set up credentials with\n"
                    "'python -m gdrive_access.setup_credentials --dir CREDENTIALDIR'".format(settings_file))
        try:
            return get_auth(settings_file)
        except FileNotFoundError:
            raise CredentialsNotFound("Credentials were not found; Perhaps you should try running\n"
                    "'python -m gdrive_access.setup_credentials --dir CREDENTIALDIR'\n"
                    "or fixing the location of the credentials location set in {}".format(settings_file))

    def _to_id(self, file_: GoogleDriveFile):
        """Return the id of the object unless it is a shortcut, then find the true id.
        """
        if file_["mimeType"] == "application/vnd.google-apps.shortcut":
            file_.FetchMetadata(fields="shortcutDetails")
            return file_["shortcutDetails"]["targetId"]
        else:
            return file_["id"]

    def _check_if_overwrite_okay(
            self,
            overwrite: Overwrite,
            gdrive_file: GoogleDriveFile,
            download_to_path: str
            ):
        if overwrite is self.Overwrite.NEVER:
            return False
        elif overwrite is self.Overwrite.ALWAYS:
            return True
        elif overwrite is self.Overwrite.ON_FILESIZE_CHANGE:
            local_filesize = os.path.getsize(download_to_path)
            gdrive_filesize = gdrive_file.metadata["fileSize"]
            return local_filesize != gdrive_filesize
        elif overwrite is self.Overwrite.ON_MD5_CHECKSUM_CHANGE:
            local_checksum = _md5(download_to_path)
            gdrive_checksum = gdrive_file.metadata["md5Checksum"]
            return local_checksum != gdrive_checksum

    def _find_one_level(self, dir: GoogleDriveFile, filename: str):
        """Look for a filename in google drive directory

        Params
        dir: a GoogleDriveFile representing a folder to locate the file in
        filename: the str name of the file or directory to look for

        Returns:
            pydrive.GoogleDriveFile object representing the file being searched for
        """
        time.sleep(0.01)
        file_list = PyDriveListWrapper(self.drive.ListFile({
            "q": "title = '{}' and '{}' in parents and "
                 "trashed = false".format(filename, self._to_id(dir))
        }).GetList())

        if not len(file_list):
            raise NotFoundError("{}/{} not found".format(dir["title"], filename))

        if len(file_list) > 1:
            raise MultipleFilesError

        return file_list[0]

    def find(self, *path):
        """Look for a specific path in google drive directory

        Params
        *path: each individual path element. The first one can optionally be a
            GoogleDriveFile representing a directory to start from

        Returns:
            pydrive.GoogleDriveFile object representing the file being searched for
        """
        root, path = self._split_root_and_path(*path)
        result = root
        for path_element in path:
            result = self._find_one_level(result, path_element)
        return result

    def ls(self, *path):
        id_ = self._to_id(self.find(*path))
        time.sleep(0.01)
        return PyDriveListWrapper(self.drive.ListFile({
            "q": "'{}' in parents and trashed = false".format(id_)
        }).GetList())

    def ls_root(self):
        return self.ls()

    def exists(self, *path):
        try:
            self.find(*path)
        except NotFoundError:
            return False
        else:
            return True

    def download_file(self, gdrive_file, download_to_path, overwrite: Overwrite=Overwrite.NEVER):
        """Download a file from google drive

        Params
        gdrive_file (pydrive file): file to download
        download_to_path (str): location on local filesystem to download data
        overwrite (GDriveCommands.Overwrite, default=NEVER): Overwrite mode
        """
        if gdrive_file["mimeType"] == "application/vnd.google-apps.folder":
            return self.download_folder(gdrive_file, download_to_path, overwrite=overwrite)

        if os.path.isdir(download_to_path):
            download_to_path = os.path.join(download_to_path, gdrive_file["title"])
        if os.path.exists(download_to_path) and not self._check_if_overwrite_okay(overwrite, gdrive_file, download_to_path):
            return

        time.sleep(0.01)
        gdrive_file.GetContentFile(download_to_path)

    def create_folder(self, create_in, folder_name, return_if_exists=True):
        """Create a folder in google drive

        Params
        create_in (pydrive object): the folder to create a new folder in on google drive (e.g. the output
            of create_folder() or find())
        folder_name (string): the name of the new folder to create
        return_if_exists (bool, default True): return the existing folder if it already exists on google
            drive. If set to False, will raise an error if the folder already exists.
        """
        if self.exists(create_in, folder_name):
            if return_if_exists:
                return self.find(create_in, folder_name)
            else:
                raise FolderExists("Folder already exists")

        new_folder = self.drive.CreateFile({
            "title": folder_name,
            "parents":  [{"id": self._to_id(create_in)}],
            "mimeType": "application/vnd.google-apps.folder"
        })
        time.sleep(0.01)
        new_folder.Upload()
        return new_folder

    def upload_file(self, local_file_path, upload_to, uploaded_name=None, overwrite: Overwrite=Overwrite.ON_MD5_CHECKSUM_CHANGE):
        """Uploads a file to a gdrive folder

        Params
        local_file_path (string): the path to the file on your computer
        upload_to (pydrive object): pydrive folder object (e.g. the output of create_folder() or find())
        uploaded_name (string, optional): name to call the uploaded file in google drive. Uses the files actual
            name if left as None. Note that google drive allows for multiple files with the same name!
        overwrite (GDriveCommands.Overwrite, default=ON_MD5_CHECKSUM_CHANGE): set to True to upload it no matter what.
            If false, won't upload if a file by the same name already exists on google drive.
            (Note that google drive allows for multiple files of the same name, so it wont actually overwrite
            even if it is set)
        """
        if uploaded_name is None:
            filename = os.path.basename(local_file_path)
        else:
            filename = uploaded_name

        self.logger.info("Uploading {} to {}".format(local_file_path, upload_to["title"]))

        if self.exists(upload_to, filename):
            existing_file = self.find(upload_to, filename)
            if not self._check_if_overwrite_okay(overwrite, existing_file, local_file_path):
                self.logger.info("{} already exists at {}".format(local_file_path, upload_to["title"]))
                raise FileExists("File already exists on google drive, can't overwrite with overwrite={}".format(overwrite))

        new_file = self.drive.CreateFile({
            "parents": [{"id": self._to_id(upload_to)}],
            "title": uploaded_name or filename,
        })
        new_file.SetContentFile(local_file_path)
        time.sleep(0.01)
        new_file.Upload()
        self.logger.info("Uploaded {} to {}".format(local_file_path, upload_to["title"]))

    def upload_folder(self, local_folder_path, upload_to, uploaded_name=None, overwrite_file: Overwrite=Overwrite.ON_MD5_CHECKSUM_CHANGE, overwrite_folder=False):
        """Upload a local folder and its contents to google drive

        Attempts to preserve folder structure. overwrite_folder False will not attempt to write at a folder that exists
        """
        if uploaded_name is None:
            foldername = os.path.basename(local_folder_path)
        else:
            foldername = uploaded_name

        gdrive_folder = self.create_folder(upload_to, foldername, return_if_exists=overwrite_folder)

        for content in glob.glob(os.path.join(local_folder_path, "*")):
            if os.path.isdir(content):
                self.upload_folder(content, gdrive_folder)
            else:
                try:
                    self.upload_file(content, gdrive_folder, overwrite=overwrite_file)
                except FileExists:
                    pass

    def download_files(self, gdrive_files, download_to_path, overwrite: Overwrite=Overwrite.NEVER):
        """Download files from google drive

        Params
        gdrive_files (list of pydrive files): files to download (e.g. the output from ls() or
            a list of ouputs from find())
        download_to_path (str): location on local filesystem to download data
        overwrite (GDriveCommands.Overwrite, default=NEVER): Overwrite mode
        """
        if not os.path.exists(download_to_path):
            os.makedirs(download_to_path)

        if not os.path.isdir(download_to_path):
            raise Exception("download_to_path must be an existing directory")

        for file in gdrive_files:
            self.download_file(file, download_to_path, overwrite=overwrite)

    def download_folder(self, gdrive_folder, download_to_path, overwrite: Overwrite=Overwrite.NEVER):
        """Download files from google drive

        Params
        gdrive_files (list of pydrive files): files to download
        download_to_path (str): location on local filesystem to download data
        """
        download_to_path = os.path.join(download_to_path, gdrive_folder["title"])
        if not os.path.exists(download_to_path):
            os.makedirs(download_to_path)

        for f in self.ls(gdrive_folder):
            time.sleep(0.01)
            if f["mimeType"] == "application/vnd.google-apps.folder":
                self.download_folder(
                        f,
                        os.path.join(download_to_path, f["title"]),
                        overwrite=overwrite)
            else:
                self.download_file(
                        f,
                        os.path.join(download_to_path, f["title"]),
                        overwrite=overwrite)


__all__ = [
    "get_auth",
    "GDriveCommands"
]
