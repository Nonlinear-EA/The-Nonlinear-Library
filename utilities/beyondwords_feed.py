import os
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from xml.etree import ElementTree

import requests


@lru_cache
def get_beyondwords_feed():
    """
    Returns the root of the beyondwords_snapshot.xml file.

    """
    if not os.path.exists('./beyondwords_snapshot.xml'):
        write_beyondwords_snapshot(n_days=14, output_filename='./beyondwords_snapshot.xml', max_entries=100)
    return ElementTree.parse('./beyondwords_snapshot.xml').getroot()


@lru_cache
def get_feed_reference_date_str(date_format='%Y-%m-%d %H:%M:%S'):
    return get_feed_reference_date().strftime(date_format)


@lru_cache
def get_feed_reference_date() -> datetime:
    rss_feed = get_beyondwords_feed()
    if rss_feed.find('./reference_date') is not None:
        return datetime.fromtimestamp(float(rss_feed.find('./reference_date').text))


def write_beyondwords_snapshot(
        n_days=7,
        output_filename: str = None,
        reference_date=datetime.now(tz=timezone.utc),
        max_entries: int = None
):
    """
    Saves a rss feed to `output_filename` based on the current BeyondWords feed, reduced to the number of posts
    published within the last `n_days`.

    The number of entries in the feed is limited to `max_entries`.

    A reference date can be passed, which is used instead of the current time to filter entries. The reference date will
    be attached to the xml file as `reference_date`

    """
    # Download rss feed from BeyondWords
    url = 'https://audio.beyondwords.io/f/8692/7888/read_8617d3aee53f3ab844a309d37895c143'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/83.0.4103.97 Safari/537.36'}
    response = requests.get(url, headers=headers)
    xml_data = response.text

    # The namespaces must be registered so the resulting xml file can incorporate them
    namespaces = {
        "atom": "http://www.w3.org/2005/Atom",
        "itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd",
        "content": "http://purl.org/rss/1.0/modules/content/"
    }
    for prefix, uri in namespaces.items():
        ElementTree.register_namespace(prefix, uri)

    # Parse to a xml tree
    root = ElementTree.fromstring(xml_data)

    # Save a reference date. It needs timezone info otherwise we get an error when comparing with dates from the feed.
    reference_date_element = ElementTree.SubElement(root, 'reference_date')
    reference_date_element.text = str(reference_date.timestamp())

    # Get podcast entries
    channel = root.find('channel')
    items = channel.findall('item')

    # Filter out entries by date
    n_items_removed = 0
    for item in items:
        date_format = '%a, %d %b %Y %H:%M:%S %z'
        date_published = datetime.strptime(item.find('pubDate').text, date_format)
        if date_published <= reference_date - timedelta(days=n_days):
            items.remove(item)
            n_items_removed += 1

    print(f"Removed {n_items_removed} items.")

    # Check if output_filename was provided
    if not output_filename:
        # Format an output_filename
        output_filename_template = 'beyondwords_snapshot_{_days_}_days.xml'
        output_filename = output_filename_template.format(_days_=n_days, _date_=reference_date.strftime('%Y-%m-%d'))

    if max_entries:
        to_remove = root.find('channel').findall('item')[max_entries:]
        for item in to_remove:
            root.find('channel').remove(item)

    print(f'Saving feed with {len(channel.findall("item"))} entries.')

    # Save xml file
    tree = ElementTree.ElementTree(root)
    tree.write(output_filename, encoding='UTF-8', xml_declaration=True)


if __name__ == '__main__':
    write_beyondwords_snapshot(n_days=14, output_filename='../tests/beyondwords_snapshot.xml', max_entries=200)
