from functions.feed import FeedGeneratorConfig


def alignment_forum_daily():
    feed_config = FeedGeneratorConfig(
        source='https://audio.beyondwords.io/f/8692/7888/read_8617d3aee53f3ab844a309d37895c143',
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
