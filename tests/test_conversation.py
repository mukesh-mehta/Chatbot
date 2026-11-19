from dataclasses import replace
from datetime import date

import pytest

from chatbot.conversation import respond
from chatbot.providers import SampleFlightProvider
from chatbot.trips import Trip


def test_multi_turn_trip_and_corrections(client):
    trip = {}
    for message, next_field in [
        ("hi", "origin"),
        ("Delhi", "destination"),
        ("Mumbai", "departure_date"),
    ]:
        result = client.post("/api/chat", json={"message": message, "trip": trip}).json
        assert result["missing_fields"][0] == next_field
        assert not result["offers"]
        trip = result["trip"]
    result = client.post(
        "/api/chat", json={"message": "tomorrow for two adults", "trip": trip}
    ).json
    assert result["trip"]["departure_date"] == "2026-11-20"
    assert result["trip"]["adults"] == 2
    assert len(result["offers"]) == 3
    result = client.post(
        "/api/chat", json={"message": "to Bengaluru business", "trip": result["trip"]}
    ).json
    assert result["trip"]["origin"] == "DEL"
    assert result["trip"]["destination"] == "BLR"
    assert result["trip"]["cabin"] == "business"
    assert all(o["legs"][0]["destination"] == "BLR" for o in result["offers"])


def test_round_trip_then_one_way(client):
    result = client.post(
        "/api/chat",
        json={"message": "from Mumbai to Delhi on 2026-11-25 returning on 2026-11-28 for 3 adults"},
    ).json
    assert result["trip"]["trip_type"] == "round_trip"
    assert len(result["offers"][0]["legs"]) == 2
    assert result["offers"][0]["legs"][1]["origin"] == "DEL"
    changed = client.post("/api/chat", json={"message": "one way", "trip": result["trip"]}).json
    assert changed["trip"]["return_date"] is None
    assert len(changed["offers"][0]["legs"]) == 1
    assert changed["offers"][0]["total_price"] * 2 == result["offers"][0]["total_price"]


def test_followup_return_date(client, trip):
    result = client.post("/api/chat", json={"message": "round trip", "trip": trip}).json
    assert result["missing_fields"] == ["return_date"]
    result = client.post("/api/chat", json={"message": "2026-11-25", "trip": result["trip"]}).json
    assert result["trip"]["departure_date"] == "2026-11-20"
    assert result["trip"]["return_date"] == "2026-11-25"
    assert len(result["offers"]) == 3


@pytest.mark.parametrize(
    "message,field",
    [
        ("from Paris to Mumbai tomorrow", "origin"),
        ("from Delhi to Atlantis tomorrow", "destination"),
        ("2026-02-30", "departure_date"),
        ("ten adults", "adults"),
        ("0 people", "adults"),
        ("to Delhi", "destination"),
    ],
)
def test_invalid_updates_never_return_offers(client, trip, message, field):
    result = client.post("/api/chat", json={"message": message, "trip": trip}).json
    assert field in result["errors"]
    assert result["offers"] == []
    assert not result["search_performed"]


def test_invalid_calendar_date_keeps_previous_date(client, trip):
    result = client.post("/api/chat", json={"message": "2026-02-30", "trip": trip}).json
    assert result["trip"]["departure_date"] == trip["departure_date"]
    assert result["errors"]


def test_reset_and_no_booking_claim(client, trip):
    result = client.post("/api/chat", json={"message": "book this ticket", "trip": trip}).json
    assert "cannot book" in result["reply"]
    assert not result["search_performed"]
    reset = client.post("/api/chat", json={"message": "start over", "trip": trip}).json
    assert reset["trip"] == Trip().to_dict()
    assert reset["offers"] == []


def test_word_boundaries_do_not_match_city_codes_inside_words(client):
    result = client.post("/api/chat", json={"message": "a delicious meal"}).json
    assert result["trip"]["origin"] is None
    assert not result["search_performed"]


def test_airport_alias_and_reversed_explicit_route(client):
    result = client.post(
        "/api/chat", json={"message": "to Bangalore from Bombay day after tomorrow"}
    ).json
    assert result["trip"]["origin"] == "BOM"
    assert result["trip"]["destination"] == "BLR"
    assert result["trip"]["departure_date"] == "2026-11-21"


def test_relative_dates_across_month_and_year():
    result = respond("Delhi to Goa tomorrow", Trip(), SampleFlightProvider(), date(2026, 12, 31))
    assert result["trip"]["departure_date"] == "2027-01-01"


def test_no_results_provider_is_not_treated_as_successful_availability(today):
    class EmptyProvider:
        def search(self, trip):
            return []

    trip = replace(Trip(), origin="DEL", destination="BOM", departure_date="2026-11-20")
    result = respond("search", trip, EmptyProvider(), today)
    assert result["search_performed"]
    assert result["offers"] == []
    assert "No matching" in result["reply"]
