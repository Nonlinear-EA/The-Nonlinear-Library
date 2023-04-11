from datetime import datetime
from difflib import SequenceMatcher
from time import strptime, mktime
from typing import List, Tuple
from urllib.parse import urlparse
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

import feedparser
import requests
from bs4 import BeautifulSoup

from feed import FeedGeneratorConfig, BeyondWordsInputConfig, BaseFeedConfig
from functions.configs import beyondwords_feed_namespaces
from storage import create_storage


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


def register_namespaces_on_elementtree():
    # Register namespaces before parsing to string.
    namespaces = {
        'atom': 'http://www.w3.org/2005/Atom',
        'itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd',
        'content': 'http://purl.org/rss/1.0/modules/content/',
        'dc': 'http://purl.org/dc/elements/1.1/'
    }
    for prefix, uri in namespaces.items():
        ElementTree.register_namespace(prefix, uri)


def remove_items_from_removed_authors(feed: Element, config: BaseFeedConfig, running_on_gcp):
    """
    Take an element tree and remove the entries whose author is in the list of removed authors.

    Args:
        running_on_gcp: Whether the function is currently running on Google Cloud Platform or locally.
        config: Configuration parameters to retrieve storage interface
        feed: An XML element tree

    """
    # Retrieve removed authors
    storage = create_storage(config, running_on_gcp)
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

    def get_number_of_entries():
        return len(feed.findall('channel/item'))

    n_entries = get_number_of_entries()

    # Remove entries from removed authors
    remove_items_from_removed_authors(feed, feed_config, running_on_gcp)
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


def item_is_in_history(item_title: str, history_titles: list[str]) -> bool:
    return any(SequenceMatcher(None, item_title, history_title).ratio() > 0.9 for history_title in history_titles)


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

    storage = create_storage(feed_config, running_on_gcp)
    history_titles = storage.read_history_titles()
    new_items_not_in_history = [item for item in
                                new_items if not item_is_in_history(item.find('title').text, history_titles)]

    print(f'{len(new_items_not_in_history)} of the new items were not in the history.')

    return new_items_not_in_history


def add_items_to_history(feed_config, items: List[Element], running_on_gcp):
    storage = create_storage(feed_config, running_on_gcp)
    history_titles = storage.read_history_titles()
    history_titles += [item.find('title').text for item in items]
    storage.write_history_titles(history_titles)


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
        return None

    storage = create_storage(feed_config, running_on_gcp)
    podcast_feed = storage.read_podcast_feed()

    # Update values from the provided configuration
    podcast_feed.find('./channel/title').text = feed_config.title
    podcast_feed.find('./channel/image/url').text = feed_config.image_url

    add_items_to_history(feed_config, new_items, running_on_gcp)

    register_namespaces_on_elementtree()

    xml_feed = ElementTree.tostring(podcast_feed, encoding='UTF-8', method='xml', xml_declaration=True)

    print(f"Writing to RSS feed with {len(new_items)} new entries")

    storage = create_storage(feed_config, running_on_gcp)
    storage.write_podcast_feed(xml_feed)

    return storage.rss_file, [episode.find('title').text for episode in new_items]


def get_beyondwords_feed_template():
    root = Element('rss')
    root.append(Element('channel'))
    channel = root.find('channel')
    channel.append(Element('title'))
    channel.append(Element('description'))
    channel.append(Element('link'))
    channel.append(Element('image'))
    image = channel.find('image')
    image.append(Element('url'))
    channel.append(Element('generator'))
    channel.append(Element('lastBuildDate'))
    channel.append(Element('atom:link'))
    return root


def cdatastr(text):
    return f"<![CDATA[{text}]]>"


def replace_cdata_strings(feed, paths_to_replace, namespaces):
    for path in paths_to_replace:
        if feed.findall(path, namespaces) is not None:
            for item in feed.findall(path, namespaces):
                item.text = cdatastr(item.text)
    return feed


def remove_posts_in_history(feed, config, running_on_gcp):
    storage = create_storage(config, running_on_gcp)

    posts = storage.read_beyondwords_history_titles()

    n_entries = len(feed.findall('channel/item'))
    for item in feed.findall('channel/item'):
        if item.find('title').text in posts:
            feed.find('channel').remove(item)
        else:
            posts += [item.find('title').text]
    print(f'Removed {n_entries - len(feed.findall("channel/item"))} existing posts.')
    return feed


def find_website(url, short=True):
    website = 'Unknown'
    if 'forum.effectivealtruism.org' in url:
        website = 'EA' if short else 'The Effective Altruism Forum'
    elif 'lesswrong.com' in url:
        website = 'LW' if short else "LessWrong"
    elif 'alignmentforum.org' in url:
        website = 'AF' if short else "The AI Alignment Forum"

    return website


def prepend_website_abbreviation_to_feed_item_titles(feed):
    prefix = find_website(feed.find('channel/link').text)
    for item_title in feed.findall('channel/item/title'):
        item_title.text = f'{prefix} - {item_title.text}'
    return feed


def save_beyondwords_feed(feed, config, running_on_gcp):
    # Register namespaces
    register_namespaces_on_elementtree()
    storage = create_storage(config, running_on_gcp)
    feed_str = ElementTree.tostring(feed, encoding='UTF-8', method='xml', xml_declaration=True)
    storage.write_podcast_feed(feed_str)
    return feed_str


def save_post_titles(feed, config, running_on_gcp):
    post_titles = [title.text for title in feed.findall('channel/item/title')]
    storage = create_storage(config, running_on_gcp)
    storage.write_beyondwords_history_titles(post_titles)


def add_author_tag_to_feed_items(feed):
    for item in feed.findall('channel/item'):
        author = Element('author')
        author.text = item.find('dc:creator', namespaces=beyondwords_feed_namespaces).text.replace('_', ' ')
        item.append(author)
    return feed


def append_author_to_item_titles(feed):
    for item in feed.findall('channel/item'):
        item.find('title').text = f'{item.find("title").text} by {item.find("author").text}'
    return feed


def get_intro_str(item):
    title = item.find('title').text
    published_date_str = item.find('pubDate').text
    published_datetime = datetime.strptime(published_date_str, '%a, %d %b %Y %H:%M:%S %Z')
    summary_date_str = published_datetime.strftime('%B %-d, %Y')
    website = find_website(item.find('link').text, short=False)
    authors = item.find('author').text
    return f"Welcome to The Nonlinear Library, where we use Text-to-Speech software to convert the best writing from " \
           f"the Rationalist and EA communities into audio. This is: {title.rstrip()}, published by " \
           f"{authors} on {summary_date_str} on {website}. "


def modify_item_content(feed):
    for item in feed.findall('channel/item'):
        intro_str = get_intro_str(item)
        pass
    return feed


def generate_beyondwords_feed(config: BeyondWordsInputConfig, running_on_gcp=True):
    """
    Download posts from source and save an XML file to storage with those posts.

    Returns:

    """

    feed = get_feed_tree_from_source(config.source)

    configparser_feed = feedparser.parse(ElementTree.tostring(feed))

    # Remove posts that have already been added to a feed
    feed = remove_posts_in_history(feed, config, running_on_gcp)

    # The author tag is used to remove posts from removed authors, append it to each item
    feed = add_author_tag_to_feed_items(feed)

    feed = modify_item_content(feed)

    # Save the new titles by appending them to the beyondwords titles file
    save_post_titles(feed, config, running_on_gcp)

    # Remove entries from removed authors
    remove_items_from_removed_authors(feed, config, running_on_gcp)

    # Modify item titles by prepending the forum abbreviation
    feed = prepend_website_abbreviation_to_feed_item_titles(feed)

    # Modify item titles by appending 'by <author>'
    feed = append_author_to_item_titles(feed)

    # The list below contains the xpaths of the items that contain XML CDATA strings
    cdata_xpaths = [
        'channel/title',
        'channel/description',
        'channel/item/description',
        'channel/item/dc:creator'
        'channel/item/title'
    ]

    # Replace text of elements with CDATA strings with CDATA strings
    feed = replace_cdata_strings(feed, cdata_xpaths, beyondwords_feed_namespaces)

    save_beyondwords_feed(feed, config, running_on_gcp)

    return feed
