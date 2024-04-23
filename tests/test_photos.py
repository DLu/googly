from googly import PhotosAPI
from creds import get_credentials


def test_basic_access():
    api = PhotosAPI(**get_credentials())

    albums = list(api.get_albums())

    assert len(albums) == 1
    album = albums[0]

    assert album['title'] == 'A Perfectly Fine Test Album'
    assert album['mediaItemsCount'] == '1'

    photos = list(api.get_album_contents(album['id']))
    assert len(photos) == 1

    photo = photos[0]
    assert photo['filename'] == 'LocusLego.png'
    assert photo['mimeType'] == 'image/png'
    assert photo['mediaMetadata']['creationTime'] == '2024-03-25T02:59:04Z'
    assert photo['mediaMetadata']['height'] == '974'
    assert photo['mediaMetadata']['width'] == '591'
