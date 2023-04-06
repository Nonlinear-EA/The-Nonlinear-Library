from functions.configs import beyondwords_input_config
from functions.podcast_feed_generator import generate_beyondwords_input

if __name__ == '__main__':
    generate_beyondwords_input(beyondwords_input_config(), False)
