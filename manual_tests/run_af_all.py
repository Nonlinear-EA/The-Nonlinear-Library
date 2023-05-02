from functions.configs import af_all_config
from functions.feed_updaters import update_podcast_feed

if __name__ == '__main__':
    update_podcast_feed(af_all_config(), False)
