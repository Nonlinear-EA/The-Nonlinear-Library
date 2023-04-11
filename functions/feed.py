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
    rss_filename: str
    gcp_bucket: str
    title: str
    guid_suffix: str = None
    search_period: SearchPeriod | None = None
    title_prefix: str = None
    date_format: str = '%a, %d %b %Y %H:%M:%S %z'
    top_post_only: bool = False

    def get_search_period_timedelta(self) -> timedelta | None:
        """
        Returns a timedelta based on the string provided as search period
        """

        if self.search_period == FeedGeneratorConfig.SearchPeriod.ONE_WEEK:
            return timedelta(weeks=1)
        elif self.search_period == FeedGeneratorConfig.SearchPeriod.ONE_DAY:
            return timedelta(days=1)
        elif self.search_period is None:
            return None
        else:
            raise NotImplementedError()
