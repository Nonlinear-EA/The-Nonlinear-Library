import os
from typing import List

from functions.feed import FeedGeneratorConfig


class StorageInterface:
    """
    Interface to read and write text files.
    """

    def __init__(self,
                 history_titles_filename,
                 removed_authors_filename,
                 output_feed_filename_base
                 ):
        self.history_titles_filename = history_titles_filename
        self.removed_authors_filename = removed_authors_filename
        self.output_feed_filename = f'{output_feed_filename_base}.xml'

    def read_history_titles(self) -> List[str]:
        raise NotImplementedError()

    def write_history_titles(self, history_titles: List[str]) -> int:
        raise NotImplementedError()

    def save_podcast_feed(self, feed: str):
        raise NotImplementedError()

    def read_removed_authors(self) -> List[str]:
        raise NotImplementedError()


class LocalStorage(StorageInterface):
    """
    StorageInterface implementation to work with local files.
    """
    history_titles_filename: str
    removed_authors_filename: str
    output_feed_filename: str

    def __init__(
            self, history_titles_filename: str, removed_authors_filename: str, output_feed_filename_base: str
    ):
        super().__init__(history_titles_filename, removed_authors_filename, output_feed_filename_base)

    def read_history_titles(self):
        return self.__read_file(self.history_titles_filename)

    def write_history_titles(self, history_titles: List[str]) -> int:
        return self.__write_file(self.history_titles_filename, "\n".join(history_titles))

    def read_removed_authors(self):
        return self.__read_file(self.removed_authors_filename)

    def save_podcast_feed(self, feed):
        self.__write_file(self.output_feed_filename, feed)

    def __read_file(self, filename: str):
        with open(os.path.basename(filename), 'r') as f:
            return [line.rstrip() for line in f.readlines()]

    def __write_file(self, filename: str, content: str):
        with open(os.path.basename(filename), 'w') as f:
            return f.write(content)


class GoogleCloudStorage(StorageInterface):
    """
    StorageInterface implementation to work with files on the cloud.
    """

    history_titles_filename: str
    removed_authors_filename: str
    gcp_bucket: str

    def __init__(self, history_titles_filename, removed_authors_filename, output_feed_filename_base, gcp_bucket):
        super().__init__(history_titles_filename, removed_authors_filename, output_feed_filename_base)
        self.gcp_bucket = gcp_bucket

    def read_history_titles(self):
        return self.__read_file(self.history_titles_filename)

    def read_removed_authors(self):
        return self.__read_file(self.removed_authors_filename)

    def write_history_titles(self, history_titles: List[str]) -> int:
        return self.__write_file(self.history_titles_filename, "\n".join(history_titles))

    def save_podcast_feed(self, feed: str):
        # TODO: Implement save_podcast_feed for cloud storage.
        pass

    def __read_file(self, filename: str):
        from google.cloud import storage
        client = storage.Client()
        bucket = client.get_bucket(self.gcp_bucket)
        blob = bucket.get_blob(filename)
        downloaded_blob = blob.download_as_string()
        return [line.rstrip() for line in downloaded_blob.decode('UTF-8').split('\n')]

    def __write_file(self, history_titles_filename: str, content: str) -> int:
        # TODO: Implement write file for cloud storage.
        return 0


def create_storage(feed_config: FeedGeneratorConfig, local=False):
    """
    Factory to retrieve a storage interface implementation for local or cloud environments.
    Args:
        feed_config: Feed configuration data
        local: Flag to signal local or cloud environment.

    Returns: StorageInterface implementation.

    """
    if local:
        return LocalStorage(removed_authors_filename=feed_config.removed_authors_filename,
                            history_titles_filename=feed_config.history_titles_filename,
                            output_feed_filename_base=feed_config.output_file_basename)
    else:
        return GoogleCloudStorage(removed_authors_filename=feed_config.removed_authors_filename,
                                  history_titles_filename=feed_config.history_titles_filename,
                                  output_feed_filename_base=feed_config.output_file_basename,
                                  gcp_bucket=feed_config.gcp_bucket)
