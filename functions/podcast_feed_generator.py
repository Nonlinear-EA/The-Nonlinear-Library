import ssl
from datetime import datetime
from difflib import SequenceMatcher
from time import strptime, mktime
from typing import Tuple

import feedparser
import requests
from bs4 import BeautifulSoup
from feedparser import FeedParserDict

from functions.feed import FeedGeneratorConfig
from functions.storage import create_storage

if hasattr(ssl, '_create_unverified_context'):
    # noinspection PyProtectedMember
    ssl._create_default_https_context = ssl._create_unverified_context


def get_html_hyperlink_from_spotify(entry):
    return (f'<a href=\"{entry["link"]}\">Link to original article</a>'
            f'<br/>'
            f'<br/>')


def get_enclosure_data(entry) -> Tuple[str, str, str]:
    enclosure_data = next(filter(lambda link: link['rel'] == 'enclosure', entry['links']), None)
    if not enclosure_data:
        raise Exception(f'No enclosure data found for entry: {entry["title"]}')
    return enclosure_data['length'], enclosure_data['type'], enclosure_data['url']


def get_entry_xml(entry: dict, image_url: str) -> str:
    enclosure_length, enclosure_type, enclosure_url = get_enclosure_data(entry)
    return (f'<item>'
            f'<guid isPermaLink="{entry["guidislink"]}">{entry["guid"]}</guid>'
            f'<title>{entry["title"]}</title>'
            f'<description><![CDATA[{entry["summary"]}]]></description>'
            f'<author>{entry["author"]}</author>'
            f'<link>{entry["link"]}</link>'
            f'<content:encoded><![CDATA[{get_html_hyperlink_from_spotify(entry)}]]></content:encoded>'
            f'<enclosure length="{enclosure_length}" type="{enclosure_type}" url="{enclosure_url}"/>'
            f'<pubDate>{entry["published"]}</pubDate>'
            f'<itunes:title>{entry["title"]}</itunes:title>'
            f'<itunes:subtitle><![CDATA[{entry["subtitle"]}]]></itunes:subtitle>'
            f'<itunes:summary><![CDATA[{entry["summary"]}]]></itunes:summary>'
            f'<itunes:author>{entry["author"]}</itunes:author>'
            f'<itunes:image>{image_url}</itunes:image>'
            f'<itunes:duration>{entry["itunes_duration"]}</itunes:duration>'
            f'<itunes:keywords></itunes:keywords>'
            f'<itunes:explicit>{entry["itunes_explicit"]}</itunes:explicit>'
            f'<itunes:episodeType>{entry["itunes_episodetype"]}</itunes:episodeType>'
            f'<itunes:episode>{entry["itunes_episode"]}</itunes:episode>'
            f'</item>')


def get_feed_xml(feed: FeedParserDict):
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


def get_podcast_feed(feedconfig: FeedGeneratorConfig):
    """
    Get an RSS feed for podcast apps that is produced from a source and applying filtering criteria defined in the
    provided feedconfig object.

    Args: feedconfig: Object with meta-data and filtering criteria to produce a RSS feed file.

    Returns: xml string
    """

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

    # Get post karma
    # TODO: Handle AssertionError when post cannot be found
    feed['entries'] = list(map(lambda entry: {**entry, 'karma': get_post_karma(entry['link'])}, feed['entries']))

    # Get post with the most karma
    max_karma_post = max(feed['entries'], key=lambda entry: entry['karma'])

    # Read history titles from storage
    history_titles = storage.read_history_titles()

    # Check if max karma post is in history
    def entry_title_is_in_history(entry):
        return max([SequenceMatcher(None, entry['title'], h).ratio() for h in history_titles]) > 0.9

    if entry_title_is_in_history(max_karma_post):
        return

    history_titles += [max_karma_post['title']]
    storage.write_history_titles(history_titles)

    # Update values from the provided configuration
    feed['feed']['title'] = feedconfig.title
    feed['feed']['image']['href'] = feedconfig.image_url

    def get_entry_with_updated_guid(entry):
        return {
            **entry,
            "guidislink": 'true' if entry['guidislink'] else 'false',
            # TODO: Original code accesses the 'guid' value, but it is not found in this case.
            "guid": entry['id'] + feedconfig.guid_suffix}

    feed['entries'] = list(map(get_entry_with_updated_guid, feed['entries']))
    xml_feed = get_feed_xml(feed)
    
    return xml_feed
