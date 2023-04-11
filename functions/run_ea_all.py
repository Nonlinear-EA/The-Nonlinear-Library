from configs import ea_all_config
from podcast_feed_generator import update_podcast_feed

if __name__ == '__main__':
    update_podcast_feed(ea_all_config(), False)
