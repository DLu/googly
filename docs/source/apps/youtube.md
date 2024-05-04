# YouTube

## Listing Subscriptions

```python
from googly import YouTubeAPI

api = YouTubeAPI()
for sub in api.get_subscription_list():
    print(sub)
```

This method returns [Subscription objects](https://developers.google.com/youtube/v3/docs/subscriptions#resource)

## Searching for Videos
```python
from googly import YouTubeAPI

api = YouTubeAPI()
for video in api.search('leeroy jenkins'):
    print(video)
```
