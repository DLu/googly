from googly import GMailAPI
from googly.apps.gmail import base64_encode_email, create_email, infer_types
from creds import get_credentials
import pytest


def test_basic_access():
    api = GMailAPI(**get_credentials())

    labels = {label['id']: label for label in api.get_labels()}

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

        label_names = {labels[l_id]['name'] for l_id in msg['labelIds']}
        assert label_names == {'IMPORTANT', 'Awesome', 'CATEGORY_PERSONAL', 'INBOX'}

    # Bonus label checks
    awesome_label = api.get_label('Label_2707116397000472531')
    assert awesome_label['color']['textColor'] == '#ffffff'
    assert awesome_label['color']['backgroundColor'] == '#2da2bb'

    # Bonus thread check
    thread = api.get_thread('18ec87a5013ae2d9')
    assert len(thread['messages']) == 2


def test_break_modify_labels():
    api = GMailAPI(**get_credentials())

    with pytest.raises(AssertionError):
        api.modify_labels('msg_id')

    label_ids = [f'Label_{i}' for i in range(200)]
    with pytest.raises(AssertionError):
        api.modify_labels('msg_id', label_ids_to_add=label_ids)
    with pytest.raises(AssertionError):
        api.modify_labels('msg_id', label_ids_to_remove=label_ids)


def test_create_error_laden_email():
    with pytest.raises(RuntimeError):
        # No recipients
        create_email(send_to='')

    with pytest.raises(RuntimeError):
        # No recipients
        create_email(send_to=[])


def test_create_simple_email():
    msg = create_email('Greetings', 'Hello World', 'to@gmail.com')
    assert msg['To'] == 'to@gmail.com'
    assert msg['Subject'] == 'Greetings'
    assert 'text/plain' in msg['Content-Type']
    assert msg.get_content().strip() == 'Hello World'

    expected_contents = ('VG86IHRvQGdtYWlsLmNvbQpTdWJqZWN0OiBHcmVldGluZ3MKQ29ud'
                         'GVudC1UeXBlOiB0ZXh0L3BsYWluOyBjaGFyc2V0PSJ1dGYtOCIKQ2'
                         '9udGVudC1UcmFuc2Zlci1FbmNvZGluZzogN2JpdApNSU1FLVZlcnN'
                         'pb246IDEuMAoKSGVsbG8gV29ybGQK')
    assert base64_encode_email(msg) == expected_contents


def test_create_email_with_more_fields():
    msg = create_email('More Greetings', 'Bonjour!',
                       ['to1@gmail.com', 'to2@gmail.com'], send_from='thegooglyapi@gmail.com')
    assert msg['To'] == 'to1@gmail.com, to2@gmail.com'
    assert msg['From'] == 'thegooglyapi@gmail.com'
    assert msg['Subject'] == 'More Greetings'
    assert 'text/plain' in msg['Content-Type']
    assert msg.get_content().strip() == 'Bonjour!'


def test_create_html_email():
    msg = create_email('HTML Email', '<blink>Hello World</blink>', 'to@gmail.com', html=True)
    assert msg['To'] == 'to@gmail.com'
    assert msg['Subject'] == 'HTML Email'
    assert 'multipart/mixed' in msg['Content-Type']

    html_found = False
    for part in msg.walk():
        if part.get_content_type() == 'text/html':
            assert part.get_payload().strip() == '<blink>Hello World</blink>'
            html_found = True
        # TODO: Maybe check for text part
    assert html_found


def test_bad_attachments():
    with pytest.raises(FileNotFoundError):
        create_email(send_to='to@gmail.com', files=['DOES_NOT_EXIST'])


def test_good_attachment():
    msg = create_email(send_to='to@gmail.com',
                       files='tests/files/words.txt')
    assert msg['To'] == 'to@gmail.com'
    assert msg['Subject'] == ''
    assert 'multipart/mixed' in msg['Content-Type']

    att_found = False
    for part in msg.walk():
        if part.get_content_type() == 'application/octet-stream':
            assert part.get_filename() == 'words.txt'
            assert part.get_payload().strip() == 'cGxhbQo='
            att_found = True
    assert att_found


def test_type_inference():
    # These files don't need to exist
    assert infer_types('tests/files/words.txt') == ('text', 'plain')
    assert infer_types('tests/files/pixel.gif') == ('image', 'gif')
    assert infer_types('pixel.jpg') == ('image', 'jpeg')
    assert infer_types('pixel.png') == ('image', 'png')
    assert infer_types('FILE_WITHOUT_EXTENSION') == (None, None)


def test_bad_images():
    with pytest.raises(FileNotFoundError):
        create_email(send_to='to@gmail.com', images={0: 'DOES_NOT_EXIST'})


def test_inline_image():
    msg = create_email('Email with Image', 'Look here - <img src="cid:picture.gif"/>',
                       'to@gmail.com', html=True, images={'picture.gif': 'tests/files/pixel.gif'})
    assert msg['To'] == 'to@gmail.com'
    assert msg['Subject'] == 'Email with Image'
    assert 'multipart/mixed' in msg['Content-Type']

    html_found = False
    img_found = False
    for part in msg.walk():
        if part.get_content_type() == 'text/html':
            assert part.get_payload().strip() == 'Look here - <img src="cid:picture.gif"/>'
            html_found = True
        elif part.get_content_type() == 'image/gif':
            assert part['Content-Disposition'] == 'inline'
            assert part['Content-ID'] == '<picture.gif>'
            img_found = True

    assert html_found
    assert img_found
