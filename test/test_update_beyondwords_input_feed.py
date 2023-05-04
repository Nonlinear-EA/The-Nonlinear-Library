import pytest
from bs4 import BeautifulSoup

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


def test_posts_with_250_characters_or_less_in_content_are_discarded(
        default_beyondwords_input_config,
        mock_get_feed_tree_from_url_to_return_test_forum_feed,
        storage
):
    update_beyondwords_input_feed(default_beyondwords_input_config, running_on_gcp=False)

    # Retrieve feed that was just written by `update_beyondwords_input_feed`
    beyondwords_feed = storage.read_podcast_feed("./files/beyondwords_input_feed.xml")

    # Check that the content from all entries is 250 characters or more.
    assert all(len(content.text) >= 250 for content in beyondwords_feed.findall('channel/item/description'))


def test_posts_with_no_paragraph_elements_in_content_are_discarded(
        default_beyondwords_input_config,
        mock_get_feed_tree_from_url_to_return_test_forum_feed,
        storage
):
    update_beyondwords_input_feed(default_beyondwords_input_config, running_on_gcp=False)

    # Retrieve feed that was just written by `update_beyondwords_input_feed`
    beyondwords_feed = storage.read_podcast_feed("./files/beyondwords_input_feed.xml")
    content_html = [BeautifulSoup(description.text, "html.parser") for description in
                    beyondwords_feed.findall("channel/item/content")]
    number_of_p_elements_per_item = [len(html_code.find_all("p")) for html_code in content_html]

    # Check that all items in the feed have at least one paragraph.
    assert all(number_of_p_tags > 0 for number_of_p_tags in number_of_p_elements_per_item)


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
