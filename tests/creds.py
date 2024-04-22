import os
import pathlib
import json
from googly.api import DEFAULT_CREDENTIALS_FOLDER


def get_credentials():
    """Set up the test environment

    The environment variables are used for GitHub Actions
    """

    secrets_path = pathlib.Path('secrets.json')
    subfolder = 'googly'

    if 'GOOGLY_CREDENTIALS' in os.environ:
        creds = json.loads(os.environ['GOOGLY_CREDENTIALS'])

        if 'secrets' in creds and not secrets_path.exists():
            with open(secrets_path, 'w') as f:
                f.write(creds['secrets'])

        for service, contents in creds['services'].items():
            credentials_path = DEFAULT_CREDENTIALS_FOLDER / subfolder / f'{service}.json'
            if credentials_path.exists():
                continue

            credentials_path.parent.mkdir(exist_ok=True, parents=True)
            with open(credentials_path, 'w') as f:
                f.write(json.dumps(contents))

    return {
        'user_credentials_subfolder': subfolder,
        'project_secrets_path': secrets_path,
    }


def collect_creds(services, include_secrets=False):
    """Load all the credentials into one datastructure for easy GitHub test integration"""
    creds = {'services': {}}
    if include_secrets:
        creds['secrets'] = json.load(open('secrets.json'))

    credentials_path = DEFAULT_CREDENTIALS_FOLDER / 'googly'
    remaining = set(services)
    for filepath in credentials_path.glob('*.json'):
        service = filepath.stem
        if services:
            if service not in services:
                continue
            else:
                remaining.remove(filepath.stem)

        creds['services'][service] = json.load(open(filepath))

    if remaining:
        raise RuntimeError(f'Cannot find credentials for {", ".join(services)}')

    return creds


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('services', metavar='service', nargs='*')
    args = parser.parse_args()

    print(json.dumps(collect_creds(args.services)))
