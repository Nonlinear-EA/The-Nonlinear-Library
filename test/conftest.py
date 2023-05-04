import random
from datetime import datetime
from unittest.mock import patch

import pytest
from lxml import etree
from lxml.etree import CDATA

from feed_processing.feed_config import PodcastFeedConfig
from feed_processing.storage import LocalStorage, create_storage

beyondwords_output_feed = "./files/beyondwords_output_feed.xml"

lorem_ipsum = """Lorem ipsum dolor sit amet, consectetur adipiscing elit. Morbi ac sollicitudin urna. Morbi mollis 
condimentum aliquet. Nulla sagittis malesuada metus, quis tincidunt libero tempor sit amet. Maecenas suscipit nisl et 
ultrices scelerisque. Nunc gravida varius diam, eget sagittis felis vehicula in. Praesent ut porta metus. Quisque 
dapibus, elit non rutrum viverra, mauris justo luctus odio, quis commodo massa risus sed nisl. Phasellus pharetra 
lorem a mauris gravida, at faucibus nunc mollis. Donec a justo nec ligula sodales malesuada vestibulum efficitur 
massa. Etiam luctus, nibh vitae fermentum cursus, lacus lorem condimentum nunc, viverra aliquet eros mi ut nulla. In 
hac habitasse platea dictumst. Etiam convallis mollis viverra. Sed ac pretium turpis, quis tincidunt purus. Aenean 
sed risus in sapien consectetur suscipit sit amet quis ipsum."""


def get_feed_reference_date_str(date_format='%Y-%m-%d %H:%M:%S'):
    return reference_date().strftime(date_format)


def reference_date():
    return datetime(year=2023, month=4, day=5)


@pytest.fixture
def mock_get_feed_tree_from_url_to_return_test_beyondwords_output_feed():
    """
    Mock the get_feed_tree_from_source from the `feed_updaters` module, so it returns the root of a static xml
    file, instead of downloading the rss feed from BeyondWords.
    Returns:

    """
    with patch('feed_processing.feed_updaters.get_feed_tree_from_url') as mock:
        mock.return_value = etree.parse('files/beyondwords_output_feed.xml').getroot()
        yield


@pytest.fixture
def mock_get_feed_tree_from_url_to_return_test_forum_feed():
    with patch('feed_processing.feed_updaters.get_feed_tree_from_url') as mock:
        mock.return_value = etree.parse("files/forum_feed.xml")
        yield


@pytest.fixture
def mock_read_podcast_feed_to_return_test_podcast_feed():
    with patch.object(LocalStorage, 'read_podcast_feed') as mock:
        mock.return_value = etree.parse('./files/feed_for_podcast_apps.xml').getroot()
        yield


@pytest.fixture
def mock_write_podcast_feed():
    with patch.object(LocalStorage, 'write_podcast_feed') as mock:
        def save_podcast_feed(*args):
            with open('./files/podcast_feed_test_output.xml', 'wb') as f:
                f.write(args[0])

        mock.side_effect = save_podcast_feed
        yield


@pytest.fixture
def mock_get_post_karma():
    """
    The post karma function is a big bottleneck since it takes a long time to check the karma for each post.

    Mocking this function allows speeding up the tests. The mocked function returns a random number.

    """
    with patch('feed_processing.feed_updaters.get_post_karma') as mock:
        mock.return_value = str(int(random.random() * 100))
        yield


@pytest.fixture
def default_config_for_podcast_apps_feed() -> PodcastFeedConfig:
    return PodcastFeedConfig(
        source='https://audio.beyondwords.io/f/8692/7888/read_8617d3aee53f3ab844a309d37895c143',
        author='The Nonlinear Fund',
        email='podcast@nonlinear.org',
        image_url='https://storage.googleapis.com/rssfile/images/Nonlinear%20Logo%203000x3000%20-%20Alignment%20Forum%20Daily.png',
        title="The Nonlinear Library: Your title goes here!",
        gcp_bucket='rssfile',
        rss_filename='./files/feed_for_podcast_apps.xml',
        removed_authors_file="./files/removed_authors.txt"
    )


@pytest.fixture()
def storage(default_config_for_podcast_apps_feed):
    return create_storage(default_config_for_podcast_apps_feed, False)


def get_empty_test_forum_feed():
    feed_namespace_map = {
        "dc": "http://purl.org/dc/elements/1.1/",
        "content": "http://purl.org/rss/1.0/modules/content/",
        "atom": "http://www.w3.org/2005/Atom"
    }
    feed_root = etree.Element("rss", nsmap=feed_namespace_map)
    channel = etree.SubElement(feed_root, "channel")
    # Add at least a single to emulate history items.
    item = etree.SubElement(channel, "item")
    title = etree.SubElement(item, "title")
    title.text = CDATA("Unknown - This is a history item by The Author")
    # Create some description and content
    description = etree.SubElement(item, "description")
    description.text = CDATA("This is a history item. It should not be included again by future feed updates.")
    content = etree.SubElement(item, "content")
    content.text = CDATA(f"This is a history item on some date by Author <p>{lorem_ipsum}</p>")
    # Add an author
    author = etree.SubElement(item, "author")
    author.text = "The Author"
    return feed_root


def write_test_beyondwords_feed(storage):
    root = get_empty_test_forum_feed()
    tree = etree.ElementTree(root)
    tree.write("./files/", pretty_print=True, xml_declaration=True)


@pytest.fixture(autouse=True)
def disable_write_podcast_feed(mocker):
    """
    Disable the `write_podcast_feed` method from the storage interface, so the test files are not overwritten.
    Args:
        mocker:

    """
    mocker.patch.object(LocalStorage, 'write_podcast_feed', lambda a, b: None)
    yield


def overwrite_beyondwords_output_feed_with_default_file():
    with open("./files/beyondwords_output_feed_default.xml") as input_file:
        with open("./files/beyondwords_output_feed.xml", mode="w") as output_file:
            output_file.writelines(input_file.readlines())
