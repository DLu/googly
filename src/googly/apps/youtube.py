import googly


class YouTubeAPI(googly.API):
    # https://developers.google.com/youtube/v3

    class Scope(googly.Scope):
        YOUTUBE_READONLY = 1

    def __init__(self, scopes=Scope.all(), **kwargs):
        googly.API.__init__(self, 'youtube', 'v3', scopes, **kwargs)

    def get_subscription_list(self, max_results=50):
        yield from self.get_paged_result(
            self.service.subscriptions().list,
            'items',
            part='snippet',
            mine=True,
            maxResults=max_results,
        )
