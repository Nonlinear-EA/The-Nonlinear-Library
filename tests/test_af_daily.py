import freezegun
import pytest

from functions.feed import FeedGeneratorConfig
from functions.podcast_feed_generator import generate_podcast_feed
from utilities.beyondwords_feed import get_feed_reference_date_str


@freezegun.freeze_time(get_feed_reference_date_str())
@pytest.mark.parametrize('title_prefix', ('AF - ', 'EA - ', 'LW - '))
def test_alignment_forum_daily_has_at_least_one_entry(
        title_prefix,
        default_config,
        mock_get_feed_tree_from_source,
        mock_get_post_karma
):
    default_config.title_prefix = title_prefix
    default_config.search_period = FeedGeneratorConfig.SearchPeriod.ONE_DAY
    _, feed_tree = generate_podcast_feed(default_config, False)
    assert len(feed_tree.findall('./channel/item'))
