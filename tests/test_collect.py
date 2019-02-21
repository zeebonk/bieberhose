import json
from queue import Empty, Queue

import pytest

from bieberhose.collect import parse_json_tweets, tweet_to_row, twitter_time_to_epoch


def test__twitter_time_to_epoch():
    assert twitter_time_to_epoch("Thu Feb 21 11:26:32 +0000 2019") == 1550748392
    assert twitter_time_to_epoch("Wed Mar 25 01:15:40 +0100 2015") == 1427242540


def test__parse_json_tweets__adds_tweets_to_queue():
    raw_message = json.dumps({"foo": "bar"}).encode("utf-8")
    queue = Queue()

    parse_json_tweets([raw_message], queue)

    assert queue.get() == {"foo": "bar"}


def test__parse_json_tweets__skips_keep_alive_messages():
    raw_message = b"\r\n"
    queue = Queue()

    parse_json_tweets([raw_message], queue)

    with pytest.raises(Empty):
        queue.get(block=False)


def test__parse_json_tweets__skips_limit_messages():
    raw_message = json.dumps({"limit": "yes"}).encode("utf-8")
    queue = Queue()

    parse_json_tweets([raw_message], queue)

    with pytest.raises(Empty):
        assert queue.get(block=False)


def test__tweet_to_row__regular_tweet():
    assert tweet_to_row(
        {
            "created_at": "Thu Feb 21 15:37:58 +0000 2019",
            "id": 1098607770922827776,
            "id_str": "1098607770922827776",
            "text": "One Direction\nHarry Potter\nEmma Watson\nTaylor Swift\nAriana Grande\nJustin Bieber\nMiley Cyrus\nVictoria Justice\nMirand… https://t.co/Tit80U2d3t",
            "user": {
                "id": 2198466355,
                "id_str": "2198466355",
                "name": "1D is my world",
                "screen_name": "love_1mu2mo3dra",
                "location": "JAPAN 14yrs Please follow me♡ ",
                "url": None,
                "created_at": "Sat Nov 16 21:48:57 +0000 2013",
            },
            "is_quote_status": False,
            "lang": "ja",
            "timestamp_ms": "1550763478390",
        }
    ) == {
        "author_created_at": 1384638537,
        "author_id": "2198466355",
        "author_name": "1D is my world",
        "author_screen_name": "love_1mu2mo3dra",
        "tweet_created_at": 1550763478,
        "tweet_id": "1098607770922827776",
        "tweet_text": "One Direction\nHarry Potter\nEmma Watson\nTaylor Swift\nAriana Grande\nJustin Bieber\nMiley Cyrus\nVictoria Justice\nMirand… https://t.co/Tit80U2d3t",
    }


def test__tweet_to_row__use_extended_text_when_available():
    assert tweet_to_row(
        {
            "created_at": "Thu Feb 21 15:37:58 +0000 2019",
            "id": 1098607770922827776,
            "id_str": "1098607770922827776",
            "text": "One Direction\nHarry Potter\nEmma Watson\nTaylor Swift\nAriana Grande\nJustin Bieber\nMiley Cyrus\nVictoria Justice\nMirand… https://t.co/Tit80U2d3t",
            "user": {
                "id": 2198466355,
                "id_str": "2198466355",
                "name": "1D is my world",
                "screen_name": "love_1mu2mo3dra",
                "location": "JAPAN 14yrs Please follow me♡ ",
                "url": None,
                "created_at": "Sat Nov 16 21:48:57 +0000 2013",
            },
            "is_quote_status": False,
            "extended_tweet": {
                "full_text": "One Direction\nHarry Potter\nEmma Watson\nTaylor Swift\nAriana Grande\nJustin Bieber\nMiley Cyrus\nVictoria Justice\nMiranda Cosgrobe\niCarly\nHannah Montana\nVictorius\nHigh School Musical\n\nこの中で１つでも好きなものがあればRT!! フォロー絶対します♡",
                "display_text_range": [0, 211],
                "entities": {
                    "hashtags": [],
                    "urls": [],
                    "user_mentions": [],
                    "symbols": [],
                },
            },
            "lang": "ja",
            "timestamp_ms": "1550763478390",
        }
    ) == {
        "author_created_at": 1384638537,
        "author_id": "2198466355",
        "author_name": "1D is my world",
        "author_screen_name": "love_1mu2mo3dra",
        "tweet_created_at": 1550763478,
        "tweet_id": "1098607770922827776",
        "tweet_text": "One Direction\nHarry Potter\nEmma Watson\nTaylor Swift\nAriana Grande\nJustin Bieber\nMiley Cyrus\nVictoria Justice\nMiranda Cosgrobe\niCarly\nHannah Montana\nVictorius\nHigh School Musical\n\nこの中で１つでも好きなものがあればRT!! フォロー絶対します♡",
    }
