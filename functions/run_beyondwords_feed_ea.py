from functions.configs import beyondwords_ea_config
from functions.feed_updaters import update_beyondwords_input_feed

if __name__ == '__main__':
    update_beyondwords_input_feed(beyondwords_ea_config(), False)
