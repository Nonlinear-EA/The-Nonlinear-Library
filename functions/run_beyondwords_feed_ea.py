from functions.configs import beyondwords_ea_config
from functions.podcast_feed_generator import update_beyondwords_input_feed

if __name__ == '__main__':
    update_beyondwords_input_feed(beyondwords_ea_config(), False)
