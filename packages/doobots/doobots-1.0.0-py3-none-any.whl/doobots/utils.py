def ensure_type(arg_name: str, value: object, expected_type: type):
    if not isinstance(value, expected_type):
        raise TypeError(f"O argumento '{arg_name}' deve ser do tipo {expected_type.__name__}, "f"mas recebeu {type(value).__name__}")