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
import base64
import functions_framework

@functions_framework.cloud_event
def af_daily(cloud_event):
    print('running af_daily')
    # Print out the data from Pub/Sub
    print(base64.b64decode(cloud_event.data["message"]["data"]))
    af_daily_main()


@functions_framework.cloud_event
def af_weekly(cloud_event):
    print('running af_weekly')
    # Print out the data from Pub/Sub
    print(base64.b64decode(cloud_event.data["message"]["data"]))
    af_weekly_main()

@functions_framework.cloud_event
def af_all(cloud_event):
    print('running af_all')
    # Print out the data from Pub/Sub
    print(base64.b64decode(cloud_event.data["message"]["data"]))
    af_all_main()

@functions_framework.cloud_event
def ea_daily(cloud_event):
    print('running ea_daily')
    # Print out the data from Pub/Sub
    print(base64.b64decode(cloud_event.data["message"]["data"]))
    ea_daily_main()

@functions_framework.cloud_event
def ea_weekly(cloud_event):
    print('running ea_weekly')
    # Print out the data from Pub/Sub
    print(base64.b64decode(cloud_event.data["message"]["data"]))
    ea_weekly_main()

@functions_framework.cloud_event
def ea_all(cloud_event):
    print('running ea_all')
    # Print out the data from Pub/Sub
    print(base64.b64decode(cloud_event.data["message"]["data"]))
    ea_all_main()

@functions_framework.cloud_event
def lw_daily(cloud_event):
    print('running lw_daily')
    # Print out the data from Pub/Sub
    print(base64.b64decode(cloud_event.data["message"]["data"]))
    lw_daily_main()

@functions_framework.cloud_event
def lw_weekly(cloud_event):
    print('running lw_weekly')
    # Print out the data from Pub/Sub
    print(base64.b64decode(cloud_event.data["message"]["data"]))
    lw_weekly_main()

@functions_framework.cloud_event
def lw_all(cloud_event):
    print('running lw_all')
    # Print out the data from Pub/Sub
    print(base64.b64decode(cloud_event.data["message"]["data"]))
    lw_all_main()

@functions_framework.cloud_event
def create_nonlinear_library_main_feed(cloud_event):
    print('running create_nonlinear_library_main_feed')
    # Print out the data from Pub/Sub
    print(base64.b64decode(cloud_event.data["message"]["data"]))
    create_main_nonlinear_library_rss()
