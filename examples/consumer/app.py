"""Consumer integration fixture: the host agent would adapt this application."""
from hello_sdk import greet


def welcome(name):
    try:
        return {"message": greet(name), "status": 200}
    except (ValueError, TypeError):
        return {"message": "Please provide a name", "status": 400}
