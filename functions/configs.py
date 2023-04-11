from feed import FeedGeneratorConfig

beyondwords_rss_output = 'https://audio.beyondwords.io/f/8692/7888/read_8617d3aee53f3ab844a309d37895c143'
nll_author = 'The Nonlinear Fund'
gcp_bucket_newcode = 'newcode'
nonlinear_email = 'podcast@nonlinear.org'


def af_all_config():
    return FeedGeneratorConfig(
        source=beyondwords_rss_output,
        author=nll_author,
        email=nonlinear_email,
        image_url='https://storage.googleapis.com/rssfile/images/Nonlinear%20Logo%203000x3000%20-%20Alignment%20Forum.png',
        title="The Nonlinear Library: Alignment Forum",
        title_prefix='AF -',
        guid_suffix='_AF',
        gcp_bucket=gcp_bucket_newcode,
        history_titles_filename='af_all',
        rss_filename='nonlinear-library-aggregated-AF.xml',
        top_post_only=False,
        search_period=None
    )


def af_daily_config():
    return FeedGeneratorConfig(
        source=beyondwords_rss_output,
        author=nll_author,
        email=nonlinear_email,
        image_url='https://storage.googleapis.com/rssfile/images/Nonlinear%20Logo%203000x3000%20-%20Alignment%20Forum%20Daily.png',
        guid_suffix='_AF-day',
        title="The Nonlinear Library: Alignment Forum Daily",
        title_prefix='AF - ',
        search_period=FeedGeneratorConfig.SearchPeriod.ONE_DAY,
        gcp_bucket=gcp_bucket_newcode,
        history_titles_filename='af_daily',
        rss_filename='nonlinear-library-aggregated-AF-daily.xml',
        top_post_only=True
    )


def af_weekly_config():
    return FeedGeneratorConfig(
        source=beyondwords_rss_output,
        author=nll_author,
        email=nonlinear_email,
        image_url='https://storage.googleapis.com/rssfile/images/Nonlinear%20Logo%203000x3000%20-%20Alignment%20Forum%20Weekly.png',
        guid_suffix='_AF-week',
        title="The Nonlinear Library: Alignment Forum Weekly",
        title_prefix='AF - ',
        search_period=FeedGeneratorConfig.SearchPeriod.ONE_WEEK,
        gcp_bucket=gcp_bucket_newcode,
        history_titles_filename='af_weekly',
        rss_filename='nonlinear-library-aggregated-AF-weekly.xml',
        top_post_only=True
    )


def ea_all_config():
    return FeedGeneratorConfig(
        source=beyondwords_rss_output,
        author=nll_author,
        email=nonlinear_email,
        image_url='https://storage.googleapis.com/rssfile/images/Nonlinear%20Logo%203000x3000%20-%20EA%20Forum.png',
        guid_suffix='_EA',
        title='The Nonlinear Library: EA Forum',
        title_prefix='EA - ',
        gcp_bucket=gcp_bucket_newcode,
        history_titles_filename='ea_all',
        rss_filename='nonlinear-library-aggregated-EA.xml',
        top_post_only=False
    )


def ea_daily_config():
    return FeedGeneratorConfig(
        source=beyondwords_rss_output,
        author=nll_author,
        email=nonlinear_email,
        image_url='https://storage.googleapis.com/rssfile/images/Nonlinear%20Logo%203000x3000%20-%20EA%20Forum%20Daily.png',
        title="The Nonlinear Library: EA Forum Daily",
        guid_suffix='_EA-day',
        search_period=FeedGeneratorConfig.SearchPeriod.ONE_DAY,
        title_prefix='EA - ',
        gcp_bucket=gcp_bucket_newcode,
        history_titles_filename='ea_daily',
        rss_filename='nonlinear-library-aggregated-EA-daily.xml',
        top_post_only=True
    )


def ea_weekly_config():
    return FeedGeneratorConfig(
        source=beyondwords_rss_output,
        author=nll_author,
        email=nonlinear_email,
        image_url='https://storage.googleapis.com/rssfile/images/Nonlinear%20Logo%203000x3000%20-%20EA%20Forum%20Weekly.png',
        guid_suffix='_EA-week',
        title='The Nonlinear Library: EA Forum Weekly',
        title_prefix='EA - ',
        search_period=FeedGeneratorConfig.SearchPeriod.ONE_WEEK,
        gcp_bucket=gcp_bucket_newcode,
        history_titles_filename='ea_weekly',
        rss_filename='nonlinear-library-aggregated-EA-weekly.xml',
        top_post_only=True
    )


def lw_all_config():
    return FeedGeneratorConfig(
        source=beyondwords_rss_output,
        author=nll_author,
        email=nonlinear_email,
        image_url='https://storage.googleapis.com/rssfile/images/Nonlinear%20Logo%203000x3000%20-%20LessWrong.png',
        guid_suffix='_LW',
        title='The Nonlinear Library: LessWrong',
        title_prefix='LW - ',
        gcp_bucket=gcp_bucket_newcode,
        history_titles_filename='lw_all',
        rss_filename='nonlinear-library-aggregated-LW.xml',
        top_post_only=False
    )


def lw_daily_config():
    return FeedGeneratorConfig(
        source=beyondwords_rss_output,
        author=nll_author,
        email=nonlinear_email,
        image_url='https://storage.googleapis.com/rssfile/images/Nonlinear%20Logo%203000x3000%20-%20LessWrong%20Daily.png',
        title='The Nonlinear Library: LessWrong Daily',
        guid_suffix='_LW-day',
        search_period=FeedGeneratorConfig.SearchPeriod.ONE_DAY,
        title_prefix='LW - ',
        gcp_bucket=gcp_bucket_newcode,
        history_titles_filename='lw_daily',
        rss_filename='nonlinear-library-aggregated-LW-daily.xml',
        top_post_only=True
    )


def lw_weekly_config():
    return FeedGeneratorConfig(
        source=beyondwords_rss_output,
        author=nll_author,
        email=nonlinear_email,
        image_url='https://storage.googleapis.com/rssfile/images/Nonlinear%20Logo%203000x3000%20-%20LessWrong%20Weekly.png',
        guid_suffix='_LW-week',
        title='The Nonlinear Library: LessWrong Weekly',
        title_prefix='LW - ',
        search_period=FeedGeneratorConfig.SearchPeriod.ONE_WEEK,
        gcp_bucket=gcp_bucket_newcode,
        history_titles_filename='lw_weekly',
        rss_filename='nonlinear-library-aggregated-LW-weekly.xml',
        top_post_only=True
    )
