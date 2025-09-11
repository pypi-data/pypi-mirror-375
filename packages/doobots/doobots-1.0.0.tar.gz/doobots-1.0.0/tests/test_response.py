import os
import pytest
from doobots import Response
from doobots.file import File

def test_response_put_and_files():
    r = Response()
    r.put("key1", "value1")
    r.put_file(file_name="test.txt", base64="dGVzdA==")
    
    with open("teste_doobots_python_response.txt", "w") as f:
        f.write("teste")
    
    r.put_file(file_path="teste_doobots_python_response.txt")
    os.remove("teste_doobots_python_response.txt")
    
    out = r.to_dict()
    data = out["data"]
    assert data is not None
    files = out["files"]
    assert files is not None
    assert isinstance(files, list)
    
    assert data["key1"] == "value1"
    assert any(f.fileName == "test.txt" for f in files)
    assert any(f.fileName == "teste_doobots_python_response.txt" for f in files)

    with pytest.raises(TypeError):
        r.put(123, "value")
    with pytest.raises(TypeError):
        r.put_all("not a dict")
    with pytest.raises(ValueError):
        r.put_json("invalid json")
    with pytest.raises(ValueError):
        r.put_file()
    with pytest.raises(FileNotFoundError):
        r.put_file(file_path="non_existent_file.txt")
    with pytest.raises(TypeError):
        r.put_file(file_name=123, base64="dGVzdA==")
    with pytest.raises(TypeError):
        r.put_file(file_name="test.txt", base64=123)
    with pytest.raises(TypeError):
        r.put_file(file_path=123)
