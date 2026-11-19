# Frontend guide

## Current experience

The workspace is a buildless HTML/CSS/JavaScript app served by Flask. Desktop uses
a conversation alongside a trip editor and flight options. Below 800px, the same
controls stack into a single column. Browser-native inputs provide date selection
and form constraints; the backend remains authoritative for validation.

`web/app.js` owns DOM events, requests, rendering, and tab persistence.
`web/state.js` contains testable state normalization, trip comparison, sorting,
and escaping helpers. `web/styles.css` holds the visual system and responsive
rules. There are no external fonts, analytics, runtime libraries, or CDN assets.

## Behavior delivered

- Chat suggestions and typed messages feed the same API.
- Enter submits a message; Shift+Enter adds a line; input-method composition is
  allowed to finish without accidentally sending.
- The form synchronizes to recognized chat updates; form edits become the context
  for the next message.
- Changing a trip clears old offers and the selected itinerary.
- One-way mode clears and disables the return date.
- Requests temporarily disable conflicting interactions and time out after
  15 seconds. Failed messages remain in the composer for another attempt.
- Sorting changes presentation without mutating provider order.
- A saved itinerary is a local selection, visibly separate from a real reservation.
- Downloaded JSON includes the trip, selected sample itinerary, and a sample-data
  notice. It excludes the conversation transcript.
- Session storage keeps at most 40 messages and a trip/selected ID. Reloading
  searches the current trip again; stale or invalid input is revalidated.
- Clearing a trip requires a local confirmation dialog. No server data is deleted.

## Accessibility implemented and not yet certified

The interface has semantic landmarks, labels, a skip link, keyboard-visible focus,
a live conversation region, inline validation, native radio/date/select controls,
and reduced-motion handling. These are implementation choices, not a formal
accessibility certification. Screen-reader behavior across browsers, touch-target
sizes, contrast, zoom, and mobile keyboard behavior still require a systematic
audit; see **F03** in [the roadmap](../ROADMAP.md).

## State and privacy boundaries

The server receives message text and current trip fields to calculate a response,
then retains neither in an application database. Production reverse proxies and
infrastructure may have their own logs and need explicit policies. The frontend
does not send messages to an AI provider or flight supplier.

Tab storage is best-effort local convenience, not encryption or a user account.
Invalid stored JSON is discarded. Closing the tab normally ends its session;
browser session restoration or tab duplication can preserve/copy data. Clearing
the trip is the reliable in-app reset. Do not enter passport, payment, or other
sensitive personal data.

## Frontend development

```bash
npm ci --ignore-scripts
npm test
npm run format:check
npm run format
```

The browser must be reloaded after editing static files; there is no bundler/hot
reload process. Keep user/provider strings out of HTML interpolation unless
escaped. Use text nodes for conversation content.

## Next frontend delivery slices

All slices below are **planned**. They use local services, fictional schedules,
and synthetic test identities. The current interface does not yet expose these
expanded workflows.

| Slice | Roadmap IDs | Screens and interactions | Completion evidence |
| --- | --- | --- | --- |
| Durable workspace | F01, F03 | Named trip list, pagination, create/rename/duplicate/archive, recoverable drafts | Reopen after restart; failed saves preserve input; late responses cannot change another trip |
| Local identities and safe edits | F02, F03, F07 | Login/logout, session expiry, account-scoped drafts, saved-versus-draft conflict view | Isolated user contexts; denied access; two-tab conflict and lost-response retry journeys |
| Multi-city planning | F04, F05 | Searchable airport combobox, leg controls, timezone details, schedule-version display | Keyboard selection; leg reorder; overnight and date-boundary cases; unsupported-search feedback |
| Comparison and portable files | F06, F09 | Combined filters, three-option comparison, import preview, printable itinerary | Correct totals; empty states; atomic import failure; escaped output; v0.2 migration |
| Shared plans and simulated changes | F08, F10 | Role/member controls, revision history, scenario playback, alert drawer | Revocation during an open edit; history restoration; duplicate-event and restart handling |
| Recovery and diagnostics | F11, F12 | Backup/restore outcomes, cleanup status, local health and workload reports | Corrupt-backup feedback; recoverable interruption; measured limits without exposing draft content |

Every new screen needs loading, empty, validation, permission-loss, and retry
states where applicable. Preserve keyboard focus, use text as well as color for
status, and keep sample-data labels visible. A saved selection or simulated
cancellation must never look like a real ticket or supplier action.

## Browser acceptance plan

Use the running local API with temporary databases and isolated browser contexts.
Select a browser executable available in the target environment; installation of
a new browser during an offline session is not a prerequisite.

- Cover complete milestone journeys through visible controls, including reload,
  session expiry, denied requests, delayed replies, and connection recovery.
- Check the primary flows by keyboard, at 200% zoom, and at a 390px viewport.
  Review screen-reader announcements and contrast alongside automated checks.
- Prove that an older response cannot overwrite a newer draft or another trip;
  switching users must not expose the previous user's stored drafts.
- Test real conflict responses and retry identities against the API, alongside
  injected delays and fixture failures. Do not replace every backend interaction
  with a browser mock and then claim integration coverage.
- Run the final workflow with external traffic blocked and loopback available.
  Record that setup and any limits; browser helper tests alone do not prove it.

Implement slices against the existing API contract first. Adopt a component
framework only if its benefits outweigh added build/dependency complexity; a
framework migration is not a prerequisite for keyboard access or reliable state.
