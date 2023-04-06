from datetime import datetime
from difflib import SequenceMatcher
from time import strptime, mktime
from typing import List, Tuple
from urllib.parse import urlparse
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

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


def remove_entries_from_removed_authors(feed: Element, storage: StorageInterface):
    """
    Take an element tree and remove the entries whose author is in the list of removed authors.

    Args:
        feed: An xml element tree
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
        feed: An xml element tree
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


def filter_episodes(feed, feed_config, running_on_gcp) -> List[Element] | None:
    """
    Return a list of xml elements representing episodes which have been filtered by author, forum and date.

    Episodes
    - written by an author present in the list of removed authors,
    - not matching the forum prefix from the `feed_config` object or
    - published outside the search period defined in the `feed_config` object
    won't be returned


    Args:
        feed: xml Element representing the feed
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


def episode_is_in_history(episode_title: str, feed_config, running_on_gcp) -> bool:
    storage = create_storage(feed_config, running_on_gcp)
    # Read history titles from storage
    history_titles = storage.read_history_titles()

    for history_title in history_titles:
        # If the title matches the history_title by more than 90%, then we have added the title to the history_titles file in the past.
        if SequenceMatcher(None, episode_title, history_title).ratio() > 0.9:
            return True
    return False


def get_new_episodes_from_beyondwords_feed(feed_config, running_on_gcp) -> List[Element] | None:
    """
    Return an xml element representing an individual episode's feed. The returned episode is selected from the
    BeyondWords feed after filtering by removed author, date and forum using the meta-data in the `feed_config` object.

    Args:
        feed_config: Object with meta-data and filtering criteria

    Returns: The xml element that fulfilled the filtering criteria and has the most karma amongst the posts that made
    it through the filter

    """
    # Get feed from source
    feed = get_feed_tree_from_source(feed_config.source)

    # Filter episodes from feed
    new_episodes = filter_episodes(feed, feed_config, running_on_gcp)

    # Get entry with the most karma
    max_karma_entry = max(new_episodes, key=lambda post: get_post_karma(post.find('link').text),
                          default=None)

    no_max_karma_entry = max_karma_entry is None

    if no_max_karma_entry:
        print('no max karma entry found. exiting.')
        return None

    max_karma_entry_title = max_karma_entry.find('title').text

    print(f"Max karma entry found: '{max_karma_entry_title}'")

    if episode_is_in_history(max_karma_entry_title, feed_config, running_on_gcp):
        print('max_karma_entry is in history, exiting.')
        return None

    print('max_karma_entry not in history, returning max_karma_entry')

    return max_karma_entry


def add_episode_to_history(feed_config, episode: Element, running_on_gcp):
    storage = create_storage(feed_config, running_on_gcp)
    history_titles = storage.read_history_titles()
    history_titles += [episode.find('title').text]
    storage.write_history_titles(history_titles)


def update_podcast_feed(
        feed_config: FeedGeneratorConfig,
        running_on_gcp
) -> Tuple[str, str] | None:
    """
    Get an RSS feed for podcast apps that is produced from a source and applying filtering criteria defined in the
    provided feed_config object.

    Args: feed_config: Object with meta-data and filtering criteria to produce an RSS feed file.

    Returns: The file name of the produced xml string and the xml string and the title of the new episode
    """

    new_episode = get_new_episodes_from_beyondwords_feed(feed_config, running_on_gcp)

    if len(new_episode) == 0:
        return None
    storage = create_storage(feed_config, running_on_gcp)
    podcast_feed = storage.read_podcast_feed()

    # Update values from the provided configuration
    podcast_feed.find('./channel/title').text = feed_config.title
    podcast_feed.find('./channel/image/url').text = feed_config.image_url

    # Register namespaces before parsing to string.
    namespaces = {
        # The atom namespace is not used in the resulting feeds and is not added to the xml files.
        "atom": "http://www.w3.org/2005/Atom",
        "itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd",
        "content": "http://purl.org/rss/1.0/modules/content/"
    }
    for prefix, uri in namespaces.items():
        ElementTree.register_namespace(prefix, uri)

    podcast_feed.find('channel').append(new_episode)
    add_episode_to_history(feed_config, new_episode, running_on_gcp)

    xml_feed = ElementTree.tostring(podcast_feed, encoding='UTF-8', method='xml', xml_declaration=True)

    print(f"writing to RSS feed with new entry {new_episode.find('title').text}")

    storage = create_storage(feed_config, running_on_gcp)
    storage.write_podcast_feed(xml_feed)
    return storage.rss_file, new_episode.find('title').text


def generate_beyondwords_feed():
    pass
