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
from feed_processing.feed_updaters import update_feed_for_podcast_apps, update_beyondwords_input_feed
from manual_tests.xml_file_integrity_check import check_xml_files_integrity


def af_daily(a=None, b=None):
    print('running af_daily')
    update_feed_for_podcast_apps(af_daily_config(), True)


def af_weekly(a=None, b=None):
    print('running af_weekly')
    update_feed_for_podcast_apps(af_weekly_config(), True)


def af_all(a=None, b=None):
    print('running af_all')
    update_feed_for_podcast_apps(af_all_config(), True)


def ea_daily(a=None, b=None):
    print('running ea_daily')
    update_feed_for_podcast_apps(ea_daily_config(), True)


def ea_weekly(a=None, b=None):
    print('running ea_weekly')
    update_feed_for_podcast_apps(ea_weekly_config(), True)


def ea_all(a=None, b=None):
    print('running ea_all')
    update_feed_for_podcast_apps(ea_all_config(), True)


def lw_daily(a=None, b=None):
    print('running lw_daily')
    update_feed_for_podcast_apps(lw_daily_config(), True)


def lw_weekly(a=None, b=None):
    print('running lw_weekly')
    update_feed_for_podcast_apps(lw_weekly_config(), True)


def lw_all(a=None, b=None):
    print('running lw_all')
    update_feed_for_podcast_apps(lw_all_config(), True)


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


def do_xml_file_integrity_checks(a=None, b=None):
    xml_files_urls = [
        "https://storage.googleapis.com/rssfile/nonlinear-library-aggregated-EA.xml",
        "https://storage.googleapis.com/rssfile/nonlinear-library-aggregated-EA-daily.xml",
        "https://storage.googleapis.com/rssfile/nonlinear-library-aggregated-EA-weekly.xml",
        "https://storage.googleapis.com/rssfile/nonlinear-library-aggregated-AF.xml",
        "https://storage.googleapis.com/rssfile/nonlinear-library-aggregated-AF-daily.xml",
        "https://storage.googleapis.com/rssfile/nonlinear-library-aggregated-AF-weekly.xml",
        "https://storage.googleapis.com/rssfile/nonlinear-library-aggregated-LW.xml",
        "https://storage.googleapis.com/rssfile/nonlinear-library-aggregated-LW-daily.xml",
        "https://storage.googleapis.com/rssfile/nonlinear-library-aggregated-LW-weekly.xml",
        "https://storage.googleapis.com/rssfile/nonlinear-library-aggregated.xml"
    ]
    check_xml_files_integrity(xml_files_urls)
