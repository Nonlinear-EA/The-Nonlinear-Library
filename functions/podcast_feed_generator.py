from datetime import datetime
from difflib import SequenceMatcher
from time import strptime, mktime
from typing import List, Tuple
from urllib.parse import urlparse
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

import requests
from bs4 import BeautifulSoup

from feed import FeedGeneratorConfig
from storage import StorageInterface, create_storage


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


def remove_entries_from_removed_authors(feed: Element, storage: StorageInterface):
    """
    Take an element tree and remove the entries whose author is in the list of removed authors.

    Args:
        feed: An XML element tree
        storage: Storage handler

    """
    # Retrieve removed authors
    removed_authors = storage.read_removed_authors()
    for item in feed.findall('channel/item'):
        author = item.find('author').text
        if author in removed_authors:
            feed.find('channel').remove(item)


def filter_entries_by_search_period(feed: Element, feed_config: FeedGeneratorConfig):
    """
    Return entries that were published within a period defined in the FeedGeneratorConfig object.
    
    Args:
        feed: An XML element tree
        feed_config: Parameters for podcast feed generation

    """
    # Filter posts based on the requested search period
    # Get search period as timedelta
    search_period = feed_config.get_search_period_timedelta()
    # Define the time of the oldest post that should come through
    oldest_post_time = datetime.now() - search_period

    for entry in feed.findall('channel/item'):
        published_date_str = entry.find('pubDate').text
        published_date = mktime(strptime(published_date_str, feed_config.date_format))
        if published_date <= oldest_post_time.timestamp():
            feed.find('channel').remove(entry)


def get_feed_tree_from_source(url) -> Element:
    """
    Return an element tree from the provided url (or path to local file).

    Args:
        url: Url to a XML document

    Returns: A XML element tree
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

    # Parse to a XML tree
    return ElementTree.fromstring(xml_data)


def filter_items(feed, feed_config, running_on_gcp) -> List[Element]:
    """
    Return a list of XML elements representing episodes which have been filtered by author, forum and date.

    Episodes
    - written by an author present in the list of removed authors,
    - not matching the forum prefix from the `feed_config` object or
    - published outside the search period defined in the `feed_config` object
    won't be returned


    Args:
        feed: XML Element representing the feed
        feed_config: Configuration object with meta-data to filter episodes

    Returns: List of episodes from the feed

    """

    # Get storage handler
    storage = create_storage(feed_config, running_on_gcp)

    def get_number_of_entries():
        return len(feed.findall('channel/item'))

    n_entries = get_number_of_entries()

    # Remove entries from removed authors
    remove_entries_from_removed_authors(feed, storage)
    print(f'Removed {n_entries - get_number_of_entries()} entries due to removed author.')

    n_entries = get_number_of_entries()

    # Filter entries by checking if their titles match the provided title_prefix
    if feed_config.title_prefix:
        for entry in feed.findall('channel/item'):
            if not entry.find('title').text.startswith(feed_config.title_prefix):
                feed.find('channel').remove(entry)

    # Update guid if provided in the feed_config
    if feed_config.guid_suffix:
        for item in feed.findall('channel/item'):
            guid = item.find('guid')
            guid.text += feed_config.guid_suffix

    print(
        f'Removed {n_entries - get_number_of_entries()} entries because of title mismatch. {get_number_of_entries()} entries remaining.')
    n_entries = get_number_of_entries()

    if feed_config.search_period:
        filter_entries_by_search_period(feed, feed_config)
    print(
        f'Removed {n_entries - get_number_of_entries()} entries because they were not within the search period. {get_number_of_entries()} entries remaining.')

    return feed.findall('channel/item')

def titles_match(title_a: str, title_b: str) -> bool:
    return SequenceMatcher(None, title_a, title_b).ratio() > 0.9


def get_new_items_from_beyondwords_feed(feed_config, running_on_gcp) -> List[Element]:
    """
    Return a XML element representing the <item></item> stanza in a RSS feed. The <item></item> stanza represents one forum post. The returned item is selected from the
    BeyondWords feed after filtering by removed author, date and forum using the meta-data in the `feed_config` object.

    Args:
        feed_config: Object with meta-data and filtering criteria

    Returns: The XML item that fulfilled the filtering criteria and has the most karma amongst the posts that made
    it through the filter

    """
    # Get feed from source
    feed = get_feed_tree_from_source(feed_config.source)

    # Filter items from feed
    new_items = filter_items(feed, feed_config, running_on_gcp)

    if feed_config.top_post_only:
        # Get item with the most karma
        max_karma_item = max(new_items, key=lambda post: get_post_karma(post.find('link').text),
                             default=None)

        if max_karma_item is None:
            print('no max karma entry found. exiting.')
            return []
        else:
            print(f"Max karma entry found: '{max_karma_item.find('title').text}'")
            new_items = [max_karma_item]

    print(f'{len(new_items)} items matched the filters')

    return new_items


def create_new_list_only_containing_items_that_havent_been_added_to_the_rss_file(podcast_feed, new_items):
    items_which_have_not_been_added = []
    for new_item in new_items:
        already_added_to_rss_file = False
        for item in podcast_feed.findall('./channel/item'):
            if titles_match(item.find('title').text, new_item.find('title').text):
                already_added_to_rss_file = True
        if not already_added_to_rss_file:
            items_which_have_not_been_added.append(new_item)
    return items_which_have_not_been_added

def update_podcast_feed(
        feed_config: FeedGeneratorConfig,
        running_on_gcp
) -> Tuple[str, list] | None:
    """
    Get an RSS feed for podcast apps that is produced from a source and applying filtering criteria defined in the
    provided feed_config object.

    Args: feed_config: Object with meta-data and filtering criteria to produce an RSS feed file.

    Returns: The file name of the produced XML string and the xml string and the title of the new episode
    """

    new_items = get_new_items_from_beyondwords_feed(feed_config, running_on_gcp)
    if len(new_items) == 0:
        print('No items match the filter. Returning.')
        return None

    storage = create_storage(feed_config, running_on_gcp)
    podcast_feed = storage.read_podcast_feed()

    new_items = create_new_list_only_containing_items_that_havent_been_added_to_the_rss_file(podcast_feed, new_items)
    if len(new_items) == 0:
        print('No items were found which are not already contained within the RSS feed. Returning.')
        return None

    # Update values from the provided configuration
    podcast_feed.find('./channel/title').text = feed_config.title
    podcast_feed.find('./channel/image/url').text = feed_config.image_url

    # Register namespaces before parsing to string.
    namespaces = {
        # The atom namespace is not used in the resulting feeds and is not added to the XML files.
        "atom": "http://www.w3.org/2005/Atom",
        "itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd",
        "content": "http://purl.org/rss/1.0/modules/content/"
    }
    for prefix, uri in namespaces.items():
        ElementTree.register_namespace(prefix, uri)

    for item in new_items:
        print('Adding item with title ', item.find('title').text, ' to the RSS feed.')
        podcast_feed.find('./channel').append(item)

    xml_feed = ElementTree.tostring(podcast_feed, encoding='UTF-8', method='xml', xml_declaration=True)

    storage = create_storage(feed_config, running_on_gcp)
    storage.write_podcast_feed(xml_feed)

    return storage.rss_filename, [item.find('title').text for item in new_items]


def generate_beyondwords_feed():
    pass
