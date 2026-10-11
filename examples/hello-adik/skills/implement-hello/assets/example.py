from hello_sdk import greet

assert greet(" Ada ") == "Hello, Ada!"
assert greet("María") == "Hello, María!"
try:
    greet("  ")
except ValueError:
    pass
else:
    raise AssertionError("Blank names must fail")
print("Hello SDK example passed")
