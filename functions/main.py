
from functions.af.alignment_forum import af_all_main
from functions.af.alignment_forum_daily import af_daily_main
from functions.af.alignment_forum_weekly import af_weekly_main
from functions.ea.effective_altruism_forum import ea_all_main
from functions.ea.effective_altruism_forum_daily import ea_daily_main
from functions.ea.effective_altruism_forum_weekly import ea_weekly_main
from functions.lw.lesswrong import lw_all_main
from functions.lw.lesswrong_daily import lw_daily_main
from functions.lw.lesswrong_weekly import lw_weekly_main
from functions.nnl import main_create_beyondwords_nonlinear_library_project_inputs


def af_daily(a=None, b=None):
    print('running af_daily')
    af_daily_main(True)

def af_weekly(a=None, b=None):
    print('running af_weekly')
    af_weekly_main(True)


def af_all(a=None, b=None):
    print('running af_all')
    af_all_main(True)


def ea_daily(a=None, b=None):
    print('running ea_daily')
    ea_daily_main(True)


def ea_weekly(a=None, b=None):
    print('running ea_weekly')
    ea_weekly_main(True)


def ea_all(a=None, b=None):
    print('running ea_all')
    ea_all_main(True)


def lw_daily(a=None, b=None):
    print('running lw_daily')
    lw_daily_main(True)


def lw_weekly(a=None, b=None):
    print('running lw_weekly')
    lw_weekly_main(True)


def lw_all(a=None, b=None):
    print('running lw_all')
    lw_all_main(True)


def create_beyondwords_nonlinear_library_project_inputs(a=None, b=None):
    print('running create_nonlinear_library_main_feed')
    main_create_beyondwords_nonlinear_library_project_inputs()
