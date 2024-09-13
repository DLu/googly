import pathlib

import googly


class DriveAPI(googly.API):
    # https://developers.google.com/drive/api/reference/rest/v3

    class Scope(googly.Scope):
        DRIVE_METADATA_READONLY = 1
        DRIVE_READONLY = 2

    def __init__(self, scopes=Scope.all(), **kwargs):
        googly.API.__init__(self, 'drive', 'v3', scopes, **kwargs)

    def get_file_info(self, fileId, **kwargs):
        return googly.destring(self.service.files().get(fileId=fileId, **kwargs).execute())

    def get_files(self, file_fields=['id', 'name'], **kwargs):
        field_s = ', '.join(file_fields)
        yield from self.get_paged_result(
            self.service.files().list,
            'files',
            fields=f'nextPageToken, files({field_s})',
            interpret=True,
            **kwargs
        )

    def walk(self, folder_id, path_parts=None):
        if path_parts is None:
            path_parts = []
        folders = {}
        files = {}
        for drive_file in self.get_files(['id', 'name', 'fileExtension'], q=f'"{folder_id}" in parents'):
            if 'fileExtension' in drive_file:
                files[drive_file['id']] = drive_file['name']
            else:
                folders[drive_file['id']] = drive_file['name']

        yield '/'.join(path_parts), folders, files

        for folder_id, folder_name in sorted(folders.items(), key=lambda d: d[1]):
            new_path = path_parts + [folder_name]
            yield from self.walk(folder_id, new_path)

    def get_file_contents(self, file_id):
        return self.service.files().get_media(
            fileId=file_id
        ).execute()

    def download_file(self, file_id, destination_path):
        res = self.get_file_contents(file_id)
        with open(destination_path, 'wb') as f:
            f.write(res)

    def download_folder(self, folder_id, destination_path, dry_run=False, quiet=False, overwrite=False):
        if not isinstance(destination_path, pathlib.Path):
            destination_path = pathlib.Path(destination_path)

        for root, dirs, files in self.walk(folder_id):
            for file_id, filename in sorted(files.items(), key=lambda p: p[1]):
                target_path = destination_path / root / filename
                if target_path.exists() and not overwrite:
                    continue
                if not quiet:
                    print(f'Downloading {target_path}...')
                if dry_run:
                    continue

                target_path.parent.mkdir(exist_ok=True, parents=True)
                self.download_file(file_id, target_path)
