# Google Drive

## Accessing Files

```python
from googly import DriveAPI
api = DriveAPI()
for drive_file in api.get_files():
    print(drive_file)

    verbose = api.get_file_info(drive_file['id'])
    print(verbose)
```

Both methods will return [Files](https://developers.google.com/drive/api/reference/rest/v3/files), although by default, `get_files` only returns the id and name of the files. Other fields can be specified using the `file_fields` parameter.
