from functions.configs import af_all_config
from functions.podcast_feed_generator import update_podcast_feed

if __name__ == '__main__':
    update_podcast_feed(af_all_config(), False)
