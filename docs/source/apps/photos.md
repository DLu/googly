# Google Photos

## Listing Albums and Photos
```python
from googly import PhotosAPI

api = PhotosAPI()

for album in api.get_albums():
    print(album['title'])
    for photo in api.get_album_contents(album['id']):
        print(f'\t{photo["mediaMetadata"]["creationTime"]} {photo["filename"]}')
```

`get_albums` returns [Album objects](https://developers.google.com/photos/library/reference/rest/v1/albums#resource:-album) and `get_album_contents` returns [MediaItem objects](https://developers.google.com/photos/library/reference/rest/v1/mediaItems#MediaItem)
