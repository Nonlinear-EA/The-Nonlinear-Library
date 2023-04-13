from configs import af_all_config, beyondwords_input_config
from configs import af_daily_config
from configs import af_weekly_config
from configs import ea_all_config
from configs import ea_daily_config
from configs import ea_weekly_config
from configs import lw_all_config
from configs import lw_daily_config
from configs import lw_weekly_config
from create_beyondwords_inputs import generate_beyondwords_input
from podcast_feed_generator import update_podcast_feed


def af_daily(a=None, b=None):
    print('running af_daily')
    update_podcast_feed(af_daily_config(), True)


def af_weekly(a=None, b=None):
    print('running af_weekly')
    update_podcast_feed(af_weekly_config(), True)


def af_all(a=None, b=None):
    print('running af_all')
    update_podcast_feed(af_all_config(), True)


def ea_daily(a=None, b=None):
    print('running ea_daily')
    update_podcast_feed(ea_daily_config(), True)


def ea_weekly(a=None, b=None):
    print('running ea_weekly')
    update_podcast_feed(ea_weekly_config(), True)


def ea_all(a=None, b=None):
    print('running ea_all')
    update_podcast_feed(ea_all_config(), True)


def lw_daily(a=None, b=None):
    print('running lw_daily')
    update_podcast_feed(lw_daily_config(), True)


def lw_weekly(a=None, b=None):
    print('running lw_weekly')
    update_podcast_feed(lw_weekly_config(), True)


def lw_all(a=None, b=None):
    print('running lw_all')
    update_podcast_feed(lw_all_config(), True)


def create_beyondwords_nonlinear_library_project_inputs(a=None, b=None):
    print('running create_beyondwords_nonlinear_library_project_inputs')
    generate_beyondwords_input(beyondwords_input_config(), True)
