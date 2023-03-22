from dataclasses import dataclass
from typing import List, IO

import feedparser
from feedparser import FeedParserDict


@dataclass
class AggregatorConfig:
    sources: List[str]


@dataclass
class FeedConfig:
    source_url: str
    image_url: str
    email: str
    author: str
    history_titles_file: str


@dataclass
class Feed:
    title: str
    image: str
    source: str = None
    feeddict: dict = None

    @classmethod
    def from_url(self, source: str):
        feed_obj = feedparser.parse(source)
        feed = Feed.from_feedparserdict(feed_obj)
        feed.source = source
        return feed

    @classmethod
    def from_feedparserdict(self, feeddict: FeedParserDict):
        return Feed(
            title=feeddict['feed']['title'],
            image=feeddict['feed']['image']['href'],
            feeddict=feeddict
        )

    def to_xml(self):
        pass


def get_feed_from_source(src: str):
    pass


def aggregate_feed(feed: Feed):
    """
    Produce an RSS file (.xml) containing the new podcasts produced by BeyondWords. This file can later be used to
    publish the podcasts on podcast apps.

    Args:
        source (str): URL of feed to be aggregated

    """
    feed = feedparser.parse(feed.source)

    pass


class StorageIfc():
    """
    Interface to read and write text files.
    """

    def get_file(self, filename: str, mode: str = 'r') -> IO:
        raise NotImplementedError()

    def write_file(self, payload: str):
        raise NotImplementedError()


class LocalStorage(StorageIfc):
    """
    StorageIfc implementation to work with local files.
    """

    def get_file(self, filename: str, mode: str = 'r') -> IO:
        return open(filename, mode)

    def write_file(self, payload: str):
        pass


class GoogleCloudStorage(StorageIfc):
    """
    StorageIfc implementation to work with files on the cloud.
    """

    def get_file(self, filename: str, mode: str = 'r') -> IO:
        pass

    def write_file(self, payload: str):
        pass


def get_storage(local=False):
    """
    Factory to retrieve a storage interface implementation for local or cloud environments.
    Args:
        local: Flag to signal local or cloud environment.

    Returns: StorageIfc implementation.

    """
    if local:
        return LocalStorage()
    else:
        return GoogleCloudStorage()


def daily_aggregator(feedconfig: FeedConfig):
    feed = Feed.from_url(feedconfig.source_url)

    # Retrieve history titles from storage
    storage = get_storage(local=True)
    history_titles_file = storage.get_file(feedconfig.history_titles_file)
    history_titles = [l.rstrip() for l in history_titles_file.readlines()]
    history_titles_file.close()

    print(history_titles)

    # Pseudo-code:
    # feed = retrieve_feed_from_url(url)
    # values_for_podcast_feed = get_values_for_podcast_feed('Alignment Forum')
    # feed.update_values(values_for_podcast_feed)
    # Filter out entries from removed authors
    # feed.entries = [e for entry in feed.entries if e.author not in removed_authors]
