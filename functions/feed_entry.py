from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import List


class EpisodeType(Enum):
    FULL = 'full'


@dataclass
class FeedEntry:
    """
    Represents an individual post from an RSS feed.
    """
    guid: str
    title: str
    description: str
    author: str
    link: str
    content: str
    audio_source: str
    audio_type: str
    audio_length: int
    itunes_title: str
    itunes_subtitle: str
    itunse_summary: str
    publication_date: datetime
    image: str
    duration: timedelta
    itunes_episode_type: EpisodeType.FULL
    itunes_episode_number: int
    is_permalink: bool = False
    itunes_keywords: List[str] = field(default_factory=list)
    itunes_explicit: bool = True

    @classmethod
    def to_xml(cls):
        pass

    @classmethod
    def from_dict(cls, d: dict):
        pass
