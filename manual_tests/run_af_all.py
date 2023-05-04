from feed_processing.configs import af_all_config
from feed_processing.feed_updaters import update_feed_for_podcast_apps

if __name__ == '__main__':
    update_feed_for_podcast_apps(af_all_config(), False)
