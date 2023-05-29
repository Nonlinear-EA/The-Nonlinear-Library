import os
from unittest.mock import MagicMock

import pytest

from feed_processing.feed_updaters import update_podcast_provider_feed


@pytest.fixture(autouse=True)
def cleanup_test_feed_for_podcast_apps():
    yield
    if os.path.exists("./files/test_feed_for_podcast_apps.xml"):
        os.remove("./files/test_feed_for_podcast_apps.xml")


def test_update_feed_for_podcast_apps_discards_new_items_from_forums_that_dont_match_the_title_prefix_in_the_config(
        default_podcast_provider_feed_config,
        storage,
        mocker,
        disable_write_podcast_feed
):
    # Set the expected title_prefix
    default_podcast_provider_feed_config.title_prefix = "AForumPrefix"
    # Change the input feed so that one item matches the prefix.
    modified_input_feed = storage.read_podcast_feed("./files/beyondwords_output_feed.xml")
    item_title_to_modify = modified_input_feed.find("channel/item/title")
    item_title_to_modify.text = "AForumPrefix - This is an entry form the TestForum"
    mock_get_feed_tree_from_url = MagicMock(return_value=modified_input_feed)
    # Mock the get_feed_tree_from_url, so it returns the modified feed
    mocker.patch("feed_processing.feed_updaters.get_feed_tree_from_url", new=mock_get_feed_tree_from_url)

    feed = update_podcast_provider_feed(default_podcast_provider_feed_config, False)

    assert all(title.text.split("-")[0].strip() == "AForumPrefix" for title in feed.findall("channel/item/title"))


def test_update_feed_for_podcast_apps_discards_new_items_from_removed_authors(
        default_podcast_provider_feed_config,
        storage,
        mocker,
        disable_write_podcast_feed
):
    # Explicitly specify the removed authors file in the configuration.
    default_podcast_provider_feed_config.removed_authors_file = "./files/removed_authors.txt"
    # Set the author on one item of the input feed, so it matches a removed author.
    modified_input_feed = storage.read_podcast_feed("./files/beyondwords_output_feed.xml")
    author_to_modify = modified_input_feed.find("channel/item/author")
    # The author 'RemovedAuthor' is present in the `./files/removed_authors.txt` file.
    author_to_modify.text = "RemovedAuthor"
    # Patch get_feed_tree_from_url, so it returns the modified feed.
    mock_get_feed_tree_from_url = MagicMock(return_value=modified_input_feed)
    mocker.patch('feed_processing.feed_updaters.get_feed_tree_from_url', new=mock_get_feed_tree_from_url)

    feed = update_podcast_provider_feed(default_podcast_provider_feed_config, False)

    assert not any(author.text.strip() == "RemovedAuthor" for author in feed.findall("channel/item/author"))


def test_update_feed_for_podcast_apps_does_not_include_duplicates_in_podcast_feed(
        default_podcast_provider_feed_config,
        storage,
        mocker,
        disable_write_podcast_feed
):
    # Get the podcast apps feed and set the title of one item.
    feed_for_podcast_apps = storage.read_podcast_feed("./files/podcast_provider_feed.xml")
    duplicate_item_title = feed_for_podcast_apps.find("channel/item/title")
    duplicate_item_title.text = "TF - This post should not be found multiple times in podcast app feed"
    # Save this feed
    feed_for_podcast_apps.write("./files/test_feed_for_podcast_apps.xml", xml_declaration=True, encoding="utf-8")
    # Set up the config to read from this feed.
    default_podcast_provider_feed_config.rss_filename = "./files/test_feed_for_podcast_apps.xml"
    # Change the BeyondWords output feed, so it contains the duplicate title
    beyondwords_output_feed = storage.read_podcast_feed("./files/beyondwords_output_feed.xml")
    duplicate_beyondwords_item_title = beyondwords_output_feed.find("channel/item/title")
    duplicate_beyondwords_item_title.text = "TF - This post should not be found multiple times in podcast app feed"
    # Mock get_feed_tree_from_url, so it returns the modified BeyondWords feed.
    mock_get_feed_tree_from_url = MagicMock(return_value=beyondwords_output_feed)
    mocker.patch("feed_processing.feed_updaters.get_feed_tree_from_url", new=mock_get_feed_tree_from_url)

    feed = update_podcast_provider_feed(default_podcast_provider_feed_config, False)

    feed_titles = [title.text.strip() for title in feed.findall("channel/item/title")]
    assert len([title for title in feed_titles if title == "TF - This post should not be found multiple times in "
                                                           "podcast app feed"]) == 1


def test_update_feed_for_podcast_provider_saves_new_items(
        default_podcast_provider_feed_config,
        storage,
        mocker, disable_write_podcast_feed
):
    feed_for_podcast_apps = storage.read_podcast_feed("./files/podcast_provider_feed.xml")
    
# TODO: Test that update feed creates feeds with appropriate meta-data, such as channel title, image, etc.
