# API contract · v0.2 prototype

All endpoints are same-origin and unauthenticated for local prototype use. There
is no public-service authentication, user account, or server conversation store.
Each chat/search request is independently validated. Request bodies are capped
at 8 KiB. Responses use JSON except the workspace and static assets.

## Routes

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/` | Browser workspace |
| GET | `/api/health` | Version, sample mode, process liveness |
| GET | `/api/config` | Airports, date bounds, timezone, message limit |
| POST | `/api/chat` | Apply a message to a supplied trip |
| POST | `/api/search` | Validate a complete trip and return sample offers |

`/api/health` is liveness for the current dependency-free sample provider, not a
readiness check for hypothetical future supplier integrations.

## Trip object

```json
{
  "origin": "DEL",
  "destination": "BOM",
  "departure_date": "2026-11-25",
  "return_date": null,
  "adults": 2,
  "cabin": "economy",
  "trip_type": "one_way"
}
```

Use dates within the bounds returned by `/api/config`; the example dates are
illustrative. Origin/destination and dates can be null while chatting. Codes
must come from the airport catalog. Adults must be a JSON integer from 1 to 9;
booleans, floats, and numeric strings are rejected. Cabin is `economy` or
`business`; trip type is `one_way` or `round_trip`. One-way state clears return
date. Unknown trip keys are rejected.

Dates must use the exact ISO calendar format, be valid, and fall between today
and 365 days ahead in India Standard Time. Return cannot precede departure.
The sample provider also ensures a same-day inbound departs at least 90 minutes
after the outbound arrives. This is a fixture rule, not an airline policy.

## Chat requests and responses

Send `{"message":"Delhi to Mumbai tomorrow","trip":{}}` for a first turn. On later
turns, send the last returned trip. Messages must contain 1–500 non-whitespace
characters. Chat errors about a date or route return a normal 200 response with
field-level `errors` and an explanatory `reply`; malformed request types return
422. A bad calendar-date update does not replace a previously valid date.

Response fields:

| Field | Meaning |
| --- | --- |
| `trip` | Updated, serializable trip state |
| `reply` | Plain-text assistant message, never trusted HTML |
| `errors` | Field-to-message mapping requiring attention |
| `missing_fields` | Required trip details that remain absent |
| `offers` | Current sample results, or an empty list |
| `search_performed` | Whether a valid complete trip reached the provider |
| `mode` | `sample`; the active app never presents live fares |

`offers: []` with `search_performed: false` can mean the user is greeting,
correcting, or filling missing details. It is not a supplier availability result.
`search_performed: true` with an empty list means the provider returned no options.

## Search and offer semantics

`POST /api/search` takes `{"trip": {...}}`. Incomplete/invalid state returns 422:

```json
{"error":"Please check your trip details.","errors":{"destination":"Departure and destination must be different."}}
```

Each offer has a stable fixture ID, sample airline/flight number, `is_sample: true`,
legs with timezone-aware ISO timestamps, total duration, cabin, adult count,
currency (`INR`), and integer `total_price`. Price covers all passengers and all
legs. No separate tax, baggage entitlement, refund condition, or ticketing promise
is implied. Never submit a sample offer ID to a real supplier.

## Errors and deployment boundary

400 malformed JSON; 403 cross-origin writes; 404 unknown route; 413 excessive
body size; 415 wrong content type; 422 invalid input. Browser input is escaped,
and headers restrict scripts/frames to the application's policy.

`CHATBOT_ALLOWED_HOSTS` is a comma-separated host allowlist, defaulting to
`localhost,127.0.0.1`. Set it deliberately behind a configured reverse proxy.
TLS, authentication, request quotas, and trusted proxy configuration must be added
before exposing a shared service. There is no wildcard CORS policy.
