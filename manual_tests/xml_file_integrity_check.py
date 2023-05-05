import logging

from lxml import etree
from lxml.etree import XMLParser, XMLSyntaxError

from feed_processing.feed_updaters import download_file_from_url

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


def xml_string_is_valid(xml_str):
    parser = XMLParser(strip_cdata=False, encoding='utf-8')

    try:
        etree.fromstring(xml_str, parser)
    except XMLSyntaxError as e:
        return e

    return None


def check_xml_files_integrity(urls):
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("xml_file_integrity_check")

    for xml_file_url in urls:
        xml_str = download_file_from_url(xml_file_url, cache=False)
        xml_file_validation_exception = xml_string_is_valid(xml_str)
        if xml_file_validation_exception:
            logger.critical(f"File '{xml_file_url}' is invalid. Exception: {xml_file_validation_exception}")
        else:
            logger.log(logging.INFO, f"File '{xml_file_url}' okay.")


if __name__ == '__main__':
    check_xml_files_integrity(xml_files_urls)
