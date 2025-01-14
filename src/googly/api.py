import pathlib
import json

from .util import destring

from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
import google.oauth2.credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

DEFAULT_CREDENTIALS_FOLDER = pathlib.Path('~/.config/googly/').expanduser()
CONFIG_PATH = DEFAULT_CREDENTIALS_FOLDER / 'config.json'


class API:
    def __init__(self, name, version, scopes, project_credentials_path=None,
                 user_credentials_folder=None, user_credentials_subfolder=None,
                 **kwargs):

        # Build Credentials Path
        if user_credentials_folder is None:
            user_credentials_folder = DEFAULT_CREDENTIALS_FOLDER
        elif isinstance(user_credentials_folder, str):  # pragma: no cover
            user_credentials_folder = pathlib.Path(user_credentials_folder)

        if user_credentials_subfolder:
            user_credentials_folder = user_credentials_folder / user_credentials_subfolder

        credentials_path = user_credentials_folder / f'{name}.json'

        self.creds = None
        run_flow = True
        write_creds = False

        if not isinstance(scopes, list):
            scopes = list(scopes)

        if credentials_path.exists():
            # Load dictionary and convert to Credentials object
            creds_d = json.load(open(credentials_path))

            cred_scopes = creds_d.get('scopes', [])
            if set(cred_scopes) == set(scopes):  # ignore order
                self.creds = google.oauth2.credentials.Credentials.from_authorized_user_info(creds_d)

                if self.creds.valid:
                    run_flow = False
                elif self.creds.expired and self.creds.refresh_token:  # pragma: no cover
                    try:
                        self.creds.refresh(Request())
                        run_flow = False
                        write_creds = True
                    except RefreshError as e:
                        self.creds = None
                        print(f'Cannot refresh token for {name}: {e.args[0]}')

        if run_flow:  # pragma: no cover
            if CONFIG_PATH.exists():
                config = json.load(open(CONFIG_PATH))
                if 'project_credentials_path' in config:
                    project_credentials_path = config['project_credentials_path']

            if not project_credentials_path:
                project_credentials_path = 'secrets.json'

            if user_credentials_subfolder:
                user_s = f' for user {user_credentials_subfolder}'
            else:
                user_s = ''
            prompt_message = f'To authorize the {name} API{user_s}, please visit this URL: {{url}}'

            flow = InstalledAppFlow.from_client_secrets_file(project_credentials_path, scopes)

            # When running multiple authentications in a row, the local server
            # sometimes takes a few minutes to stop, resulting in
            # OSError: [Errno 98] Address already in use
            # We iterate over a few ports here to avoid that problem
            for i in range(15):  # 15 ports oughta be enough for anyone
                try:
                    self.creds = flow.run_local_server(
                        port=8080 + i,
                        authorization_prompt_message=prompt_message
                    )
                    break
                except OSError:
                    pass
            else:
                raise RuntimeError('Unable to authenticate :(')
            write_creds = True

        if write_creds:  # pragma: no cover
            # Convert credentials object to dictionary and write to file
            json_s = self.creds.to_json()
            credentials_path.parent.mkdir(exist_ok=True, parents=True)
            with open(credentials_path, 'w') as f:
                f.write(json_s)

        self.service = build(name, version, credentials=self.creds, **kwargs)

    def get_paged_result(self, api_method, result_keyword,
                         max_results=0, max_results_param_name='pageSize',
                         interpret=False,
                         **kwargs):
        next_token = None
        seen = 0
        if max_results:
            kwargs[max_results_param_name] = max_results

        while True:
            results = api_method(
                pageToken=next_token,
                **kwargs,
            ).execute()

            items = results.get(result_keyword, [])

            if interpret:
                yield from destring(items)
            else:
                yield from items
            seen += len(items)
            next_token = results.get('nextPageToken')

            if not next_token or (max_results and seen >= max_results):
                break
