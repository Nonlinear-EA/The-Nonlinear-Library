from typing import List

from lxml import etree
from lxml.etree import XMLParser, Element

from feed import BaseFeedConfig


class StorageInterface:
    """
    Interface to read and write text files.
    """

    def __init__(self, rss_filename: str):
        self.removed_authors_filename = 'removed_authors.txt'
        self.rss_filename = rss_filename

    def write_podcast_feed(self, feed: str):
        raise NotImplementedError()

    def read_podcast_feed(self, filename: str = None) -> Element:
        raise NotImplementedError()

    def read_removed_authors(self) -> List[str]:
        raise NotImplementedError()

    def get_xml_parser(self):
        return XMLParser(encoding='utf-8', strip_cdata=False)


class LocalStorage(StorageInterface):
    """
    StorageInterface implementation to work with local files.
    """

    def __init__(
            self, rss_filename: str
    ):
        super().__init__(rss_filename)

    def read_removed_authors(self):
        removed_authors = self.__read_file('./removed_authors.txt')
        print('Returning removed authors of ', ', '.join(removed_authors))
        return removed_authors

    def read_podcast_feed(self, filename: str = None) -> Element:
        parser = XMLParser(encoding='utf-8', strip_cdata=False)
        if not filename:
            filename = self.rss_filename
        try:
            return etree.parse(filename, parser)
        except (FileNotFoundError, OSError) as e:
            empty_xml_feed = 'rss_files/empty_feed.xml'
            print(type(e).__name__, 'when trying to parse XML from file at ', filename,
                  ' so returning XML from ',
                  empty_xml_feed, ' instead.')
            return etree.parse(empty_xml_feed, parser)

    def write_podcast_feed(self, feed):
        print('writing RSS content to ', self.rss_filename)
        self.__write_file_as_bytes(self.rss_filename, feed)

    def __read_file(self, filename: str):
        print('reading from file with name ', filename)
        with open(filename, 'r') as f:
            return [line.rstrip() for line in f.readlines()]

    def __write_file_as_bytes(self, filename: str, content: bytes):
        with open(filename, 'wb') as f:
            return f.write(content)

    def __write_file(self, filename: str, content: str):
        with open(filename, 'w') as f:
            return f.write(content)


class GoogleCloudStorage(StorageInterface):
    """
    StorageInterface implementation to work with files on the cloud.
    """
    gcp_bucket: str

    def __init__(self, gcp_bucket, rss_filename: str):
        super().__init__(rss_filename)
        self.gcp_bucket = gcp_bucket

    def read_removed_authors(self):
        removed_authors = self.__read_file('./removed_authors.txt')
        print('Returning removed authors of ', ', '.join(removed_authors))
        return removed_authors

    def write_podcast_feed(self, feed: str):
        print('Writing podcast feed ', feed, ' to file ', self.rss_filename)
        self.__write_file(self.rss_filename, feed)

    def read_podcast_feed(self, filename: str = None) -> Element:
        # TODO: check if this works on GCP
        if not filename:
            filename = self.rss_filename
        rss_feed_str = "".join(self.__read_file(filename))
        parser = XMLParser(encoding='utf-8', strip_cdata=False)
        try:
            return etree.fromstring(rss_feed_str, parser)
        except OSError:
            return etree.parse('rss_files/empty_feed.xml', parser)

    def __read_file(self, path: str):
        print('Reading from bucket ', self.gcp_bucket, ' and path ', path)
        from google.cloud import storage
        client = storage.Client()
        bucket = client.get_bucket(self.gcp_bucket)
        blob = bucket.get_blob(path)
        if blob is None:
            print('blob ', blob, ' not found, so returning an empty List.')
            return []
        downloaded_blob = blob.download_as_string()
        return [line.rstrip() for line in downloaded_blob.decode('UTF-8').split('\n')]

    def __write_file(self, path: str, content: str):
        print('Writing to bucket ', self.gcp_bucket, ' and path ', path)
        from google.cloud import storage
        client = storage.Client()
        bucket = client.get_bucket(self.gcp_bucket)
        blob = bucket.blob(path)
        blob.upload_from_string(content)


def create_storage(feed_config: BaseFeedConfig, running_on_gcp: bool):
    """
    Factory to retrieve a storage interface implementation for local or cloud environments.
    Args:
        feed_config: Feed configuration data
        running_on_gcp: True if running on GCP. False if running locally.

    Returns: StorageInterface implementation.

    """
    if running_on_gcp:
        return GoogleCloudStorage(gcp_bucket=feed_config.gcp_bucket, rss_filename=feed_config.rss_filename)
    else:
        return LocalStorage(rss_filename=feed_config.rss_filename)
