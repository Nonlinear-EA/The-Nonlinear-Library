import freezegun

from functions.feed import FeedGeneratorConfig
from functions.podcast_feed_generator import update_podcast_feed
from tests.conftest import get_feed_reference_date_str

search_periods = (FeedGeneratorConfig.SearchPeriod.ONE_DAY, FeedGeneratorConfig.SearchPeriod.ONE_WEEK)


@freezegun.freeze_time(get_feed_reference_date_str())
def test_update_podcast_feed_updates_channel_title(
        feed_config,
        mock_get_feed_tree_from_source,
        mock_read_podcast_feed,
        mock_write_podcast_feed,
        mock_get_post_karma,
        storage,
        cleanup_podcast_feed
):
    update_podcast_feed(feed_config, False)
    feed = storage.read_podcast_feed()
    assert feed.find('channel/title').text == feed_config.title


@freezegun.freeze_time(get_feed_reference_date_str())
def test_update_podcast_feed_updates_channel_image_url(
        feed_config,
        mock_get_feed_tree_from_source,
        mock_read_podcast_feed,
        mock_write_podcast_feed,
        mock_get_post_karma,
        storage,
        cleanup_podcast_feed
):
    update_podcast_feed(feed_config, False)
    feed = storage.read_podcast_feed()
    assert feed.find('channel/image/url').text == feed_config.image_url


@freezegun.freeze_time(get_feed_reference_date_str())
def test_update_podcast_feed_updates_title_history(
        feed_config,
        mock_get_feed_tree_from_source,
        mock_read_podcast_feed,
        mock_write_podcast_feed,
        mock_get_post_karma,
        storage,
        cleanup_podcast_feed
):
    _, new_episode_titles = update_podcast_feed(feed_config, False)
    history_titles = storage.read_history_titles()
    assert all([episode in history_titles for episode in new_episode_titles])


@freezegun.freeze_time(get_feed_reference_date_str())
def test_udpate_podcast_feed_does_not_write_episodes_in_history_titles(
        feed_config,
        mock_get_feed_tree_from_source,
        mock_read_podcast_feed,
        mock_get_post_karma,
        mock_write_podcast_feed,
        storage,
        cleanup_podcast_feed
):
    history_titles = storage.read_history_titles()
    _, new_episode_titles = update_podcast_feed(feed_config, False)
    assert all([episode not in history_titles for episode in new_episode_titles])
