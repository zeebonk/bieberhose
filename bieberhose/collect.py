import csv
import json
import sys
from queue import Empty as QueueEmptyError
from queue import Queue
from threading import Thread
from time import monotonic as monotonic_time

import click
import pendulum
import requests
from click import ClickException

from . import credentials


@click.command()
@click.option(
    "keywords",
    "-k",
    "--keyword",
    help="Keywords to track",
    multiple=True,
    default=["bieber"],
    show_default=True,
)
@click.option(
    "-s",
    "--max-seconds",
    help="Maximum number of seconds to run",
    default=30,
    show_default=True,
)
@click.option(
    "-n",
    "--max-tweets",
    help="Maximum number of Tweets to collect",
    default=100,
    show_default=True,
)
def collect(keywords, max_seconds, max_tweets):
    """
    Collect tweets from the Twitter firehose and output as TSV.
    """
    if not credentials.exists():
        raise ClickException("No credentials found, please authenticate first")

    # Take an iterator over the streaming results of the API request
    json_lines_iterator = requests.post(
        f"https://stream.twitter.com/1.1/statuses/filter.json?track={','.join(keywords)}",
        auth=credentials.load(),
        stream=True,
    ).iter_lines()

    # Read the streaming results on a separte thread because consuming the
    # iterator is a blocking operation and because we must be able to exit the
    # program when `max_seconds` have ellapsed. Results are put on the passed
    # queue, on which we can specify timeouts on read operations.
    tweets_queue = Queue()
    Thread(
        target=parse_json_tweets,
        args=(json_lines_iterator, tweets_queue),
        daemon=True,  # Kill thread automatically when main thread exits
    ).start()

    # To prevent users from having to look at a blank screen for `max_seconds`
    # seconds, we show them a progressbar during the collection of the tweets.
    progress_bar = click.progressbar(
        length=max_tweets,
        label=f"Collecting max. {max_tweets} tweets for {max_seconds} seconds",
        show_pos=True,
        show_eta=False,
        # Write to stderr so that users can redirect/pipe the TSV results on
        # stdout to somewhere else without including the progressbar.
        file=sys.stderr,
    )

    tweet_rows = []
    started_at = monotonic_time()
    while len(tweet_rows) < max_tweets:
        try:
            # Block on reading from the queue until `max_seconds` have ellapsed
            # and we can stop aggregating entirely, or until we have a new tweet
            # to process.
            seconds_till_end = max(max_seconds - (monotonic_time() - started_at), 0)
            tweet = tweets_queue.get(timeout=seconds_till_end)

            # There are three types of system messages, as defined here:
            # https://developer.twitter.com/en/docs/tutorials/consuming-streaming-data.html#consuming-the-stream
            # In theory only error messages can occour while streaming from the
            # filter API, but for the sake of completeness we'll handle them
            # all, and as if they are errors.
            for system_message_type in ["error", "warn", "info"]:
                if system_message_type in tweet:
                    raise ClickException(tweet[system_message_type]["message"])

            tweet_rows.append(tweet_to_row(tweet))
            progress_bar.update(1)
        except QueueEmptyError:
            break  # `max_seconds` have ellapsed, stop collecting

    if not tweet_rows:
        print("No tweets collected", file=sys.stderr)
        return

    tweet_rows = sorted(  # Ascending by default
        tweet_rows,
        key=lambda tweet_row: (
            tweet_row["author_created_at"],  # Users sorted chronologicly
            tweet_row["author_id"],  # Grouped by user
            tweet_row["tweet_created_at"],  # Tweets sorted chronologicly
        ),
    )
    writer = csv.DictWriter(
        sys.stdout, fieldnames=tweet_rows[0].keys(), dialect="excel-tab"
    )
    writer.writeheader()
    writer.writerows(tweet_rows)


def parse_json_tweets(tweet_lines_iter, queue):
    """
    Read tweets serialized as json line by line, coverting them to dictionaries
    and putting them on the given queue.
    """
    for line in tweet_lines_iter:
        line = line.strip()
        if not line:
            continue  # Keep-alive messages
        message = json.loads(line, encoding="utf-8")
        if "limit" in message:
            # Limit messages indicate that you we can't keep up with the stream
            # of messages and we're starting to lag behind.
            continue
        queue.put(message)


def tweet_to_row(tweet):
    """
    Convert a full tweet to a row for TSV output.
    """
    row = {
        "tweet_id": tweet["id_str"],
        "tweet_created_at": twitter_time_to_epoch(tweet["created_at"]),
        "author_id": tweet["user"]["id_str"],
        "author_created_at": twitter_time_to_epoch(tweet["user"]["created_at"]),
        "author_name": tweet["user"]["name"],
        "author_screen_name": tweet["user"]["screen_name"],
    }

    # In the olden days tweets could have a maximum length of 140, but in 2017
    # they doubled it to 280. To keep backwards compatibiliy with API consumers
    # that expect 140 characters, the longer messages are put under a new field
    # in the `extended_tweet` object.
    if "extended_tweet" in tweet:
        row["tweet_text"] = tweet["extended_tweet"]["full_text"]
    else:
        row["tweet_text"] = tweet["text"]

    return row


def twitter_time_to_epoch(ts):
    return int(pendulum.from_format(ts, "ddd MMM DD HH:mm:ss Z YYYY").timestamp())
