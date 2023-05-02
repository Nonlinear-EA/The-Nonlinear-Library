from configs import ea_weekly_config
from feed_updaters import update_podcast_feed

if __name__ == '__main__':
    update_podcast_feed(ea_weekly_config(), False)
