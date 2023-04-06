from datetime import datetime

import freezegun
from dateutil.tz import tz

from functions.feed import FeedGeneratorConfig
from functions.podcast_feed_generator import filter_episodes, update_podcast_feed, \
    get_new_episodes_from_beyondwords_feed
from tests.conftest import get_feed_reference_date_str

search_periods = (FeedGeneratorConfig.SearchPeriod.ONE_DAY, FeedGeneratorConfig.SearchPeriod.ONE_WEEK)


@freezegun.freeze_time(get_feed_reference_date_str())
def test_filter_episodes_filters_out_entries_from_removed_authors(
        beyondwords_feed,
        forum_title_prefix,
        default_config,
        removed_authors,
        mock_get_feed_tree_from_source,
        mock_get_post_karma
):
    new_episodes = filter_episodes(beyondwords_feed, default_config, False)
    posts_from_removed_authors = [episode for episode in new_episodes if episode.find('author').text in removed_authors]

    assert not posts_from_removed_authors


@freezegun.freeze_time(get_feed_reference_date_str())
def test_filter_episode_filters_out_entries_from_other_forums(
        beyondwords_feed,
        forum_title_prefix,
        default_config
):
    default_config.title_prefix = forum_title_prefix
    episodes = filter_episodes(beyondwords_feed, default_config, False)

    def title_matches_forum_prefix(episode):
        episode.find('title').text.startswith(forum_title_prefix)

    episodes_from_other_forums = [episode for episode in episodes if title_matches_forum_prefix(episode)]

    assert not episodes_from_other_forums


@freezegun.freeze_time(get_feed_reference_date_str())
def test_filter_episodes_filters_out_entries_outside_search_period(
        search_period,
        beyondwords_feed,
        default_config
):
    default_config.search_period = search_period

    episodes = filter_episodes(beyondwords_feed, default_config, False)

    def episode_pub_date(episode):
        return datetime.strptime(episode.find('pubDate').text, default_config.date_format)

    episode_publication_dates = [episode_pub_date(episode) for episode in episodes]
    oldest_episode_date = datetime.now(tz=tz.tzutc()) - default_config.get_search_period_timedelta()
    episodes_outside_search_period = [publication_date for publication_date in episode_publication_dates if
                                      publication_date < oldest_episode_date]

    assert not episodes_outside_search_period


@freezegun.freeze_time(get_feed_reference_date_str())
def test_update_podcast_feed_updates_channel_title(
        feed_config_top_post,
        mock_get_feed_tree_from_source,
        mock_read_podcast_feed,
        mock_write_podcast_feed,
        mock_get_post_karma,
        storage,
        cleanup_podcast_feed
):
    update_podcast_feed(feed_config_top_post, False)
    feed = storage.read_podcast_feed()
    assert feed.find('channel/title').text == feed_config_top_post.title


@freezegun.freeze_time(get_feed_reference_date_str())
def test_update_podcast_feed_updates_channel_image_url(
        feed_config_top_post,
        mock_get_feed_tree_from_source,
        mock_read_podcast_feed,
        mock_write_podcast_feed,
        mock_get_post_karma,
        storage,
        cleanup_podcast_feed
):
    update_podcast_feed(feed_config_top_post, False)
    feed = storage.read_podcast_feed()
    assert feed.find('channel/image/url').text == feed_config_top_post.image_url


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


def test_filter_episodes_returns_multiple_posts_if_top_post_only_flag_is_false(
        feed_config_all,
        beyondwords_feed,
        mock_get_feed_tree_from_source,
        mock_get_post_karma
):
    episodes = filter_episodes(beyondwords_feed, feed_config_all, False)

    assert len(episodes) > 1


def test_get_new_episodes_from_beyond_words_adds_multiple_episodes_if_top_post_only_flag_is_false(
        feed_config_all,
        mock_get_feed_tree_from_source,
        mock_get_post_karma,
        cleanup_podcast_feed
):
    episodes = get_new_episodes_from_beyondwords_feed(feed_config_all, False)

    assert isinstance(episodes, list) and len(episodes) > 1
