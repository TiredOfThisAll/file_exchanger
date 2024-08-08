import os


def file_exists_on_disk(path, file_uuid):
    try:
        with open(os.path.join(path, file_uuid)) as file:
            return file_uuid
    except FileNotFoundError:
        pass
