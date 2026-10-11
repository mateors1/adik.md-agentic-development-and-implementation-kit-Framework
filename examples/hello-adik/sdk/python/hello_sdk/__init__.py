"""Generated reference SDK. No I/O or external dependencies."""
def greet(name: str) -> str:
    """Return a greeting; reject non-string or blank names."""
    if not isinstance(name, str):
        raise TypeError("name must be a string")
    name = name.strip()
    if not name:
        raise ValueError("name must not be blank")
    return f"Hello, {name}!"
