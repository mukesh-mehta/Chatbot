"""Provider boundary. All offers here are deterministic, fictional fixtures."""

import hashlib
from datetime import datetime, timedelta
from typing import Protocol
from zoneinfo import ZoneInfo

from .trips import Trip


class FlightProvider(Protocol):
    def search(self, trip: Trip) -> list[dict]: ...


class SampleFlightProvider:
    mode = "sample"

    def search(self, trip: Trip) -> list[dict]:
        seed = int(hashlib.sha256(f"{trip.origin}:{trip.destination}".encode()).hexdigest()[:6], 16)
        offers = []
        for index, (airline, departure, offset) in enumerate(
            (("Cloudline", "07:10", 600), ("Skylark", "12:45", 0), ("Altitude", "18:20", 950))
        ):
            duration = 85 + (seed % 10) * 10 + index * 15
            amount = (3400 + seed % 1600 + offset) * (2 if trip.cabin == "business" else 1)
            legs = [
                self._leg(trip.origin, trip.destination, trip.departure_date, departure, duration)
            ]
            if trip.trip_type == "round_trip":
                connection_ready = datetime.fromisoformat(legs[0]["arrival"]) + timedelta(
                    minutes=90
                )
                legs.append(
                    self._leg(
                        trip.destination,
                        trip.origin,
                        trip.return_date,
                        "16:10",
                        duration,
                        not_before=connection_ready,
                    )
                )
                if legs[-1]["departure"][:10] != trip.return_date:
                    continue
            identifier = hashlib.sha256(f"{trip.to_dict()}:{index}".encode()).hexdigest()[:16]
            offers.append(
                {
                    "id": identifier,
                    "airline": airline,
                    "flight_number": f"SAMPLE-{index + 101}",
                    "legs": legs,
                    "duration_minutes": sum(leg["duration_minutes"] for leg in legs),
                    "total_price": amount * trip.adults * len(legs),
                    "currency": "INR",
                    "adults": trip.adults,
                    "cabin": trip.cabin,
                    "stops": 0,
                    "is_sample": True,
                }
            )
        return offers

    @staticmethod
    def _leg(origin, destination, day, departure, duration, not_before=None):
        start = datetime.fromisoformat(f"{day}T{departure}").replace(
            tzinfo=ZoneInfo("Asia/Kolkata")
        )
        if not_before:
            start = max(start, not_before)
        return {
            "origin": origin,
            "destination": destination,
            "departure": start.isoformat(),
            "arrival": (start + timedelta(minutes=duration)).isoformat(),
            "duration_minutes": duration,
        }
