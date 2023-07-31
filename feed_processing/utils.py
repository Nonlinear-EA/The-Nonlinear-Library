import logging
from datetime import datetime
from difflib import SequenceMatcher
from time import strptime, mktime
from typing import List, Tuple
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from lxml import etree
from lxml.etree import XMLParser, Element, CDATA

from feed_processing.configs import beyondwords_feed_namespaces
from feed_processing.feed_config import PodcastProviderFeedConfig, BaseFeedConfig
from feed_processing.storage import create_storage

outro_str = '<p>Thanks for listening. To help us out with The Nonlinear Library or to learn more, please visit ' \
            'nonlinear.org</p>'


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


def remove_items_from_removed_authors(feed: Element, config: BaseFeedConfig, running_on_gcp):
    """
    Take an element tree and remove the entries whose author is in the list of removed authors.

    Args:
        running_on_gcp: True if running in Google Cloud Platform, False if running locally.
        config: Configuration parameters to retrieve storage interface
        feed: An XML element tree

    """
    logger = logging.getLogger("remove_items_from_removed_authors")
    # Retrieve removed authors
    storage = create_storage(config, running_on_gcp)
    removed_authors = storage.read_removed_authors()
    for item in feed.findall('channel/item'):
        author = item.find('author').text.strip()
        if author in removed_authors:
            feed.find('channel').remove(item)
            logger.info(f"Removing post '{item.find('title').text}' because it was written by removed author {author}.")
    return feed


def filter_entries_by_search_period(feed: Element, feed_config: PodcastProviderFeedConfig):
    """
    Return entries that were published within a period defined in the FeedGeneratorConfig object.

    Args:
        feed: An XML element tree
        feed_config: Parameters for podcast feed generation

    """
    # Filter posts based on the requested search period
    # Get search period as timedelta
    period_timedelta = feed_config.get_search_period_timedelta()
    # Define the time of the oldest post that should come through
    oldest_post_time = datetime.now() - period_timedelta

    for entry in feed.findall('channel/item'):
        published_date_str = entry.find('pubDate').text
        published_datetime = strptime(published_date_str, feed_config.date_format)
        published_date = mktime(published_datetime)
        if published_date <= oldest_post_time.timestamp():
            feed.find('channel').remove(entry)

    return feed


def download_file_from_url(url, cache: bool = True, encoding: str = "utf-8"):
    parsed_uri = urlparse(url)

    if parsed_uri.scheme not in ['http', 'https']:
        raise ValueError('Invalid url scheme')

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/83.0.4103.97 Safari/537.36'}
    if not cache:
        headers = {
            **headers,
            "Cache-Control": "no-cache",
            "Pragma": "no-cache"
        }

    response = requests.get(url, headers=headers)
    return bytes(response.text, encoding)


def get_feed_tree_from_url(url, cache: bool = True) -> Element:
    """
    Return an element tree from the provided url (or path to local file).

    Args:
        cache: Cache requests data
        url: Url to a XML document

    Returns: A XML element tree
    """

    parser = XMLParser(strip_cdata=False, encoding='utf-8')

    try:
        xml_data = download_file_from_url(url, cache=False, encoding="utf-8")
    except ValueError:
        tree = etree.parse(url, parser)
        return tree.getroot()

    # Parse to an XML tree
    return etree.fromstring(xml_data, parser)


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
    feed = get_feed_tree_from_url(feed_config.source)

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


def cdata_element(tag, text):
    element = etree.Element(tag)
    element.text = etree.CDATA(text)
    return element


def replace_cdata_strings(feed, paths_to_replace, namespaces):
    for path in paths_to_replace:
        for item in feed.findall(path, namespaces):
            item.text = etree.CDATA(item.text)
    return feed


def remove_posts_in_history(feed, config, running_on_gcp):
    storage = create_storage(config, running_on_gcp)

    posts = storage.read_podcast_feed()
    history_titles = [title.text for title in posts.findall('channel/item/title')]

    def title_is_in_titles(title):
        return any([title in history_title for history_title in history_titles])

    n_entries = len(feed.findall('channel/item'))
    for item in feed.findall('channel/item'):
        if title_is_in_titles(item.find('title').text):
            feed.find('channel').remove(item)
        else:
            history_titles += [item.find('title').text]
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
        item_title.text = f'{prefix} - {item_title.text.strip()}'
    return feed


def get_feed_str(feed):
    return etree.tostring(feed, xml_declaration=True, encoding='utf-8')


def save_feed(feed, storage):
    xml_str = get_feed_str(feed)
    storage.write_podcast_feed(xml_str)


def append_new_items_to_feed(new_items, feed):
    """
    Returns a feed with appended `new_items`, while checking that the item titles are not duplicated.
    Args:
        new_items: Items to be added to the feed.
        feed: Feed which will be appended the new items.

    Returns: Feed with new items.

    """
    logger = logging.getLogger(f"function:{append_new_items_to_feed.__name__}")

    existing_titles = [title.text.strip() for title in feed.findall("channel/item/title")]
    appended_items = []
    for item in new_items:
        if not item_title_is_duplicate(item.find("title").text, existing_titles):
            feed.find('channel').append(item)
            appended_items += [item]
            logger.info(f"New item titled '{item.find('title').text}' found.")
    return appended_items, feed


def add_author_tag_to_feed_items(feed):
    for item in feed.findall('channel/item'):
        author = etree.Element('author')
        author.text = item.find('dc:creator', namespaces=beyondwords_feed_namespaces).text.replace('_', ' ')
        item.append(author)
    return feed


def append_author_to_item_titles(feed):
    for item in feed.findall('channel/item'):
        item.find('title').text = CDATA(f'{item.find("title").text.strip()} by {item.find("author").text.strip()}')
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


def get_html_link_to_original_article(item):
    link = item.find("link")
    return f'<a href="{link.text}">Link to original article</a><br/>'


def edit_item_description(feed):
    for item in feed.findall('channel/item'):
        description_text = item.find('description').text
        description_html = BeautifulSoup(description_text, "html.parser")
        description_text_without_date = "".join(str(content) for content in description_html.contents[3:])
        intro_str = get_intro_str(item)
        description = f"<p>{intro_str}</p> {description_text_without_date} <p>{outro_str}</p>"
        item.find('description').text = etree.CDATA(description)

    return feed


def get_titles_from_feed(feed_filename: str, config: BaseFeedConfig, running_on_gcp: bool = True):
    feed = get_feed(feed_filename, config, running_on_gcp)
    return [title.text for title in feed.findall('channel/item/title')]


def get_feed(filename: str, config: BaseFeedConfig, running_on_gcp: bool = True):
    storage = create_storage(config, running_on_gcp)
    return storage.read_podcast_feed(filename)


def item_title_is_duplicate(title: str, existing_titles: List[str]):
    title_exists = (title.strip() in existing_title.strip() for existing_title in existing_titles)
    return any(title_exists)


def remove_items_also_found_in_other_relevant_files(feed: Element, existing_titles: List[str]) -> Element:
    logger = logging.getLogger(f"function:{remove_items_also_found_in_other_relevant_files.__name__}")
    n_entries = len(feed.findall('channel/item'))
    for item in feed.findall('channel/item'):
        if item_title_is_duplicate(item.find('title').text, existing_titles):
            feed.find('channel').remove(item)
    logger.info(f'Removed {n_entries - len(feed.findall("channel/item"))} duplicate entries.')
    return feed


def filter_entries_by_forum_title_prefix(feed, title_prefix):
    # Filter entries by checking if their titles match the provided title_prefix
    n_items = len(feed.findall("channel/item"))
    if title_prefix:
        for entry in feed.findall('channel/item'):
            if not entry.find('title').text.startswith(title_prefix):
                feed.find('channel').remove(entry)
    logger = logging.getLogger(f"function:{filter_entries_by_forum_title_prefix.__name__}")
    logger.info(
        f"Removed {n_items - len(feed.findall('channel/item'))} because they didn't match the prefix '{title_prefix}'")
    return feed


def find_top_post(feed: Element) -> Tuple[Element, int]:
    top_karma = 0
    top_post = None
    for i, item in enumerate(feed.findall("channel/item")):
        post_karma = get_post_karma(item.find("link").text)
        if post_karma > top_karma:
            top_karma = post_karma
            top_post = item
    return top_post, top_karma


def filter_top_post(feed: Element):
    top_post, _ = find_top_post(feed)
    top_post_id = top_post.find("guid").text

    non_top_posts = feed.xpath(f"//channel/item[guid != '{top_post_id}']")

    for item in non_top_posts:
        feed.find("channel").remove(item)

    return feed


def create_feed_element(feed, xpath, namespaces=None):
    element = feed.find(xpath)
    if element is None:
        breadcrumbs = xpath.split("/")
        if not breadcrumbs:
            raise ValueError(f"Invalid XPath {breadcrumbs}")

        parent_path = "/".join(breadcrumbs[:-1])
        child = breadcrumbs[-1]
        parent = feed.find(parent_path)
        if parent is None:
            feed, parent = create_feed_element(feed, parent_path)
        element = etree.SubElement(parent, child)

    return feed, element


def update_feed_datum(feed, xpath: str, new_value: str, namespaces: object = None,
                      create_element_if_xpath_element_is_none=True):
    element = feed.find(xpath, namespaces=namespaces)
    if element is None and create_element_if_xpath_element_is_none:
        feed, element = create_feed_element(feed, xpath, namespaces)
    elif element is None and not create_element_if_xpath_element_is_none:
        return feed
    element.text = new_value
    return feed


def add_link_to_original_article_to_feed_items_description(feed):
    for item in feed.findall("channel/item"):

        item_description = item.find("description")

        if item_description is None:
            continue

        description_text = item_description.text
        description_html = BeautifulSoup(description_text, features="lxml")

        # TODO: Check for a tag with the post to the original article before adding it, otherwise it might be
        #  duplicated.
        link_to_original_article = item.find("link")
        if link_to_original_article is None:
            continue

        link_to_original_article_html = get_html_link_to_original_article(item)
        description_html.body.insert(0, BeautifulSoup(link_to_original_article_html, "html.parser").a)
        item.find("description").text = CDATA(str(description_html))

    return feed


def remove_posts_with_less_than_the_minimum_characters_in_description(feed, min_chars: int):
    logger = logging.getLogger(f"function:{remove_posts_with_less_than_the_minimum_characters_in_description.__name__}")
    for item in feed.findall('channel/item'):
        if len(item.find("description").text) < min_chars:
            feed.find('channel').remove(item)
            logger.info(f"Removed item '{item.find('title').text}' because it has less than {min_chars}.")
    return feed


def remove_posts_without_paragraphs_in_description(feed):
    logger = logging.getLogger(f"function:{remove_posts_without_paragraphs_in_description.__name__}")
    for item in feed.findall('channel/item'):
        description_html = BeautifulSoup(item.find('description').text, 'html.parser')
        if len(description_html.find_all('p')) < 1:
            feed.find('channel').remove(item)
            logger.info(f"Removed item '{item.find('title').text}' due to empty content, possibly a cross post.")

    return feed


def add_content_to_feed_items(feed):
    for item in feed.findall("channel/item"):
        intro_str = get_intro_str(item)
        description_text = item.find('description').text
        content_text = intro_str + description_text + outro_str
        content_element = etree.SubElement(item, "content")
        content_element.text = CDATA(content_text)

    return feed
