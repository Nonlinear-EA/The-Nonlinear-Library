from functions.podcast_feed_generator import FeedConfig, get_podcast_feed

if __name__ == "__main__":
    af_feed_cfg = FeedConfig(
        source='./beyondwords_feed_snapshot.xml',
        author='The Nonlinear Fund',
        email='podcast@nonlinear.org',
        image_url='https://storage.googleapis.com/rssfile/images/Nonlinear%20Logo%203000x3000%20-%20Alignment%20Forum%20Daily.png',
        history_titles_file='./history_titles_nonlinear-library-aggregated-AF-daily.txt',
        removed_authors_file='./removed_authors.txt',
        guid_suffix='_AF-day',
        title="The Nonlinear Library: Alignment Forum Daily",
        title_regex=r'^AF -',
        search_period='-1 day'
    )

    get_podcast_feed(af_feed_cfg)
