from typing import IO


class StorageInterface:
    """
    Interface to read and write text files.
    """

    # TODO: Figure out how to use a context manager for handling files, either from the cloud or from memory.
    def get_file(self, filename: str, mode: str = 'r') -> IO:
        raise NotImplementedError()

    def write_file(self, payload: str):
        raise NotImplementedError()


class LocalStorage(StorageInterface):
    """
    StorageIfc implementation to work with local files.
    """

    def get_file(self, filename: str, mode: str = 'r') -> IO:
        return open(filename, mode)

    def write_file(self, payload: str):
        pass


class GoogleCloudStorage(StorageInterface):
    """
    StorageIfc implementation to work with files on the cloud.
    """

    def get_file(self, filename: str, mode: str = 'r') -> IO:
        pass

    def write_file(self, payload: str):
        pass


def get_storage(local=False):
    """
    Factory to retrieve a storage interface implementation for local or cloud environments.
    Args:
        local: Flag to signal local or cloud environment.

    Returns: StorageIfc implementation.

    """
    if local:
        return LocalStorage()
    else:
        return GoogleCloudStorage()
