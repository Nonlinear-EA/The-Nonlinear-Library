from feed_processing.configs import af_all_config, beyondwords_ea_config, beyondwords_af_config, beyondwords_lw_config
from feed_processing.configs import af_daily_config
from feed_processing.configs import af_weekly_config
from feed_processing.configs import ea_all_config
from feed_processing.configs import ea_daily_config
from feed_processing.configs import ea_weekly_config
from feed_processing.configs import lw_all_config
from feed_processing.configs import lw_daily_config
from feed_processing.configs import lw_weekly_config
from feed_processing.create_beyondwords_inputs import main_create_beyondwords_nonlinear_library_project_inputs
from feed_processing.feed_updaters import update_podcast_feed, update_beyondwords_input_feed


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


def beyondwords_af(a=None, b=None):
    print('running beyondwords_af')
    update_beyondwords_input_feed(beyondwords_af_config(), True)


def beyondwords_ea(a=None, b=None):
    print('running beyondwords_ea')
    update_beyondwords_input_feed(beyondwords_ea_config(), True)


def beyondwords_lw(a=None, b=None):
    print('running beyondwords_lw')
    update_beyondwords_input_feed(beyondwords_lw_config(), True)


def create_beyondwords_nonlinear_library_project_inputs(a=None, b=None):
    print("running create_beyondwords_nonlinear_library_project_inputs")
    main_create_beyondwords_nonlinear_library_project_inputs(False)