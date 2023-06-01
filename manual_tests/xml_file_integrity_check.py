import logging

from google.cloud import logging as gcloud_logging
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
    if running_on_gcp:
        logging_client = gcloud_logging.Client()

        # This log can be found in the Cloud Logging console under 'Custom Logs'.
        logger = logging_client.logger("XML_Integrity_Checks")
    else:
        logger = logging.getLogger("XML_Integrity_Checks", )

    for xml_file_url in urls:
        try:
            xml_str = download_file_from_url(xml_file_url, cache=False)
        except ValueError:
            with open(xml_file_url, "rb") as f:
                xml_str = f.read()
        xml_file_validation_exception = xml_string_is_valid(xml_str)
        if xml_file_validation_exception:
            message = f"File '{xml_file_url}' is invalid. Exception: {xml_file_validation_exception}"
            if running_on_gcp:
                logger.log_text(message,
                                severity="CRITICAL")
            else:
                logger.error(message)
        else:
            print(f"File {xml_file_url} okay.")


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
        "https://storage.googleapis.com/newcode/rss_files/nonlinear-library-EA.xml",
        "https://storage.googleapis.com/newcode/nonlinear-library-aggregated-EA.xml",
    ]

    local_xml_files = [
        "./integrity_check_files/nonlinear-library-aggregated-EA.xml"
    ]
    # check_xml_files_integrity(xml_files_urls, running_on_gcp=False)
    check_xml_files_integrity(local_xml_files, running_on_gcp=False)
