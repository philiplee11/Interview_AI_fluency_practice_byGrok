import pytest
from src.core import db


@pytest.fixture(autouse=True)
def clean_db():
    db.reset()
    yield
    db.reset()
