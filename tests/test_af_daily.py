import feedparser
import pytest as pytest

from functions.feed import FeedGeneratorConfig


@pytest.fixture(scope='session')
def rss_source():
    # return 'https://audio.beyondwords.io/f/8692/7888/read_8617d3aee53f3ab844a309d37895c143'
    return '../manual_tests/beyondwords_snapshot_1_days.xml'


@pytest.fixture(scope='session')
def rss_feed(rss_source):
    return feedparser.parse(rss_source)


@pytest.fixture()
def feed_generator_config(rss_source):
    return FeedGeneratorConfig(
        source=rss_source,
        author='The Nonlinear Fund',
        email='podcast@nonlinear.org',
        image_url='https://storage.googleapis.com/rssfile/images/Nonlinear%20Logo%203000x3000%20-%20Alignment%20Forum%20Daily.png',
        history_titles_filename='./history_titles_empty.txt',
        removed_authors_filename='./removed_authors.txt',
        guid_suffix='_AF-day',
        title="The Nonlinear Library: Alignment Forum Daily",
        title_prefix='AF -',
        search_period=FeedGeneratorConfig.SearchPeriod.ONE_WEEK,
        gcp_bucket='rssfile',
        output_file_basename='nonlinear-library-aggregated-AF-daily-new'
    )


def test_alignment_forum_daily_output(rss_feed, feed_generator_config: FeedGeneratorConfig, mocker):
    pass
