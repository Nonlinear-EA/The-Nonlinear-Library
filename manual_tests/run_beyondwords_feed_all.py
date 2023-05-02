from feed_processing.configs import beyondwords_af_config, beyondwords_ea_config, beyondwords_lw_config
from feed_processing.feed_updaters import update_beyondwords_input_feed

if __name__ == '__main__':
    update_beyondwords_input_feed(beyondwords_af_config(), False)
    update_beyondwords_input_feed(beyondwords_ea_config(), False)
    update_beyondwords_input_feed(beyondwords_lw_config(), False)
