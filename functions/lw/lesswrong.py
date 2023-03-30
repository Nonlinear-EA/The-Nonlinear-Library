import re
import ssl

import feedparser


def lw_all_main():
    config = {
        'feed': {
            'max_articles': 30,
            'author': 'The Nonlinear Fund',
            'email': 'podcast@nonlinear.org',
            'image_url': 'https://storage.googleapis.com/rssfile/images/Nonlinear%20Logo%203000x3000%20-%20LessWrong.png'
        },
        'sources': {
            'list': [
                'https://audio.beyondwords.io/f/8692/7888/read_8617d3aee53f3ab844a309d37895c143'  # TNLL
            ]
        },
        'system': {
            'output_file_basename': 'nonlinear-library-aggregated-LW',
            'gcp_bucket_name': 'rssfile'
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

    class Feed(object):
        def __init__(self, config, local=False):
            # Obtain SSL certificate
            if hasattr(ssl, '_create_unverified_context'):
                ssl._create_default_https_context = ssl._create_unverified_context
            self.max_number = config['feed']['max_articles']
            self.sources_list = config['sources']['list']
            self.output_file_basename = config['system']['output_file_basename']
            self.gcp_bucket_name = config['system']['gcp_bucket_name']
            self.local = local
            self.list_modified_sources = []
            self.image_url = config['feed']['image_url']

        def modify_feed(self):
            print('ENTERING THE modify_feed FUNCTION')
            for i in range(len(self.sources_list)):
                if ('http' in self.sources_list[i]):
                    self.list_modified_sources.append(self._modify_feed(self.sources_list[i], i))

        def _modify_feed(self, url, src_idx):
            print('ENTERING THE _modify_feed subFUNCTION')
            news_feed = feedparser.parse(url)
            reg = "(?<=%s).*?(?=%s)" % ('rss&', 'karma')
            r = re.compile(reg, re.DOTALL)

            news_feed['feed']['title'] = 'The Nonlinear Library: LessWrong'
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

            for i in range(len(news_feed.entries)):
                item = news_feed.entries[i]

                if item['title'].startswith('LW - '):
                    item['title'] = item['title'].replace('&', 'and')

                    rss_feed += item_str.format(
                        item_guidislink=str(item['guidislink']).lower(),
                        # does the guid have to be unique PER SHOW or GLOBALLY?
                        item_guid=item['guid'] + '_LW',
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
