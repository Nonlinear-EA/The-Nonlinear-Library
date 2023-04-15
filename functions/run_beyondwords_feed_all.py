from functions.configs import beyondwords_af_config, beyondwords_ea_config, beyondwords_lw_config
from functions.podcast_feed_generator import update_beyondwords_input_feed

if __name__ == '__main__':
    update_beyondwords_input_feed(beyondwords_af_config(), False)
    update_beyondwords_input_feed(beyondwords_ea_config(), False)
    update_beyondwords_input_feed(beyondwords_lw_config(), False)
