from feed_processing.feed_updaters import update_podcast_feed


def test_update_podcast_feed_discards_new_items_from_forums_that_dont_match_the_title_prefix_in_the_config(
        default_podcast_feed_config,
        mock_get_feed_tree_from_url_to_return_test_beyondwords_output_feed
):
    feed = update_podcast_feed(default_podcast_feed_config, False)

    assert all(title.text.split("-")[0].strip() == "TF" for title in feed.findall("channel/item/title"))


def test_update_podcast_feed_discards_new_items_from_removed_authors(
        default_podcast_feed_config,
        mock_get_feed_tree_from_url_to_return_test_beyondwords_output_feed
):
    feed = update_podcast_feed(default_podcast_feed_config, False)

    assert not any(author.text.strip() == "RemovedAuthor" for author in feed.findall("channel/item/author"))


def test_update_podcast_feed_does_not_include_duplicates_in_podcast_feed(
        default_podcast_feed_config,
        mock_get_feed_tree_from_url_to_return_test_beyondwords_output_feed,
):
    existing_title = "TF - A post from an episode that's already online by Online Author"

    feed = update_podcast_feed(default_podcast_feed_config, False)
    feed_titles = [title.text.strip() for title in feed.findall("channel/item/title")]

    assert existing_title not in feed_titles

# TODO: Test that update feed creates feeds with appropriate meta-data, such as channel title, image, etc.
