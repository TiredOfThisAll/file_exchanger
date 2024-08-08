import aiofiles


class DrivePersistence:
    def open(self, path):
        return aiofiles.open(path, 'wb')
