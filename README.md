# Chatbot · Flight assistant

A **Python 3.12 flight-planning prototype** with a responsive chat workspace,
an editable trip form, and clearly labeled sample itineraries.

[![Python 3.12 and frontend checks](https://github.com/mukesh-mehta/Chatbot/actions/workflows/ci.yml/badge.svg)](https://github.com/mukesh-mehta/Chatbot/actions/workflows/ci.yml)

![The flight-planning workspace](docs/workspace.jpg)

This update makes the project's flight-assistant concept runnable on a current
Python environment. The original Python 3.6-era Rasa, Goibibo, and Facebook
implementation is preserved in [`legacy/`](legacy/ARCHIVE.md). The supported
application lives in `chatbot/`, `web/`, and the root `run.py`.

**The archived Rasa code has not been ported to Python 3.12.** The maintained
runtime replaces it with a small, deterministic conversation baseline. It does
not load old model files, contact flight suppliers, use an LLM, book tickets,
or collect payment. Sample airlines, fares, durations, and availability are
fictional. See the [migration notes](docs/MIGRATION.md) for the exact boundary.

## Run with Python 3.12

```bash
git clone https://github.com/mukesh-mehta/Chatbot.git
cd Chatbot
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python run.py
```

Open **http://127.0.0.1:8000**. No credentials, model download, database, Node.js,
or frontend build is required to run the app. Stop it with Ctrl+C.

On Windows PowerShell, replace the environment commands with:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python run.py
```

You can also run `.venv\Scripts\python.exe run.py` without activating the
environment. The optional Conda definition now selects Python 3.12 and installs
the same requirements: `conda env create -f environment.yml`.

For another local port, use `python run.py --port 8120`.

## Try a complete workflow

1. Send **Delhi to Mumbai tomorrow for 2 adults**.
2. Watch the route, departure date, and traveller count fill into the trip editor.
3. Send **business**, or change the cabin in the form and search again.
4. Choose **Round trip**, enter a return date, and search for both legs.
5. Sort by price or duration; save an itinerary and download the JSON trip file.
6. Refresh to restore this tab's conversation and revalidate its trip.
7. Use **New trip** to clear the local conversation and saved selection.

The chat understands supported airport cities/codes, `today`, `tomorrow`,
`day after tomorrow`, ISO dates (`YYYY-MM-DD`), adult counts, and cabin/trip types.
It asks for missing details. This is a deliberately limited parser: use the form
for phrasing it does not recognize. Dates and times use `Asia/Kolkata`.

Supported airports: Delhi, Mumbai, Bengaluru, Hyderabad, Chennai, Kolkata,
Goa (Dabolim), and Kochi. Searches support 1–9 adults and dates within 365 days.

## What is implemented

| Capability | Current behavior |
| --- | --- |
| Python 3.12 runtime | Portable pinned requirements, Flask API, Waitress launcher |
| Conversational planning | Multiple turns, route/date updates, greetings, reset, missing-field questions |
| Shared trip state | Chat and structured form use the same validated trip model |
| Trip validation | Known airports, different endpoints, real/future dates, return ordering, adult limits |
| One-way / round-trip search | Deterministic sample provider; total prices include every adult and leg |
| Frontend workspace | Responsive layout, chat suggestions, editable dates/cabin, airport swap |
| Flight comparison | Price/duration sorting, outbound and return legs, explicit sample-data labels |
| Saved itinerary | One local selection and a JSON download; no reservation is created |
| Tab persistence | Last 40 messages, trip, and selected offer ID in session storage |
| Error handling | Bounded requests, validation feedback, network timeout, retained unsent input |
| Development checks | Python tests, JavaScript tests, Python 3.12 Linux/Windows CI, container smoke check |

The [roadmap](ROADMAP.md) contains the substantially larger remaining scope,
including a dedicated frontend phase and measurable delivery gates. The
[frontend guide](docs/FRONTEND.md) describes the current interface and its limits.

## Architecture

```mermaid
flowchart LR
    UI[Chat and trip editor] --> API[Flask JSON API]
    API --> Parser[Deterministic slot parser]
    Parser --> Trip[Trip validation]
    API --> Trip
    Trip --> Provider[FlightProvider interface]
    Provider --> Sample[SampleFlightProvider]
    Sample --> UI
    UI --> Tab[Browser tab storage and JSON export]
```

The API is stateless: each request supplies the current trip. There is no shared
in-memory conversation dictionary, so separate requests do not overwrite one
another. This is a useful starting point for replication; authentication,
durable storage, rate limits, supplier resilience, and capacity testing remain
roadmap work. Adding a real provider requires a deliberate integration release;
changing the injected class alone is not sufficient to claim live booking support.

## API

```bash
curl http://127.0.0.1:8000/api/health

curl -X POST http://127.0.0.1:8000/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"Delhi to Mumbai tomorrow for 2 adults","trip":{}}'
```

Send the returned `trip` with the next message to continue the conversation.
`POST /api/search` accepts the same trip without a chat message.
Responses include `trip`, `reply`, `errors`, `missing_fields`, `offers`,
`search_performed`, and `mode`. [Full API contract](docs/API.md).

## Docker

```bash
docker build -t flight-chatbot .
docker run --rm --read-only --tmpfs /tmp -p 127.0.0.1:8000:8000 flight-chatbot
```

The image uses Python 3.12 and a non-root user. Only the active application and
runtime dependencies are copied; archived code and serialized models are excluded.
No public hosting or cloud resources are created by these commands.

## Development and verification

Node.js 18+ is only needed for frontend tests/formatting; CI uses Node 20.

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -m compileall -q chatbot run.py scripts tests
python -m pip check
ruff check .
ruff format --check .
npm ci --ignore-scripts
npm test
npm run format:check
# With the server already running:
python scripts/smoke.py
```

Tests and formatting intentionally exclude `legacy/`. Do not use the archived
requirements file to install the modern application. Runtime versions are
declared in `pyproject.toml` and resolved in `requirements.txt`; development
dependencies are separately recorded in `requirements-dev.txt`.

See [verification](docs/VALIDATION.md) and [contribution guidance](CONTRIBUTING.md).

## Repository layout

```text
chatbot/          Active API, trip validation, conversation, provider boundary
web/              Buildless HTML, CSS, JavaScript workspace
tests/            Python behavior tests and JavaScript state tests
scripts/          Real-HTTP smoke check
docs/             Migration, API, frontend, verification, screenshots
legacy/           Unmodified historical implementation and model artifacts
ROADMAP.md        Prioritized product and engineering backlog
run.py            Supported Python 3.12 entry point
```

New implementation code is MIT licensed. Historical third-party material under
`legacy/` is excluded from that grant; its original notices and terms remain
applicable. See [LICENSE](LICENSE) and [third-party notes](THIRD_PARTY_NOTICES.md).
