import os

from functions.feed import FeedGeneratorConfig


class StorageInterface:
    """
    Interface to read and write text files.
    """

    def read_history_titles(self):
        raise NotImplementedError()

    def read_removed_authors(self):
        raise NotImplementedError()


class LocalStorage(StorageInterface):
    """
    StorageInterface implementation to work with local files.
    """
    history_titles_filename: str
    removed_authors_filename: str

    def __init__(self, history_titles_filename, removed_authors_filename):
        self.history_titles_filename = history_titles_filename
        self.removed_authors_filename = removed_authors_filename

    def read_history_titles(self):
        return self.__read_file(self.history_titles_filename)

    def read_removed_authors(self):
        return self.__read_file(self.removed_authors_filename)

    def __read_file(self, filename: str):
        with open(os.path.basename(filename), 'r') as f:
            return [line.rstrip() for line in f.readlines()]


class GoogleCloudStorage(StorageInterface):
    """
    StorageInterface implementation to work with files on the cloud.
    """
    history_titles_filename: str
    removed_authors_filename: str
    gcp_bucket: str

    def __init__(self, history_titles_filename, removed_authors_filename, gcp_bucket):
        self.history_titles_filename = history_titles_filename
        self.removed_authors_filename = removed_authors_filename
        self.gcp_bucket = gcp_bucket

    def read_history_titles(self):
        return self.__read_file(self.history_titles_filename)

    def read_removed_authors(self):
        return self.__read_file(self.removed_authors_filename)

    def __read_file(self, filename: str):
        from google.cloud import storage
        client = storage.Client()
        bucket = client.get_bucket(self.gcp_bucket)
        blob = bucket.get_blob(filename)
        downloaded_blob = blob.download_as_string()
        return [line.rstrip() for line in downloaded_blob.decode('UTF-8').split('\n')]


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
                                  history_titles_filename=feed_config.history_titles_filename,
                                  gcp_bucket=feed_config.gcp_bucket)
    else:
        return LocalStorage(removed_authors_filename=feed_config.removed_authors_filename,
                            history_titles_filename=feed_config.history_titles_filename)
