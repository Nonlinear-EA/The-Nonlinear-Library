import datetime
import os
import re
import ssl
from difflib import SequenceMatcher

import feedparser
import requests
from bs4 import BeautifulSoup


def ea_weekly_main(running_on_gcp):
    config = {
        'feed': {
            'max_articles': 30,
            'author': 'The Nonlinear Fund',
            'email': 'podcast@nonlinear.org',
            'image_url': 'https://storage.googleapis.com/rssfile/images/Nonlinear%20Logo%203000x3000%20-%20EA%20Forum%20Weekly.png'
        },
        'sources': {
            'list': [
                'https://audio.beyondwords.io/f/8692/7888/read_8617d3aee53f3ab844a309d37895c143'  # TNLL
            ]
        },
        'system': {
            'output_file_basename': 'nonlinear-library-aggregated-EA-weekly',
            'gcp_bucket_name': 'rssfile',
            'history_titles_filename': 'histories/history_titles_nonlinear-library-aggregated-EA-weekly.txt',
            'removed_authors_filename': 'removed_authors.txt'
        }
    }

    feed_initial_str = """<?xml version="1.0" encoding="{_encoding}"?>\
        <rss xmlns:atom="{_namespaces_}" xmlns:itunes="{_namespaces_itunes}" xmlns:content="{_namespaces_content}" \
        version="2.0"><channel><title>{_feed_title}</title>\
        <description>{_feed_subtitle}</description>\
        <author>{_feed_author}</author>\
        <copyright>{_feed_rights}</copyright>\
        <language>{_feed_language}</language>\
        <link>{_feed_link}</link>\
        <image><url>{_feed_image_href}</url></image>\
        <itunes:keywords></itunes:keywords>\
        <itunes:owner>\
          <itunes:name>{_feed_publishderdetail_name}</itunes:name>\
          <itunes:email>{_feed_publishderdetail_email}</itunes:email>\
        </itunes:owner>\
        <itunes:category text="{_feed_tags0}"><itunes:category text="{_feed_tags0}"/></itunes:category>\
        <itunes:explicit>{_feed_itunesexplicit}</itunes:explicit>\
        <itunes:image href="{_feed_image_href}"/>\
        <itunes:author>{_feed_publishderdetail_name}</itunes:author>\
        <itunes:summary><![CDATA[{_feed_subtitle}]]></itunes:summary>\
        <lastBuildDate>{_feed_updated}</lastBuildDate>"""

    item_str = """<item><guid isPermaLink="{item_guidislink}">{item_guid}</guid>\
        <title>{item_title}</title>\
        <description><![CDATA[{item_summary}]]></description>\
        <author>{item_author}</author>\
        <link>{item_link}</link>\
        <content:encoded><![CDATA[{item_summary}]]></content:encoded>\
        <enclosure length="{item_enclosure_length}" type="{item_enclosure_type}" url="{item_enclosure_url}"/>\
        <pubDate>{item_published}</pubDate>\
        <itunes:title>{item_title}</itunes:title>\
        <itunes:subtitle><![CDATA[{item_summary}]]></itunes:subtitle>\
        <itunes:summary><![CDATA[{item_summary}]]></itunes:summary>\
        <itunes:author>{item_author}</itunes:author>\
        <itunes:image>{_feed_image_href}</itunes:image>\
        <itunes:duration>{item_itunes_duration}</itunes:duration>\
        <itunes:keywords></itunes:keywords>\
        <itunes:explicit>{item_itunesexplicit}</itunes:explicit>\
        <itunes:episodeType>{item_itunes_episodetype}</itunes:episodeType>\
        <itunes:episode>{item_itunes_episode}</itunes:episode></item>"""

    feed_final_str = '</channel></rss>'

    html_hyperlink_format_spotify = "<a href=\"{hyperlink}\">{hyperlink_text}</a>"

    def get_karma(url):
        # disguising the request using headers
        page = requests.get(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'})
        soup = BeautifulSoup(page.content, "html.parser")
        if soup.title and soup.title == '403 Forbidden':
            raise AssertionError(
                '403 Forbidden error when trying to access ' + url + ' You may need to change the headers to something else.')
        return soup.find('h1', {'class': 'PostsVote-voteScore'}).text

    def get_previous_week_start_and_end(weeks_back):
        # today_index=6 because this will run every sunday
        today = datetime.date.today()
        today_index = today.weekday()
        start_of_this_week = datetime.timedelta(days=today_index, weeks=weeks_back)
        start_of_last_week = today - start_of_this_week
        end_of_last_week = start_of_last_week + datetime.timedelta(days=7)

        return start_of_last_week, end_of_last_week

    def format_published_datetime(datetime_str):
        try:
            formatted_datetime = datetime.datetime.strptime(datetime_str[:-6], "%a, %m %b %Y %H:%M:%S")
        except ValueError as e:
            if 'does not match' in str(e):
                formatted_datetime = datetime.datetime.strptime(datetime_str[:-6], "%a, %d %b %Y %H:%M:%S")
            else:
                formatted_datetime = None
        return formatted_datetime

    def is_datetime_between(target, before, after):
        return before < target < after

    def string_similarity(a, b):
        return SequenceMatcher(None, a, b).ratio()

    def datetime_to_int(dt):
        return dt.year * 10000000000 + dt.month * 100000000 + dt.day * 1000000 + dt.hour * 10000 + dt.minute * 100 + dt.second

    class Feed(object):
        def __init__(self, config, local=False):
            # Obtain SSL certificate
            if hasattr(ssl, '_create_unverified_context'):
                ssl._create_default_https_context = ssl._create_unverified_context
            self.max_number = config['feed']['max_articles']
            self.sources_list = config['sources']['list']
            self.output_file_basename = config['system']['output_file_basename']
            self.history_titles_filename = config['system']['history_titles_filename']
            self.gcp_bucket_name = config['system']['gcp_bucket_name']
            self.removed_authors_filename = config['system']['removed_authors_filename']
            self.local = local
            self.list_modified_sources = []
            self.image_url = config['feed']['image_url']
            # get list of removed authors
            if self.local:
                with open(self.removed_authors_filename, 'r') as f:
                    self.list_removed_authors = [line.rstrip() for line in f.readlines()]
            else:
                from google.cloud import storage
                client = storage.Client()
                bucket = client.get_bucket(self.gcp_bucket_name)
                blob = bucket.get_blob(self.removed_authors_filename)
                downloaded_blob = blob.download_as_string()
                self.list_removed_authors = [line.rstrip() for line in downloaded_blob.decode('UTF-8').split('\n')]

        def modify_feed(self):
            print('ENTERING THE modify_feed FUNCTION')
            for i in range(len(self.sources_list)):
                if ('http' in self.sources_list[i]):
                    self.list_modified_sources.append(
                        self._modify_feed(self.sources_list[i], 'EA - ', 'The Nonlinear Library: EA Forum Weekly',
                                          '_EA-week'))

        def _modify_feed(self, url, title_beginning, feed_title, guid_suffix):
            print('ENTERING THE _modify_feed subFUNCTION')
            news_feed = feedparser.parse(url)
            reg = "(?<=%s).*?(?=%s)" % ('rss&', 'karma')
            r = re.compile(reg, re.DOTALL)

            news_feed['feed']['title'] = feed_title
            news_feed['feed']['image']['href'] = self.image_url

            rss_feed = feed_initial_str.format(
                _encoding=news_feed['encoding'].upper(),
                _namespaces_=news_feed['namespaces'][''],
                _namespaces_itunes=news_feed['namespaces']['itunes'],
                _namespaces_content=news_feed['namespaces']['content'],
                _feed_title=news_feed['feed']['title'],
                _feed_subtitle=news_feed['feed']['subtitle'],
                _feed_author=news_feed['feed']['author'],
                _feed_rights=news_feed['feed']['rights'],
                _feed_language=news_feed['feed']['language'],
                _feed_link=news_feed['feed']['link'],
                _feed_image_href=news_feed['feed']['image']['href'],
                _feed_publishderdetail_name=news_feed['feed']['publisher_detail']['name'],
                _feed_publishderdetail_email=news_feed['feed']['publisher_detail']['email'],
                _feed_tags0=news_feed['feed']['tags'][0]['term'],
                # _feed_tags1=news_feed['feed']['tags'][1]['term'], #NOTE: removed due to IndexError: list index out of range
                _feed_itunesexplicit='yes' if news_feed['feed']['itunes_explicit'] else 'no',
                _feed_updated=news_feed['feed']['updated'],
            )

            if self.local:
                with open(os.path.basename(self.history_titles_filename), 'r') as f:
                    self.history_titles = [line.rstrip() for line in f.readlines()]
            else:
                from google.cloud import storage
                client = storage.Client()
                bucket = client.get_bucket(self.gcp_bucket_name)
                blob = bucket.get_blob(self.history_titles_filename)
                downloaded_blob = blob.download_as_string()
                self.history_titles = [line.rstrip() for line in downloaded_blob.decode('UTF-8').split('\n')]

            list_indices_karmas = []
            weeks_back = -1
            list_indices = []
            while not list_indices_karmas:
                weeks_back += 1
                print(f'\n\n\n~ ~ ~ ~ ~ Trying with weeks_back = {weeks_back} ~ ~ ~ ~ ~')
                for i in range(len(news_feed.entries)):
                    item = news_feed.entries[i]

                    if item['title'].startswith(title_beginning):
                        # check for removed authors
                        if item['author'] in self.list_removed_authors:
                            continue

                        published_datetime_str = item['published']
                        published_datetime_object = format_published_datetime(published_datetime_str)

                        # published_datetime_int = datetime_to_int(published_datetime_object) # not necessary yet
                        for title in self.history_titles:
                            if string_similarity(item['title'], title) > 0.9:
                                list_indices += [i]
                        list_indices = sorted(list(set(list_indices)))

                        start_of_previous_week, end_of_previous_week = get_previous_week_start_and_end(
                            weeks_back=weeks_back)
                        print('\n\n\n', i, item['title'], published_datetime_object, start_of_previous_week,
                              end_of_previous_week)
                        if is_datetime_between(
                                target=published_datetime_object.date(),
                                before=start_of_previous_week,
                                after=end_of_previous_week
                        ):
                            list_indices_karmas.append((i, int(get_karma(item['link'])), item['title'], item['link']))

            print('\n\n\n\n', list_indices_karmas)
            if list_indices_karmas:
                max_karma_post = sorted(list_indices_karmas, key=lambda x: x[1])[-1]
                list_indices += [max_karma_post[0]]
                if max_karma_post[2] not in self.history_titles:
                    self.history_titles += [max_karma_post[2]]
                print('MAX KARMA POST FOUND!', max_karma_post)
            else:
                print('NO ARTICLES FOUND!')

            # write updated list of previous article titles to the database
            if self.local:
                with open(os.path.basename(self.history_titles_filename), 'w') as f:
                    f.write('\n'.join(self.history_titles))
            else:
                client = storage.Client()
                bucket = client.get_bucket(self.gcp_bucket_name)
                blob = bucket.blob(self.history_titles_filename)
                blob.upload_from_string('\n'.join(self.history_titles))

            for i in list_indices:
                item = news_feed.entries[i]
                if item['title'].startswith(title_beginning):

                    item['title'] = item['title'].replace('&', 'and')

                    # check for removed authors
                    if item['author'] in self.list_removed_authors:
                        continue

                    rss_feed += item_str.format(
                        item_guidislink=str(item['guidislink']).lower(),
                        # does the guid have to be unique PER SHOW or GLOBALLY? ==>> GLOBALLY :(
                        item_guid=item['guid'] + guid_suffix,
                        item_title=item['title'],
                        item_summary=html_hyperlink_format_spotify.format(
                            hyperlink=item['link'], hyperlink_text='Link to original article') + '<br/>' + '<br/>' +
                                     item['summary'],
                        item_author=item['author'],
                        item_link=item['link'],
                        item_enclosure_length=item['links'][1]['length'] if 'enclosure' in item['links'][1].values() \
                            else item['links'][0]['length'],
                        item_enclosure_type=item['links'][1]['type'] if 'enclosure' in item['links'][1].values() \
                            else item['links'][0]['type'],
                        item_enclosure_url=item['links'][1]['href'] if 'enclosure' in item['links'][1].values() \
                            else item['links'][0]['href'],
                        item_published=item['published'],
                        _feed_image_href=news_feed['feed']['image']['href'],
                        item_itunes_duration=item['itunes_duration'],
                        item_itunesexplicit=item['itunes_explicit'],
                        item_itunes_episodetype=item['itunes_episodetype'],
                        item_itunes_episode=item['itunes_episode']
                    )

            print('WRITING THE MODIFIED FEED TO AN XML FILE')

            filename = '{}.xml'.format(self.output_file_basename)

            if self.local:
                with open(filename, 'w') as f:
                    f.write(rss_feed + feed_final_str)
            else:
                client = storage.Client()
                bucket = client.get_bucket(self.gcp_bucket_name)
                blob = bucket.blob(filename)
                blob.upload_from_string(rss_feed + feed_final_str)

            return news_feed

    Feed(config, local=True).modify_feed()
