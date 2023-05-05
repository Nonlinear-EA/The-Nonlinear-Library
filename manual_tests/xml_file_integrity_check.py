import logging
import os.path

from lxml import etree
from lxml.etree import XMLParser, XMLSyntaxError

from feed_processing.feed_updaters import download_file_from_url

xml_files_urls = [
    "https://storage.googleapis.com/rssfile/nonlinear-library-aggregated-EA.xml"
]


def xml_string_is_valid(xml_str):
    parser = XMLParser(strip_cdata=False, encoding='utf-8')

    try:
        etree.fromstring(xml_str, parser)
    except XMLSyntaxError as e:
        return e

    return None


if __name__ == '__main__':
    logger = logging.getLogger("xml_file_integrity_check")
    logger.setLevel(logging.INFO)

    for xml_file_url in xml_files_urls:
        xml_str = download_file_from_url(xml_file_url, cache=False)
        xml_file_validation_exception = xml_string_is_valid(xml_str)
        if xml_file_validation_exception:
            logger.critical(f"File '{xml_file_url}' is invalid. Exception: {xml_file_validation_exception}")

            # Save file for inspection
            with open(os.path.join("./integrity_check_files", os.path.basename(xml_file_url)), "rb") as f:
                f.write(xml_str)
        else:
            logger.log(logging.INFO, "File '{xml_file_url}' okay.")
