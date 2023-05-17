from google.cloud import logging
from lxml import etree
from lxml.etree import XMLParser, XMLSyntaxError

from feed_processing.feed_updaters import download_file_from_url


def xml_string_is_valid(xml_str):
    parser = XMLParser(strip_cdata=False, encoding='utf-8')

    try:
        etree.fromstring(xml_str, parser)
    except XMLSyntaxError as e:
        return e

    return None


def check_xml_files_integrity(urls, running_on_gcp=True):
    logging_client = logging.Client()

    # This log can be found in the Cloud Logging console under 'Custom Logs'.
    logger = logging_client.logger("XML_Integrity_Checks")

    for xml_file_url in urls:
        xml_str = download_file_from_url(xml_file_url, cache=False)
        xml_file_validation_exception = xml_string_is_valid(xml_str)
        if xml_file_validation_exception:
            logger.log_text(f"File '{xml_file_url}' is invalid. Exception: {xml_file_validation_exception}",
                            severity="CRITICAL")
        else:
            logger.log_text(f"File '{xml_file_url}' okay.")


if __name__ == '__main__':
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
        "https://storage.googleapis.com/rssfile/nonlinear-library-aggregated.xml",
        "https://storage.googleapis.com/newcode/rss_files/nonlinear-library-EA.xml"
    ]
    check_xml_files_integrity(xml_files_urls)
