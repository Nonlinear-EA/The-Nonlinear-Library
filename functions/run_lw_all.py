from functions.configs import lw_all_config
from functions.podcast_feed_generator import update_podcast_feed

if __name__ == '__main__':
    update_podcast_feed(lw_all_config(), False)
