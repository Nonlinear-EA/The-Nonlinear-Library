from functions.feed import FeedConfig, Feed
from functions.storage import get_storage


def daily_aggregator(feedconfig: FeedConfig):
    feed = Feed.from_url(feedconfig.source)

    # Retrieve history titles from storage
    storage = get_storage(local=True)
    history_titles_file = storage.get_file(feedconfig.history_titles_file)
    history_titles = [l.rstrip() for l in history_titles_file.readlines()]
    history_titles_file.close()

    print(history_titles)

    # Pseudo-code:
    # feed = retrieve_feed_from_url(url)
    # values_for_podcast_feed = get_values_for_podcast_feed('Alignment Forum')
    # feed.update_values(values_for_podcast_feed)
    # Filter out entries from removed authors
    # feed.entries = [e for entry in feed.entries if e.author not in removed_authors]
