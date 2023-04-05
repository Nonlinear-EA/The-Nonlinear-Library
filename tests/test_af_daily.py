import freezegun
import pytest

from functions.feed import FeedGeneratorConfig
from functions.podcast_feed_generator import get_new_episodes_from_beyondwords_feed
from tests.conftest import get_feed_reference_date_str


@freezegun.freeze_time(get_feed_reference_date_str())
@pytest.mark.parametrize('title_prefix', ('AF - ', 'EA - ', 'LW - '))
def test_get_new_episodes_returns_least_one_entry(
        title_prefix,
        default_config,
        mock_get_feed_tree_from_source,
        mock_get_post_karma
):
    default_config.title_prefix = title_prefix
    default_config.search_period = FeedGeneratorConfig.SearchPeriod.ONE_DAY
    new_episodes = get_new_episodes_from_beyondwords_feed(default_config, False)
    assert len(new_episodes) == 1


def test_get_new_episodes_filters_out_entries_from_removed_authors():
    assert False


def test_get_new_episodes_filters_out_entries_outside_search_period():
    assert False


def test_update_podcast_feed_updates_channel_title():
    assert False


def test_update_podcast_feed_updates_channel_image_url():
    assert False


def test_update_podcast_feed_updates_title_history():
    assert False
