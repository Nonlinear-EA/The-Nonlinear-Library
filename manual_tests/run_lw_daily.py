from configs import lw_daily_config
from feed_updaters import update_podcast_feed

if __name__ == '__main__':
    update_podcast_feed(lw_daily_config(), False)
