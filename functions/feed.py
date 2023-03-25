from dataclasses import dataclass
from datetime import timedelta
from enum import Enum


@dataclass
class FeedGeneratorConfig:
    class SearchPeriod(Enum):
        ONE_WEEK = 7
        ONE_DAY = 1

    source: str
    image_url: str
    email: str
    author: str
    history_titles_filename: str
    removed_authors_filename: str
    output_file_basename: str
    gcp_bucket: str
    title: str
    guid_suffix: str
    search_period: SearchPeriod = SearchPeriod.ONE_WEEK
    title_prefix: str = None
    date_format: str = '%a, %d %b %Y %H:%M:%S %z'

    def get_search_period_timedelta(self) -> timedelta | None:
        """
        Returns a timedelta based on the string provided as search period
        """

        if self.search_period == FeedGeneratorConfig.SearchPeriod.ONE_WEEK:
            return timedelta(weeks=1)
        elif self.search_period == FeedGeneratorConfig.SearchPeriod.ONE_DAY:
            return timedelta(days=1)
