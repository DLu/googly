from googly import YouTubeAPI
from creds import get_credentials


def test_basic_access():
    api = YouTubeAPI(**get_credentials())

    subscriptions = list(api.get_subscription_list())

    assert len(subscriptions) == 1

    sub = subscriptions[0]

    assert sub['kind'] == 'youtube#subscription'
    assert sub['etag'] == 'J23V1HldvQntvO9rTHOTZ_ce-g0'
    assert sub['id'] == 'v0bWhG8NV_3S7we6l-TRxEkeNo9vxxxoucp59Bz0W_4'
    channel = sub['snippet']

    assert channel['title'] == 'Matt Denton'
    assert channel['resourceId']['channelId'] == 'UCbOrJwJsd4vFS4aLIILa_7Q'
    assert channel['channelId'] == 'UCymhhrwqneZRBsgnVPtlwzQ'


def test_basic_search():
    api = YouTubeAPI(**get_credentials())

    vids = list(api.search('avengers'))
    assert len(vids) == 10

    vids = list(api.search('iron man', max_results=14))
    assert len(vids) == 14
