
import os
import aiofiles
import logging

logger = logging.getLogger(__name__)

class StorageService:
    def __init__(self, base_dir: str = "recordings"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    async def save_file(self, filename: str, data: bytes) -> str:
        """
        Saves data to a file in the storage directory.
        Returns the absolute file path.
        """
        file_path = os.path.join(self.base_dir, filename)
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(data)
        return file_path

    async def append_file(self, filename: str, data: bytes) -> str:
        """
        Appends data to an existing file (or creates it).
        Returns the absolute file path.
        """
        file_path = os.path.join(self.base_dir, filename)
        async with aiofiles.open(file_path, 'ab') as f:
            await f.write(data)
        return file_path
