import random
from datetime import datetime, timedelta
from unittest.mock import patch
from xml.etree import ElementTree

import pytest

from functions.feed import FeedGeneratorConfig
from functions.storage import LocalStorage, create_storage

forum_prefixes = ('AF - ', 'EA - ', 'LW - ')  # TODO: Not necessary to test different prefixes
history_titles = [
    'AF - This is a history AF episode',
    'EA - This is a history EA episode',
    'LW - This is a history LW episode'
]


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
def empty_history(storage):
    """
    Empties the history_titles_file file and adds a mock entry

    """
    yield
    storage.write_history_titles(history_titles)


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
def mock_read_podcast_feed():
    with patch.object(LocalStorage, 'read_podcast_feed') as mock:
        mock.return_value = ElementTree.parse('podcast_feed.xml').getroot()
        yield


@pytest.fixture
def mock_write_podcast_feed():
    with patch.object(LocalStorage, 'write_podcast_feed') as mock:
        def save_podcast_feed(*args):
            with open('podcast_feed.xml', 'wb') as f:
                f.write(args[0])

        mock.side_effect = save_podcast_feed
        yield


@pytest.fixture
def cleanup_podcast_feed():
    yield
    podcast_feed = ElementTree.parse('podcast_feed.xml').getroot()
    i = 0
    for item in podcast_feed.findall('channel/item'):
        i += 1
        if i == 1:
            continue
        podcast_feed.find('channel').remove(item)
    # Register namespaces before parsing to string.
    namespaces = {
        # The atom namespace is not used in the resulting feeds and is not added to the xml files.
        "atom": "http://www.w3.org/2005/Atom",
        "itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd",
        "content": "http://purl.org/rss/1.0/modules/content/"
    }
    for prefix, uri in namespaces.items():
        ElementTree.register_namespace(prefix, uri)
    tree = ElementTree.ElementTree(podcast_feed)
    tree.write('./podcast_feed.xml')


@pytest.fixture
def mock_get_post_karma():
    """
    The post karma function is a big bottleneck since it takes a long time to check the karma for each post.

    Mocking this function allows speeding up the tests. The mocked function returns a random number.

    """
    with patch('functions.podcast_feed_generator.get_post_karma') as mock:
        mock.return_value = str(int(random.random() * 100))
        yield


@pytest.fixture
def default_config() -> FeedGeneratorConfig:
    return FeedGeneratorConfig(
        source='https://audio.beyondwords.io/f/8692/7888/read_8617d3aee53f3ab844a309d37895c143',
        author='The Nonlinear Fund',
        email='podcast@nonlinear.org',
        image_url='https://storage.googleapis.com/rssfile/images/Nonlinear%20Logo%203000x3000%20-%20Alignment%20Forum%20Daily.png',
        title="The Nonlinear Library: Your title goes here!",
        gcp_bucket='rssfile',
        history_titles_filename='podcast_feed'
    )


@pytest.fixture()
def removed_authors():
    with open('removed_authors.txt', 'r') as f:
        return [author for author in f.readlines()]


@pytest.fixture(params=forum_prefixes)
def forum_title_prefix(request):
    return request.param


@pytest.fixture
def beyondwords_feed():
    return ElementTree.parse('test_beyondwords_feed.xml').getroot()


@pytest.fixture(params=(FeedGeneratorConfig.SearchPeriod.ONE_DAY, FeedGeneratorConfig.SearchPeriod.ONE_DAY, None))
def search_period(request):
    return request.param


@pytest.fixture()
def search_period_time_delta(search_period: FeedGeneratorConfig.SearchPeriod):
    return timedelta(days=search_period.value)


@pytest.fixture(params=(True, False))
def feed_config(
        default_config,
        search_period,
        forum_title_prefix,
        request
):
    default_config.search_period = search_period
    default_config.title_prefix = forum_title_prefix
    default_config.top_post_only = request.param
    return default_config


@pytest.fixture()
def feed_config_all(default_config, forum_title_prefix):
    default_config.title_prefix = forum_title_prefix
    default_config.top_post_only = False
    return default_config


@pytest.fixture()
def storage(default_config):
    return create_storage(default_config, False)
