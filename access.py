import datetime
import glob
import os
import time
import json
import yaml

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive


def get_auth():
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    return gauth


class NotFoundError(Exception):
    """Item not Found"""


class GDriveCommands(object):
    """
    Access google drive with methods

    Setup
    =====
    # Initialize the object and authenticate
    g = GDriveCommands()

    # Set the root google drive directory (should be a folder name in the top
    # level of your google drive)
    root = g.get_root(ROOTDIR)

    Access Files
    ============
    g.search(GDRIVE_DIRECTORY, filename) -> GDRIVE_FILE
    g.locate(root, *path_elements) -> GDRIVE_FILE
    g.ls(GDRIVE_DIRECTORY) -> GDRIVE_FILELIST
    g.exists(root, *path_elements) -> bool

    Download Files
    ==============
    g.download_file(GDRIVE_FILE, local_path, overwrite=False)
    g.download_files([GDRIVE_FILE1, GDRIVE_FILE2, ...], local_folder_path, overwrite=False) 
    g.download_folder(GDRIVE_DIRECTORY, local_folder_path) 

    Upload Files/Create Folders
    ===========================
    g.create_folder(GDRIVE_DIRECTORY, folder_name)
    g.upload_file(local_file_path, GDRIVE_DIRECTORY)
    """
    def __init__(self):
        self.drive = GoogleDrive(self._get_auth())
        
    def get_root(self, folder_name, shared=False):
        """Get the root directory to start queries from

        Params
        ======
        folder_name: Name of folder to search for
        shared (default=False): If true, only searches for folders in "Shared with Me"
        """
        if shared is False:
            result_list = self.drive.ListFile({
                "q": "title = '{}'".format(folder_name)
            }).GetList()
            if len(result_list) > 1:
                print("Warning: Located {} files by name {}. Selecting the first one".format(
                    len(result_list), folder_name
                ))
            return result_list[0]
        else:
            return self.drive.ListFile({
                "q": "title = '{}' and sharedWithMe".format(folder_name)
            }).GetList()[0]
    
    def _get_auth(self):
        gauth = GoogleAuth()
        gauth.LocalWebserverAuth()
        return gauth

    def search(self, dir, filename):
        """Look for a filename in google drive directory

        Params
        dir: a str name of the Google Drive directory to search in
        filename: the str name of the file or directory to search for

        Returns:
            PyDrive object representing the file being searched for
        """
        time.sleep(0.01)
        file_list = self.drive.ListFile({
            "q": "title = '{}' and '{}' in parents and "
                 "trashed = false".format(filename, dir["id"])
        }).GetList()
        if not len(file_list):
            raise NotFoundError("{}/{} not found".format(dir["title"], filename))
        return file_list[0]
    
    def locate(self, root, *dirnames):
        """Look for a specific path in google drive directory
        
        Params
        root: the root directory to start looking from
        *dirnames: each individual path element
        """
        result = root
        for dirname in dirnames:
            result = self.search(result, dirname)
        return result
    
    def ls(self, dir):
        time.sleep(0.01)
        return self.drive.ListFile({
            "q": "'{}' in parents and trashed = false".format(dir["id"])
        }).GetList()
    
    def exists(self, root, *dirnames):
        try:
            self.locate(root, *dirnames)
        except NotFoundError:
            return False
        else:
            return True
            
    def download_file(self, gdrive_file, download_to_path, overwrite=False):
        """Download a file from google drive

        Params
        gdrive_file (pydrive file): file to download
        download_to_path (str): location on local filesystem to download data
        """
        if os.path.isdir(download_to_path):
            download_to_path = os.path.join(download_to_path, gdrive_file["title"])
        if os.path.exists(download_to_path) and not overwrite:
            return
            
        time.sleep(0.01)
        gdrive_file.GetContentFile(download_to_path)
    
    def create_folder(self, create_in, folder_name, return_if_exists=True):
        """Create a folder in google drive
        
        Params
        create_in (pydrive object): the folder to create a new folder in on google drive (e.g. the output
            of create_folder() or locate())
        folder_name (string): the name of the new folder to create
        return_if_exists (bool, default True): return the existing folder if it already exists on google
            drive. If set to False, will raise an error if the folder already exists.
        """
        if self.exists(create_in, folder_name):
            if return_if_exists:
                return self.locate(create_in, folder_name)
            else:
                raise Exception("Folder already exists")

        new_folder = drive.CreateFile({
            "title": folder_name, 
            "parents":  [{"id": create_in["id"]}], 
            "mimeType": "application/vnd.google-apps.folder"
        })
        time.sleep(0.01)
        new_folder.Upload()
        return new_folder

    def upload_file(self, local_file_path, upload_to, uploaded_name=None, overwrite=False):
        """Uploads a file to a gdrive folder
        
        Params
        local_file_path (string): the path to the file on your computer
        upload_to (pydrive object): pydrive folder object (e.g. the output of create_folder() or locate())
        uploaded_name (string, optional): name to call the uploaded file in google drive. Uses the files actual
            name if left as None. Note that google drive allows for multiple files with the same name!
        overwrite (bool, default False): set to True to upload it no matter what. If false, won't upload if
            a file by the same name already exists on google drive. (Note that google drive allows for multiple
            files of the same name, so it wont actually overwrite even if set to True)
        """
        filename = os.path.basename(local_file_path)
        if not overwrite:
            if self.exists(upload_to, filename):
                raise Exception("File already exists, can't overwrite with overwrite=False")

        new_file = drive.CreateFile({
            "parents": [{"id": upload_to["id"]}],
            "title": uploaded_name or filename,
        })
        new_file.SetContentFile(local_file_path)
        time.sleep(0.01)
        new_file.Upload()

    def download_files(self, gdrive_files, download_to_path, overwrite=False):
        """Download files from google drive

        Params
        gdrive_files (list of pydrive files): files to download (e.g. the output from ls() or
            a list of ouputs from locate())
        download_to_path (str): location on local filesystem to download data
        """
        if not os.path.exists(download_to_path):
            os.makedirs(download_to_path)

        if not os.path.isdir(download_to_path):
            raise Exception("download_to_path must be an existing directory")
        
        for file in gdrive_files:
            self.download_file(file, download_to_path, overwrite=overwrite)

    def download_folder(self, gdrive_folder, download_to_path):
        """Download files from google drive

        Params
        gdrive_files (list of pydrive files): files to download
        download_to_path (str): location on local filesystem to download data
        """
        if not os.path.exists(download_to_path):
            os.makedirs(download_to_path)

        for f in self.ls(gdrive_folder):
            time.sleep(0.01)
            if f["mimeType"] == "application/vnd.google-apps.folder":
                self.download_folder(f, os.path.join(download_to_path, f["title"]))
            else:
#                 print("Downloading {}".format(f["title"]))
                self.download_file(f, os.path.join(download_to_path, f["title"]))

