import re
from datetime import datetime, timezone, timedelta
from difflib import SequenceMatcher
from time import strptime, mktime

import feedparser
import requests
from bs4 import BeautifulSoup

from functions.feed import FeedGeneratorConfig
from functions.storage import create_storage


def get_post_karma(url) -> str:
    """
    Return a post's karma based on the provided url
    Args:
        url: Post url

    Returns: String with the post's karma

    """
    # disguising the request using headers
    page = requests.get(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/83.0.4103.97 Safari/537.36'})
    soup = BeautifulSoup(page.content, "html.parser")
    if soup.title and soup.title == '403 Forbidden':
        raise AssertionError(
            '403 Forbidden error when trying to access ' + url + 'You may need to change the headers to something '
                                                                 'else.')
    return soup.find('h1', {'class': 'PostsVote-voteScore'}).text


def get_podcast_feed(feedconfig: FeedGeneratorConfig):
    """
    Get a RSS feed for podcast apps that is produced from a source and applying filtering criteria defined in the
    provided feedconfig object.

    Args: feedconfig: Object with meta-data and filtering criteria to produce a RSS feed file.

    Returns: xml string

    TODO: Document usage in readme?
    """

    import feedparser
    import ssl
    if hasattr(ssl, '_create_unverified_context'):
        # noinspection PyProtectedMember
        ssl._create_default_https_context = ssl._create_unverified_context
    # Get feed from source
    feed = feedparser.parse(feedconfig.source)
    n_entries = len(feed['entries'])

    # Get storage handler
    storage = create_storage(feedconfig, local=True)

    # Retrieve removed authors
    removed_authors = storage.read_removed_authors()

    # Filter out entries from removed authors
    feed['entries'] = [e for e in feed['entries'] if e['author'] not in removed_authors]
    print(f'{n_entries - len(feed["entries"])} removed because of removed authors...')
    n_entries = len(feed['entries'])

    # Filter entries by checking if their titles match the provided title_prefix
    if feedconfig.title_prefix:
        def title_starts_with_config_prefix(entry):
            return entry['title'].startswith(feedconfig.title_prefix)
        feed['entries'] = list(filter(title_starts_with_config_prefix, feed['entries']))
        print(f'{n_entries - len(feed["entries"])} removed because of title mismatch...')
        n_entries = len(feed['entries'])

    # Filter posts based on the requested search period
    # Get search period as timedelta
    search_period = feedconfig.get_search_period_timedelta()
    # Define the time of the oldest post that should come through
    oldest_post_time = datetime.now() - search_period
    # Filter out posts published later than oldest_post_time
    feed['entries'] = [entry for entry in feed['entries'] if
                       mktime(strptime(entry['published'], feedconfig.date_format)) >= oldest_post_time.timestamp()]
    print(f'{n_entries - len(feed["entries"])} outside search period removed')

    # Read history titles from storage
    history_titles = storage.read_history_titles()

    # Find posts that are also in the history.
    def entry_title_is_in_history(entry):
        return max([SequenceMatcher(None, entry['title'], h).ratio() for h in history_titles]) > 0.9

    history_entries = [entry for entry in feed['entries'] if entry_title_is_in_history(entry)]
    print(f"Found {len(history_entries)} file(s) from history.")

    # Get post karma
    history_entries = map(lambda entry: {**entry, 'karma': get_post_karma(entry['link'])}, history_entries)
    print("\n".join([f"{entry['title']} - Karma: {entry['karma']}" for entry in history_entries]))

    print(f'{len(feed["entries"])} entries remaining')

    # Update values from the provided configuration
    feed['feed']['title'] = feedconfig.title
    feed['feed']['image']['href'] = feedconfig.image_url

    return feed
