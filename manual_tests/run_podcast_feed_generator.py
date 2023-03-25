from functions.podcast_feed_generator import FeedGeneratorConfig, get_podcast_feed

if __name__ == "__main__":
    # Empty history_titles_empty.txt to guarantee an entry.
    with open('./history_titles_empty.txt', 'w') as f:
        f.write("This is a sample entry that won't match anything from the feed!")

    af_feed_cfg = FeedGeneratorConfig(
        source='./beyondwords_feed_snapshot.xml',
        author='The Nonlinear Fund',
        email='podcast@nonlinear.org',
        image_url='https://storage.googleapis.com/rssfile/images/Nonlinear%20Logo%203000x3000%20-%20Alignment%20Forum%20Daily.png',
        history_titles_filename='./history_titles_empty.txt',
        removed_authors_filename='./removed_authors.txt',
        guid_suffix='_AF-day',
        title="The Nonlinear Library: Alignment Forum Daily",
        title_prefix='AF -',
        search_period=FeedGeneratorConfig.SearchPeriod.ONE_WEEK,
        gcp_bucket='rssfile'
    )

    feed = get_podcast_feed(af_feed_cfg)
