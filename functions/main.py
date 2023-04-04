from configs import af_all_config
from configs import af_daily_config
from configs import af_weekly_config
from configs import ea_all_config
from configs import ea_daily_config
from configs import ea_weekly_config
from configs import lw_all_config
from configs import lw_daily_config
from configs import lw_weekly_config
from nnl import main_create_beyondwords_nonlinear_library_project_inputs
from podcast_feed_generator import generate_podcast_feed


def af_daily(a=None, b=None):
    print('running af_daily')
    generate_podcast_feed(af_daily_config(), True)


def af_weekly(a=None, b=None):
    print('running af_weekly')
    generate_podcast_feed(af_weekly_config(), True)


def af_all(a=None, b=None):
    print('running af_all')
    generate_podcast_feed(af_all_config(), True)


def ea_daily(a=None, b=None):
    print('running ea_daily')
    generate_podcast_feed(ea_daily_config(), True)


def ea_weekly(a=None, b=None):
    print('running ea_weekly')
    generate_podcast_feed(ea_weekly_config(), True)


def ea_all(a=None, b=None):
    print('running ea_all')
    generate_podcast_feed(ea_all_config(), True)


def lw_daily(a=None, b=None):
    print('running lw_daily')
    generate_podcast_feed(lw_daily_config(), True)


def lw_weekly(a=None, b=None):
    print('running lw_weekly')
    generate_podcast_feed(lw_weekly_config(), True)


def lw_all(a=None, b=None):
    print('running lw_all')
    generate_podcast_feed(lw_all_config(), True)


def create_beyondwords_nonlinear_library_project_inputs(a=None, b=None):
    print('running create_beyondwords_nonlinear_library_project_inputs')
    main_create_beyondwords_nonlinear_library_project_inputs()
