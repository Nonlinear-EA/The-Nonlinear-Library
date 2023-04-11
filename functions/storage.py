import os
from typing import List
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, ParseError

from feed import FeedGeneratorConfig


class StorageInterface:
    """
    Interface to read and write text files.
    """

    def __init__(self, output_basename: str, rss_filename: str):
        self.removed_authors_filename = 'removed_authors.txt'
        self.history_titles_path = os.path.join('history_titles', output_basename + '.txt')
        self.rss_filename = rss_filename

    def read_history_titles(self) -> List[str]:
        raise NotImplementedError()

    def write_history_titles(self, history_titles: List[str]) -> int:
        raise NotImplementedError()

    def write_podcast_feed(self, feed: str):
        raise NotImplementedError()

    def read_podcast_feed(self) -> Element:
        raise NotImplementedError()

    def read_removed_authors(self) -> List[str]:
        raise NotImplementedError()


class LocalStorage(StorageInterface):
    """
    StorageInterface implementation to work with local files.
    """

    def __init__(
            self, output_basename: str, rss_filename: str
    ):
        super().__init__(output_basename, rss_filename)

    def read_history_titles(self):
        if not os.path.isfile(self.history_titles_path):
            print('No file found at ', self.history_titles_path, ' so returning an empty List of item titles.')
            return []
        history_titles = self.__read_file(self.history_titles_path)
        print('Found item titles in history of ', ', '.join(history_titles))
        return history_titles

    def write_history_titles(self, history_titles: List[str]) -> int:
        print('Writing ', ', '.join(history_titles), ' to ', self.history_titles_path)
        return self.__write_file(self.history_titles_path, '\n'.join(history_titles))

    def read_removed_authors(self):
        removed_authors = self.__read_file('./removed_authors.txt')
        print('Returning removed authors of ', ', '.join(removed_authors))
        return removed_authors

    def read_podcast_feed(self) -> Element:
        try:
            return ElementTree.parse(self.rss_filename).getroot()
        except ParseError:
            empty_xml_feed = 'rss_files/empty_feed.xml'
            print('ParseError when trying to parse XML from file at ', self.rss_filename, ' so returning XML from ',
                  empty_xml_feed, ' instead.')
            return ElementTree.parse(empty_xml_feed).getroot()

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

    def __init__(self, output_basename, gcp_bucket, rss_filename: str):
        super().__init__(output_basename, rss_filename)
        self.gcp_bucket = gcp_bucket

    def read_history_titles(self):
        return self.__read_file(self.history_titles_path)

    def read_removed_authors(self):
        removed_authors = self.__read_file('./removed_authors.txt')
        print('Returning removed authors of ', ', '.join(removed_authors))
        return removed_authors

    def write_history_titles(self, history_titles: List[str]):
        print('Writing history titles ', ', '.join(history_titles), ' to ', self.history_titles_path)
        return self.__write_file(self.history_titles_path, "\n".join(history_titles))

    def write_podcast_feed(self, feed: str):
        print('Writing podcast feed ', feed, ' to file ', self.rss_filename)
        self.__write_file(self.rss_filename, feed)

    def read_podcast_feed(self) -> Element:
        # TODO: check if this works on GCP
        rss_feed_str = "".join(self.__read_file(self.rss_filename))
        try:
            return ElementTree.fromstring(rss_feed_str)
        except ParseError:
            return ElementTree.parse('rss_files/empty_feed.xml').getroot()

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


def create_storage(feed_config: FeedGeneratorConfig, running_on_gcp: bool):
    """
    Factory to retrieve a storage interface implementation for local or cloud environments.
    Args:
        feed_config: Feed configuration data
        running_on_gcp: True if running on GCP. False if running locally.

    Returns: StorageInterface implementation.

    """
    if running_on_gcp:
        return GoogleCloudStorage(output_basename=feed_config.history_titles_filename,
                                  gcp_bucket=feed_config.gcp_bucket, rss_filename=feed_config.rss_filename)
    else:
        return LocalStorage(output_basename=feed_config.history_titles_filename, rss_filename=feed_config.rss_filename)
