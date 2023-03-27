from af.alignment_forum import af_all_main
from af.alignment_forum_daily import af_daily_main
from af.alignment_forum_weekly import af_weekly_main
from ea.effective_altruism_forum import ea_all_main
from ea.effective_altruism_forum_daily import ea_daily_main
from ea.effective_altruism_forum_weekly import ea_weekly_main
from lw.lesswrong import lw_all_main
from lw.lesswrong_daily import lw_daily_main
from lw.lesswrong_weekly import lw_weekly_main
from nnl import create_main_nonlinear_library_rss
import functions_framework

@functions_framework.cloud_event
def af_daily():
    print('running af_daily')
    af_daily_main()


@functions_framework.cloud_event
def af_weekly():
    print('running af_weekly')
    af_weekly_main()

@functions_framework.cloud_event
def af_all():
    print('running af_all')
    af_all_main()

@functions_framework.cloud_event
def ea_daily():
    print('running ea_daily')
    ea_daily_main()

@functions_framework.cloud_event
def ea_weekly():
    print('running ea_weekly')
    ea_weekly_main()

@functions_framework.cloud_event
def ea_all():
    print('running ea_all')
    ea_all_main()

@functions_framework.cloud_event
def lw_daily():
    print('running lw_daily')
    lw_daily_main()

@functions_framework.cloud_event
def lw_weekly():
    print('running lw_weekly')
    lw_weekly_main()

@functions_framework.cloud_event
def lw_all():
    print('running lw_all')
    lw_all_main()

@functions_framework.cloud_event
def create_nonlinear_library_main_feed():
    print('running create_nonlinear_library_main_feed')
    create_main_nonlinear_library_rss()
