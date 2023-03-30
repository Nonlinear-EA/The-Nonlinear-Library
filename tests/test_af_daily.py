import freezegun

from functions.feed import FeedGeneratorConfig
from functions.podcast_feed_generator import generate_podcast_feed
from utilities.beyondwords_feed import get_feed_reference_date_str


@freezegun.freeze_time(get_feed_reference_date_str())
def test_alignment_forum_daily_has_at_least_one_entry(
        alignment_forum_config_daily: FeedGeneratorConfig,
        mock_get_feed_tree_from_source,
        mock_get_post_karma
):
    _, feed_tree = generate_podcast_feed(alignment_forum_config_daily)
    assert len(feed_tree.findall('./channel/item'))
