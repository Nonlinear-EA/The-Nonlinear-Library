import logging
import sys

from feed_processing.configs import ea_all_config
from feed_processing.feed_updaters import update_podcast_provider_feed

if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    update_podcast_provider_feed(ea_all_config(), False)
