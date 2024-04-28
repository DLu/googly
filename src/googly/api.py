import pathlib
import json

from .util import destring

from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
import google.oauth2.credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

DEFAULT_CREDENTIALS_FOLDER = pathlib.Path('~/.config/googly/').expanduser()


class API:
    def __init__(self, name, version, scopes, project_credentials_path='secrets.json',
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

        creds = None
        run_flow = True
        write_creds = False

        if not isinstance(scopes, list):
            scopes = list(scopes)

        if credentials_path.exists():
            # Load dictionary and convert to Credentials object
            creds_d = json.load(open(credentials_path))

            cred_scopes = creds_d.get('scopes', [])
            if set(cred_scopes) == set(scopes):  # ignore order
                creds = google.oauth2.credentials.Credentials.from_authorized_user_info(creds_d)

                if creds.valid:
                    run_flow = False
                elif creds.expired and creds.refresh_token:  # pragma: no cover
                    try:
                        creds.refresh(Request())
                        run_flow = False
                        write_creds = True
                    except RefreshError as e:
                        creds = None
                        print(f'Cannot refresh token for {name}: {e.args[0]}')

        if run_flow:  # pragma: no cover
            flow = InstalledAppFlow.from_client_secrets_file(project_credentials_path, scopes)
            creds = flow.run_local_server()
            write_creds = True

        if write_creds:  # pragma: no cover
            # Convert credentials object to dictionary and write to file
            json_s = creds.to_json()
            credentials_path.parent.mkdir(exist_ok=True, parents=True)
            with open(credentials_path, 'w') as f:
                f.write(json_s)

        self.service = build(name, version, credentials=creds, **kwargs)

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

            if interpret:
                yield from destring(results[result_keyword])
            else:
                yield from results[result_keyword]
            seen += len(results[result_keyword])
            next_token = results.get('nextPageToken')

            if not next_token or (max_results and seen >= max_results):
                break
