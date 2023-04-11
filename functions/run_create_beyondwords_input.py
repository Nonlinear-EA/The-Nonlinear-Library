from functions.configs import beyondwords_af_config, beyondwords_ea_config, beyondwords_lw_config
from functions.podcast_feed_generator import generate_beyondwords_feed

if __name__ == '__main__':
    generate_beyondwords_feed(beyondwords_af_config(), False)
    generate_beyondwords_feed(beyondwords_ea_config(), False)
    generate_beyondwords_feed(beyondwords_lw_config(), False)
