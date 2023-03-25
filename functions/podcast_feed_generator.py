import ssl
from datetime import datetime
from difflib import SequenceMatcher
from time import strptime, mktime
from typing import Tuple, List

import feedparser
import requests
from bs4 import BeautifulSoup
from feedparser import FeedParserDict

from functions.feed import FeedGeneratorConfig
from functions.storage import create_storage, StorageInterface

if hasattr(ssl, '_create_unverified_context'):
    # noinspection PyProtectedMember
    ssl._create_default_https_context = ssl._create_unverified_context


def get_enclosure_data(entry) -> Tuple[str, str, str]:
    """
    Receives a dict that represents a feed entry and, if found, returns its enclosure's data (length, type and url).
    Args:
        entry: Dict representing a feed entry

    Returns: Tuple containing enclosure's length, type and url

    """
    enclosure_data = next(filter(lambda link: link['rel'] == 'enclosure', entry['links']), None)
    if not enclosure_data:
        raise Exception(f'No enclosure data found for entry: {entry["title"]}')
    return enclosure_data['length'], enclosure_data['type'], enclosure_data['url']


def get_entry_xml(entry: dict, image_url: str) -> str:
    """
    Returns a xml substring representing a single feed entry.
    Args:
        entry: Dict representing a single feed entry
        image_url: An url for the image to attach to this feed entry's xml

    Returns:

    """
    enclosure_length, enclosure_type, enclosure_url = get_enclosure_data(entry)

    def get_html_hyperlink_from_spotify(entry):
        return (f'<a href=\"{entry["link"]}\">Link to original article</a>'
                f'<br/>'
                f'<br/>')

    return (
        f'<item>'
        f'  <guid isPermaLink="{entry["guidislink"]}">{entry["guid"]}</guid>'
        f'  <title>{entry["title"].replace("&", "and")}</title>'
        f'  <description><![CDATA[{entry["summary"]}]]></description>'
        f'  <author>{entry["author"]}</author>'
        f'  <link>{entry["link"]}</link>'
        f'  <content:encoded><![CDATA[{get_html_hyperlink_from_spotify(entry)}]]></content:encoded>'
        f'  <enclosure length="{enclosure_length}" type="{enclosure_type}" url="{enclosure_url}"/>'
        f'  <pubDate>{entry["published"]}</pubDate>'
        f'  <itunes:title>{entry["title"]}</itunes:title>'
        f'  <itunes:subtitle><![CDATA[{entry["subtitle"]}]]></itunes:subtitle>'
        f'  <itunes:summary><![CDATA[{entry["summary"]}]]></itunes:summary>'
        f'  <itunes:author>{entry["author"]}</itunes:author>'
        f'  <itunes:image>{image_url}</itunes:image>'
        f'  <itunes:duration>{entry["itunes_duration"]}</itunes:duration>'
        f'  <itunes:keywords></itunes:keywords>'
        f'  <itunes:explicit>{entry["itunes_explicit"]}</itunes:explicit>'
        f'  <itunes:episodeType>{entry["itunes_episodetype"]}</itunes:episodeType>'
        f'  <itunes:episode>{entry["itunes_episode"]}</itunes:episode>'
        f'</item>')


def get_feed_xml(feed: FeedParserDict):
    """
    Returns a xml string representing an RSS feed from a dictionary.
    Args:
        feed: Dict representing a feed.

    Returns: xml string representing a feed.

    """
    entries_xml = "\n".join([get_entry_xml(entry, feed["feed"]["image"]["href"]) for entry in feed['entries']])
    return (
        f'<?xml version="1.0" encoding="{feed["encoding"]}"?>'
        f'  <rss xmlns:atom="{feed["namespaces"][""]}" xmlns:itunes="{feed["namespaces"]["itunes"]}" '
        f'      xmlns:content="{feed["namespaces"]["content"]}"'
        f'      version="2.0">'
        f'      <channel>'
        f'          <title>{feed["feed"]["title"]}</title>'
        f'          <description>{feed["feed"]["subtitle"]}</description>'
        f'          <author>{feed["feed"]["author"]}</author>'
        f'          <copyright>{feed["feed"]["rights"]}</copyright>'
        f'          <language>{feed["feed"]["language"]}</language>'
        f'          <link>{feed["feed"]["link"]}</link>'
        f'          <image><url>{feed["feed"]["image"]["href"]}</url></image>'
        f'          <itunes:keywords></itunes:keywords>'
        f'          <itunes:owner>'
        f'            <itunes:name>{feed["feed"]["publisher_detail"]["name"]}</itunes:name>'
        f'            <itunes:email>{feed["feed"]["publisher_detail"]["email"]}</itunes:email>'
        f'          </itunes:owner>'
        f'          <itunes:explicit>{"yes" if feed["feed"]["itunes_explicit"] else "no"}</itunes:explicit>'
        f'          <itunes:image href="{feed["feed"]["image"]["href"]}"/>'
        f'          <itunes:author>{feed["feed"]["publisher_detail"]["name"]}</itunes:author>'
        f'          <itunes:summary><![CDATA[{feed["feed"]["summary"]}]]></itunes:summary>'
        f'          <lastBuildDate>{feed["feed"]["updated"]}</lastBuildDate>'
        f'          {entries_xml}'
        '       </channel>'
        '   </rss>'
    )


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


def remove_entries_from_removed_authors(entries: List[dict], storage: StorageInterface):
    """
    Take a list of entries and remove those whose author is in the list of removed authors.

    Args:
        entries: List of feed entries
        storage: Storage handler

    """
    # Retrieve removed authors
    removed_authors = storage.read_removed_authors()

    # Filter out entries from removed authors
    return [e for e in entries if e['author'] not in removed_authors]


def filter_entries_by_search_period(entries: List[dict], feed_config: FeedGeneratorConfig):
    """
    Return entries that were published within a period defined in the FeedGeneratorConfig object.
    Args:
        entries: List of feed entries
        feed_config: Parameters for podcast feed generation

    Returns:

    """
    # Filter posts based on the requested search period
    # Get search period as timedelta
    search_period = feed_config.get_search_period_timedelta()
    # Define the time of the oldest post that should come through
    oldest_post_time = datetime.now() - search_period

    # Filter out posts published later than oldest_post_time
    def get_entry_published_time(entry: dict):
        return mktime(strptime(entry['published'], feed_config.date_format))

    return [entry for entry in entries if get_entry_published_time(entry) >= oldest_post_time.timestamp()]


def get_podcast_feed(feed_config: FeedGeneratorConfig):
    """
    Get an RSS feed for podcast apps that is produced from a source and applying filtering criteria defined in the
    provided feed_config object.

    Args: feed_config: Object with meta-data and filtering criteria to produce a RSS feed file.

    Returns: xml string
    """

    # Get feed from source
    feed = feedparser.parse(feed_config.source)
    n_entries = len(feed['entries'])

    # Get storage handler
    storage = create_storage(feed_config, local=True)

    # Remove entries from removed authors
    feed['entries'] = remove_entries_from_removed_authors(feed['entries'], storage)

    # Filter entries by checking if their titles match the provided title_prefix
    if feed_config.title_prefix:
        def title_starts_with_config_prefix(entry):
            return entry['title'].startswith(feed_config.title_prefix)

        feed['entries'] = list(filter(title_starts_with_config_prefix, feed['entries']))
        print(f'{n_entries - len(feed["entries"])} removed because of title mismatch...')

    if feed_config.search_period:
        feed['entries'] = filter_entries_by_search_period(feed['entries'], feed_config.search_period)

    # Get entry with the most karma
    max_karma_entry = max(feed['entries'], key=lambda entry: get_post_karma(entry['link']))

    # Read history titles from storage
    history_titles = storage.read_history_titles()

    # Check if max karma post is in history
    def entry_title_is_in_history(entry):
        return max([SequenceMatcher(None, entry['title'], h).ratio() for h in history_titles]) > 0.9

    if entry_title_is_in_history(max_karma_entry):
        return

    history_titles += [max_karma_entry['title']]
    storage.write_history_titles(history_titles)

    # Update values from the provided configuration
    feed['feed']['title'] = feed_config.title
    feed['feed']['image']['href'] = feed_config.image_url

    def get_entry_with_updated_guid(entry):
        return {
            **entry,
            "guidislink": 'true' if entry['guidislink'] else 'false',
            # TODO: Original code accesses the 'guid' value, but it is not found in this case. For now use id
            "guid": entry['id'] + feed_config.guid_suffix}

    feed['entries'] = list(map(get_entry_with_updated_guid, feed['entries']))
    xml_feed = get_feed_xml(feed)

    return xml_feed
