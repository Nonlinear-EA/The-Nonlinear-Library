import logging
from typing import List

from lxml import etree
from lxml.etree import XMLParser, Element

from feed_processing.feed_config import BaseFeedConfig


class StorageInterface:
    """
    Interface to read and write text files.
    """

    def __init__(self, rss_filename: str, removed_authors_filename: str = "./removed_authors"):
        self.removed_authors_filename = removed_authors_filename
        self.rss_filename = rss_filename
        self._logger = logging.getLogger("Storage")
        self._parser = XMLParser(encoding="utf-8", strip_cdata=True, remove_blank_text=True)

    def write_podcast_feed(self, feed: str):
        raise NotImplementedError()

    def read_podcast_feed(self, filename: str = None) -> Element:
        raise NotImplementedError()

    def read_removed_authors(self) -> List[str]:
        raise NotImplementedError()


class LocalStorage(StorageInterface):
    """
    StorageInterface implementation to work with local files.
    """

    def __init__(
            self, rss_filename: str, removed_authors_filename: str = "./removed_authors.txt"
    ):
        super().__init__(rss_filename, removed_authors_filename)

    def read_removed_authors(self):
        removed_authors = self.__read_file(self.removed_authors_filename)
        self._logger.info(f"Returning removed authors {', '.join(removed_authors)}")
        return removed_authors

    def read_podcast_feed(self, filename: str = None) -> Element:
        if not filename:
            filename = self.rss_filename
        try:
            return etree.parse(filename, self._parser)
        except (FileNotFoundError, OSError) as e:
            empty_xml_feed = 'rss_files/empty_feed.xml'
            self._logger.info(
                f"{type(e).__name__} when trying to parse XML from file at '{filename}', so returning XML from "
                f"'{empty_xml_feed}' instead."
            )
            return etree.parse(empty_xml_feed, self._parser)

    def write_podcast_feed(self, feed):
        self._logger.info(f"writing RSS content to '{self.rss_filename}'")
        self.__write_file_as_bytes(self.rss_filename, feed)

    def __read_file(self, filename: str):
        self._logger.info(f"reading from file with name {filename}")
        with open(filename, 'r') as f:
            return [line.rstrip() for line in f.readlines()]

    def __write_file_as_bytes(self, filename: str, content: bytes):
        with open(filename, 'wb') as f:
            self._logger.info(f"Writing {int(len(content) / 1024)} KB to {filename}")
            return f.write(content)

    def __write_file(self, filename: str, content: str):
        with open(filename, 'w') as f:
            self._logger.info(f"Writing {int(len(content.encode('utf-8')) / 1024)} KB to {filename}")
            return f.write(content)


class GoogleCloudStorage(StorageInterface):
    """
    StorageInterface implementation to work with files on the cloud.
    """
    gcp_bucket: str

    def __init__(self, gcp_bucket, rss_filename: str, removed_authors_filename: str = "./removed_authors.txt"):
        super().__init__(rss_filename, removed_authors_filename)
        self.gcp_bucket = gcp_bucket

    def read_removed_authors(self):
        self._logger.info(f"Loading removed authors from {self.removed_authors_filename}")
        removed_authors = self.__read_file(self.removed_authors_filename)
        self._logger.info(f"Returning list of removed authors: {', '.join(removed_authors)}")
        return removed_authors

    def write_podcast_feed(self, feed: str):
        self._logger.info(f"Writing podcast feed '{feed}' to file '{self.rss_filename}'")
        self.__write_file(self.rss_filename, feed)

    def read_podcast_feed(self, filename: str = None) -> Element:
        if not filename:
            filename = self.rss_filename
        self._logger.info(f'Reading podcast feed from file {filename}')
        rss_feed_str = "".join(self.__read_file(filename))
        if rss_feed_str:
            return etree.fromstring(bytes(rss_feed_str, "utf-8"), self._parser)
        else:
            self._logger.info(f'File {filename} not found, trying to return an empty feed file.')
            return etree.parse('rss_files/empty_feed.xml', self._parser)

    def __read_file(self, path: str):
        self._logger.info(f"Reading from bucket '{self.gcp_bucket}' and path '{path}'")
        from google.cloud import storage
        client = storage.Client()
        bucket = client.get_bucket(self.gcp_bucket)
        blob = bucket.get_blob(path)
        if blob is None:
            self._logger.info(f"blob {blob} not found, so returning an empty List.")
            return []
        downloaded_blob = blob.download_as_string()
        return [line.rstrip() for line in downloaded_blob.decode('UTF-8').split('\n')]

    def __write_file(self, path: str, content: str):
        self._logger.info(f"Writing to bucket {self.gcp_bucket} and path {path}")
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
        return GoogleCloudStorage(
            gcp_bucket=feed_config.gcp_bucket,
            rss_filename=feed_config.rss_filename,
            removed_authors_filename=feed_config.removed_authors_file)
    else:
        return LocalStorage(rss_filename=feed_config.rss_filename,
                            removed_authors_filename=feed_config.removed_authors_file, )
