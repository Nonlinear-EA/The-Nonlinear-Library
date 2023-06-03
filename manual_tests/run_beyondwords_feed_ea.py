import os

from feed_processing.configs import beyondwords_ea_config
from feed_processing.feed_updaters import update_beyondwords_input_feed

if __name__ == '__main__':
    os.environ["GCP_BUCKET_NAME"] = "newcode"
    update_beyondwords_input_feed(beyondwords_ea_config(), False)
