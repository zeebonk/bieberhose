import pickle
from pathlib import Path


"""
Pickle binary serialization is not the prettiest way of storing user settings
and some plain-text format should be used in the future.
"""

CREDENTIALS_PATH = Path.home() / ".bieberhose"


def save(oauth):
    with CREDENTIALS_PATH.open("wb") as fp:
        pickle.dump(oauth, fp)


def load():
    with CREDENTIALS_PATH.open("rb") as f:
        return pickle.load(f)


def exists():
    return CREDENTIALS_PATH.exists()
