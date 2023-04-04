from datetime import datetime
from difflib import SequenceMatcher
from time import strptime, mktime
from typing import Tuple
from urllib.parse import urlparse
from xml.etree import ElementTree

import requests
from bs4 import BeautifulSoup

from functions.feed import FeedGeneratorConfig
from functions.storage import StorageInterface, create_storage


def get_post_karma(url) -> int:
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
    return int(soup.find('h1', {'class': 'PostsVote-voteScore'}).text)


def remove_entries_from_removed_authors(feed: ElementTree, storage: StorageInterface):
    """
    Take an element tree and remove the entries whose author is in the list of removed authors.

    Args:
        feed: An xml element tree
        storage: Storage handler

    """

    # Retrieve removed authors
    removed_authors = storage.read_removed_authors()

    for item in feed.findall('./channel/item'):
        author = item.find('author').text
        if author in removed_authors:
            feed.remove(item)


def filter_entries_by_search_period(feed: ElementTree, feed_config: FeedGeneratorConfig):
    """
    Return entries that were published within a period defined in the FeedGeneratorConfig object.
    
    Args:
        feed: An xml element tree
        feed_config: Parameters for podcast feed generation

    """
    # Filter posts based on the requested search period
    # Get search period as timedelta
    search_period = feed_config.get_search_period_timedelta()
    # Define the time of the oldest post that should come through
    oldest_post_time = datetime.now() - search_period

    for entry in feed.findall('./channel/item'):
        published_date_str = entry.find('pubDate').text
        published_date = mktime(strptime(published_date_str, feed_config.date_format))
        if published_date <= oldest_post_time.timestamp():
            feed.find('./channel').remove(entry)


def get_feed_tree_from_source(url) -> ElementTree:
    """
    Return an element tree from the provided url (or path to local file).

    Args:
        url: Url to a xml document

    Returns: A xml element tree
    """

    parsed_uri = urlparse(url)
    if not parsed_uri.scheme:
        # If url has no scheme, treat it as a local path.
        tree = ElementTree.parse(url)
        return tree.getroot()

    if parsed_uri.scheme not in ['http', 'https']:
        raise ValueError('Invalid url scheme')

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/83.0.4103.97 Safari/537.36'}
    response = requests.get(url, headers=headers)
    xml_data = response.text

    # Parse to a xml tree
    return ElementTree.fromstring(xml_data)


def generate_podcast_feed(
        feed_config: FeedGeneratorConfig,
        running_on_gcp
) -> Tuple[str | None, ElementTree.ElementTree | None]:
    """
    Get an RSS feed for podcast apps that is produced from a source and applying filtering criteria defined in the
    provided feed_config object.

    Args: feed_config: Object with meta-data and filtering criteria to produce an RSS feed file.

    Returns: The file name of the produced xml string and the xml string.
    """

    # Get feed from source
    feed = get_feed_tree_from_source(feed_config.source)
    n_entries = len(feed.findall('./channel/item'))

    # Get storage handler
    storage = create_storage(feed_config, running_on_gcp)

    # Remove entries from removed authors
    remove_entries_from_removed_authors(feed, storage)
    print(f'Removed {n_entries - len(feed.findall("./channel/item"))} entries due to removed author.')

    def get_number_of_entries():
        return len(feed.findall('channel/item'))

    n_entries = get_number_of_entries()
    # Filter entries by checking if their titles match the provided title_prefix
    if feed_config.title_prefix:
        for entry in feed.findall('./channel/item'):
            if not entry.find('title').text.startswith(feed_config.title_prefix):
                feed.find('channel').remove(entry)

    print(f'Removed {n_entries - len(feed.findall("./channel/item"))} entries because of title mismatch...')
    n_entries = get_number_of_entries()

    if feed_config.search_period:
        filter_entries_by_search_period(feed, feed_config)
    print(f'Removed {n_entries - len(feed.findall("./channel/item"))} entries outside search period...')

    # Get entry with the most karma
    max_karma_entry = max(feed.findall('./channel/item'), key=lambda entry: get_post_karma(entry.find('link').text))

    # Read history titles from storage
    history_titles = storage.read_history_titles()

    # Check if max karma post is in history
    def entry_title_is_in_history(entry):
        return max([SequenceMatcher(None, entry.find('title').text, h).ratio() for h in history_titles]) > 0.9

    if entry_title_is_in_history(max_karma_entry):
        return None, None

    history_titles += [max_karma_entry.find('title').text]
    storage.write_history_titles(history_titles)

    # Update values from the provided configuration
    feed.find('./channel/title').text = feed_config.title
    feed.find('./channel/image/url').text = feed_config.image_url

    # Update guid if provided in the feed_config
    if feed_config.guid_suffix:
        for item in feed.findall('./channel/item'):
            guid = item.find('guid')
            guid.text += feed_config.guid_suffix

    # Register namespaces before parsing to string.
    namespaces = {
        # The atom namespace is not used in the resulting feeds and is not added to the xml files.
        "atom": "http://www.w3.org/2005/Atom",
        "itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd",
        "content": "http://purl.org/rss/1.0/modules/content/"
    }
    for prefix, uri in namespaces.items():
        ElementTree.register_namespace(prefix, uri)

    xml_feed = ElementTree.tostring(feed, encoding='UTF-8', method='xml', xml_declaration=True)
    storage.write_podcast_feed(xml_feed)

    return storage.output_feed_filename, feed


def generate_beyondwords_feed():
    pass
