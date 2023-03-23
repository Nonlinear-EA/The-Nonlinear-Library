from dataclasses import dataclass, field
from datetime import datetime, date, timezone, timedelta
from typing import List

import feedparser
from feedparser import FeedParserDict


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
    itunes_explicit: str = 'yes'
    updated: datetime = field(default=datetime.combine(
        date.today(), datetime.min.time(), tzinfo=timezone(offset=timedelta(0))))
    feeddict: dict = None

    @classmethod
    def dict_from_url(cls, source: str):
        feed_obj = feedparser.parse(source)
        feed = Feed.from_feedparserdict(feed_obj)
        feed.source = source
        return feed

    @classmethod
    def from_url(cls, source: str):
        pass

    @classmethod
    def from_feedparserdict(cls, feeddict: FeedParserDict):
        return Feed(
            title=feeddict['feed']['title'],
            image=feeddict['feed']['image']['href'],
            feeddict=feeddict
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
                <lastBuildDate>{self.updated}</lastBuildDate>')
