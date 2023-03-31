import random
from unittest.mock import patch

import pytest

from functions.feed import FeedGeneratorConfig
from functions.storage import LocalStorage
from utilities.beyondwords_feed import get_feed_reference_date, get_beyondwords_feed


@pytest.fixture(autouse=True)
def set_random_seed_to_reference_time():
    """
    Initialize the random package using the reference date from the beyondwords_snapshot.xml file.

    This fixture is flaged as `autouse` so it will be called before every test

    """
    random.seed(get_feed_reference_date().timestamp())


@pytest.fixture(autouse=True)
def empty_history():
    """
    Empties the history_titles_file file and adds a mock entry

    """
    with open('./history_titles_empty.txt', 'w') as f:
        f.write("This is a sample entry that won't match anything from the feed!")


@pytest.fixture(scope='session')
def beyondwords_feed():
    """
    This fixture returns the root of the xml tree of the beyondwords_feed.xml file.

    """
    return get_beyondwords_feed()


@pytest.fixture
def mock_get_feed_tree_from_source():
    """
    Mock the get_feed_tree_from_source from the podcast_feed_generator module, so it returns the root of a static xml
    file, instead of downloading the rss feed from BeyondWords.
    Returns:

    """
    with patch('functions.podcast_feed_generator.get_feed_tree_from_source') as mock:
        mock.return_value = get_beyondwords_feed()
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
        with open('../manual_tests/history_titles_empty.txt', 'r') as f:
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
        history_titles_filename='./history_titles_empty.txt',
        removed_authors_filename='./removed_authors.txt',
        guid_suffix='',
        title="The Nonlinear Library: Your title goes here!",
        title_prefix='Generic - ',
        search_period=FeedGeneratorConfig.SearchPeriod.ONE_WEEK,
        gcp_bucket='rssfile',
        output_file_basename='nonlinear-library-aggregated'
    )
