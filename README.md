# Google Drive Access via Python (gdrive-access)

Instructions to get started on accessing Google Drive via Python functions.

## Install

```bash
# Optional: activate your virtual environment first
git clone https://github.com/theunissenlab/gdrive_python.git
cd gdrive_python
pip install .
```

#### First time setup

Run the following script and follow the instructions. Optionally, specify a CREDENTIALS_DIR where gdrive-access will put credential files (defaults to current working directory).

```bash
python -m gdrive_access.setup_credentials --dir CREDENTIALS_DIR
```

## Uninstall
```
pip uninstall gdrive-access
```

## Usage

#### Import the GDriveCommands class

```python
from gdrive_access import GDriveCommands
```

#### Initialize the object and authenticate
```python
g = GDriveCommands()
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
g.download_folder(GDRIVE_DIRECTORY, local_folder_path) 
```

#### Upload Files/Create Folders
```python
g.create_folder(GDRIVE_DIRECTORY, folder_name)  # -> GDRIVE_DIRECTORY
g.upload_file(local_file_path, GDRIVE_DIRECTORY)
```

## TODO

Have a way to resolve when multiple files have the same name

Make the forced choice of root dir smoother?
