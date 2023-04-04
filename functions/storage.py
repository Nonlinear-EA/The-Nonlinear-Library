from typing import List

from functions.feed import FeedGeneratorConfig


class StorageInterface:
    """
    Interface to read and write text files.
    """

    def __init__(self,
                 removed_authors_filename,
                 output_basename
                 ):
        self.removed_authors_filename = removed_authors_filename
        self.output_basename = output_basename
        self.history_titles_path = './history_titles/' + self.output_basename + '.txt'
        self.rss_file = './rss_files/' + self.output_basename + '.xml'

    def read_history_titles(self) -> List[str]:
        raise NotImplementedError()

    def write_history_titles(self, history_titles: List[str]) -> int:
        raise NotImplementedError()

    def write_podcast_feed(self, feed: str):
        raise NotImplementedError()

    def read_removed_authors(self) -> List[str]:
        raise NotImplementedError()


class LocalStorage(StorageInterface):
    """
    StorageInterface implementation to work with local files.
    """
    removed_authors_filename: str
    output_basename: str

    def __init__(
            self, removed_authors_filename: str, output_basename: str
    ):
        super().__init__(removed_authors_filename, output_basename)

    def read_history_titles(self):
        return self.__read_file(self.history_titles_path)

    def write_history_titles(self, history_titles: List[str]) -> int:
        return self.__write_file(self.history_titles_path, "\n".join(history_titles))

    def read_removed_authors(self):
        return self.__read_file('./removed_authors.txt')

    def write_podcast_feed(self, feed):
        self.__write_file(self.rss_file, feed)

    def __read_file(self, filename: str):
        with open(filename, 'r') as f:
            return [line.rstrip() for line in f.readlines()]

    def __write_file(self, filename: str, content: str | bytes):
        if isinstance(content, bytes):
            mode = 'wb'
        else:
            mode = 'w'
        with open(filename, mode) as f:
            return f.write(content)


class GoogleCloudStorage(StorageInterface):
    """
    StorageInterface implementation to work with files on the cloud.
    """
    gcp_bucket: str

    def __init__(self, removed_authors_filename, output_basename, gcp_bucket):
        super().__init__(removed_authors_filename, output_basename)
        self.gcp_bucket = gcp_bucket

    def read_history_titles(self):
        return self.__read_file(self.history_titles_path)

    def read_removed_authors(self):
        return self.__read_file('./removed_authors.txt')

    def write_history_titles(self, history_titles: List[str]) -> int:
        return self.__write_file(self.history_titles_path, "\n".join(history_titles))

    def write_podcast_feed(self, feed: str):
        self.__write_file(self.rss_file, feed)

    def __read_file(self, path: str):
        from google.cloud import storage
        client = storage.Client()
        bucket = client.get_bucket(self.gcp_bucket)
        blob = bucket.get_blob(path)
        downloaded_blob = blob.download_as_string()
        return [line.rstrip() for line in downloaded_blob.decode('UTF-8').split('\n')]

    def __write_file(self, path: str, content: str) -> int:
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
        return GoogleCloudStorage(removed_authors_filename=feed_config.removed_authors_filename,
                                  output_basename=feed_config.output_basename,
                                  gcp_bucket=feed_config.gcp_bucket)
    else:
        return LocalStorage(removed_authors_filename=feed_config.removed_authors_filename,
                            output_basename=feed_config.output_basename)
