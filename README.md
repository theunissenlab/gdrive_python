# Google Drive Access via Python (gdrive-access)

gdrive-access is a simplified set of Python functions for navigating Google Drive folders and uploading/downloading files, built on PyDrive. To get set up, you will need to install gdrive-access and run the "setup credentials" script (`python -m gdrive_access.setup_credentials --dir CREDENTIALS_DIR`) to give it permission to access your Google Drive through the Google Drive web API.

## 1 Install

gdrive-access should work on any version of Python 3 but has only been tested on Python 3.9. It is recommended to install it in a virtual environment.

```bash
pip install git+https://github.com/theunissenlab/gdrive_python.git@v0.0.3
```

### First time credentials setup

Run the following script and follow the instructions carefully. Optionally, specify a CREDENTIALS_DIR where gdrive-access will put credential files (defaults to current working directory). It will create files `settings.yaml` and `credentials.json` in that directory. You will also create a file in it called `client_secrets.json` during the setup process.

```bash
python -m gdrive_access.setup_credentials --dir CREDENTIALS_DIR
```

## 2 Usage

#### Import the GDriveCommands class

```python
from gdrive_access import GDriveCommands
```

#### Initialize the object and authenticate

Alternatively, specify the custom path to [`CREDENTIALS_DIR/settings.yaml`](https://github.com/theunissenlab/gdrive_python#first-time-credentials-setup) if you did not use the default during setup.
```python
g = GDriveCommands("settings.yaml")
```

#### Set the root google drive directory (should be a folder name in the top level of your google drive)
```python
root = g.get_root(ROOTDIR)  # -> GDRIVE_DIRECTORY
```

#### Access Files
```python
g.find(GDRIVE_DIRECTORY, *path_elements)  # -> GDRIVE_FILE/GDRIVE_DIRECTORY
g.ls(GDRIVE_DIRECTORY, *path_elements)  # -> list of GDRIVE_FILEs
g.exists(GDRIVE_DIRECTORY, *path_elements)  # -> bool
```

#### Download Files
```python
g.download_file(GDRIVE_FILE, local_path, overwrite=False)
g.download_files([GDRIVE_FILE1, GDRIVE_FILE2, ...], local_folder_path, overwrite=False) 
g.download_folder(GDRIVE_DIRECTORY, local_folder_path, overwrite=False) 
```

#### Upload Files/Create Folders
```python
g.create_folder(GDRIVE_DIRECTORY, folder_name)  # -> GDRIVE_DIRECTORY
g.upload_file(local_file_path, GDRIVE_DIRECTORY)
```

## 3 Uninstall
```shell
pip uninstall gdrive-access
```

## 4 TODO

* Have a way to resolve when multiple files have the same name?
