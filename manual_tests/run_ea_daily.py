from functions.configs import ea_daily_config
from functions.podcast_feed_generator import generate_podcast_feed

if __name__ == '__main__':
    generate_podcast_feed(ea_daily_config(), False)
