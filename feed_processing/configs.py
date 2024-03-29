import os

from feed_processing.feed_config import PodcastProviderFeedConfig, BeyondWordsInputConfig

beyondwords_rss_output = 'https://audio.beyondwords.io/f/8692/7888/read_8617d3aee53f3ab844a309d37895c143'
beyondwords_sandbox_rss_output = "https://audio.beyondwords.io/f/28554/88747/read_8617d3aee53f3ab844a309d37895c143"
nll_author = 'The Nonlinear Fund'
gcp_bucket_newcode = 'newcode'
nonlinear_email = 'podcast@nonlinear.org'

podcast_description = """The Nonlinear Library allows you to easily listen to top EA and rationalist content on your 
podcast player. We use text-to-speech software to create an automatically updating repository of audio content from 
the EA Forum, Alignment Forum, LessWrong, and other EA blogs. To find out more, please visit us at nonlinear.org"""

beyondwords_feed_input_sources = [
    'https://forum.effectivealtruism.org/feed.xml?view=community-rss&karmaThreshold=25',
    'https://www.lesswrong.com/feed.xml?view=community-rss&karmaThreshold=30',
    'https://www.alignmentforum.org/feed.xml?view=community-rss&karmaThreshold=0'
]

beyondwords_feed_namespaces = {
    'dc': 'http://purl.org/dc/elements/1.1/',
    'content': 'http://purl.org/rss/1.0/modules/content/',
    'atom': 'http://www.w3.org/2005/Atom',
    'itunes': "http://www.itunes.com/dtds/podcast-1.0.dtd"
}


def af_all_config():
    return PodcastProviderFeedConfig(
        source=beyondwords_rss_output,
        author=nll_author,
        email=nonlinear_email,
        image_url='https://storage.googleapis.com/rssfile/images/Nonlinear%20Logo%203000x3000%20-%20Alignment%20Forum.png',
        title="The Nonlinear Library: Alignment Forum",
        description=podcast_description,
        title_prefix='AF -',
        guid_suffix='_AF',
        gcp_bucket=os.environ["GCP_BUCKET_NAME"],
        rss_filename='nonlinear-library-aggregated-AF.xml',
        top_post_only=False,
        search_period=None,
        removed_authors_file="removed_authors.txt"
    )


def af_daily_config():
    return PodcastProviderFeedConfig(
        source=beyondwords_rss_output,
        author=nll_author,
        email=nonlinear_email,
        image_url='https://storage.googleapis.com/rssfile/images/Nonlinear%20Logo%203000x3000%20-%20Alignment%20Forum%20Daily.png',
        guid_suffix='_AF-day',
        title="The Nonlinear Library: Alignment Forum Daily",
        description=podcast_description,
        title_prefix='AF - ',
        search_period=PodcastProviderFeedConfig.SearchPeriod.ONE_DAY,
        gcp_bucket=gcp_bucket_newcode,
        rss_filename='nonlinear-library-aggregated-AF-daily.xml',
        top_post_only=True
    )


def af_weekly_config():
    return PodcastProviderFeedConfig(
        source=beyondwords_rss_output,
        author=nll_author,
        email=nonlinear_email,
        image_url='https://storage.googleapis.com/rssfile/images/Nonlinear%20Logo%203000x3000%20-%20Alignment%20Forum%20Weekly.png',
        guid_suffix='_AF-week',
        title="The Nonlinear Library: Alignment Forum Weekly",
        description=podcast_description,
        title_prefix='AF - ',
        search_period=PodcastProviderFeedConfig.SearchPeriod.ONE_WEEK,
        gcp_bucket=gcp_bucket_newcode,
        rss_filename='nonlinear-library-aggregated-AF-weekly.xml',
        top_post_only=True
    )


def ea_all_config():
    return PodcastProviderFeedConfig(
        source=beyondwords_rss_output,
        author=nll_author,
        email=nonlinear_email,
        image_url='https://storage.googleapis.com/rssfile/images/Nonlinear%20Logo%203000x3000%20-%20EA%20Forum.png',
        guid_suffix='_EA',
        title='The Nonlinear Library: EA Forum',
        description=podcast_description,
        title_prefix='EA - ',
        gcp_bucket=os.environ["GCP_BUCKET_NAME"],
        rss_filename='nonlinear-library-aggregated-EA.xml',
        top_post_only=False,
        removed_authors_file="removed_authors.txt"
    )


def ea_daily_config():
    return PodcastProviderFeedConfig(
        source=beyondwords_rss_output,
        author=nll_author,
        email=nonlinear_email,
        image_url='https://storage.googleapis.com/rssfile/images/Nonlinear%20Logo%203000x3000%20-%20EA%20Forum%20Daily.png',
        title="The Nonlinear Library: EA Forum Daily",
        description=podcast_description,
        guid_suffix='_EA-day',
        search_period=PodcastProviderFeedConfig.SearchPeriod.ONE_DAY,
        title_prefix='EA - ',
        gcp_bucket=gcp_bucket_newcode,
        rss_filename='nonlinear-library-aggregated-EA-daily.xml',
        top_post_only=True
    )


def ea_weekly_config():
    return PodcastProviderFeedConfig(
        source=beyondwords_rss_output,
        author=nll_author,
        email=nonlinear_email,
        image_url='https://storage.googleapis.com/rssfile/images/Nonlinear%20Logo%203000x3000%20-%20EA%20Forum%20Weekly.png',
        guid_suffix='_EA-week',
        title='The Nonlinear Library: EA Forum Weekly',
        description=podcast_description,
        title_prefix='EA - ',
        search_period=PodcastProviderFeedConfig.SearchPeriod.ONE_WEEK,
        gcp_bucket=gcp_bucket_newcode,
        rss_filename='nonlinear-library-aggregated-EA-weekly.xml',
        top_post_only=True
    )


def lw_all_config():
    return PodcastProviderFeedConfig(
        source=beyondwords_rss_output,
        author=nll_author,
        email=nonlinear_email,
        image_url='https://storage.googleapis.com/rssfile/images/Nonlinear%20Logo%203000x3000%20-%20LessWrong.png',
        guid_suffix='_LW',
        title='The Nonlinear Library: LessWrong',
        description=podcast_description,
        title_prefix='LW - ',
        gcp_bucket=gcp_bucket_newcode,
        rss_filename='nonlinear-library-aggregated-LW.xml',
        top_post_only=False
    )


def lw_daily_config():
    return PodcastProviderFeedConfig(
        source=beyondwords_rss_output,
        author=nll_author,
        email=nonlinear_email,
        image_url='https://storage.googleapis.com/rssfile/images/Nonlinear%20Logo%203000x3000%20-%20LessWrong%20Daily.png',
        title='The Nonlinear Library: LessWrong Daily',
        description=podcast_description,
        guid_suffix='_LW-day',
        search_period=PodcastProviderFeedConfig.SearchPeriod.ONE_DAY,
        title_prefix='LW - ',
        gcp_bucket=os.environ["GCP_BUCKET_NAME"],
        rss_filename='nonlinear-library-aggregated-LW-daily.xml',
        top_post_only=True,
        removed_authors_file="removed_authors.txt"
    )


def lw_weekly_config():
    return PodcastProviderFeedConfig(
        source=beyondwords_rss_output,
        author=nll_author,
        email=nonlinear_email,
        image_url='https://storage.googleapis.com/rssfile/images/Nonlinear%20Logo%203000x3000%20-%20LessWrong%20Weekly.png',
        guid_suffix='_LW-week',
        title='The Nonlinear Library: LessWrong Weekly',
        description=podcast_description,
        title_prefix='LW - ',
        search_period=PodcastProviderFeedConfig.SearchPeriod.ONE_WEEK,
        gcp_bucket=gcp_bucket_newcode,
        rss_filename='nonlinear-library-aggregated-LW-weekly.xml',
        top_post_only=True
    )


def beyondwords_ea_config():
    return BeyondWordsInputConfig(
        author=nll_author,
        email=nonlinear_email,
        gcp_bucket=os.environ["GCP_BUCKET_NAME"],
        source='https://forum.effectivealtruism.org/feed.xml?view=community-rss&karmaThreshold=25',
        max_entries=30,
        rss_filename='nonlinear-library-EA.xml',
        relevant_feeds=['nonlinear-library-EA.xml',
                        'nonlinear-library-AF.xml',
                        'nonlinear-library-LW.xml'],
        removed_authors_file="removed_authors.txt",
    )


def beyondwords_af_config():
    return BeyondWordsInputConfig(
        author=nll_author,
        email=nonlinear_email,
        gcp_bucket=os.environ["GCP_BUCKET_NAME"],
        source='https://www.alignmentforum.org/feed.xml?view=community-rss&karmaThreshold=0',
        max_entries=30,
        rss_filename='nonlinear-library-AF.xml',
        relevant_feeds=['nonlinear-library-AF.xml',
                        'nonlinear-library-EA.xml',
                        'nonlinear-library-LW.xml'],
        removed_authors_file="removed_authors.txt",
    )


def beyondwords_lw_config():
    return BeyondWordsInputConfig(
        author=nll_author,
        email=nonlinear_email,
        gcp_bucket=os.environ["GCP_BUCKET_NAME"],
        source='https://www.lesswrong.com/feed.xml?view=community-rss&karmaThreshold=30',
        max_entries=30,
        rss_filename='nonlinear-library-LW.xml',
        relevant_feeds=['nonlinear-library-LW.xml',
                        'nonlinear-library-AF.xml',
                        'nonlinear-library-EA.xml'],
        removed_authors_file="removed_authors.txt"
    )
