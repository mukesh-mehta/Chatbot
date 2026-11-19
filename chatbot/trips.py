"""Validated trip state shared by the chat and structured search interfaces."""

from dataclasses import asdict, dataclass, fields
from datetime import date, timedelta

AIRPORTS = (
    {
        "code": "DEL",
        "city": "Delhi",
        "name": "Indira Gandhi International",
        "aliases": ["new delhi"],
    },
    {
        "code": "BOM",
        "city": "Mumbai",
        "name": "Chhatrapati Shivaji Maharaj International",
        "aliases": ["bombay"],
    },
    {
        "code": "BLR",
        "city": "Bengaluru",
        "name": "Kempegowda International",
        "aliases": ["bangalore"],
    },
    {"code": "HYD", "city": "Hyderabad", "name": "Rajiv Gandhi International", "aliases": []},
    {"code": "MAA", "city": "Chennai", "name": "Chennai International", "aliases": ["madras"]},
    {
        "code": "CCU",
        "city": "Kolkata",
        "name": "Netaji Subhas Chandra Bose International",
        "aliases": ["calcutta"],
    },
    {"code": "GOI", "city": "Goa", "name": "Dabolim Airport", "aliases": ["dabolim"]},
    {"code": "COK", "city": "Kochi", "name": "Cochin International", "aliases": ["cochin"]},
)
AIRPORT_BY_CODE = {airport["code"]: airport for airport in AIRPORTS}
FIELD_LABELS = {
    "origin": "departure airport",
    "destination": "destination airport",
    "departure_date": "departure date",
    "return_date": "return date",
}


class InputError(ValueError):
    def __init__(self, message, errors=None):
        super().__init__(message)
        self.errors = errors or {}


@dataclass(frozen=True)
class Trip:
    origin: str | None = None
    destination: str | None = None
    departure_date: str | None = None
    return_date: str | None = None
    adults: int = 1
    cabin: str = "economy"
    trip_type: str = "one_way"

    @classmethod
    def from_payload(cls, value):
        if not isinstance(value, dict):
            raise InputError("Trip must be a JSON object.")
        if set(value) - {field.name for field in fields(cls)}:
            raise InputError("Trip contains unsupported fields.")
        data = value.copy()
        for key in ("origin", "destination", "departure_date", "return_date"):
            item = data.get(key)
            if item is not None and (not isinstance(item, str) or len(item) > 32):
                raise InputError(f"Invalid {key}.")
            if item is not None:
                data[key] = item.strip() or None
        for key in ("origin", "destination"):
            if data.get(key):
                data[key] = data[key].upper()
        if type(data.get("adults", 1)) is not int or not 1 <= data.get("adults", 1) <= 9:
            raise InputError(
                "Choose between 1 and 9 adults.", {"adults": "Use a whole number from 1 to 9."}
            )
        if data.get("cabin", "economy") not in ("economy", "business"):
            raise InputError("Choose economy or business cabin.")
        if data.get("trip_type", "one_way") not in ("one_way", "round_trip"):
            raise InputError("Choose one way or round trip.")
        if data.get("trip_type", "one_way") == "one_way":
            data["return_date"] = None
        return cls(**data)

    def to_dict(self):
        return asdict(self)

    def missing_fields(self):
        required = ["origin", "destination", "departure_date"]
        if self.trip_type == "round_trip":
            required.append("return_date")
        return [field for field in required if not getattr(self, field)]

    def errors(self, today: date, *, require_complete=False):
        errors = {}
        if require_complete:
            errors.update(
                {field: f"Choose a {FIELD_LABELS[field]}." for field in self.missing_fields()}
            )
        for field in ("origin", "destination"):
            value = getattr(self, field)
            if value and value not in AIRPORT_BY_CODE:
                errors[field] = "Choose one of the eight supported airports."
        if self.origin and self.origin == self.destination:
            errors["destination"] = "Departure and destination must be different."
        parsed = {}
        for field in ("departure_date", "return_date"):
            value = getattr(self, field)
            if not value:
                continue
            try:
                parsed[field] = date.fromisoformat(value)
                if parsed[field].isoformat() != value:
                    raise ValueError
            except ValueError:
                errors[field] = "Enter a real date in YYYY-MM-DD format."
                continue
            if not today <= parsed[field] <= today + timedelta(days=365):
                errors[field] = "Choose a date from today through the next 365 days."
        if parsed.get("return_date") and parsed.get("departure_date"):
            if parsed["return_date"] < parsed["departure_date"]:
                errors["return_date"] = "Return must be on or after departure."
        return errors
