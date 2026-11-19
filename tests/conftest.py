from datetime import date

import pytest

from chatbot.app import create_app


@pytest.fixture
def today():
    return date(2026, 11, 19)


@pytest.fixture
def client(today):
    return create_app({"TESTING": True, "TODAY": lambda: today}).test_client()


@pytest.fixture
def trip():
    return {
        "origin": "DEL",
        "destination": "BOM",
        "departure_date": "2026-11-20",
        "return_date": None,
        "adults": 2,
        "cabin": "economy",
        "trip_type": "one_way",
    }
