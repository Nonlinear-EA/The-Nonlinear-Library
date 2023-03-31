from functions.feed import FeedGeneratorConfig
from functions.podcast_feed_generator import generate_podcast_feed


def ea_weekly_main():
    generate_podcast_feed(
        FeedGeneratorConfig(
            source='https://audio.beyondwords.io/f/8692/7888/read_8617d3aee53f3ab844a309d37895c143',
            author='The Nonlinear Fund',
            email='podcast@nonlinear.org',
            image_url='https://storage.googleapis.com/rssfile/images/Nonlinear%20Logo%203000x3000%20-%20EA%20Forum%20Weekly.png',
            history_titles_filename='./history_titles_nonlinear-library-aggregated-EA-weekly.txt',
            removed_authors_filename='./removed_authors.txt',
            guid_suffix='_EA-week',
            title='The Nonlinear Library: EA Forum Weekly',
            title_prefix='EA - ',
            search_period=FeedGeneratorConfig.SearchPeriod.ONE_WEEK,
            output_file_basename='nonlinear-library-aggregated-AF-weekly',
            gcp_bucket='rssfile'
        )
    )