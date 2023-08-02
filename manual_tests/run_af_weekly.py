import logging
import os
import sys

from feed_processing.configs import af_weekly_config
from feed_processing.feed_updaters import update_podcast_provider_feed

if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    os.environ["GCP_BUCKET_NAME"] = "newcode"
    update_podcast_provider_feed(af_weekly_config(), False)
