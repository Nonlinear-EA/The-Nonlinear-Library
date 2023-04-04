from feed import FeedGeneratorConfig
from podcast_feed_generator import generate_podcast_feed


def af_daily_main(running_on_gcp):
    generate_podcast_feed(
        FeedGeneratorConfig(
            source='https://audio.beyondwords.io/f/8692/7888/read_8617d3aee53f3ab844a309d37895c143',
            author='The Nonlinear Fund',
            email='podcast@nonlinear.org',
            image_url='https://storage.googleapis.com/rssfile/images/Nonlinear%20Logo%203000x3000%20-%20Alignment%20Forum%20Daily.png',
            guid_suffix='_AF-day',
            title="The Nonlinear Library: Alignment Forum Daily",
            title_prefix='AF - ',
            search_period=FeedGeneratorConfig.SearchPeriod.ONE_DAY,
            gcp_bucket='newcode',
            output_basename='af_daily'
        ), running_on_gcp)
