from functions.configs import beyondwords_af_config
from functions.podcast_feed_generator import generate_beyondwords_feed

if __name__ == '__main__':
    generate_beyondwords_feed(beyondwords_af_config(), False)
