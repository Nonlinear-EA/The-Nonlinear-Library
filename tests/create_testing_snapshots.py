import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

import requests


def save_beyondwords_snapshot(n_days=7, output_filename: str = None):
    """
    Saves a rss feed based on the current BeyondWords feed, reduced to the number of posts published within the last
    `n_days`

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
        ET.register_namespace(prefix, uri)

    # Parse to a xml tree
    root = ET.fromstring(xml_data)

    # Save a reference date. It needs timezone info otherwise we get an error when comparing with dates from the feed.
    reference_date = datetime.now(tz=timezone.utc)
    reference_date_element = ET.SubElement(root, 'reference_date')
    reference_date_element.text = str(reference_date.timestamp())

    # Get podcast entries
    items = root.find('channel').findall('item')

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

    # Save xml file
    tree = ET.ElementTree(root)
    tree.write(output_filename, encoding='UTF-8', xml_declaration=True)


if __name__ == '__main__':
    save_beyondwords_snapshot()
    save_beyondwords_snapshot(1)
