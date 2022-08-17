import os


class FileNotExistsError(Exception):
    pass


def check_file_exist(filepath: str) -> None:
    if os.path.isfile(filepath):
        raise FileExistsError

def check_file_not_exist(filepath: str) -> None:
    if not os.path.isfile(filepath):
        raise FileNotExistsError

def check_dir_exist(dirpath: str) -> None:
    if os.path.isdir(dirpath):
        raise FileExistsError
