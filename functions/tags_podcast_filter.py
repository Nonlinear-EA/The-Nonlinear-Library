import asyncio
import copy
import functools
import json
import logging
import pathlib
import re
import ssl
import sys

import feedparser
import httpx
from bs4 import BeautifulSoup
from google.cloud import storage
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
from tqdm import tqdm
from tqdm.asyncio import tqdm_asyncio

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('[%(asctime)s][%(name)s][%(levelname)s] %(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)

TAG_URL_PATTERN = re.compile(r'.*/tag/([^/]+).*')


def load_channels(graphql_url="https://forum.effectivealtruism.org/graphql", channels_filename="channels.json"):
    log.info(f'Fetching tag slugs from: {graphql_url}')
    channels_config = json.loads(pathlib.Path(channels_filename).read_text())
    transport = AIOHTTPTransport(url=graphql_url)
    client = Client(transport=transport, fetch_schema_from_transport=True)
    query = gql("""
    query {
        tags {
            results {
                slug
                name
    
            }
        }
    }
    """)
    result = client.execute(query)
    tags = result["tags"]["results"]
    tag_to_slug = {
        tag['name']: tag['slug']
        for tag in tags
    }
    slugs_per_channel = {
        channel_name: [
            tag_to_slug[tag]
            for tag in channel['tags']
            # TODO: maybe throw error if human readable name is not found
            if tag in tag_to_slug
        ]
        for channel_name, channel in channels_config.items()
    }
    for channel_name, slugs in slugs_per_channel.items():
        channels_config[channel_name]['slugs'] = slugs
    return channels_config


def merge_topics_to_feed(_feed, list_of_topics):
    feed = copy.deepcopy(_feed)
    for i in range(len(feed.entries)):
        feed.entries[i]['article_tags'] = list_of_topics[i]
    return feed


def parse_tags(text):
    soup = BeautifulSoup(text, "html.parser")
    tags = {
        re.sub(TAG_URL_PATTERN, r'\1', a['href'])
        for a in soup.find_all('a', href=True)
        if '/tag/' in a['href']
    }
    return tags


async def fetch_tags_async(feed):
    log.info(f'Fetching article tags')
    limits = httpx.Limits(max_connections=50, max_keepalive_connections=10)
    timeout = httpx.Timeout(None)
    transport = httpx.AsyncHTTPTransport(retries=10)
    client = httpx.AsyncClient(limits=limits, timeout=timeout, transport=transport)
    results = await tqdm_asyncio.gather(*[
        client.get(item['link'])
        for item in feed.entries
    ], desc='Fetch Articles')
    list_of_tags = [
        parse_tags(r.text)
        for r in tqdm(results, desc='Parse Tags')
    ]
    return list_of_tags


def fetch_tags(feed):
    return asyncio.run(fetch_tags_async(feed))


@functools.lru_cache()
def get_feed(url):
    log.info(f'Fetching feed from: {url}')
    news_feed = feedparser.parse(url)
    list_of_topics = fetch_tags(news_feed)
    news_feed = merge_topics_to_feed(news_feed, list(list_of_topics))
    return news_feed


# def filter_feed(news_feed, channel_tags: set[str]):
def filter_feed(news_feed, channel_tags):
    feed = copy.deepcopy(news_feed)
    feed.entries = [
        item
        for item in feed.entries
        if channel_tags.intersection(item['article_tags'])
    ]
    return feed


def main(data, context):
    config = {
        'feed': {
            'max_articles': 30,
            'author': 'The Nonlinear Fund',
            'email': 'podcast@nonlinear.org',
            'image_url': 'https://storage.googleapis.com/rssfile/images/Nonlinear%20Logo%203000x3000%20-%20EA%20Forum.png'
        },
        'sources': {
            'list': [
                'https://audio.beyondwords.io/f/8692/7888/read_8617d3aee53f3ab844a309d37895c143'  # TNLL
            ]
        },
        'system': {
            'output_file_basename': 'nonlinear-library-aggregated',
            'gcp_bucket_name': 'rssfile'
        }
    }

    feed_initial_str = """<?xml version="1.0" encoding="{_encoding}"?>\
        <rss xmlns:atom="{_namespaces_}" xmlns:itunes="{_namespaces_itunes}" xmlns:content="{_namespaces_content}" \
        version="2.0"><channel><title>{_feed_title}</title>\
        <description>{_feed_subtitle}</description>\
        <author>{_feed_author}</author>\
        <copyright>{_feed_rights}</copyright>\
        <language>{_feed_language}</language>\
        <link>{_feed_link}</link>\
        <image><url>{_feed_image_href}</url></image>\
        <itunes:keywords></itunes:keywords>\
        <itunes:owner>\
          <itunes:name>{_feed_publishderdetail_name}</itunes:name>\
          <itunes:email>{_feed_publishderdetail_email}</itunes:email>\
        </itunes:owner>\
        <itunes:category text="{_feed_tags0}"><itunes:category text="{_feed_tags0}"/></itunes:category>\
        <itunes:explicit>{_feed_itunesexplicit}</itunes:explicit>\
        <itunes:image href="{_feed_image_href}"/>\
        <itunes:author>{_feed_publishderdetail_name}</itunes:author>\
        <itunes:summary><![CDATA[{_feed_subtitle}]]></itunes:summary>\
        <lastBuildDate>{_feed_updated}</lastBuildDate>
"""

    item_str = """<item><guid isPermaLink="{item_guidislink}">{item_guid}</guid>\
        <title>{item_title}</title>\
        <description><![CDATA[{item_summary}]]></description>\
        <author>{item_author}</author>\
        <link>{item_link}</link>\
        <content:encoded><![CDATA[{item_summary}]]></content:encoded>\
        <enclosure length="{item_enclosure_length}" type="{item_enclosure_type}" url="{item_enclosure_url}"/>\
        <pubDate>{item_published}</pubDate>\
        <itunes:title>{item_title}</itunes:title>\
        <itunes:subtitle><![CDATA[{item_summary}]]></itunes:subtitle>\
        <itunes:summary><![CDATA[{item_summary}]]></itunes:summary>\
        <itunes:author>{item_author}</itunes:author>\
        <itunes:image>{_feed_image_href}</itunes:image>\
        <itunes:duration>{item_itunes_duration}</itunes:duration>\
        <itunes:keywords></itunes:keywords>\
        <itunes:explicit>{item_itunesexplicit}</itunes:explicit>\
        <itunes:episodeType>{item_itunes_episodetype}</itunes:episodeType>\
        <itunes:episode>{item_itunes_episode}</itunes:episode></item>
"""

    feed_final_str = '\n</channel></rss>'

    html_hyperlink_format_spotify = "<a href=\"{hyperlink}\">{hyperlink_text}</a>"

    class Feed(object):
        def __init__(self, config, local=False):
            # Obtain SSL certificate
            if hasattr(ssl, '_create_unverified_context'):
                ssl._create_default_https_context = ssl._create_unverified_context
            self.max_number = config['feed']['max_articles']
            self.sources_list = config['sources']['list']
            self.output_file_basename = config['system']['output_file_basename']
            self.gcp_bucket_name = config['system']['gcp_bucket_name']
            self.local = local
            self.list_modified_sources = []
            self.image_url = config['feed']['image_url']

        def modify_feed(self):
            for i in range(len(self.sources_list)):
                if ('http' in self.sources_list[i]):
                    self.list_modified_sources.append(self._modify_feed(self.sources_list[i], i))

        def _modify_feed(self, url, src_idx):
            log.info(f'Creating modified feeds per channel')
            channels = load_channels()
            news_feed = get_feed(url)

            for channel_name, channel in tqdm(channels.items(), desc='Write Feed XML'):
                slugs = set(channel['slugs'])
                feed = filter_feed(news_feed, slugs)
                rss_feed = self.format_feed(feed, channel, channel_name)
                filename = f'{self.output_file_basename}-{channel_name}.xml'
                if self.local:
                    pathlib.Path(filename).write_text(rss_feed)
                else:
                    client = storage.Client()
                    bucket = client.get_bucket(self.gcp_bucket_name)
                    blob = bucket.blob(filename)
                    blob.upload_from_string(rss_feed)

        def format_feed(self, news_feed, channel_config, channel_name):
            news_feed['feed']['title'] = f'The Nonlinear Library: {channel_name.replace("-", " ")}'
            news_feed['feed']['image']['href'] = channel_config['imageUrl']

            rss_feed = feed_initial_str.format(
                _encoding=news_feed['encoding'].upper(),
                _namespaces_=news_feed['namespaces'][''],
                _namespaces_itunes=news_feed['namespaces']['itunes'],
                _namespaces_content=news_feed['namespaces']['content'],
                _feed_title=news_feed['feed']['title'],
                _feed_subtitle=news_feed['feed']['subtitle'],
                _feed_author=news_feed['feed']['author'],
                _feed_rights=news_feed['feed']['rights'],
                _feed_language=news_feed['feed']['language'],
                _feed_link=news_feed['feed']['link'],
                _feed_image_href=news_feed['feed']['image']['href'],
                _feed_publishderdetail_name=news_feed['feed']['publisher_detail']['name'],
                _feed_publishderdetail_email=news_feed['feed']['publisher_detail']['email'],
                _feed_tags0=news_feed['feed']['tags'][0]['term'],
                # _feed_tags1=news_feed['feed']['tags'][1]['term'], #NOTE: removed due to IndexError: list index out of range
                _feed_itunesexplicit='yes' if news_feed['feed']['itunes_explicit'] else 'no',
                _feed_updated=news_feed['feed']['updated'],
            )
            for item in news_feed.entries:
                item['title'] = item['title'].replace('&', 'and')

                rss_feed += item_str.format(
                    item_guidislink=str(item['guidislink']).lower(),
                    # does the guid have to be unique PER SHOW or GLOBALLY?
                    item_guid=item['guid'] + channel_name.replace("-", "_"),
                    item_title=item['title'],
                    item_summary=html_hyperlink_format_spotify.format(
                        hyperlink=item['link'], hyperlink_text='Link to original article') + '<br/>' + '<br/>' + item[
                                     'summary'],
                    item_author=item['author'],
                    item_link=item['link'],
                    item_enclosure_length=item['links'][1]['length'] if 'enclosure' in item['links'][1].values() \
                        else item['links'][0]['length'],
                    item_enclosure_type=item['links'][1]['type'] if 'enclosure' in item['links'][1].values() \
                        else item['links'][0]['type'],
                    item_enclosure_url=item['links'][1]['href'] if 'enclosure' in item['links'][1].values() \
                        else item['links'][0]['href'],
                    item_published=item['published'],
                    _feed_image_href=news_feed['feed']['image']['href'],
                    item_itunes_duration=item['itunes_duration'],
                    item_itunesexplicit=item['itunes_explicit'],
                    item_itunes_episodetype=item['itunes_episodetype'],
                    item_itunes_episode=item['itunes_episode']
                )
            # harcoded solution to solve unescaped `<` XML RSS feed validation problem
            rss_feed = rss_feed.replace('<5', '5')
            rss_feed += feed_final_str
            return rss_feed

    feed = Feed(config, local=False)
    # feed = Feed(config, local=True)
    list_modified_sources = feed.modify_feed()


if __name__ == '__main__':
    main(None, None)
