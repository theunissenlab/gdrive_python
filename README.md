# Google Drive Access via Python
Instructions to get started on accessing Google Drive via Python functions

## Files

`setup_gdrive.py` is a script for initial setup to acquire credential files from Google Drive

`access.py` contains the Python object used for communicating with Google Drive's API

## Setup

* Install PyDrive (`pip install -r requirements.txt`)

* Run `python setup_gdrive.py`. Follow the instructions that involve creating a Google Cloud project and creating client credentials, and downloading a `client_secrets.json` file)


## Usage
```
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
```
