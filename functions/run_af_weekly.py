from configs import af_weekly_config
from podcast_feed_generator import update_podcast_feed

if __name__ == '__main__':
    update_podcast_feed(af_weekly_config(), False)
