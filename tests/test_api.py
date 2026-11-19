from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import pytest

from chatbot.app import create_app
from chatbot.providers import SampleFlightProvider
from chatbot.trips import Trip


def test_search_includes_all_adults_and_preserves_deterministic_ids(client, trip):
    response = client.post("/api/search", json={"trip": trip})
    assert response.status_code == 200
    offers = response.json["offers"]
    assert len(offers) == 3
    assert all(o["is_sample"] and o["currency"] == "INR" for o in offers)
    again = client.post("/api/search", json={"trip": trip}).json
    assert again["offers"] == offers
    solo = client.post("/api/search", json={"trip": {**trip, "adults": 1}}).json["offers"]
    assert offers[0]["total_price"] == 2 * solo[0]["total_price"]
    for offer in offers:
        leg = offer["legs"][0]
        elapsed = datetime.fromisoformat(leg["arrival"]) - datetime.fromisoformat(leg["departure"])
        assert elapsed.total_seconds() == leg["duration_minutes"] * 60


@pytest.mark.parametrize(
    "patch,field",
    [
        ({"origin": None}, "origin"),
        ({"destination": "DEL"}, "destination"),
        ({"origin": "XXX"}, "origin"),
        ({"departure_date": "2026-02-30"}, "departure_date"),
        ({"departure_date": "2026-11-18"}, "departure_date"),
        ({"departure_date": "2028-01-01"}, "departure_date"),
        ({"departure_date": "20261120"}, "departure_date"),
        ({"trip_type": "round_trip"}, "return_date"),
        ({"trip_type": "round_trip", "return_date": "2026-11-19"}, "return_date"),
    ],
)
def test_search_domain_validation(client, trip, patch, field):
    response = client.post("/api/search", json={"trip": {**trip, **patch}})
    assert response.status_code == 422
    assert field in response.json["errors"]


@pytest.mark.parametrize(
    "patch",
    [
        {"adults": True},
        {"adults": 1.5},
        {"adults": "2"},
        {"adults": 10},
        {"origin": []},
        {"departure_date": 7},
        {"cabin": "first"},
        {"trip_type": []},
        {"untrusted": "ignore validation"},
    ],
)
def test_strict_request_types(client, trip, patch):
    assert client.post("/api/search", json={"trip": {**trip, **patch}}).status_code == 422


@pytest.mark.parametrize("message", [None, [], 42, "", " ", "x" * 501])
def test_message_limits(client, message):
    assert client.post("/api/chat", json={"message": message}).status_code == 422


def test_malformed_requests_and_security_headers(client):
    assert (
        client.post("/api/chat", data="not json", content_type="application/json").status_code
        == 400
    )
    assert client.post("/api/chat", data="hello").status_code == 415
    assert client.post("/api/chat", json=[]).status_code == 422
    assert client.post("/api/chat", json={"message": "hello", "role": "admin"}).status_code == 422
    assert (
        client.post("/api/chat", data="x" * 9000, content_type="application/json").status_code
        == 413
    )
    assert (
        client.post(
            "/api/chat", json={"message": "hi"}, headers={"Origin": "https://unrelated.example"}
        ).status_code
        == 403
    )
    assert client.get("/api/health", headers={"Host": "unrelated.example"}).status_code == 400
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert "frame-ancestors 'none'" in response.headers["Content-Security-Policy"]


def test_no_legacy_files_are_served(client):
    assert client.get("/").status_code == 200
    assert client.get("/assets/app.js").status_code == 200
    assert client.get("/assets/../../legacy/actions.py").status_code == 404
    assert client.get("/legacy/models/nlu/current_py3/metadata.json").status_code == 404


def test_config_uses_injected_clock(client):
    config = client.get("/api/config").json
    assert config["today"] == "2026-11-19"
    assert config["max_date"] == "2027-11-19"
    assert config["timezone"] == "Asia/Kolkata"
    assert len(config["airports"]) == 8


def test_conversations_do_not_share_server_state(today):
    app = create_app({"TESTING": True, "TODAY": lambda: today})

    def run(message):
        with app.test_client() as client:
            return client.post("/api/chat", json={"message": message}).json["trip"]

    with ThreadPoolExecutor(max_workers=2) as pool:
        a, b = list(pool.map(run, ["Delhi to Mumbai tomorrow", "Bengaluru to Kochi tomorrow"]))
    assert (a["origin"], a["destination"]) == ("DEL", "BOM")
    assert (b["origin"], b["destination"]) == ("BLR", "COK")


def test_provider_is_replaceable_without_chat_or_frontend_changes(trip):
    assert len(SampleFlightProvider().search(Trip.from_payload(trip))) == 3


def test_same_day_round_trip_never_returns_before_arrival(client, trip):
    result = client.post(
        "/api/search",
        json={"trip": {**trip, "trip_type": "round_trip", "return_date": trip["departure_date"]}},
    ).json
    assert result["offers"]
    for offer in result["offers"]:
        outbound, inbound = offer["legs"]
        connection = datetime.fromisoformat(inbound["departure"]) - datetime.fromisoformat(
            outbound["arrival"]
        )
        assert connection.total_seconds() >= 90 * 60
        assert inbound["departure"].startswith(trip["departure_date"])
