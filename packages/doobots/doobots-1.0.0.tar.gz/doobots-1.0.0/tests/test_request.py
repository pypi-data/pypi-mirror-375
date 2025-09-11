import pytest
from doobots import Request
from doobots.file import File

def test_request_get_and_files():
    input_data = {
        "name": "Matheus"
    }

    input_files: list[dict] = [{"base64": "dGVzdA==", "fileName": "test.txt"}]

    req = Request(input_data, input_files)
    assert req.get("name") == "Matheus"
    
    file = req.get_file("test.txt")
    assert file is not None
    
    assert file.base64 == "dGVzdA=="
    assert file.fileName == "test.txt"
    assert req.get_file("nonexistent") is None

    with pytest.raises(TypeError):
        req.get_file(123)
