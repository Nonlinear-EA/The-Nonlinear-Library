import logging
import re
import ssl

import feedparser


def create_main_nonlinear_library_rss():
    """Create an RSS file containing input from all three of the forums.

    The RSS file that is output is read by BeyondWords to create a new RSS file that has XML elements containing the MP3
    links to the audio synthesis of the text. This new RSS file with MP3s is then used as input to the other files which
    split it into EA, AF, etc. streams.
    """

    config = {
        'feed': {
            'max_articles': 30,
            'author': 'The Nonlinear Fund',
            'email': 'info@nonlinear.org'
        },
        'sources': {
            'list': [
                'https://forum.effectivealtruism.org/feed.xml?view=community-rss&karmaThreshold=25',
                'https://www.lesswrong.com/feed.xml?view=community-rss&karmaThreshold=30',
                'https://www.alignmentforum.org/feed.xml?view=community-rss&karmaThreshold=0'
            ]
        },
        'system': {
            'output_file_basename': 'nonlinear-library',
            'gcp_bucket_name': 'rssfile',
            'removed_authors_filename': 'removed_authors.txt'
        }
    }

    print('PRINTING THE data ARGUMENT')
    print('PRINTING THE context ARGUMENT')

    print('ENTERING THE MAIN FUNCTION')

    feed_initial_str="""<?xml version="1.0" encoding="{_encoding}"?>\
        <rss xmlns:dc="{_namespaces_dc}" xmlns:content="{_namespaces_content}" \
        xmlns:atom="{_namespaces_}" version="2.0"><channel><title><![CDATA[{_feed_title}]]></title>\
        <description><![CDATA[{_feed_subtitle}]]></description><link>{_feed_link}</link>\
        <image><url>https://res.cloudinary.com/lesswrong-2-0/image/upload/v1497915096/favicon_lncumn.ico</url>\
        <title>{_feed_title}</title><link>{_feed_link}</link></image><generator>{_feed_generator}</generator>\
        <lastBuildDate>{_feed_updated}</lastBuildDate><atom:link \
        href="{_feed_titledetail_base}" \
        rel="self" type="application/rss+xml"/>"""

    item_str="""<item><title><![CDATA[{item_web_short} - {item_title} by {item_author}]]></title><description>\
        <![CDATA[{item_summary}]]></description>
        <link>{item_link}</link><guid isPermaLink="{item_guidislink}">{item_id}</guid><dc:creator><![CDATA[{item_author}]]></dc:creator><pubDate>{item_published}</pubDate></item>"""

    feed_final_str = '</channel></rss>'

    intro_str = """ Welcome to The Nonlinear Library, where we use Text-to-Speech software to convert the best writing from the Rationalist and EA communities into audio. 
    This is: {item_title}, published by {item_author} on {item_date} on {item_web_long}. """
    outro_str = ' <p>Thanks for listening. To help us out with The Nonlinear Library or to learn more, please visit nonlinear.org. </p>'


    def find_website_short(url):
        website = 'Unknown'
        if 'forum.effectivealtruism.org' in url:
            website = 'EA'
        elif 'lesswrong.com' in url:
            website = 'LW'
        elif 'alignmentforum.org' in url:
            website = 'AF'

        return website

    def find_website_long(url):
        website = 'Unknown'
        if 'forum.effectivealtruism.org' in url:
            website = 'The Effective Altruism Forum'
        elif 'lesswrong.com' in url:
            website = 'LessWrong'
        elif 'alignmentforum.org' in url:
            website = 'The AI Alignment Forum'

        return website


    class Feed(object):
        def __init__(self, config, local=False):
            # Obtain SSL certificate
            logging.info('INITIALIZING A Feed OBJECT')
            if hasattr(ssl, '_create_unverified_context'):
                ssl._create_default_https_context = ssl._create_unverified_context
            self.max_number = config['feed']['max_articles']
            self.sources_list = config['sources']['list']
            self.output_file_basename = config['system']['output_file_basename']
            self.gcp_bucket_name = config['system']['gcp_bucket_name']
            self.removed_authors_filename = config['system']['removed_authors_filename']
            self.local = local
            self.list_modified_sources = []
            self.list_titles = []
            # get list of removed authors
            if self.local:
                with open(self.removed_authors_filename, 'r') as f:
                    self.list_removed_authors = [line.rstrip() for line in f.readlines()]
            else:
                from google.cloud import storage
                client = storage.Client(project='crucial-alpha-321109')
                bucket = client.get_bucket(self.gcp_bucket_name)
                blob = bucket.get_blob(self.removed_authors_filename)
                downloaded_blob = blob.download_as_string()
                self.list_removed_authors = [line.rstrip() for line in downloaded_blob.decode('UTF-8').split('\n')]

        def modify_feed(self):
            print('ENTERING THE modify_feed FUNCTION')
            for i in range(len(self.sources_list)):
                if ('http' in self.sources_list[i]):
                    self.list_modified_sources.append(self._modify_feed(self.sources_list[i], i))



        def _modify_feed(self, url, src_idx):
            print('ENTERING THE _modify_feed subFUNCTION')
            news_feed = feedparser.parse(url)
            reg = "(?<=%s).*?(?=%s)" % ('rss&','karma')
            r = re.compile(reg,re.DOTALL)

            rss_feed = feed_initial_str.format(
                _encoding=news_feed['encoding'].upper(),
                _namespaces_dc=news_feed['namespaces']['dc'],
                _namespaces_content=news_feed['namespaces']['content'],
                _namespaces_=news_feed['namespaces'][''],
                _feed_title=news_feed['feed']['title'],
                _feed_subtitle=news_feed['feed']['subtitle'],
                _feed_link=news_feed['feed']['link'],
                _feed_generator=news_feed['feed']['generator'],
                _feed_updated=news_feed['feed']['updated'],
                _feed_titledetail_base=r.sub('amp;', news_feed['feed']['title_detail']['base'])
            )

            # get website
            feed_web_short = find_website_short(news_feed['feed']['link'])
            feed_web_long = find_website_long(news_feed['feed']['link'])

            for i in range(self.max_number):
                # check if there are more entries available
                if i == (len(news_feed.entries) - 1):
                    break
                # get new entry
                item = news_feed.entries[i]
                # check for cross-posts
                if item['title'] in self.list_titles:
                    continue
                self.list_titles.append(item['title'])
                # check for removed authors
                if item['author'] in self.list_removed_authors:
                    continue
                # add author to feed title
                authors_str = ''
                for j, auth in enumerate(item['authors']):
                    authors_str += auth['name'].replace('_', ' ')
                    if j == (len(item['authors'])-2):
                        authors_str += ' and '
                    elif j == (len(item['authors'])-1):
                        pass
                    else:
                        authors_str += ', '

                # get date
                item_date = item['summary'].split('<br /><br />')[0].split(':')[0][13:-2]  # TODO: make more robust
                item_body_no_outro = '<br /><br />'.join([p for p in item['summary'].split('<br /><br />')[1:]])
                last_str = '<br /><br /><a href="{}#comments">Discuss</a>'.format(item['link'])
                item_body_with_outro = item_body_no_outro.split(last_str)[0] + outro_str + last_str
                rss_feed += item_str.format(
                    item_web_short=feed_web_short,
                    item_title=item['title'],
                    item_author=authors_str,
                    item_summary=intro_str.format(
                        item_title=item['title'], item_author=authors_str,
                        item_date=item_date, item_web_long=feed_web_long) + \
                                 '<br /><br />' + item_body_with_outro,  # TODO: make more robust
                    item_link=item['link'],
                    item_guidislink=str(item['guidislink']).lower(),
                    item_id=item['id'] + f'_NL_{feed_web_short}',
                    item_published=item['published']
                )
                item['title'] = f'{feed_web_short} - {item["title"]} by {authors_str}'

            print('WRITING THE MODIFIED FEED TO AN XML FILE')

            filename = '{}-{}.xml'.format(
                self.output_file_basename, feed_web_short.replace(' ', '_')
            )

            if self.local:
                with open(filename, 'w') as f:
                    f.write(rss_feed + feed_final_str)
            else:
                from google.cloud import storage
                client = storage.Client()
                bucket = client.get_bucket(self.gcp_bucket_name)
                blob = bucket.blob(filename)
                blob.upload_from_string(rss_feed + feed_final_str)

            return news_feed

    Feed(config).modify_feed()
