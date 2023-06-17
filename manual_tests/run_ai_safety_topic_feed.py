import logging
import os
import sys

from feed_processing.configs import beyondwords_rss_output, nll_author, nonlinear_email, podcast_description, \
    gcp_bucket_newcode
from feed_processing.feed_config import PodcastProviderFeedConfig
from feed_processing.feed_updaters import update_podcast_provider_feed

ai_safety_feed_config = PodcastProviderFeedConfig(
    source=beyondwords_rss_output,
    author=nll_author,
    email=nonlinear_email,
    image_url='https://storage.googleapis.com/rssfile/images/Nonlinear%20Logo%203000x3000%20-%20LessWrong%20Weekly.png',
    guid_suffix='_LW-week',
    title='The Nonlinear Library: LessWrong Weekly',
    description=podcast_description,
    title_prefix='LW - ',
    search_period=PodcastProviderFeedConfig.SearchPeriod.ONE_WEEK,
    gcp_bucket=gcp_bucket_newcode,
    rss_filename='nonlinear-library-ai-safety.xml',
    top_post_only=True,
    podcast_topic="AI Safety",
    removed_authors_file="removed_authors.txt"
)

if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    os.environ["GCP_BUCKET_NAME"] = "newcode"
    update_podcast_provider_feed(ai_safety_feed_config, False)
