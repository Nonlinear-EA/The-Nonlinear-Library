import feedparser
import pytest

from functions.feed import FeedGeneratorConfig


@pytest.fixture(autouse=True)
def empty_history():
    with open('./history_titles_empty.txt', 'w') as f:
        f.write("This is a sample entry that won't match anything from the feed!")


@pytest.fixture(scope='session')
def rss_source():
    return './beyondwords_snapshot_7_days.xml'


@pytest.fixture(scope='session')
def rss_feed(rss_source):
    return feedparser.parse(rss_source)


@pytest.fixture()
def alignment_forum_config_weekly(rss_source):
    return FeedGeneratorConfig(
        source=rss_source,
        author='The Nonlinear Fund',
        email='podcast@nonlinear.org',
        image_url='https://storage.googleapis.com/rssfile/images/Nonlinear%20Logo%203000x3000%20-%20Alignment%20Forum%20Daily.png',
        history_titles_filename='./history_titles_empty.txt',
        removed_authors_filename='./removed_authors.txt',
        guid_suffix='_AF-day',
        title="The Nonlinear Library: Alignment Forum Weekly",
        title_prefix='AF -',
        search_period=FeedGeneratorConfig.SearchPeriod.ONE_WEEK,
        gcp_bucket='rssfile',
        output_file_basename='../manual_tests/nonlinear-library-aggregated-AF-daily-new'
    )


@pytest.fixture()
def alignment_forum_config_daily(rss_source):
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
        search_period=FeedGeneratorConfig.SearchPeriod.ONE_DAY,
        gcp_bucket='rssfile',
        output_file_basename='nonlinear-library-aggregated-AF-daily-new'
    )
