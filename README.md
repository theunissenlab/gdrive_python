# Google Drive Access via Python (gdrive-access)

Instructions to get started on accessing Google Drive via Python functions.

## Install

* `git clone`

* `cd gdrive_python`

* (from in your favorite virtual environment) `pip install .`

#### First time setup

Run the following script and follow the instructions. Optionally, specify a CREDENTIALS_DIR where gdrive-access will put credential files (defaults to current working directory).

* `python -m gdrive_access.setup_credentials --dir CREDENTIALS_DIR`

### Uninstall

* `pip uninstall gdrive-access`

## Usage

#### Initialize the object and authenticate
```
g = GDriveCommands()
```

#### Set the root google drive directory (should be a folder name in the top level of your google drive)
```
root = g.get_root(ROOTDIR) -> GDRIVE_DIRECTORY
```

#### Access Files
```
g.find(GDRIVE_DIRECTORY, *path_elements) -> GDRIVE_FILE/GDRIVE_DIRECTORY
g.ls(GDRIVE_DIRECTORY, *path_elements) -> list of GDRIVE_FILEs
g.exists(GDRIVE_DIRECTORY, *path_elements) -> bool
```

#### Download Files
```
g.download_file(GDRIVE_FILE, local_path, overwrite=False)
g.download_files([GDRIVE_FILE1, GDRIVE_FILE2, ...], local_folder_path, overwrite=False) 
g.download_folder(GDRIVE_DIRECTORY, local_folder_path) 
```

#### Upload Files/Create Folders
```
g.create_folder(GDRIVE_DIRECTORY, folder_name) -> GDRIVE_DIRECTORY
g.upload_file(local_file_path, GDRIVE_DIRECTORY)
```

## TODO

Have a way to resolve when multiple files have the same name

Make the forced choice of root dir smoother?
