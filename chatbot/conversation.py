"""Small, explainable slot-filling baseline; no trained model or LLM is implied."""

import re
from dataclasses import replace
from datetime import date, timedelta

from .trips import AIRPORT_BY_CODE, AIRPORTS, FIELD_LABELS, Trip

ALIASES = {
    alias.casefold(): airport["code"]
    for airport in AIRPORTS
    for alias in [airport["city"], airport["code"], *airport["aliases"]]
}
AIRPORT_PATTERN = re.compile(
    r"\b("
    + "|".join(re.escape(alias) for alias in sorted(ALIASES, key=len, reverse=True))
    + r")\b",
    re.I,
)
DATE_PATTERN = re.compile(r"\b(?:\d{4}-\d{2}-\d{2}|day after tomorrow|tomorrow|today)\b", re.I)
NUMBERS = {
    name: i
    for i, name in enumerate(
        ("zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten")
    )
}


def _date_value(text, today):
    offsets = {"today": 0, "tomorrow": 1, "day after tomorrow": 2}
    if text in offsets:
        return (today + timedelta(days=offsets[text])).isoformat()
    return date.fromisoformat(text).isoformat()


def extract_changes(message: str, trip: Trip, today: date):
    text = message.casefold()
    changes, errors = {}, {}
    if re.search(r"\b(one[ -]way)\b", text):
        changes.update(trip_type="one_way", return_date=None)
    elif re.search(r"\b(round[ -]trip|return(?:ing)?)\b", text):
        changes["trip_type"] = "round_trip"
    for cabin in ("economy", "business"):
        if re.search(rf"\b{cabin}\b", text):
            changes["cabin"] = cabin

    matches = list(AIRPORT_PATTERN.finditer(text))
    for index, match in enumerate(matches[:2]):
        prefix = re.search(r"\b(from|to)\s*$", text[: match.start()])
        if prefix:
            field = "origin" if prefix[1] == "from" else "destination"
        elif len(matches) > 1:
            field = "origin" if index == 0 else "destination"
        else:
            field = "origin" if not trip.origin else "destination"
        changes[field] = ALIASES[match[0]]
    # Explicit but unknown places must not silently reuse an earlier route.
    for marker, place in re.findall(
        r"\b(from|to)\s+(.+?)(?=\s+(?:to|from|on|for|return(?:ing)?|in|today|tomorrow|day after tomorrow|\d{4}-\d{2}-\d{2})\b|[,.!?]|$)",
        text,
    ):
        if not AIRPORT_PATTERN.search(place) and not DATE_PATTERN.search(place):
            errors["origin" if marker == "from" else "destination"] = (
                "I couldn't match that airport. Please use a city or code from the trip editor."
            )

    passenger = re.search(
        r"\b(\d+|zero|one|two|three|four|five|six|seven|eight|nine|ten)\s+(?:adults?|people|passengers?|travellers?|travelers?)\b",
        text,
    )
    if passenger:
        value = NUMBERS.get(passenger[1], passenger[1])
        if 1 <= int(value) <= 9:
            changes["adults"] = int(value)
        else:
            errors["adults"] = "This prototype supports 1 to 9 adults."

    for index, match in enumerate(DATE_PATTERN.finditer(text)):
        is_return = re.search(r"\breturn(?:ing)?(?:\s+on)?\s*$", text[: match.start()])
        awaiting_return = (
            trip.trip_type == "round_trip" and trip.departure_date and not trip.return_date
        )
        field = (
            "return_date"
            if is_return
            or index > 0
            or (awaiting_return and not re.search(r"\b(depart|departure|leave)\b", text))
            else "departure_date"
        )
        try:
            changes[field] = _date_value(match[0], today)
            if field == "return_date":
                changes["trip_type"] = "round_trip"
        except ValueError:
            errors[field] = "That date doesn't exist. Try YYYY-MM-DD or tomorrow."
    return changes, errors


def result_for(trip, provider, today, *, reply=None, errors=None, search=False):
    errors = errors or trip.errors(today)
    missing = trip.missing_fields()
    offers = provider.search(trip) if search and not errors and not missing else []
    performed = search and not errors and not missing
    if reply is None:
        if errors:
            reply = next(iter(errors.values()))
        elif missing:
            reply = f"Got it. What is your {FIELD_LABELS[missing[0]]}?"
        elif offers:
            origin = AIRPORT_BY_CODE[trip.origin]["city"]
            destination = AIRPORT_BY_CODE[trip.destination]["city"]
            travellers = f"{trip.adults} adult" + ("s" if trip.adults != 1 else "")
            legs = "both flights" if trip.trip_type == "round_trip" else "the outbound flight"
            reply = f"Here are {len(offers)} sample itineraries from {origin} to {destination}. Prices cover {travellers} and {legs}. You can sort them or save one to your trip."
        else:
            reply = "No matching itineraries were returned. Try another route or date."
    return {
        "trip": trip.to_dict(),
        "reply": reply,
        "errors": errors,
        "missing_fields": missing,
        "offers": offers,
        "search_performed": bool(performed),
        "mode": "sample",
    }


def respond(message, trip, provider, today):
    text = message.casefold().strip(" .!?")
    if text in {"reset", "start over", "new trip", "cancel", "clear"}:
        return result_for(
            Trip(), provider, today, reply="A fresh start. Where are you flying from?"
        )
    if text in {"hi", "hello", "hey", "help", "hello there"}:
        return result_for(
            trip,
            provider,
            today,
            reply="I can help plan a flight. Try 'Delhi to Mumbai tomorrow for 2 adults', or use the trip editor. The itineraries are fictional; no booking or payment takes place.",
        )
    if text in {"thanks", "thank you", "bye", "goodbye"}:
        return result_for(
            trip,
            provider,
            today,
            reply="You're welcome. Your trip stays in this browser tab until you start a new one.",
        )
    changes, errors = extract_changes(message, trip, today)
    updated = replace(trip, **changes)
    if updated.trip_type == "one_way":
        updated = replace(updated, return_date=None)
    errors = {**updated.errors(today), **errors}
    if (
        not changes
        and not errors
        and text not in {"search", "search flights", "find flights", "show flights"}
    ):
        return result_for(
            trip,
            provider,
            today,
            reply="I couldn't match that request. Try a supported city, an ISO date, '2 adults', or 'business'. You can also edit the trip directly. This prototype cannot book tickets.",
        )
    return result_for(updated, provider, today, errors=errors, search=True)
