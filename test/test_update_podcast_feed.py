import freezegun

from feed_processing.feed_updaters import update_podcast_feed
from test.conftest import get_feed_reference_date_str


@freezegun.freeze_time(get_feed_reference_date_str())
def test_update_podcast_feed_updates_channel_title(
        default_podcast_feed_config,
        storage,
        mock_get_beyondwords_output_feed,
        mock_read_podcast_feed
):
    default_podcast_feed_config.title = 'This is the title'

    update_podcast_feed(default_podcast_feed_config, False)
    feed = storage.read_podcast_feed()

    assert feed.find('channel/title').text == 'This is the title'


def test_update_podcast_feed_discards_new_items_from_forums_that_dont_match_the_title_prefix_in_the_config(
        default_podcast_feed_config,
        storage,
        mock_get_beyondwords_output_feed
):
    default_podcast_feed_config.title_prefix = "Unknown"

    feed = update_podcast_feed(default_podcast_feed_config, False)

    assert all(title.text.split("-")[0].strip() == "Unknown" for title in feed.findall("channel/item/title"))


def test_update_podcast_feed_discards_new_items_from_removed_authors(
        default_podcast_feed_config,
        storage,
        mock_get_beyondwords_output_feed_with_removed_author
):



@freezegun.freeze_time(get_feed_reference_date_str())
def test_update_podcast_feed_updates_channel_image_url(
        feed_config,
        mock_get_beyondwords_output_feed_from_url,
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
        mock_get_beyondwords_output_feed_from_url,
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
def test_update_podcast_feed_does_not_write_episodes_in_history_titles(
        feed_config,
        mock_get_beyondwords_output_feed_from_url,
        mock_read_podcast_feed,
        mock_get_post_karma,
        mock_write_podcast_feed,
        storage,
        cleanup_podcast_feed
):
    history_titles = storage.read_history_titles()
    _, new_episode_titles = update_podcast_feed(feed_config, False)
    assert all([episode not in history_titles for episode in new_episode_titles])
