import logging
from functools import reduce

from lxml import etree

from feed_processing.configs import beyondwords_feed_namespaces
from feed_processing.feed_config import PodcastProviderFeedConfig, BeyondWordsInputConfig
from feed_processing.storage import create_storage
from feed_processing.utils import save_feed, get_feed_tree_from_url, filter_entries_by_forum_title_prefix, \
    filter_entries_by_search_period, filter_top_post, add_link_to_original_article_to_feed_items_description, \
    append_new_items_to_feed, update_feed_datum, get_titles_from_feed, remove_items_also_found_in_other_relevant_files, \
    add_author_tag_to_feed_items, remove_posts_without_paragraphs_in_description, \
    remove_posts_with_less_than_the_minimum_characters_in_description, edit_item_description, \
    prepend_website_abbreviation_to_feed_item_titles, append_author_to_item_titles, remove_items_from_removed_authors


def update_podcast_provider_feed(
        feed_config: PodcastProviderFeedConfig,
        running_on_gcp
):
    """
    Get an RSS feed for podcast apps that is produced from a source and applying filtering criteria defined in the
    provided feed_config object.

    Args:
        feed_config: Object with meta-data and filtering criteria to produce an RSS feed file.
        running_on_gcp: True if function is running on Google Cloud else False

    Returns: The file name of the produced XML string and the xml string and the title of the new episode
    """

    logger = logging.getLogger(f"function:{update_podcast_provider_feed.__name__}")

    feed = get_feed_tree_from_url(feed_config.source)

    # Apply filters and formatting to the feed items.
    feed = filter_entries_by_forum_title_prefix(feed, feed_config.title_prefix)
    if feed_config.search_period:
        feed = filter_entries_by_search_period(feed, feed_config)
    if feed_config.top_post_only:
        feed = filter_top_post(feed)
    feed = remove_items_from_removed_authors(feed, feed_config, running_on_gcp)
    feed = add_link_to_original_article_to_feed_items_description(feed)

    # Add new items to the podcast apps feed.
    storage = create_storage(feed_config, running_on_gcp)
    feed_for_podcast_apps = storage.read_podcast_feed()
    items_from_beyondwords_output_feed = feed.findall("channel/item")
    new_items, feed = append_new_items_to_feed(items_from_beyondwords_output_feed, feed_for_podcast_apps)

    # Update feed meta-data
    feed = update_feed_datum(feed, "channel/title", feed_config.title)
    feed = update_feed_datum(feed, "channel/description", feed_config.description)
    feed = update_feed_datum(feed, "channel/author", feed_config.author)
    feed = update_feed_datum(feed, "channel/image/url", feed_config.image_url)

    # Update meta-data with custom namespaces
    itunes_summary = feed.find("channel/{%s}summary" % beyondwords_feed_namespaces["itunes"])
    if itunes_summary is None:
        itunes_summary = etree.Element("{%s}summary" % beyondwords_feed_namespaces["itunes"],
                                       nsmap=beyondwords_feed_namespaces)
        itunes_summary.text = feed_config.description
        feed.find("channel").append(itunes_summary)
    else:
        itunes_summary.text = feed_config.description

    itunes_image = feed.find("channel/{%s}image" % beyondwords_feed_namespaces["itunes"])
    if itunes_image is None:
        itunes_image = etree.Element("{%s}image" % beyondwords_feed_namespaces["itunes"],
                                     attrib={"href": feed_config.image_url},
                                     nsmap=beyondwords_feed_namespaces)
        feed.find("channel").append(itunes_image)
    else:
        itunes_image.attrib["href"] = feed_config.image_url

    # Update meta-data of new items
    for item in feed.findall("channel/item"):
        feed_itunes_image = item.find("{%s}image" % beyondwords_feed_namespaces["itunes"])
        if feed_itunes_image is None:
            item_itunes_image = etree.Element("{%s}image" % beyondwords_feed_namespaces["itunes"],
                                              attrib={"href": feed_config.image_url},
                                              nsmap=beyondwords_feed_namespaces)
            item.append(item_itunes_image)
        else:
            feed_itunes_image.attrib["href"] = feed_config.image_url

    if not new_items:
        logger.info("No new items to add to podcast provider feed input feed.")
    else:
        logger.info(f"Adding {len(new_items)} items to the podcast provider feed in {feed_config.rss_filename}")

    save_feed(feed, storage)

    return feed


def update_beyondwords_input_feed(config: BeyondWordsInputConfig, running_on_gcp=True):
    """
    Update the BeyondWords input feed with the new posts from a forum.

    Args:
        config: Object with meta-data and to update the BeyondWords RSS feed file.
        running_on_gcp: True if function is running on GCP otherwise False

    """
    logger = logging.getLogger(f"function:{update_beyondwords_input_feed.__name__}")

    feed = get_feed_tree_from_url(config.source)

    # Peek into other relevant feeds and retrieve the titles.
    def concatenate_item_titles(previous_titles, next_feed_filename):
        return previous_titles + get_titles_from_feed(next_feed_filename, config, running_on_gcp)

    titles_from_other_feeds = reduce(concatenate_item_titles, config.relevant_feeds, [])

    # Remove duplicates from other relevant feeds.
    feed = remove_items_also_found_in_other_relevant_files(feed, titles_from_other_feeds)

    # The author tag is used to remove posts from removed authors, append it to each item
    feed = add_author_tag_to_feed_items(feed)

    # Remove items that are too short.
    feed = remove_posts_without_paragraphs_in_description(feed)
    feed = remove_posts_with_less_than_the_minimum_characters_in_description(feed, config.min_chars)

    # Appends intro and outro to description and creates content tag if not present.
    # Create content tag.
    feed = edit_item_description(feed)

    feed = remove_items_from_removed_authors(feed, config, running_on_gcp)

    # Modify item titles by prepending the forum abbreviation
    feed = prepend_website_abbreviation_to_feed_item_titles(feed)

    # Modify item titles by appending 'by <author>'
    feed = append_author_to_item_titles(feed)

    new_feed_items = feed.findall('channel/item')

    if not new_feed_items:
        logger.info("No new items to add to BeyondWords input feed.")

    # Append new items to feed
    storage = create_storage(config, running_on_gcp)
    beyondwords_input_feed = storage.read_podcast_feed()
    new_items, feed = append_new_items_to_feed(new_feed_items, beyondwords_input_feed)

    if not new_items:
        logger.info("No new items to add to BeyondWords input feed.")
    else:
        logger.info(f"Adding {len(new_items)} to the BeyondWords input feed in {config.rss_filename}")

    save_feed(beyondwords_input_feed, storage)

    return feed
