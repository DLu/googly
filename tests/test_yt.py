from googly import YouTubeAPI
from googly.apps.youtube import parse_isoduration
from creds import get_credentials
import pytest


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


def test_parts():
    api = YouTubeAPI(**get_credentials())

    with pytest.raises(RuntimeError):
        list(api.get_subscription_list(parts=['bogus']))

    subscriptions = list(api.get_subscription_list(
        parts=['contentDetails', 'id', 'subscriberSnippet']
    ))

    assert len(subscriptions) == 1

    sub = subscriptions[0]
    assert 'contentDetails' in sub
    assert 'etag' in sub
    assert 'id' in sub
    assert 'snippet' not in sub
    assert 'kind' in sub
    assert 'subscriberSnippet' in sub


def test_basic_search():
    api = YouTubeAPI(**get_credentials())

    vids = list(api.search('avengers'))
    assert len(vids) == 10

    vids = list(api.search('iron man', max_results=14))
    assert len(vids) == 14


def test_isoduration():
    assert parse_isoduration('PT1H5M26S') == 3926
    assert parse_isoduration('P4DT12H30M5S') == 390605
    assert parse_isoduration('PT42S') == 42


def test_playlists():
    api = YouTubeAPI(**get_credentials())
    playlists = list(api.get_playlists())

    assert len(playlists) == 1

    playlist = playlists[0]
    assert playlist['snippet']['title'] == 'Testing Playlist'

    contents = list(api.get_playlist(playlist['id']))
    assert len(contents) == 2

    assert contents[0]['snippet']['title'] == 'Giant LEGO Forklift - Mantis Hacks E9'


def test_video_info():
    api = YouTubeAPI(**get_credentials())

    # No Parts
    info = api.get_video_info('OPCm9aoIxUs')
    assert info['snippet']['title'] == 'Working Lego Minifig Light Saber! - Mantis Hacks'
    assert 'lightsaber' in info['snippet']['tags']

    # No Matching Video
    with pytest.raises(RuntimeError):
        api.get_video_info('000')
