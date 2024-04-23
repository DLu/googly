import googly


class PhotosAPI(googly.API):
    # https://developers.google.com/photos/library/guides/overview

    class Scope(googly.Scope):
        PHOTOSLIBRARY = 1

    def __init__(self, scopes=Scope.all(), **kwargs):
        googly.API.__init__(self, 'photoslibrary', 'v1', scopes, static_discovery=False, **kwargs)

    def get_albums(self):
        yield from self.get_paged_result(
            self.service.albums().list,
            'albums',
        )

    def get_album_contents(self, album_id):
        # Annoyingly, for this call, pageToken goes in body
        #  so we cannot use get_paged_result
        next_token = None
        while True:
            results = self.service.mediaItems().search(
                body={'albumId': album_id, 'pageToken': next_token},
            ).execute()

            yield from results['mediaItems']
            next_token = results.get('nextPageToken')

            if not next_token:
                break
