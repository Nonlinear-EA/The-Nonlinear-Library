from dataclasses import dataclass, field
from datetime import datetime, date, timezone, timedelta
from time import mktime
from typing import List

import feedparser
from feedparser import FeedParserDict

from functions.feed_entry import FeedEntry


@dataclass
class FeedConfig:
    source: str
    image_url: str
    email: str
    author: str
    history_titles_file: str


@dataclass
class Feed:
    title: str
    image: str
    source: str = None
    subtitle: str = None
    encoding: str = 'utf-8'
    namespaces: dict = None
    author: str = None
    rights: str = None
    language: str = 'en-us'
    link: str = None
    publisher_name: str = None
    publisher_email: str = None
    tags: List[str] = field(default_factory=list)
    itunes_explicit: bool = True
    updated: datetime = field(default=datetime.combine(
        date.today(), datetime.min.time(), tzinfo=timezone(offset=timedelta(0))))
    entries: List[FeedEntry] = field(default_factory=list)
    feeddict: dict = None

    @classmethod
    def from_url(cls, source: str):
        feed_obj = feedparser.parse(source)
        return Feed.from_feedparserdict(feed_obj, source=source)

    @classmethod
    def from_feedparserdict(cls, d: FeedParserDict, source: str = None):
        feed = d['feed']
        return Feed(
            source=source,
            encoding=d['encoding'].upper(),
            namespaces=d['namespaces'],
            title=feed['title'],
            subtitle=feed['subtitle'],
            author=feed['author'],
            rights=feed['rights'],
            language=feed['language'],
            link=feed['link'],
            image=feed['image']['href'],
            publisher_name=feed['publisher_detail']['name'],
            publisher_email=feed['publisher_detail']['email'],
            tags=[tag.term for tag in feed['tags']],
            itunes_explicit=True if feed['itunes_explicit'] else False,
            updated=datetime.fromtimestamp(mktime(feed['updated_parsed'])),
            feeddict=feed
        )

    def to_xml(self):
        return (
            f'<?xml version="1.0" encoding="{self.encoding}"?>\
            <rss xmlns:atom="{self.namespaces[""]}" xmlns:itunes="{self.namespaces["itunes"]}" xmlns:content="{self.namespaces["content"]}" \
                version="2.0"><channel><title>{self.title}</title>\
                <description>{self.subtitle}</description>\
                <author>{self.author}</author>\
                <copyright>{self.rights}</copyright>\
                <language>{self.language}</language>\
                <link>{self.link}</link>\
                <image><url>{self.image}</url></image>\
                <itunes:keywords></itunes:keywords>\
                <itunes:owner>\
                    <itunes:name>{self.publisher_name}</itunes:name>\
                    <itunes:email>{self.publisher_email}</itunes:email>\
                </itunes:owner>\
                <itunes:category text="{self.tags[0]}"><itunes:category text="{self.tags[0]}"/></itunes:category>\
                <itunes:explicit>{self.itunes_explicit}</itunes:explicit>\
                <itunes:image href="{self.image}"/>\
                <itunes:author>{self.publisher_name}</itunes:author>\
                <itunes:summary><![CDATA[{self.subtitle}]]></itunes:summary>\
                <lastBuildDate>{self.updated}</lastBuildDate>\
                <channel> \
                </channel> \
            </rss>'
        )
