from unittest.mock import MagicMock

import pytest

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


def test_posts_with_250_characters_or_less_in_description_are_discarded(
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
    default_beyondwords_input_config.min_chars = 100
    item_description = """This description is shorter than usual but the character threshold is set so that it is not 
    discarded because of that. It should be discarded because it has no p tags"""
    item_to_modify = forum_feed.find("channel/item")
    item_to_modify.find("description").text = item_description
    item_to_modify.find("title").text = "This item should be discarded"

    # Mock get_feed_tree_from_url, so it returns the modified feed.
    mock_get_feed_tree_from_url = MagicMock(return_value=forum_feed)
    mocker.patch("feed_processing.feed_updaters.get_feed_tree_from_url", new=mock_get_feed_tree_from_url)

    beyondwords_input_feed = update_beyondwords_input_feed(default_beyondwords_input_config, running_on_gcp=False)

    # Retrieve feed that was just written by `update_beyondwords_input_feed`
    item_titles = [title.text for title in beyondwords_input_feed.findall("channel/item/title")]

    # Check that all items in the feed have at least one paragraph.
    assert not any("This item should be discarded" in title for title in item_titles)


def test_posts_that_area_already_present_in_other_relevant_files_are_discarded(
        default_beyondwords_input_config,
        mock_get_feed_tree_from_url_to_return_test_forum_feed,
        storage
):
    update_beyondwords_input_feed(default_beyondwords_input_config, running_on_gcp=False)

    # Retrieve titles from newly written feed.
    beyondwords_feed = storage.read_podcast_feed("./files/beyondwords_input_feed.xml")
    item_titles = [title.text for title in beyondwords_feed.findall("channel/item/title")]

    # An item with title 'This entry is in relevant_forum_feed_1.xml' is indeed present in the file
    # `test/files/relevant_forum_feed_1.xml` and in `test/files/forum_feed.xml`.
    assert not any("This entry is in relevant_forum_feed_1.xml" in title for title in item_titles)


def test_posts_from_removed_authors_are_discarded(
        default_beyondwords_input_config,
        mock_get_feed_tree_from_url_to_return_test_forum_feed,
        storage
):
    update_beyondwords_input_feed(default_beyondwords_input_config, running_on_gcp=False)

    # Retrieve the newly updated feed.
    beyondwords_feed = storage.read_podcast_feed("./files/beyondwords_input_feed.xml")
    # Retrieve the authors.
    authors = [creator.text.strip() for creator in beyondwords_feed.findall("channel/item/author")]

    # 'RemovedAuthor' is present in the `files/removed_authors.txt` file, so any posts from them should be excluded
    # from the beyondwords feed.
    assert not any(author == "RemovedAuthor" for author in authors)


def test_forum_items_that_are_already_present_in_beyondwords_feed_are_discarded(
        default_beyondwords_input_config,
        mock_get_feed_tree_from_url_to_return_test_forum_feed,
        storage
):
    update_beyondwords_input_feed(default_beyondwords_input_config, running_on_gcp=False)

    # Retrieve the newly generated feed
    beyondwords_feed = storage.read_podcast_feed("./files/beyondwords_input_feed.xml")

    # Check that the item with title 'This is a history item' is present only once.
    # Retrieve titles that match 'This is a history item'
    titles = [title.text.strip() for title in beyondwords_feed.findall("channel/item/title") if
              "This is a history item" in title.text.strip()]

    # An item with the title "Unknown - This is a history item by The Author" is present in both the beyondwords feed
    # and the forum's test feed. Each entry should appear only once in the beyondwords feed.
    assert len(titles) == 1
