import re
from datetime import datetime, timezone, timedelta
from difflib import SequenceMatcher
from time import strptime, mktime

import feedparser
import requests
from bs4 import BeautifulSoup

from functions.feed import FeedGeneratorConfig
from functions.storage import get_storage


def get_post_karma(url) -> str | None:
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
            '403 Forbidden error when trying to access ' + url + ' You may need to change the headers to something else.')
    return soup.find('h1', {'class': 'PostsVote-voteScore'}).text


def get_podcast_feed(feedconfig: FeedGeneratorConfig):
    """
    Get a RSS feed for podcast apps that is produced from a source and applying filtering criteria defined in the
    provided feedconfig object.

    Args: feedconfig: Object with meta-data and filtering criteria to produce a RSS feed file.

    Returns: xml string

    TODO: Document usage in readme?
    """
    # Get feed from source
    feed = feedparser.parse(feedconfig.source)
    n_entries = len(feed['entries'])

    # Get storage handler
    storage = get_storage(local=True)

    # Retrieve removed authors
    removed_authors_file = storage.get_file(feedconfig.removed_authors_file)
    removed_authors = [l for l in removed_authors_file.readlines()]
    removed_authors_file.close()

    # Filter out entries from removed authors
    feed['entries'] = [e for e in feed['entries'] if e['author'] not in removed_authors]
    print(f'{n_entries - len(feed["entries"])} removed because of removed authors...')
    n_entries = len(feed['entries'])

    # Filter entries by forum using the provided title regex
    if feedconfig.title_regex:
        regex = re.compile(feedconfig.title_regex)
        feed['entries'] = list(filter(lambda s: regex.match(s['title']), feed['entries']))
        print(f'{n_entries - len(feed["entries"])} removed because of title mismatch...')
        n_entries = len(feed['entries'])

    # Filter posts based on the requested search period
    # Get search period as timedelta
    search_period = feedconfig.get_search_period_timedelta()
    # Define the time of the oldest post that should come through
    oldest_post_time = datetime.now(tz=timezone(timedelta(0))).replace(hour=0, minute=0, second=0,
                                                                       microsecond=0) - search_period
    # Filter out posts published later than oldest_post_time
    feed['entries'] = [e for e in feed['entries'] if
                       mktime(strptime(e['published'], feedconfig.date_format)) >= oldest_post_time.timestamp()]
    print(f'{n_entries - len(feed["entries"])} outside search period removed')

    # Retrieve history titles from storage
    history_titles_file = storage.get_file(feedconfig.history_titles_file)
    history_titles = [l.rstrip() for l in history_titles_file.readlines()]
    history_titles_file.close()

    # Find posts that are also in the history. This list comprehension compares every entry title with the history
    # titles and adds entries with a result greater than 0.9
    history_entries = [e for e in feed['entries'] if
                       max([SequenceMatcher(None, e['title'], h).ratio() for h in history_titles]) > 0.9]
    print(f"Found {len(history_entries)} file(s) from history.")

    # Get post karma
    history_entries = map(lambda e: {**e, 'karma': get_post_karma(e['link'])}, history_entries)
    print("\n".join([f"{e['title']} - Karma: {e['karma']}" for e in history_entries]))

    print(f'{len(feed["entries"])} entries remaining')

    # Update values from provided configuration
    feed['feed']['title'] = feedconfig.title
    feed['feed']['image']['href'] = feedconfig.image_url

    return feed
