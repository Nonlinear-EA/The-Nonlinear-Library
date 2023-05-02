from feed_processing.configs import beyondwords_lw_config
from feed_processing.feed_updaters import update_beyondwords_input_feed

if __name__ == '__main__':
    update_beyondwords_input_feed(beyondwords_lw_config(), False)
