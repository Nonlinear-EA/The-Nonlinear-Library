from feed import FeedGeneratorConfig
from podcast_feed_generator import generate_podcast_feed


def lw_daily_main(running_on_gcp):
    generate_podcast_feed(
        FeedGeneratorConfig(
            source='https://audio.beyondwords.io/f/8692/7888/read_8617d3aee53f3ab844a309d37895c143',
            author='The Nonlinear Fund',
            email='podcast@nonlinear.org',
            image_url='https://storage.googleapis.com/rssfile/images/Nonlinear%20Logo%203000x3000%20-%20LessWrong%20Daily.png',
            title='The Nonlinear Library: LessWrong Daily',
            guid_suffix='_LW-day',
            search_period=FeedGeneratorConfig.SearchPeriod.ONE_DAY,
            title_prefix='LW - ',
            gcp_bucket='newcode',
            output_basename='lw_daily'
        ),
        running_on_gcp
    )
