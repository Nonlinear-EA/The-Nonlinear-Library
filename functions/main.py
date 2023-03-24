from functions.af.alignment_forum import af_all_main
from functions.af.alignment_forum_daily import af_daily_main
from functions.af.alignment_forum_weekly import af_weekly_main
from functions.ea.effective_altruism_forum import ea_all_main
from functions.ea.effective_altruism_forum_daily import ea_daily_main
from functions.ea.effective_altruism_forum_weekly import ea_weekly_main
from functions.lw.lesswrong import lw_all_main
from functions.lw.lesswrong_daily import lw_daily_main
from functions.lw.lesswrong_weekly import lw_weekly_main
from functions.nnl import create_main_nonlinear_library_rss


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
