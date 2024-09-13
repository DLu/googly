# Google Drive

## Listing Files and Getting Metainfo

```python
from googly import DriveAPI
api = DriveAPI()
for drive_file in api.get_files():
    print(drive_file)

    verbose = api.get_file_info(drive_file['id'])
    print(verbose)
```

Both methods will return [Files](https://developers.google.com/drive/api/reference/rest/v3/files), although by default, `get_files` only returns the id and name of the files. Other fields can be specified using the `file_fields` parameter.

### Search Query
You can also get more granular with listing the files by using a custom query with a `q` keyword argument, using [the Drive search spec](https://developers.google.com/drive/api/guides/search-files).

```python
from googly import DriveAPI
api = DriveAPI()
for drive_file in api.get_files(q='fullText contains "robots"'):
    print(drive_file)
```

### Sorting Results
You can also use the `orderBy` keyword argument to change the order results are returned, as long as you use a [valid `orderBy` key list](https://developers.google.com/drive/api/reference/rest/v3/files/list)

In this example, we list all the files in decreasing size order.

```python
from googly import DriveAPI
import humanize
api = DriveAPI()
for item in api.get_files(file_fields=['name, size'],
                          orderBy='quotaBytesUsed desc'):
    sz = humanize.naturalsize(item['size'])
    print(f'{sz:15} {item["name"]}')
```

## Listing Files Recursively
We can use `parents` in the `file_fields` parameter to figure out what folders things are in. However, you can also use the `walk` method of the API to get an API similar to [`os.walk`](https://docs.python.org/3/library/os.html#os.walk).

`walk` takes one parameter (the folder ID) and iterates over all the subfolders. Each subfolder (including the initial folder) yields a 3-tuple:
 * `dirpath` - a `/`-joined path to the folder relative to the initial folder. The initial folder has the value `''`
 * `dirnames` - a dictionary where the keys are folder IDs and the values are folder names
 * `filenames` - a dictionary where the keys are file IDs and the values are filenames.

```python
from googly import DriveAPI
api = DriveAPI()
folder_id = '1qT-RcncvXni9kGSVUYWXZ1yVYWEfp0hU'
for dirpath, dirnames, filenames in api.walk(folder_id):
    dirpath = dirpath or 'root folder'
    print(f'{dirpath} has {len(dirnames)} subfolders '
          f'and {len(filenames)} files.')
```

## Downloads!
To download a file, you simply pass a file ID and destination path into `download_file`.

```python
from googly import DriveAPI
api = DriveAPI()
api.download_file('1GfhOvySpKSSKupHV9hP7Nvb63GfT00V0', 'music.mp3')
```

Internally, this uses `get_file_contents` to get the raw bytestream of the contents of the file before writing to the filesystem.

You can also use `download_folder` in a similar manner to download all the files from a folder recursively while maintaining the folder structure.
