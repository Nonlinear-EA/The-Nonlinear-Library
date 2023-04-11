import os
from typing import List
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, ParseError

from feed import BaseFeedConfig


class StorageInterface:
    """
    Interface to read and write text files.
    """

    def __init__(self, output_basename):
        self.removed_authors_filename = 'removed_authors.txt'
        self.history_titles_path = os.path.join('history_titles', output_basename + '.txt')
        self.beyondwords_feed_history_titles = os.path.join('history_titles', 'beyondwords_titles.txt')
        self.rss_file = os.path.join('rss_files', output_basename + '.xml')

    def read_history_titles(self) -> List[str]:
        raise NotImplementedError()

    def read_past_post_titles(self) -> List[str]:
        raise NotImplementedError()

    def read_beyondwords_history_titles(self) -> List[str]:
        raise NotImplementedError()

    def write_beyondwords_history_titles(self, titles):
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
            self, output_basename: str
    ):
        super().__init__(output_basename)

    def read_history_titles(self):
        if not os.path.isfile(self.history_titles_path):
            return []
        return self.__read_file(self.history_titles_path)

    def write_history_titles(self, history_titles: List[str]) -> int:
        return self.__write_file(self.history_titles_path, '\n'.join(history_titles))

    def read_removed_authors(self):
        return self.__read_file('./removed_authors.txt')

    def read_podcast_feed(self) -> Element:
        try:
            return ElementTree.parse(self.rss_file).getroot()
        except ParseError:
            return ElementTree.parse('rss_files/empty_feed.xml').getroot()

    def read_beyondwords_history_titles(self) -> List[str]:
        self.__read_file(self.beyondwords_feed_history_titles)

    def write_beyondwords_history_titles(self, titles):
        self.__write_file(self.beyondwords_feed_history_titles, '\n'.join(titles))

    def write_podcast_feed(self, feed):
        self.__write_file_as_bytes(self.rss_file, feed)

    def __read_file(self, filename: str):
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

    def __init__(self, output_basename, gcp_bucket):
        super().__init__(output_basename)
        self.gcp_bucket = gcp_bucket

    def read_history_titles(self):
        return self.__read_file(self.history_titles_path)

    def read_removed_authors(self):
        return self.__read_file('./removed_authors.txt')

    def read_beyondwords_history_titles(self) -> List[str]:
        return self.__read_file(self.beyondwords_feed_history_titles)

    def write_beyondwords_history_titles(self, titles):
        return self.__write_file(self.beyondwords_feed_history_titles, "\n".join(titles))

    def write_history_titles(self, history_titles: List[str]) -> int:
        return self.__write_file(self.history_titles_path, "\n".join(history_titles))

    def write_podcast_feed(self, feed: str):
        self.__write_file(self.rss_file, feed)

    def read_podcast_feed(self) -> Element:
        # TODO: check if this works on GCP
        rss_feed_str = "".join(self.__read_file(self.rss_file))
        try:
            return ElementTree.fromstring(rss_feed_str)
        except ParseError:
            return ElementTree.parse('rss_files/empty_feed.xml').getroot()

    def read_past_post_titles(self) -> List[str]:
        return self.__read_file(self.past_forum_post_titles)

    def __read_file(self, path: str):
        from google.cloud import storage
        client = storage.Client()
        bucket = client.get_bucket(self.gcp_bucket)
        blob = bucket.get_blob(path)
        if blob is None:
            return []
        downloaded_blob = blob.download_as_string()
        return [line.rstrip() for line in downloaded_blob.decode('UTF-8').split('\n')]

    def __write_file(self, path: str, content: str) -> int:
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
        return GoogleCloudStorage(output_basename=feed_config.output_basename,
                                  gcp_bucket=feed_config.gcp_bucket)
    else:
        return LocalStorage(output_basename=feed_config.output_basename)
