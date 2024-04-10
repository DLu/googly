import pathlib
import json

from google.auth.transport.requests import Request
import google.oauth2.credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

DEFAULT_CREDENTIALS_FOLDER = pathlib.Path('~/.config/googly/').expanduser()


class API:
    def __init__(self, name, version, scopes, user_credentials_folder=None, user_credentials_subfolder=None,
                 project_secrets_path='secrets.json',
                 **kwargs):

        # Build Credentials Path
        if user_credentials_folder is None:
            user_credentials_folder = DEFAULT_CREDENTIALS_FOLDER
        elif isinstance(user_credentials_folder, str):  # pragma: no cover
            user_credentials_folder = pathlib.Path(user_credentials_folder)

        if user_credentials_subfolder:
            user_credentials_folder = user_credentials_folder / user_credentials_subfolder

        credentials_path = user_credentials_folder / f'{name}.json'

        creds = None
        if credentials_path.exists():
            # Load dictionary and convert to Credentials object
            creds_d = json.load(open(credentials_path))

            cred_scopes = creds_d.get('scopes', [])
            if cred_scopes == scopes:
                creds = google.oauth2.credentials.Credentials.from_authorized_user_info(creds_d)

        if not creds or not creds.valid:  # pragma: no cover
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(project_secrets_path, scopes)
                creds = flow.run_local_server()

            # Convert credentials object to dictionary and write to file
            json_s = creds.to_json()
            credentials_path.parent.mkdir(exist_ok=True, parents=True)
            with open(credentials_path, 'w') as f:
                f.write(json_s)

        self.service = build(name, version, credentials=creds, **kwargs)
