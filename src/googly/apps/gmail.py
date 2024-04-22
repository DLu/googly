import googly
import collections


class GMailAPI(googly.API):
    # https://developers.google.com/gmail/api

    class Scope(googly.Scope):
        GMAIL_READONLY = 1

    def __init__(self, scopes=Scope.all(), **kwargs):
        googly.API.__init__(self, 'gmail', 'v1', scopes, **kwargs)

    def get_messages(self, query='', user_id='me', **kwargs):
        yield from self.get_paged_result(
            self.service.users().messages().list,
            'messages',
            userId=user_id,
            q=query,
            **kwargs
        )

    def get_threads(self, query='in:inbox', user_id='me'):
        threads = collections.defaultdict(list)
        for m in self.get_messages(query, user_id):
            threads[m['threadId']].append(m)
        return dict(threads)

    def get_message(self, msg_id, user_id='me'):
        return self.service.users().messages().get(
            userId=user_id,
            id=msg_id
        ).execute()
