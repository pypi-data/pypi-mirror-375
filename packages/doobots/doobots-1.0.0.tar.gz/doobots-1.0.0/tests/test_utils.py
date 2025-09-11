import pytest
from doobots.utils import ensure_type

def test_ensure_type():
    ensure_type("age", 29, int)
    ensure_type("price", 19.99, float)
    ensure_type("name", "Matheus", str)
    ensure_type("is_active", True, bool)
    with pytest.raises(TypeError):
        ensure_type("age", "29", int)
    with pytest.raises(TypeError):
        ensure_type("price", "19.99", float)
    with pytest.raises(TypeError):
        ensure_type("name", 123, str)
    with pytest.raises(TypeError):
        ensure_type("is_active", "True", bool)