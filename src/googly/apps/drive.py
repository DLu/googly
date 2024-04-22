import googly


class DriveAPI(googly.API):
    # https://developers.google.com/drive/api/reference/rest/v3

    class Scope(googly.Scope):
        DRIVE_METADATA_READONLY = 1

    def __init__(self, scopes=Scope.all(), **kwargs):
        googly.API.__init__(self, 'drive', 'v3', scopes, **kwargs)

    def get_file_info(self, fileId, **kwargs):
        return self.service.files().get(fileId=fileId, **kwargs).execute()

    def get_files(self, file_fields=['id', 'name'], **kwargs):
        yield from self.get_paged_result(
            self.service.files().list,
            'files',
            fields=f'nextPageToken, files({", ".join(file_fields)})',
            **kwargs
        )
