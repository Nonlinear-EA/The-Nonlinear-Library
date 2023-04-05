import random
from datetime import datetime, timedelta
from unittest.mock import patch
from xml.etree import ElementTree

import pytest

from functions.feed import FeedGeneratorConfig
from functions.storage import LocalStorage

forum_prefixes = ('AF - ', 'EA - ', 'LW - ')


def get_feed_reference_date_str(date_format='%Y-%m-%d %H:%M:%S'):
    return reference_date().strftime(date_format)


def reference_date():
    return datetime(year=2023, month=4, day=5)


@pytest.fixture(autouse=True)
def set_random_seed_to_reference_time():
    """
    Initialize the random package using the reference date from the test_beyondwords_feed.xml file.

    This fixture is flaged as `autouse` so it will be called before every test

    """
    random.seed(reference_date().timestamp())


@pytest.fixture(autouse=True)
def empty_history():
    """
    Empties the history_titles_file file and adds a mock entry

    """
    with open('history_titles.txt', 'w') as f:
        f.write("This is a sample entry that won't match anything from the feed!")


@pytest.fixture
def mock_get_feed_tree_from_source():
    """
    Mock the get_feed_tree_from_source from the podcast_feed_generator module, so it returns the root of a static xml
    file, instead of downloading the rss feed from BeyondWords.
    Returns:

    """
    with patch('functions.podcast_feed_generator.get_feed_tree_from_source') as mock:
        mock.return_value = ElementTree.parse('test_beyondwords_feed.xml').getroot()
        yield


@pytest.fixture
def mock_get_post_karma():
    """
    The post karma function is a big bottleneck since it takes a long time to check the karma for each post.

    Mocking this function allows speeding up the tests. The mocked function returns a random number.

    """
    with patch('functions.podcast_feed_generator.get_post_karma') as mock:
        mock.return_value = str(int(random.random() * 100))
        yield


@pytest.fixture(autouse=True)
def mock_read_history_titles():
    with patch.object(LocalStorage, 'read_history_titles') as mock:
        with open('history_titles.txt', 'r') as f:
            mock.return_value = [line for line in f.readlines()]
            yield


@pytest.fixture(autouse=True)
def mock_write_history_titles():
    with patch.object(LocalStorage, 'write_history_titles') as mock:
        yield


@pytest.fixture
def default_config() -> FeedGeneratorConfig:
    return FeedGeneratorConfig(
        source='https://audio.beyondwords.io/f/8692/7888/read_8617d3aee53f3ab844a309d37895c143',
        author='The Nonlinear Fund',
        email='podcast@nonlinear.org',
        image_url='https://storage.googleapis.com/rssfile/images/Nonlinear%20Logo%203000x3000%20-%20Alignment%20Forum%20Daily.png',
        guid_suffix='',
        title="The Nonlinear Library: Your title goes here!",
        title_prefix='Generic - ',
        search_period=FeedGeneratorConfig.SearchPeriod.ONE_WEEK,
        gcp_bucket='rssfile',
        output_basename='testbucket'
    )


@pytest.fixture()
def removed_authors():
    with open('./removed_authors.txt', 'r') as f:
        return [author for author in f.readlines()]


@pytest.fixture(params=forum_prefixes)
def forum_title_prefix(request):
    return request.param


@pytest.fixture
def beyondwords_feed():
    return ElementTree.parse('./test_beyondwords_feed.xml').getroot()


@pytest.fixture(params=(FeedGeneratorConfig.SearchPeriod.ONE_DAY, FeedGeneratorConfig.SearchPeriod.ONE_DAY))
def search_period(request):
    return request.param


@pytest.fixture()
def search_period_time_delta(search_period: FeedGeneratorConfig.SearchPeriod):
    return timedelta(days=search_period.value)
