# YouTube

## Parts
Many of the YouTube API functions have a `part` variable to specify which information you want returned.

With the `googly` YouTube API, you specify a list of strings as the `parts` parameter to the calls.
The valid values for the parts will be linked in the documentation below.

## Getting Video Information
[Valid Parts](https://developers.google.com/youtube/v3/docs/videos/list#parameters)

Note that the `duration` field of the `contentDetails` part is [encoded with the "ISO 8601" standard](https://developers.google.com/youtube/v3/docs/videos#contentDetails.duration).
A utility function is included to decode the field (without additional dependencies).

```python
from googly import YouTubeAPI
from googly.apps.youtube import parse_isoduration

api = YouTubeAPI()
print(api.get_video_info('r8E0CbYZcjE'))
info = api.get_video_info('r8E0CbYZcjE', parts=['contentDetails', 'statistics'])
print(parse_isoduration(info['contentDetails']['duration']))
```

## Listing Subscriptions
[Valid Parts](https://developers.google.com/youtube/v3/docs/subscriptions/list#parameters)

```python
from googly import YouTubeAPI

api = YouTubeAPI()
for sub in api.get_subscription_list():
    print(sub)
```

This method returns [Subscription objects](https://developers.google.com/youtube/v3/docs/subscriptions#resource)

## Searching for Videos
[Valid Parts](https://developers.google.com/youtube/v3/docs/search/list#parameters)
```python
from googly import YouTubeAPI

api = YouTubeAPI()
for video in api.search('leeroy jenkins'):
    print(video)
```

## Playlists
[Valid Parts](https://developers.google.com/youtube/v3/docs/playlists/list#parameters)
```python
from googly import YouTubeAPI

api = YouTubeAPI()
# By default, get all playlists for the authenticated user
print(api.get_playlists())
# You can also specify another user
print(api.get_playlists(filter_args={'channelId': 'UCu13RTPnsShX1uvU7Xypwrg'}))
```

There is a separate API call to get the videos within a playlist. [Valid Parts](https://developers.google.com/youtube/v3/docs/playlistItems/list#parameters)

```python
from googly import YouTubeAPI

api = YouTubeAPI()
for video in api.get_playlist('PLTSAQ5KEjPVDnWraOtIeTLP2-NKToaG7y'):
    print(video['snippet']['title'])
```

Annoyingly, [you cannot get information about certain playlists](https://developers.google.com/youtube/v3/revision_history#september-15-2016), namely History and Watch Later, through this API.
