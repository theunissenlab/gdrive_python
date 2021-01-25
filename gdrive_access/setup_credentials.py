import os
import json
import yaml
from pathlib import Path


def first_time_setup(credential_location="."):
    settings_path = os.path.join(credential_location, "settings.yaml")
    client_secrets_path = os.path.join(credential_location, "client_secrets.json")
    credentials_json_path = os.path.join(credential_location, "credentials.json")

    if not os.path.exists(settings_path):
        settings_dict = {
            "client_config_backend": "settings",
            "client_config": {
                "client_id": None,
                "client_secret": None,
            },
            "save_credentials": True,
            "save_credentials_backend": "file",
            "save_credentials_file": credentials_json_path,
            "get_refresh_token": True
        }
        with open(settings_path, "w") as settings_file:
            yaml.dump(settings_dict, settings_file, default_flow_style=False)
    else:
        with open(settings_path, "r") as settings_file:
            settings_dict = yaml.safe_load(settings_file)
    

    print("""
Instructions (based on: https://pythonhosted.org/PyDrive/quickstart.html#authentication)

    1. Go here https://console.developers.google.com/iam-admin/projects

    2. Search for "Google Drive API", select the entry

    3. Create a project, select it in the top dropdown, and click "Enable".

    4. Select "Credentials" from the left menu. Select configure OAuth Consent Screen.

    5. Set it to Internal and fill in Application name (e.g. PyDrive Access)

    6. Select `Credentials` again from the left menu. Click "+Create Credentials", select "OAuth client ID".

      You can choose now to log in with a web browser (log in with Google) or in the command line.

      For web browser login:
        Select "Application type" to be Web application.
        Enter an appropriate name (e.g. gdrive-access)
        Input http://localhost:8080 for "Authorized JavaScript origins".
        Input http://localhost:8080/ for "Authorized redirect URIs".
      For command line login:
        Select "Application type" to be Desktop.
        Enter an appropriate name (e.g. gdrive-access)

    7. Click "Save".

    8. Click "Download JSON" on the right side of Client ID to download client_secret_<really long ID>.json.


    The downloaded file has all authentication information of your application. Rename the file to "client_secrets.json" and place it in {}.
    """.format("your working directory" if credential_location == "." else credential_location))

    while not os.path.exists(client_secrets_path):
        input("Follow the above instructions to get Google Drive client credentials.\n"
            "Hit enter when you have saved {} (Ctrl-C to abort)\n".format(client_secrets_path))

    with open(client_secrets_path, "r") as json_file:  
        data = json.load(json_file)

    if "web" in data:
        settings_dict["client_config"]["client_id"] = data["web"]["client_id"]
        settings_dict["client_config"]["client_secret"] = data["web"]["client_secret"]
    elif "installed" in data:
        settings_dict["client_config"]["client_id"] = data["installed"]["client_id"]
        settings_dict["client_config"]["client_secret"] = data["installed"]["client_secret"]
    else:
        raise Exception("Unexpected key found in client_secrets.json. Expected web or installed, but"
                " got {}. Maybe you didn't choose Application Type 'Web Application' or "
                "'Desktop'?".format(list(data.keys())))

    with open(settings_path, "w") as settings_file:
        yaml.dump(settings_dict, settings_file, default_flow_style=False)
    
    Path(credentials_json_path).touch()


if __name__ == "__main__":
    import argparse
    from .access import get_auth

    parser = argparse.ArgumentParser(description="Setup Google Drive API credentials")
    parser.add_argument("--dir", type=str, default=".", help="Directory to store credentials")
    args = parser.parse_args()

    first_time_setup(credential_location=args.dir)

    settings_path = os.path.join(args.dir, "settings.yaml")

    with open(settings_path, "r") as settings_file:
        settings_dict = yaml.safe_load(settings_file)

    auth = get_auth(settings_path, webauth="web" in settings_dict)

    print("\nCongrats you are authenticated!\n")
