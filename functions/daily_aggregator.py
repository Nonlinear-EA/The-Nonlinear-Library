import re

import feedparser

from functions.feed import FeedConfig
from functions.storage import get_storage


def daily_aggregator(feedconfig: FeedConfig):
    # Get feed from source
    feed = feedparser.parse(feedconfig.source)

    # Update values from provided configuration
    feed['feed']['title'] = feedconfig.title
    feed['feed']['image']['href'] = feedconfig.image_url

    # Filter entries by forum using the provided title regex
    if feedconfig.title_regex:
        regex = re.compile(feedconfig.title_regex)
        feed['entries'] = list(filter(lambda s: regex.match(s['title']), feed['entries']))

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
