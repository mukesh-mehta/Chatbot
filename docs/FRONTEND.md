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
audit; see **FE-02** and **FE-03** in [the roadmap](../ROADMAP.md).

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

1. **Reliable interactions:** component boundaries, automated browser journeys,
   stale-response tests, draft persistence, focused announcements (FE-01–FE-04).
2. **Finding the right flight:** searchable airport combobox, date-range selection,
   filters, comparison, and expanded fare details (FE-05–FE-08).
3. **Returning to a trip:** accessible itinerary drawer, saved searches, expiration
   cues, localization, and share permissions (FE-09–FE-12).
4. **Production feedback:** measured performance, error recovery, design-system
   documentation, and telemetry that avoids message content (FE-13–FE-16).

Implement slices against the existing API contract first. Adopt a component
framework only if its benefits outweigh added build/dependency complexity; a
framework migration is not a prerequisite for keyboard access or reliable state.
