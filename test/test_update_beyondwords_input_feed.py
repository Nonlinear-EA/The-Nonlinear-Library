import os
from unittest.mock import MagicMock

import pytest

from feed_processing.configs import beyondwords_feed_namespaces
from feed_processing.feed_config import BeyondWordsInputConfig
from feed_processing.feed_updaters import update_beyondwords_input_feed

"""
Note: The unit tests for the `update_beyondwords_feed` function use static files located inside `test/files`.
These files are used in place of the actual feeds or the removed_authors.txt file that are present on GCP.
"""


@pytest.fixture
def default_beyondwords_input_config():
    return BeyondWordsInputConfig(
        author="The Nonlinear Fund",
        email="main@nonlinear.com",
        gcp_bucket="newcode",
        source="https://someurl.com/forum-feed.xml",
        max_entries=30,
        rss_filename="./files/beyondwords_input_feed.xml",
        removed_authors_file="./files/removed_authors.txt",
        relevant_feeds=["./files/relevant_forum_feed_1.xml"]
    )


@pytest.fixture(autouse=True)
def cleanup_test_beyondwords_input_feed():
    yield
    if os.path.exists("./files/test_beyondwords_input_feed.xml"):
        os.remove("./files/test_beyondwords_input_feed.xml")


def test_posts_with_the_minimum_characters_or_less_in_description_are_discarded(
        default_beyondwords_input_config,
        disable_write_podcast_feed,
        storage,
        mocker
):
    # Retrieve test forum feed
    forum_feed = storage.read_podcast_feed("./files/forum_feed.xml")
    # Set the description of an item to a string less than 250 words.
    forum_feed.find('channel/item/description').text = "Very short string"
    # Mock get_feed_tree_from_url, so it returns the modified feed.
    mock_get_feed_tree_from_url = MagicMock(return_value=forum_feed)
    mocker.patch('feed_processing.feed_updaters.get_feed_tree_from_url', new=mock_get_feed_tree_from_url)
    default_beyondwords_input_config.min_chars = 250
    beyondwords_input_feed = update_beyondwords_input_feed(default_beyondwords_input_config, running_on_gcp=False)

    # Check that the content from all entries is 250 characters or more.
    assert all(len(content.text) >= 250 for content in beyondwords_input_feed.findall('channel/item/description'))


def test_posts_with_no_paragraph_elements_in_description_are_discarded(
        default_beyondwords_input_config,
        mocker,
        storage,
        disable_write_podcast_feed,
):
    # Retrieve test forum feed.
    forum_feed = storage.read_podcast_feed("./files/forum_feed.xml")
    # Change the min chars threshold on the config so the item is not discarded because of very few chars.
    default_beyondwords_input_config.min_chars = 100
    item_description = """This description is shorter than usual but the character threshold is set so that it is not 
    discarded because of that. It should be discarded because it has no p tags"""
    item_to_modify = forum_feed.find("channel/item")
    item_to_modify.find("description").text = item_description
    # Mock get_feed_tree_from_url, so it returns the modified feed.
    mock_get_feed_tree_from_url = MagicMock(return_value=forum_feed)
    mocker.patch("feed_processing.feed_updaters.get_feed_tree_from_url", new=mock_get_feed_tree_from_url)

    beyondwords_input_feed = update_beyondwords_input_feed(default_beyondwords_input_config, running_on_gcp=False)

    # Retrieve feed that was just written by `update_beyondwords_input_feed`
    item_descriptions = [description.text for description in beyondwords_input_feed.findall("channel/item/description")]

    # Check that all items in the feed have at least one paragraph.
    assert not any(item_description in title for title in item_descriptions)


def test_posts_that_are_already_present_in_other_relevant_files_are_discarded(
        default_beyondwords_input_config,
        storage,
        mocker,
        disable_write_podcast_feed
):
    forum_feed = storage.read_podcast_feed("./files/forum_feed.xml")
    # Change an item's title, so it matches a title in the `./files/relevant_forum_feed_1.xml` file.
    forum_feed.find("channel/item/title").text = "This entry is in relevant_feed_1.xml"
    # Mock get_feed_tree_from_url, so it returns the modified feed.
    mock_get_feed_tree_from_url = MagicMock(return_value=forum_feed)
    mocker.patch("feed_processing.feed_updaters.get_feed_tree_from_url", new=mock_get_feed_tree_from_url)

    beyondwords_feed = update_beyondwords_input_feed(default_beyondwords_input_config, running_on_gcp=False)

    item_titles = [title.text for title in beyondwords_feed.findall("channel/item/title")]
    # An item with title 'This entry is in relevant_forum_feed_1.xml' is indeed present in the file
    # `test/files/relevant_forum_feed_1.xml` and in `test/files/forum_feed.xml`.
    assert not any("This entry is in relevant_forum_feed_1.xml" in title for title in item_titles)


def test_posts_from_removed_authors_are_discarded(
        default_beyondwords_input_config,
        storage,
        mocker,
        disable_write_podcast_feed
):
    forum_feed = storage.read_podcast_feed("./files/forum_feed.xml")
    # Change an item's author, so it matches an author ('RemovedAuthor') in the `./files/removed_authors.txt` file.
    forum_feed.find("channel/item/dc:creator", namespaces=beyondwords_feed_namespaces).text = "RemovedAuthor"
    # Mock get_feed_tree_from_url, so it returns the modified feed.
    mock_get_feed_tree_from_url = MagicMock(return_value=forum_feed)
    mocker.patch("feed_processing.feed_updaters.get_feed_tree_from_url", new=mock_get_feed_tree_from_url)

    beyondwords_feed = update_beyondwords_input_feed(default_beyondwords_input_config, running_on_gcp=False)

    # Retrieve the authors. 'RemovedAuthor' is present in the `files/removed_authors.txt` file, assert that no posts
    # from that author are present in the resulting feed.
    authors = [creator.text.strip() for creator in beyondwords_feed.findall("channel/item/author")]
    assert not any(author == "RemovedAuthor" for author in authors)


def test_forum_items_that_are_already_present_in_beyondwords_feed_are_discarded(
        default_beyondwords_input_config,
        storage,
        mocker,
        disable_write_podcast_feed
):
    forum_feed = storage.read_podcast_feed("./files/forum_feed.xml")
    duplicate_item_title = "This item should appear once in the beyondwords input feed"
    forum_feed.find("channel/item/title").text = duplicate_item_title
    # Mock get_feed_tree_from_url, so it returns the modified feed.
    mock_get_feed_tree_from_url = MagicMock(return_value=forum_feed)
    mocker.patch("feed_processing.feed_updaters.get_feed_tree_from_url", new=mock_get_feed_tree_from_url)
    # Create a file to act as the current beyondwords_input feed based on the file `./files/beyondwords_input_feed.xml`
    existing_beyondwords_input_feed = storage.read_podcast_feed("./files/beyondwords_input_feed.xml")
    # Set the value of an item in the existing beyondwords feed, so it matches the item that should not be duplicated.
    # The update function adds a shorthand as prefix and 'by <Author>' as suffix. Do this too for the test feed.
    existing_beyondwords_input_feed.find("channel/item/title").text = f"Unknown - {duplicate_item_title} by The Author"
    existing_beyondwords_input_feed.write("./files/test_beyondwords_input_feed.xml", xml_declaration=True,
                                          encoding="utf-8")
    # Set up the config so the update function loads the feed from the file we just created.
    default_beyondwords_input_config.rss_filename = "./files/test_beyondwords_input_feed.xml"

    beyondwords_input_feed = update_beyondwords_input_feed(default_beyondwords_input_config, running_on_gcp=False)

    # Retrieve titles with the substring `duplicate_item_title` in them, then assert that it is only found once.
    titles = [title.text.strip() for title in beyondwords_input_feed.findall("channel/item/title") if
              duplicate_item_title in title.text.strip()]
    assert len(titles) == 1
