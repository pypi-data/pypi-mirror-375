from doobots.file import File
from doobots.utils import ensure_type
class Request:
    def __init__(self, data: dict, files: list[dict] = []):
        self._data = dict(data)
        self._files: list[File] = []

        for i in range(len(files)):
            if isinstance(files[i], dict):
                self._files.append(File(files[i].get("base64", ""), files[i].get("fileName", "")))

    def get(self, key, default_value=None) -> any:
        return self._data.get(key, default_value)
    
    def to_dict(self) -> dict:
        return self._data

    def get_files(self) -> list[File]:
        return self._files

    def get_file(self, file_name: str) -> File | None:
        ensure_type("file_name", file_name, str)
        
        for f in self._files:
            if f.fileName == file_name:
                return f
        return None
