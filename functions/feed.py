import re
from dataclasses import dataclass
from datetime import timedelta


@dataclass
class FeedGeneratorConfig:
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
    date_format: str = '%a, %d %b %Y %H:%M:%S %z'

    # TODO: Check python version on the cloud since this syntax works for python >= 3.10
    def get_search_period_timedelta(self) -> timedelta | None:
        """
        Returns a timedelta based on the string provided as search period
        """
        search_period_re = re.compile(
            r'((?P<days>\d+?)days)?((?P<hours>\d+?)hr)?((?P<minutes>\d+?)m)?((?P<seconds>\d+?)s)?')
        parts = search_period_re.match(self.search_period)
        if not parts:
            return None
        parts_dict = {n: float(p) for n, p in parts.groupdict().items() if p}
        return timedelta(**parts_dict)
