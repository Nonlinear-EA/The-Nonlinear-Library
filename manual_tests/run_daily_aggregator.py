from functions.daily_aggregator import FeedConfig, daily_aggregator

if __name__ == "__main__":
    af_feed_cfg = FeedConfig(
        source_url='https://audio.beyondwords.io/f/8692/7888/read_8617d3aee53f3ab844a309d37895c143',
        author='The Nonlinear Fund',
        email='podcast@nonlinear.org',
        image_url='https://storage.googleapis.com/rssfile/images/Nonlinear%20Logo%203000x3000%20-%20Alignment%20Forum%20Daily.png',
        history_titles_file='./history_titles_nonlinear-library-aggregated-AF-daily.txt'
    )

    daily_aggregator(af_feed_cfg)
