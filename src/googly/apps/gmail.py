import googly
import collections
import pathlib
import base64
import mimetypes
from email.message import EmailMessage
from email.utils import COMMASPACE


def set_address_list(message, key, value):
    if not value:
        return
    if isinstance(value, str):
        value = [value]
    message[key] = COMMASPACE.join(value)


def infer_types(fn):
    the_type, encoding = mimetypes.guess_type(fn)
    if not the_type:
        return None, None
    parts = the_type.split('/')
    return parts[0], parts[1]


def create_email(subject='', body='',
                 send_to=[], cc=[], bcc=[],
                 send_from=None,
                 html=False, files=[], images={}):
    if not send_to:
        raise RuntimeError('No recipients specified.')

    message = EmailMessage()

    set_address_list(message, 'To', send_to)
    message['Subject'] = subject
    set_address_list(message, 'CC', cc)
    set_address_list(message, 'BCC', bcc)

    if send_from:
        message['From'] = send_from

    if html:
        message.add_attachment(body, subtype='html')
    else:
        message.set_content(body)

    if not isinstance(files, list):
        files = [files]

    for fn in files:
        filepath = pathlib.Path(fn)
        if not filepath.exists():
            raise FileNotFoundError(f'Cannot find attachment: {filepath.resolve()}')

        with open(filepath, 'rb') as att_f:
            message.add_attachment(att_f.read(),
                                   maintype='application',
                                   subtype='octet-stream',
                                   filename=filepath.name
                                   )

    for cid, fn in images.items():
        filepath = pathlib.Path(fn)
        if not filepath.exists():
            raise FileNotFoundError(f'Cannot find image: {filepath.resolve()}')

        maintype, subtype = infer_types(fn)
        with open(fn, 'rb') as im_f:
            message.add_attachment(im_f.read(),
                                   maintype=maintype,
                                   subtype=subtype,
                                   cid=f'<{cid}>',
                                   disposition='inline')

    return message


def base64_encode_email(message):
    return base64.urlsafe_b64encode(message.as_bytes()).decode()


def get_header(header_list, name):
    """Return the first header with a matching name."""
    for header in header_list:
        if header['name'] == name:
            return header['value']


class GMailAPI(googly.API):
    # https://developers.google.com/gmail/api

    class Scope(googly.Scope):
        GMAIL_READONLY = 1
        GMAIL_MODIFY = 2
        GMAIL_SEND = 4

    def __init__(self, scopes=Scope.all(), **kwargs):
        googly.API.__init__(self, 'gmail', 'v1', scopes, **kwargs)

    def get_labels(self, user_id='me'):
        response = self.service.users().labels().list(userId=user_id).execute()
        return response['labels']

    def get_label(self, label_id, user_id='me'):
        return self.service.users().labels().get(
            userId=user_id,
            id=label_id
        ).execute()

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

    def get_message(self, msg_id, msg_format='full', metadata_headers=[], user_id='me'):
        if msg_format not in ['minimal', 'full', 'raw', 'metadata']:
            raise RuntimeError(f'{repr(msg_format)} is not a valid message format')
        if msg_format != 'metadata' and metadata_headers:
            raise RuntimeError(f'Cannot specify metadata headers when format = {msg_format}')

        return self.service.users().messages().get(
            userId=user_id,
            id=msg_id,
            format=msg_format,
            metadataHeaders=metadata_headers,
        ).execute()

    def get_attachment(self, msg_id, attachment_id, user_id='me'):
        return self.service.users().messages().attachments().get(
            userId=user_id,
            messageId=msg_id,
            id=attachment_id,
        ).execute()

    def get_thread(self, thread_id, user_id='me', format='minimal'):
        return self.service.users().threads().get(
            id=thread_id,
            userId=user_id,
            format=format,
        ).execute()

    def modify_labels(self, msg_id,
                      label_ids_to_add=[],
                      label_ids_to_remove=[],
                      user_id='me'):
        assert label_ids_to_add or label_ids_to_remove
        assert len(label_ids_to_add) <= 100
        assert len(label_ids_to_remove) <= 100

        return self.service.users().messages().modify(
            userId=user_id,
            id=msg_id,
            body={
                'addLabelIds': label_ids_to_add,
                'removeLabelIds': label_ids_to_remove
            }
        ).execute()

    def mark_as_read(self, msg_id):
        self.modify_labels(msg_id, label_ids_to_remove=['UNREAD'])

    def mark_as_unread(self, msg_id):
        self.modify_labels(msg_id, label_ids_to_add=['UNREAD'])

    def move_to_archive(self, msg_id):
        self.modify_labels(msg_id, label_ids_to_remove=['INBOX'])

    def unarchive(self, msg_id):
        self.modify_labels(msg_id, label_ids_to_add=['INBOX'])

    def move_to_trash(self, msg_id, user_id='me'):
        return self.service.users().messages().trash(
            userId=user_id,
            id=msg_id,
        ).execute()

    def untrash(self, msg_id, user_id='me'):
        return self.service.users().messages().untrash(
            userId=user_id,
            id=msg_id,
        ).execute()

    def send_email(self, *args, **kwargs):
        message = create_email(*args, **kwargs)
        self.send_email_object(message)

    def send_email_object(self, message, user_id='me'):
        return self.service.users().messages().send(
            userId=user_id,
            body={
                'raw': base64_encode_email(message)
            }
        ).execute()
