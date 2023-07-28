import random
from unittest.mock import patch

import pytest

from feed_processing.feed_config import PodcastProviderFeedConfig
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
def default_podcast_provider_feed_config() -> PodcastProviderFeedConfig:
    return PodcastProviderFeedConfig(
        source='https://audio.beyondwords.io/f/8692/7888/read_8617d3aee53f3ab844a309d37895c143',
        author='The Nonlinear Fund',
        email='podcast@nonlinear.org',
        image_url='https://storage.googleapis.com/rssfile/images/Nonlinear%20Logo%203000x3000%20-%20Alignment%20Forum%20Daily.png',
        title="The Nonlinear Library: Your title goes here!",
        gcp_bucket='rssfile',
        rss_filename='files/podcast_provider_feed.xml',
        removed_authors_file="./files/removed_authors.txt",
        description="This is the podcast description, so, bla bla bla",
    )


@pytest.fixture()
def storage(default_podcast_provider_feed_config):
    return create_storage(default_podcast_provider_feed_config, False)


@pytest.fixture(autouse=True)
def disable_write_podcast_feed(mocker):
    """
    Disable the `write_podcast_feed` method from the storage interface, so the test files are not overwritten.
    """
    mocker.patch.object(LocalStorage, 'write_podcast_feed', lambda a, b: None)
    yield
