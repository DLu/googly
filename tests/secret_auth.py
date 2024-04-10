import os
import pathlib
from googly.api import DEFAULT_CREDENTIALS_FOLDER


def get_secrets():
    """Set up the test environment

    The environment variables are used for GitHub Actions
    """

    secrets_path = pathlib.Path('secrets.json')
    if 'SECRETSJSON' in os.environ and not secrets_path.exists():
        with open(secrets_path, 'w') as f:
            f.write(os.environ['SECRETSJSON'])

    subfolder = 'googly'
    for k, v in os.environ.items():
        if not k.endswith('_CREDS'):
            continue
        name = k.split('_')[0].lower()

        credentials_path = DEFAULT_CREDENTIALS_FOLDER / subfolder / f'{name}.json'
        if credentials_path.exists():
            continue

        credentials_path.parent.mkdir(exist_ok=True, parents=True)
        with open(credentials_path, 'w') as f:
            f.write(v)

    return {
        'user_credentials_subfolder': subfolder,
        'project_secrets_path': secrets_path,
    }
