from dataclasses import dataclass


@dataclass
class FeedConfig:
    source: str
    image_url: str
    email: str
    author: str
    history_titles_file: str
    removed_authors_file: str
    title: str
    guid_suffix: str
    search_period: str
    title_regex: str = None


