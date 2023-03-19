from functions.af.aggregator_af import af_all_main
from functions.af.aggregator_af_daily import af_daily_main
from functions.af.aggregator_af_weekly import af_weekly_main
from functions.ea.aggregator_ea import ea_all_main
from functions.ea.aggregator_ea_daily import ea_daily_main
from functions.ea.aggregator_ea_weekly import ea_weekly_main
from functions.first_generator import create_main_nonlinear_library_rss
from functions.lw.aggregator_lw import lw_all_main
from functions.lw.aggregator_lw_daily import lw_daily_main
from functions.lw.aggregator_lw_weekly import lw_weekly_main


def af_daily():
    af_daily_main()


def af_weekly():
    af_weekly_main()


def af_all():
    af_all_main()


def ea_daily():
    ea_daily_main()


def ea_weekly():
    ea_weekly_main()


def ea_all():
    ea_all_main()


def lw_daily():
    lw_daily_main()


def lw_weekly():
    lw_weekly_main()


def lw_all():
    lw_all_main()


def create_nonlinear_library_main_feed():
    create_main_nonlinear_library_rss()
