from . import _core  

def greet(name: str) -> str:
    return f"{_core.hello()} {name}!"