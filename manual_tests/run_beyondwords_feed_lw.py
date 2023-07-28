import logging
import os
import sys

from feed_processing.configs import beyondwords_lw_config
from feed_processing.feed_updaters import update_beyondwords_input_feed

if __name__ == '__main__':
    os.environ["GCP_BUCKET_NAME"] = "newcode"
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    update_beyondwords_input_feed(beyondwords_lw_config(), False)
