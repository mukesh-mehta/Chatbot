import assert from "node:assert/strict";
import test from "node:test";
import {
  emptyTrip,
  escapeHTML,
  readyToSearch,
  restoreSession,
  sortedOffers,
  tripKey,
} from "../web/state.js";

test("document-like chat strings cannot become executable markup", () => {
  assert.equal(
    escapeHTML('<img src=x onerror="alert(1)">&'),
    "&lt;img src=x onerror=&quot;alert(1)&quot;&gt;&amp;",
  );
});
test("damaged or incompatible tab storage safely starts a new trip", () => {
  for (const raw of [
    null,
    "not-json",
    "{}",
    '{"version":9}',
    JSON.stringify({ version: 1, trip: { ...emptyTrip(), adults: true } }),
  ])
    assert.deepEqual(restoreSession(raw).trip, emptyTrip());
});
test("restored history is bounded and excludes invalid roles and objects", () => {
  const data = restoreSession(
    JSON.stringify({
      version: 1,
      trip: emptyTrip(),
      messages: [
        { role: "system", text: "not allowed" },
        ...Array.from({ length: 60 }, (_, i) => ({
          role: "user",
          text: String(i),
        })),
        { role: "assistant", text: { html: "bad" } },
      ],
    }),
  );
  assert.equal(data.messages.length, 40);
  assert.equal(data.messages[0].text, "20");
});
test("round trips require a return date before refreshing offers", () => {
  const trip = {
    ...emptyTrip(),
    origin: "DEL",
    destination: "BOM",
    departure_date: "2026-11-20",
  };
  assert.equal(readyToSearch(trip), true);
  assert.equal(readyToSearch({ ...trip, trip_type: "round_trip" }), false);
});
test("sorting does not mutate the original provider order", () => {
  const offers = [
    { id: "a", total_price: 400, duration_minutes: 70 },
    { id: "b", total_price: 200, duration_minutes: 95 },
  ];
  assert.equal(sortedOffers(offers, "price")[0].id, "b");
  assert.equal(sortedOffers(offers, "duration")[0].id, "a");
  assert.equal(offers[0].id, "a");
});
test("trip comparison is independent of JSON field order but detects route changes", () => {
  const trip = emptyTrip();
  const reordered = Object.fromEntries(Object.entries(trip).reverse());
  assert.equal(tripKey(trip), tripKey(reordered));
  assert.notEqual(tripKey(trip), tripKey({ ...trip, destination: "BOM" }));
});
