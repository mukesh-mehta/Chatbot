export const emptyTrip = () => ({
  origin: null,
  destination: null,
  departure_date: null,
  return_date: null,
  adults: 1,
  cabin: "economy",
  trip_type: "one_way",
});
export const welcome =
  "Hi there. Tell me your route and dates, and we’ll put a trip together. You can also use the trip editor. All flight options here are fictional samples.";

export function escapeHTML(value) {
  return String(value ?? "").replace(
    /[&<>"']/g,
    (char) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[
        char
      ],
  );
}

export function tripKey(trip) {
  return JSON.stringify(
    Object.keys(emptyTrip()).map((key) => trip[key] ?? null),
  );
}

export function restoreSession(raw) {
  const fresh = {
    trip: emptyTrip(),
    messages: [{ role: "assistant", text: welcome }],
    selectedId: null,
  };
  try {
    const data = JSON.parse(raw);
    if (data?.version !== 1 || !data.trip || typeof data.trip !== "object")
      return fresh;
    const t = data.trip;
    for (const key of [
      "origin",
      "destination",
      "departure_date",
      "return_date",
    ]) {
      if (t[key] !== null && (typeof t[key] !== "string" || t[key].length > 32))
        return fresh;
    }
    if (
      !Number.isInteger(t.adults) ||
      t.adults < 1 ||
      t.adults > 9 ||
      !["economy", "business"].includes(t.cabin) ||
      !["one_way", "round_trip"].includes(t.trip_type)
    )
      return fresh;
    const trip = Object.fromEntries(
      Object.keys(emptyTrip()).map((key) => [key, t[key]]),
    );
    if (trip.trip_type === "one_way") trip.return_date = null;
    const messages = Array.isArray(data.messages)
      ? data.messages
          .filter(
            (m) =>
              m &&
              ["user", "assistant"].includes(m.role) &&
              typeof m.text === "string" &&
              m.text.length <= 1500,
          )
          .slice(-40)
          .map((m) => ({ role: m.role, text: m.text }))
      : [];
    return {
      trip,
      messages: messages.length ? messages : fresh.messages,
      selectedId:
        typeof data.selectedId === "string" &&
        /^[a-f0-9]{16}$/.test(data.selectedId)
          ? data.selectedId
          : null,
    };
  } catch {
    return fresh;
  }
}

export function sortedOffers(offers, order) {
  const copy = [...offers];
  if (order === "price") copy.sort((a, b) => a.total_price - b.total_price);
  if (order === "duration")
    copy.sort((a, b) => a.duration_minutes - b.duration_minutes);
  return copy;
}

export function readyToSearch(trip) {
  return Boolean(
    trip.origin &&
      trip.destination &&
      trip.departure_date &&
      (trip.trip_type === "one_way" || trip.return_date),
  );
}
