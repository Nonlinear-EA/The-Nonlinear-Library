from functions.daily_aggregator import FeedConfig, daily_aggregator

if __name__ == "__main__":
    af_feed_cfg = FeedConfig(
        source='./beyondwords_feed_snapshot.xml',
        author='The Nonlinear Fund',
        email='podcast@nonlinear.org',
        image_url='https://storage.googleapis.com/rssfile/images/Nonlinear%20Logo%203000x3000%20-%20Alignment%20Forum%20Daily.png',
        history_titles_file='./history_titles_nonlinear-library-aggregated-AF-daily.txt',
        guid_suffix='_AF-day',
        title="The Nonlinear Library: Alignment Forum Daily",
        title_regex=r'^AF -'
    )

    daily_aggregator(af_feed_cfg)
