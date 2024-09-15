import googly

import json
import mimetypes
import requests


class PhotosAPI(googly.API):
    # https://developers.google.com/photos/library/guides/overview

    class Scope(googly.Scope):
        PHOTOSLIBRARY = 1
        PHOTOSLIBRARY_APPENDONLY = 2

    def __init__(self, scopes=Scope.all(), version='v1', **kwargs):
        googly.API.__init__(self, 'photoslibrary', version, scopes, static_discovery=False, **kwargs)
        self.base_url = f'{self.service._baseUrl}{version}/'

    def get_albums(self):
        yield from self.get_paged_result(
            self.service.albums().list,
            'albums',
            interpret=True,
        )

    def get_album(self, title):
        for album in self.get_albums():
            if album['title'] == title:
                return album

    def create_album(self, title):
        return self.service.albums().create(
            body={
                'album': {
                    'title': title,
                },
            }
        ).execute()

    def get_album_contents(self, album_id):
        # Annoyingly, for this call, pageToken goes in body
        #  so we cannot use get_paged_result
        next_token = None
        while True:
            results = self.service.mediaItems().search(
                body={'albumId': album_id, 'pageToken': next_token},
            ).execute()

            yield from googly.destring(results.get('mediaItems', []))
            next_token = results.get('nextPageToken')

            if not next_token:
                break

    def _request(self, url_path, headers=None, data=None):
        if headers is None:
            headers = {}
        headers['Authorization'] = f'Bearer {self.creds.token}'
        headers['Content-Type'] = 'application/octet-stream'

        return requests.post(self.base_url + url_path, headers=headers, data=data)

    def _run_batch(self, url_path, **kwargs):
        r = self._request(url_path, data=json.dumps(kwargs))
        response = r.json()
        if 'error' in response:
            raise RuntimeError('{status}({code}): {message}'.format(**response['error']))

    def upload_file(self, path):
        the_contents = open(path, 'rb').read()

        mime_type, _ = mimetypes.guess_type(path)
        headers = {
            'X-Goog-Upload-Content-Type': mime_type,
            'X-Goog-Upload-Protocol': 'raw',
        }
        r = self._request('uploads', headers, the_contents)
        return r.content.decode('utf-8')

    def add_uploaded_to_album(self, album_id, items):
        if not isinstance(items, list):
            items = [items]
        media_items = []
        for item in items:
            if isinstance(item, str):
                item = {'token': item}

            media = {'simpleMediaItem': {'uploadToken': item.pop('token')}}
            if 'description' in item:
                media['description'] = item.pop('description')
            if 'filename' in item:
                media['simpleMediaItem']['fileName'] = str(item.pop('filename'))
            assert not item

            media_items.append(media)

        # batch in groups of 50
        for i in range(0, len(media_items), 50):
            batch_of_items = media_items[i:i+50]
            self._run_batch('mediaItems:batchCreate', albumId=album_id, newMediaItems=batch_of_items)

    def remove_items_from_album(self, album_id, media_ids):
        if not isinstance(media_ids, list):
            media_ids = [media_ids]
        url_path = f'albums/{album_id}:batchRemoveMediaItems'
        self._run_batch(url_path, mediaItemIds=media_ids)

    def upload_to_album(self, album_id, images):
        items = []
        if not isinstance(images, list):
            images = [images]
        for image in images:
            if not isinstance(image, dict):
                image = {'path': image}

            token = self.upload_file(image['path'])
            item = {'token': token, 'filename': image['path']}
            if 'description' in image:
                item['description'] = image['description']
            items.append(item)
        self.add_uploaded_to_album(album_id, items)
