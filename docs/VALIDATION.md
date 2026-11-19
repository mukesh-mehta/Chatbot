# Verification record

Verified on 19 November 2026. These checks cover the active application; the
historical code under `legacy/` is intentionally outside the compatibility claim.

## Local automated checks

- **Python 3.12.3:** 46 Python tests passed, covering multi-turn planning, corrections,
  reset, airport aliases, unknown routes, strict input types, date boundaries,
  same-day return ordering, total prices, request limits, headers, and independent
  conversations.
- **Node 18:** six JavaScript tests passed for escaping, corrupted/bounded session
  state, round-trip completeness, sorting, and trip-change detection.
- Active Python source compiled successfully; installed dependencies passed
  `pip check`; Python lint and Python/frontend formatting checks passed.
- A real HTTP smoke check exercised health, HTML delivery, chat, and search.
- A non-root, read-only Python **3.12.16** container served the application and
  passed the same HTTP smoke check.

The CI workflow repeats Python checks on Linux and Windows with Python 3.12,
frontend checks with Node 20, and a separately built container smoke check.
Use the repository's Actions page for the exact commit's remote results.

## Browser checks

- Submitted a route through both a suggestion and typed Enter-key submission.
- Verified route/date/adult fields synchronized into the editor.
- Changed adult count and confirmed result totals changed.
- Sorted by lowest price and saved a specific itinerary.
- Downloaded the JSON through the UI and checked its trip and sample-data fields.
- Reloaded and observed the trip, conversation, and selected itinerary restored.
- Submitted an impossible calendar date and observed field feedback plus removal
  of outdated results/saved selection.
- Used the form to create a round trip with outbound and return legs.
- Used the confirmation dialog to clear the current trip.
- Inspected desktop and 390px-wide layouts; no horizontal overflow was observed
  at the tested mobile width. Saved [desktop](workspace.jpg) and
  [mobile](mobile.jpg) screenshots.
- The final browser check reported no JavaScript console errors.

## Archive preservation

All 211 previously tracked files were moved under `legacy/`. Their Git content
hashes were compared with the starting commit and matched. The new archive notice
is additional documentation; original file contents and existing Git history
were preserved.

## Limits of this verification

No live supplier, messaging-channel, LLM, booking, payment, or cloud-hosting
integration was attempted. No model accuracy benchmark, capacity benchmark,
formal accessibility audit, or independent security assessment is claimed.
The optional Conda definition was updated but not executed with a Conda client.
Browser checks were interactive; automated cross-browser coverage is roadmap work.
