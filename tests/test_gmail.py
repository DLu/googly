from googly import GMailAPI
from creds import get_credentials


def test_basic_access():
    api = GMailAPI(**get_credentials())

    threads = api.get_threads('in:anywhere')

    assert threads

    for thread_id, thread in threads.items():
        if thread_id != '18ec87a5013ae2d9':
            continue
        assert len(thread) == 2

        msg = api.get_message(thread[-1]['id'])
        assert msg['snippet'].startswith('Lorem ipsum')

        headers = {a['name']: a['value'] for a in msg['payload']['headers']}
        assert headers['Subject'] == 'This is a test email'
        assert 'davidvlu' in headers['From']
