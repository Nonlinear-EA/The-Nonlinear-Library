from functions.configs import beyondwords_input_config
from functions.podcast_feed_generator import generate_beyondwords_feed

if __name__ == '__main__':
    generate_beyondwords_feed(beyondwords_input_config(), False)
