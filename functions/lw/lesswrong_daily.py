from functions.feed import FeedGeneratorConfig
from functions.podcast_feed_generator import generate_podcast_feed


def lw_daily_main():
    generate_podcast_feed(
        FeedGeneratorConfig(
            source='https://audio.beyondwords.io/f/8692/7888/read_8617d3aee53f3ab844a309d37895c143',
            author='The Nonlinear Fund',
            email='podcast@nonlinear.org',
            image_url='https://storage.googleapis.com/rssfile/images/Nonlinear%20Logo%203000x3000%20-%20LessWrong%20Daily.png',
            history_titles_filename='./history_titles_nonlinear-library-aggregated-LW-daily.txt',
            removed_authors_filename='./removed_authors.txt',
            title="The Nonlinear Library: LessWrong Daily",
            guid_suffix='_LW-day',
            search_period=FeedGeneratorConfig.SearchPeriod.ONE_DAY,
            title_prefix='LW - ',
            gcp_bucket='rssfile',
            output_file_basename='nonlinear-library-aggregated-LW-daily'
        )
    )
