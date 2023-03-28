from functions.feed import FeedGeneratorConfig
from functions.podcast_feed_generator import generate_podcast_feed


def test_alignment_forum_daily_output(rss_feed, alignment_forum_config_daily: FeedGeneratorConfig, mocker):
    generate_podcast_feed(alignment_forum_config_daily)
