import datetime
import glob
import os
import time
import json
import yaml

from access import get_auth


def first_time_setup():
    if not os.path.exists("settings.yaml"):
        settings_dict = {
            "client_config_backend": "settings",
            "client_config": {
                "client_id": None,
                "client_secret": None,
            },
            "save_credentials": True,
            "save_credentials_backend": "file",
            "save_credentials_file": "credentials.json",
            
            "get_refresh_token": True
        }
        with open("settings.yaml", "w") as settings_file:
            yaml.dump(settings_dict, settings_file, default_flow_style=False)
    else:
        with open("settings.yaml", "r") as settings_file:
            settings_dict = yaml.safe_load(settings_file)
    

    print("""
Instructions (sourced from: https://pythonhosted.org/PyDrive/quickstart.html#authentication)

1. Go here https://console.developers.google.com/iam-admin/projects
2. Search for ‘Google Drive API’, select the entry
3. Create a project, select it in the top dropdown, and click ‘Enable’.
4. Select ‘Credentials’ from the left menu. Select configure OAuth Consent Screen.
5. Set it to Internal and fill in Application name (e.g. PyDrive Access)
6. Select `Credentials` again from the left menu. Click ‘+Create Credentials’, select ‘OAuth client ID’.

Select ‘Application type’ to be Web application.
Enter an appropriate name (e.g. PyDrive)
Input http://localhost:8080 for ‘Authorized JavaScript origins’.
Input http://localhost:8080/ for ‘Authorized redirect URIs’.
Click ‘Save’.
Click ‘Download JSON’ on the right side of Client ID to download client_secret_<really long ID>.json.

The downloaded file has all authentication information of your application. Rename the file to “client_secrets.json” and place it in your working directory.

    """)

    while not os.path.exists("client_secrets.json"):
        input("\nHit enter when you have saved client_secrets.json in this folder\n")

    with open("client_secrets.json") as json_file:  
        data = json.load(json_file)

    settings_dict["client_config"]["client_id"] = data["web"]["client_id"]
    settings_dict["client_config"]["client_secret"] = data["web"]["client_secret"]
    # May need to set redirect uris?

    with open("settings.yaml", "w") as settings_file:
        yaml.dump(settings_dict, settings_file, default_flow_style=False)
    
    if not os.path.exists("credentials.json"):
        with open("credentials.json", "w") as credentials_file:
            pass
    
    # instructions to log in


if __name__ == "__main__":
    first_time_setup()

    from access import get_auth

    auth = get_auth()

    print("\nCongrats you are authenticated!\n")
