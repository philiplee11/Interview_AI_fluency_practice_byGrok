import pytest
from src.core import db
from src.services.pricing import PricingService


@pytest.fixture(autouse=True)
def clean_db():
    db.reset()
    PricingService._cache.clear()
    yield
    db.reset()
    PricingService._cache.clear()
