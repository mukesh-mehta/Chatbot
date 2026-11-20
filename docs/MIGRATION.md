# Python 3.12 migration

## Why this is a runtime replacement

The previous root `environment.yml` selected Python 3.6.13 and Windows-specific
Conda builds. Its pip requirements contained local `file:///C:/ci/...` and
`file:///opt/conda/...` paths, old scientific-library pins, and obsolete compatibility
backports. The entry point imported vendored Rasa modules and old serialized
models. `actions.py` also had an unfinished token assignment that prevented it
from being parsed as Python.

Updating a version number would not make that application runnable on Python 3.12.
The update therefore preserves all tracked original files under `legacy/` and
introduces a small supported runtime around the same flight-planning use case.
The archive is a reference, not a working compatibility layer.

| Previous entry or behavior | Current replacement |
| --- | --- |
| Root `run.py` loading Rasa models | Root `run.py` starts Waitress and the Flask application factory |
| Vendored Rasa NLU / dialogue manager | `chatbot/conversation.py` implements an explicit, limited slot parser |
| Tracker slots and global Messenger bot | Validated immutable `Trip`; caller supplies state on each request |
| Goibibo supplier calls | Injected `FlightProvider` interface with deterministic fictional data |
| Facebook-only conversation | Browser chat and structured trip editor |
| Model training scripts | Preserved under `legacy/`; no training is required for the active runtime |
| Windows environment export | Portable Python 3.12 requirements and a small Conda definition |
| Old public tunnel scripts | Archived; default server binds to loopback |

## Intentionally not migrated

Facebook callbacks, message signatures, user-profile lookups, old supplier
credentials, old model weights, machine-learning training, passenger names,
ticket issuance, and payment behavior are not supported by the new runtime.
Archived models, NLU examples, and third-party source are not inputs to the active
roadmap. Do not load the archived pickles into the modern application or include
the archive in a distributable source bundle without clearing its contents and
licensing file by file.

The current route parser is not equivalent to a trained Rasa pipeline. It is
deterministic and exposes its limits through clear fallback messages and an
editable form. Roadmap features **F03–F05** extend the local frontend, multi-city
trip representation, and fictional schedule search. AI model work and live
supplier integration are outside that development phase.

## Compatibility contract

- Active source is targeted and tested on Python 3.12.
- Dependency resolution is recorded for Python 3.12; no local machine paths remain
  in active requirement files.
- Linux and Windows Python 3.12 checks are configured in GitHub Actions.
- `tzdata` provides the India timezone on systems without an OS timezone database.
- The web UI uses native ES modules; there is no Python/JavaScript build coupling.
- The archive is excluded from test discovery, formatting, the Docker context,
  and the application's imports and static-file routes.
- The original archive move preserved file contents and repository history.
  The later credential cleanup is documented in [the archive notice](../legacy/ARCHIVE.md).

## Verification before dependency changes

Create a clean Python 3.12 environment, install the locked requirements, run the
unit tests, compile active modules, and start the HTTP server. Exercise at least
one multi-turn conversation, a round trip, an invalid date, and itinerary export.
The local checks require no container. The existing hosted CI additionally checks
both operating systems and optional container packaging; run its container smoke
check locally when Docker is available, or inspect the hosted result.

If re-resolving dependencies with `uv`, use:

```bash
uv pip compile pyproject.toml --python-version 3.12 --universal -o requirements.txt
uv pip compile requirements-dev.in --python-version 3.12 --universal -o requirements-dev.txt
```

## References

- [Flask installation and supported Python versions](https://flask.palletsprojects.com/en/stable/installation/)
- [Waitress platform and Python support](https://docs.pylonsproject.org/projects/waitress/en/stable/)
- [Python 3.12 changes and removals](https://docs.python.org/3.12/whatsnew/3.12.html)

These describe maintained dependencies and runtime changes. They do not establish
compatibility for the archived Rasa fork.
