from functions.configs import ea_weekly_config
from functions.podcast_feed_generator import update_podcast_feed

if __name__ == '__main__':
    update_podcast_feed(ea_weekly_config(), False)
