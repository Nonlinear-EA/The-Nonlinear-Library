from bs4 import BeautifulSoup

from feed_processing.feed_updaters import update_beyondwords_input_feed


def test_posts_with_250_characters_or_less_in_content_are_discarded(
        default_beyondwords_input_config,
        mock_get_forum_feed_from_source,
        storage
):
    update_beyondwords_input_feed(default_beyondwords_input_config, running_on_gcp=False)

    # Retrieve feed that was just written by `update_beyondwords_input_feed`
    beyondwords_feed = storage.read_podcast_feed("./files/test_beyondwords_feed.xml")

    # Check that the content from all entries is 250 characters or more.
    assert all(len(content.text) >= 250 for content in beyondwords_feed.findall('channel/item/description'))


def test_posts_with_no_paragraph_elements_in_content_are_discarded(
        default_beyondwords_input_config,
        mock_get_forum_feed_from_source,
        storage
):
    update_beyondwords_input_feed(default_beyondwords_input_config, running_on_gcp=False)

    # Retrieve feed that was just written by `update_beyondwords_input_feed`
    beyondwords_feed = storage.read_podcast_feed("./files/test_beyondwords_feed.xml")
    content_html = [BeautifulSoup(description.text, "html.parser") for description in
                    beyondwords_feed.findall("channel/item/content")]

    # Check that all items in the feed have at least one paragraph.
    assert all(len(html_code.find_all("p")) > 0 for html_code in content_html)


def test_posts_from_other_relevant_files_are_discarded():
    pass
