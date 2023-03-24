import re
from difflib import SequenceMatcher

import feedparser
import requests
from bs4 import BeautifulSoup

from functions.feed import FeedConfig
from functions.storage import get_storage


def get_post_karma(url):
    # disguising the request using headers
    page = requests.get(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'})
    soup = BeautifulSoup(page.content, "html.parser")
    if soup.title and soup.title == '403 Forbidden':
        raise AssertionError(
            '403 Forbidden error when trying to access ' + url + ' You may need to change the headers to something else.')
    return soup.find('h1', {'class': 'PostsVote-voteScore'}).text


def get_podcast_feed(feedconfig: FeedConfig):
    # Get feed from source
    feed = feedparser.parse(feedconfig.source)
    # Get storage handler
    storage = get_storage(local=True)

    # Update values from provided configuration
    feed['feed']['title'] = feedconfig.title
    feed['feed']['image']['href'] = feedconfig.image_url

    # Retrieve removed authors
    removed_authors_file = storage.get_file(feedconfig.removed_authors_file)
    removed_authors = [l for l in removed_authors_file.readlines()]
    removed_authors_file.close()

    # Filter out entries from removed authors
    feed['entries'] = [e for e in feed['entries'] if e['author'] not in removed_authors]

    # Filter entries by forum using the provided title regex
    if feedconfig.title_regex:
        regex = re.compile(feedconfig.title_regex)
        feed['entries'] = list(filter(lambda s: regex.match(s['title']), feed['entries']))

    # TODO: Filter out entries based on the search period.

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

    # Pseudo-code:
    # feed = retrieve_feed_from_url(url) - done
    # values_for_podcast_feed = get_values_for_podcast_feed('Alignment Forum')
    # feed.update_values(values_for_podcast_feed) - done
    # Filter out entries from removed authors - done
    # feed.entries = [e for entry in feed.entries if e.author not in removed_authors] - done
