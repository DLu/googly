import googly
import datetime


VALID_PARTS = {
    'subscriptions': ['contentDetails', 'id', 'snippet', 'subscriberSnippet'],
    'search': ['id', 'snippet'],
    'playlist_items': ['contentDetails', 'id', 'snippet', 'status'],
    'playlists': ['contentDetails', 'id', 'localizations', 'player', 'snippet', 'status'],
    'videos': ['contentDetails', 'fileDetails', 'id', 'liveStreamingDetails', 'localizations',
               'paidProductPlacementDetails', 'player', 'processingDetails', 'recordingDetails',
               'snippet', 'statistics', 'status', 'suggestions', 'topicDetails'],
}


def get_valid_parts(key, values):
    valid = []
    invalid = []

    reference = VALID_PARTS[key]
    for part in values:
        if part in reference:
            valid.append(part)
        else:
            invalid.append(part)

    if invalid:
        raise RuntimeError(f'Invalid value(s) for parts parameters: {"/".join(invalid)}')

    return ','.join(valid)


def parse_isoduration(s):
    # Isoduration via https://stackoverflow.com/a/64232786/27837036
    def get_isosplit(s, split):
        if split in s:
            n, s = s.split(split)
        else:
            n = 0
        return n, s

    # Remove prefix
    s = s.split('P')[-1]

    # Step through letter dividers
    days, s = get_isosplit(s, 'D')
    _, s = get_isosplit(s, 'T')
    hours, s = get_isosplit(s, 'H')
    minutes, s = get_isosplit(s, 'M')
    seconds, s = get_isosplit(s, 'S')

    # Convert all to seconds
    dt = datetime.timedelta(days=int(days), hours=int(hours), minutes=int(minutes), seconds=int(seconds))
    return int(dt.total_seconds())


class YouTubeAPI(googly.API):
    # https://developers.google.com/youtube/v3

    class Scope(googly.Scope):
        YOUTUBE_READONLY = 1

    def __init__(self, scopes=Scope.all(), **kwargs):
        googly.API.__init__(self, 'youtube', 'v3', scopes, **kwargs)

    def get_subscription_list(self, parts=['snippet'], max_results=50):
        yield from self.get_paged_result(
            self.service.subscriptions().list,
            'items',
            part=get_valid_parts('subscriptions', parts),
            mine=True,
            maxResults=max_results,
        )

    def search(self, query, parts=['id', 'snippet'], max_results=10, order='viewCount', type='video'):
        yield from self.get_paged_result(
            self.service.search().list,
            'items',
            q=query,
            part=get_valid_parts('search', parts),
            order=order,
            type=type,
            max_results=max_results,
            max_results_param_name='maxResults',

        )

    def get_playlist(self, playlist_id, parts=['snippet']):
        yield from self.get_paged_result(
            self.service.playlistItems().list,
            'items',
            playlistId=playlist_id,
            part=get_valid_parts('playlist_items', parts),
        )

    def get_playlists(self, parts=['snippet'], filter_args={'mine': True}):
        yield from self.get_paged_result(
            self.service.playlists().list,
            'items',
            part=get_valid_parts('playlists', parts),
            **filter_args,
        )

    def get_video_info(self, video_id, parts=['snippet']):
        result = self.service.videos().list(
            id=video_id,
            part=get_valid_parts('videos', parts),
        ).execute()
        if not result['items']:
            raise RuntimeError(f'Video {video_id} not found')
        return result['items'][0]
