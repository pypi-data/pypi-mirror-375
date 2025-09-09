import os
import shutil
import tempfile


# FR-47422: Created class.
class TempFileHandler:
    """
    A utility class to manage temporary files and directories.
    """
    directories: list[str]
    files: list[str]

    def __init__(self) -> None:
        self.directories = []
        self.files = []

    def create_temp_directory(self) -> str:
        """
        :return: The path to a newly created temporary directory.
        """
        directory: str = tempfile.mkdtemp()
        self.directories.append(directory)
        return directory

    def create_temp_file(self, data: str | bytes, suffix: str = "") -> str:
        """
        :param data: The data to write to the temporary file.
        :param suffix: An optional suffix for the temporary file.
        :return: The path to a newly created temporary file containing the provided data.
        """
        mode: str = 'w' if isinstance(data, str) else 'wb'
        with tempfile.NamedTemporaryFile(mode=mode, suffix=suffix, delete=False) as tmp_file:
            tmp_file.write(data)
            file_path: str = tmp_file.name
            self.files.append(file_path)
        return file_path

    def cleanup(self) -> None:
        """
        Delete all temporary files and directories created by this handler.
        """
        for directory in self.directories:
            if os.path.exists(directory):
                shutil.rmtree(directory)

        for file_path in self.files:
            if os.path.exists(file_path):
                os.remove(file_path)
