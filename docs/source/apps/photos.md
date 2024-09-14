# Google Photos

## Albums

### Create an Album
You can create albums by title using `create_album`, which takes a single string as a parameter.

```python
from googly import PhotosAPI

api = PhotosAPI()
api.create_album('Pictures of rainbows')
```

### Retrieving Album(s)
 * `get_albums` yields [Album objects](https://developers.google.com/photos/library/reference/rest/v1/albums#resource:-album)
 * `get_album` also yields an Album object, but takes a single string parameter for the exact title of the album.

## Getting Photos/Media

`get_album_contents` yields [MediaItem objects](https://developers.google.com/photos/library/reference/rest/v1/mediaItems#MediaItem) and takes the album's id field as a parameter.

```python
from googly import PhotosAPI

api = PhotosAPI()

for album in api.get_albums():
    print(album['title'])
    for photo in api.get_album_contents(album['id']):
        print(f'\t{photo["mediaMetadata"]["creationTime"]} {photo["filename"]}')
```

## Photo/Media Upload

The easiest way to upload media is with `upload_to_album`, which takes an album id as the first parameter. The second parameter specifies what to upload, in a flexible way.
 * The most expressive way is to specify a list of dictionaries, using the fields:
   * `path` (required) - The file path to the media to upload
   * `description` (optional) - A string of text related to the image. Limited to 1000 characters. As per [the upload guide](https://developers.google.com/photos/library/guides/upload-media), the value "should only include meaningful text created by users...Do not include metadata such as filenames, programmatic tags, or other automatically generated text."
 * Without descriptions, you can also specify a list of paths.
 * You can also just specify a single dictionary, or a single path.

```python
from googly import PhotosAPI

api = PhotosAPI()
album = api.get_album('Pictures of rainbows')
api.upload_to_album(album['id'], [
    {'path': 'DSCN0030.jpg', 'description': 'Rainbow over Yosemite'},
    {'path': 'IMG_0065.jpg', 'description': 'Acadia National Park rainbow'},
])
```
or
```python
# No description version
api.upload_to_album(album['id'], ['DSCN0030.jpg', 'IMG_0065.jpg'])
```
or
```python
# Single upload
api.upload_to_album(album['id'], 'DSCN0030.jpg')
```

### Note
`upload_to_album` internally calls two functions that you can use independently:
 * `upload_file` which takes the file path as the single argument.
 * `add_uploaded_to_album` which takes the album id and a similarly flexible second parameter.

You can also `remove_items_from_album` by specifying an album id and list of media ids.
