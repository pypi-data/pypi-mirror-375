import dynaplex as dp

def test_hello():
    assert dp.hello() == "Hello from DynaPlex!"

def test_goodbye():
    assert dp.goodbye() == "Goodbye from DynaPlex!"

def test_greet():
    assert "Hello from DynaPlex!" in dp.greet("World")

def test_add():
    assert dp.add(2, 3) == 5
