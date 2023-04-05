from podcast_feed_generator import FeedGeneratorConfig, generate_podcast_feed

if __name__ == "__main__":
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
        gcp_bucket='rssfile',
        output_file_basename='nonlinear-library-aggregated-AF-daily-new'
    )

    feed = generate_podcast_feed(af_feed_cfg, False)
