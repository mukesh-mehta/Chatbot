import {
  emptyTrip,
  escapeHTML as esc,
  readyToSearch,
  restoreSession,
  sortedOffers,
  tripKey,
  welcome,
} from "./state.js";

const $ = (selector) => document.querySelector(selector);
const storageKey = "flight-chatbot:workspace:v1";
let restored;
try {
  restored = restoreSession(sessionStorage.getItem(storageKey));
} catch {
  restored = restoreSession(null);
}
const state = {
  ...restored,
  offers: [],
  config: null,
  busy: false,
  connected: false,
};
const emptyMarkup = $("#results").innerHTML;
const money = (value) =>
  new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(value);
const duration = (minutes) => `${Math.floor(minutes / 60)}h ${minutes % 60}m`;
const time = (iso) =>
  new Date(iso).toLocaleTimeString("en-GB", {
    timeZone: "Asia/Kolkata",
    hour: "2-digit",
    minute: "2-digit",
  });
const day = (iso) =>
  new Date(iso).toLocaleDateString("en-IN", {
    timeZone: "Asia/Kolkata",
    month: "short",
    day: "numeric",
  });
const city = (code) =>
  state.config?.airports.find((a) => a.code === code)?.city || code || "";

function save() {
  state.messages = state.messages.slice(-40);
  try {
    sessionStorage.setItem(
      storageKey,
      JSON.stringify({
        version: 1,
        trip: state.trip,
        messages: state.messages,
        selectedId: state.selectedId,
      }),
    );
  } catch {
    $("#privacy-note").textContent =
      "Tab storage is unavailable. Refreshing will clear this trip.";
  }
}

function renderMessages() {
  const container = $("#messages");
  const existing = [...container.children];
  const isPrefix =
    existing.length <= state.messages.length &&
    existing.every(
      (node, index) =>
        node.classList.contains(state.messages[index].role) &&
        node.querySelector(".message-body").textContent ===
          state.messages[index].text,
    );
  if (!isPrefix) container.replaceChildren();
  for (const message of state.messages.slice(isPrefix ? existing.length : 0)) {
    const article = document.createElement("div");
    article.className = `message ${message.role}`;
    const label = document.createElement("div");
    label.className = "message-label";
    label.textContent =
      message.role === "assistant" ? "Travel assistant" : "You";
    const body = document.createElement("div");
    body.className = "message-body";
    body.textContent = message.text;
    article.append(label, body);
    container.append(article);
  }
  container.scrollTop = container.scrollHeight;
}

function setBusy(busy) {
  state.busy = busy;
  for (const control of document.querySelectorAll(
    "#trip-form input, #trip-form select, #trip-form button, #chat-form button, #chat-form textarea, #suggestions button, #new-trip, #download-trip",
  ))
    control.disabled = busy || !state.connected;
  $("#return_date").disabled =
    busy || !state.connected || state.trip.trip_type === "one_way";
  $("#return_date").required = state.trip.trip_type === "round_trip";
  $("#sort").disabled = busy || state.offers.length === 0;
  document
    .querySelectorAll("[data-offer]")
    .forEach((button) => (button.disabled = busy));
  $("#working").hidden = !busy;
  $(".results-section").setAttribute("aria-busy", String(busy));
  $("#connection-status").textContent = !state.connected
    ? "Connecting to your workspace…"
    : busy
      ? "Working on your trip"
      : "Ready to help you plan";
}

function writeForm() {
  for (const key of Object.keys(emptyTrip())) {
    if (key === "trip_type")
      document.querySelector(
        `input[name="trip_type"][value="${state.trip.trip_type}"]`,
      ).checked = true;
    else $(`#${key}`).value = state.trip[key] ?? "";
  }
  updateFormMeta();
}

function readForm() {
  const data = Object.fromEntries(new FormData($("#trip-form")));
  return {
    origin: data.origin || null,
    destination: data.destination || null,
    departure_date: data.departure_date || null,
    return_date:
      data.trip_type === "round_trip" ? data.return_date || null : null,
    adults: Number(data.adults),
    cabin: data.cabin,
    trip_type: data.trip_type,
  };
}

function updateFormMeta() {
  const required = [
    "origin",
    "destination",
    "departure_date",
    ...(state.trip.trip_type === "round_trip" ? ["return_date"] : []),
  ];
  $("#trip-progress").textContent =
    `${required.filter((key) => state.trip[key]).length} of ${required.length} details ready`;
  $("#return_date").disabled = state.busy || state.trip.trip_type === "one_way";
  $("#return_date").required = state.trip.trip_type === "round_trip";
  $("#return_date").min =
    state.trip.departure_date || state.config?.today || "";
}

function showErrors(errors = {}) {
  const target = $("#form-errors");
  target.replaceChildren();
  document
    .querySelectorAll("[aria-invalid]")
    .forEach((el) => el.removeAttribute("aria-invalid"));
  for (const [key, message] of Object.entries(errors)) {
    const text = document.createElement("p");
    text.textContent = message;
    target.append(text);
    // Never turn an arbitrary server key into a selector.
    if (Object.hasOwn(emptyTrip(), key) && key !== "trip_type")
      document.getElementById(key)?.setAttribute("aria-invalid", "true");
  }
  target.hidden = !Object.keys(errors).length;
}

function renderResults() {
  const offers = sortedOffers(state.offers, $("#sort").value);
  $("#sort").disabled = state.busy || !offers.length;
  $("#results-caption").textContent = offers.length
    ? `${offers.length} sample itineraries · Illustrative prices only`
    : "A few possibilities for your next trip.";
  $("#results").innerHTML = offers.length
    ? offers
        .map(
          (offer) =>
            `<article class="flight-card ${offer.id === state.selectedId ? "selected" : ""}"><div class="flight-top"><span class="airline-mark" aria-hidden="true">${esc(offer.airline.slice(0, 1))}</span><div><h3 class="airline-name">${esc(offer.airline)}</h3><span class="flight-number">${esc(offer.flight_number)} · Sample airline</span></div><div class="price"><strong>${money(offer.total_price)}</strong><span>total for ${offer.adults} adult${offer.adults === 1 ? "" : "s"}</span></div></div>${offer.legs.map((leg, index) => `<div class="leg"><div><span class="flight-time">${time(leg.departure)}</span><span class="airport-code">${esc(leg.origin)} · ${day(leg.departure)}</span></div><div class="leg-meta">${duration(leg.duration_minutes)}<div class="route-line"></div>${index === 0 ? "Outbound" : "Return"} · Nonstop</div><div class="leg-end"><span class="flight-time">${time(leg.arrival)}</span><span class="airport-code">${esc(leg.destination)} · ${day(leg.arrival)}</span></div></div>`).join("")}<div class="flight-footer"><p>${esc(offer.cabin === "business" ? "Business" : "Economy")} · ${offer.legs.length === 2 ? "Round trip" : "One way"}<br>No live availability</p><button class="button secondary" type="button" data-offer="${esc(offer.id)}" aria-label="Save ${esc(offer.airline)} itinerary" aria-pressed="${offer.id === state.selectedId}" ${state.busy ? "disabled" : ""}>${offer.id === state.selectedId ? "Itinerary saved" : "Save itinerary"}</button></div></article>`,
        )
        .join("")
    : emptyMarkup;
  const selected = state.offers.find((offer) => offer.id === state.selectedId);
  $("#saved-trip").hidden = !selected;
  if (selected)
    $("#saved-description").textContent =
      `${city(state.trip.origin)} to ${city(state.trip.destination)} · ${selected.airline} · ${money(selected.total_price)}`;
}

async function api(path, body) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 15000);
  try {
    const response = await fetch(path, {
      method: body ? "POST" : "GET",
      headers: body ? { "Content-Type": "application/json" } : {},
      body: body ? JSON.stringify(body) : undefined,
      signal: controller.signal,
    });
    const data = await response.json();
    if (!response.ok)
      throw Object.assign(
        new Error(data.error || "The request could not be completed."),
        { fields: data.errors },
      );
    return data;
  } catch (error) {
    if (
      error.fields ||
      error.message?.startsWith("Please") ||
      error.message?.startsWith("Choose")
    )
      throw error;
    throw new Error(
      "Couldn't reach the workspace. Your input is still here. Check the connection and try again.",
    );
  } finally {
    clearTimeout(timeout);
  }
}

function applyResult(result) {
  const changed = tripKey(state.trip) !== tripKey(result.trip);
  state.trip = result.trip;
  if (result.search_performed) state.offers = result.offers;
  else if (changed || Object.keys(result.errors).length) state.offers = [];
  if (!state.offers.some((offer) => offer.id === state.selectedId))
    state.selectedId = null;
  writeForm();
  showErrors(result.errors);
  renderResults();
  save();
}

async function sendMessage(message, clearInput = false) {
  if (state.busy || !state.connected || !message.trim()) return;
  setBusy(true);
  $("#connection-error").hidden = true;
  try {
    const result = await api("/api/chat", {
      message: message.trim(),
      trip: state.trip,
    });
    state.messages.push(
      { role: "user", text: message.trim() },
      { role: "assistant", text: result.reply },
    );
    applyResult(result);
    renderMessages();
    if (clearInput) $("#message").value = "";
  } catch (error) {
    reportError(error);
  } finally {
    setBusy(false);
    if (clearInput) $("#message").focus();
  }
}

function reportError(error) {
  $("#connection-error").textContent = error.message;
  $("#connection-error").hidden = false;
  if (error.fields) {
    showErrors(error.fields);
    document.querySelector('[aria-invalid="true"]')?.focus();
  }
}

async function search(silent = false) {
  if (state.busy || !state.connected) return;
  setBusy(true);
  $("#connection-error").hidden = true;
  try {
    const result = await api("/api/search", { trip: state.trip });
    if (!silent)
      state.messages.push(
        {
          role: "user",
          text: `Find ${state.trip.trip_type === "round_trip" ? "round-trip" : "one-way"} flights from ${city(state.trip.origin)} to ${city(state.trip.destination)} on ${state.trip.departure_date}.`,
        },
        { role: "assistant", text: result.reply },
      );
    applyResult(result);
    renderMessages();
  } catch (error) {
    state.offers = [];
    state.selectedId = null;
    renderResults();
    reportError(error);
  } finally {
    setBusy(false);
  }
}

$("#chat-form").addEventListener("submit", (event) => {
  event.preventDefault();
  sendMessage($("#message").value, true);
});
$("#message").addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey && !event.isComposing) {
    event.preventDefault();
    if (!state.busy) $("#chat-form").requestSubmit();
  }
});
$("#suggestions").addEventListener("click", (event) => {
  const button = event.target.closest("[data-prompt]");
  if (button) sendMessage(button.dataset.prompt);
});
$("#trip-form").addEventListener("change", () => {
  state.trip = readForm();
  if (state.trip.trip_type === "one_way") $("#return_date").value = "";
  state.offers = [];
  state.selectedId = null;
  updateFormMeta();
  showErrors();
  renderResults();
  save();
});
$("#trip-form").addEventListener("submit", (event) => {
  event.preventDefault();
  state.trip = readForm();
  search();
});
$("#swap-airports").addEventListener("click", () => {
  [state.trip.origin, state.trip.destination] = [
    state.trip.destination,
    state.trip.origin,
  ];
  state.offers = [];
  state.selectedId = null;
  writeForm();
  showErrors();
  renderResults();
  save();
});
$("#sort").addEventListener("change", renderResults);
$("#results").addEventListener("click", (event) => {
  const button = event.target.closest("[data-offer]");
  if (!button || state.busy) return;
  state.selectedId = button.dataset.offer;
  renderResults();
  save();
  $("#saved-title").setAttribute("tabindex", "-1");
  $("#saved-title").focus();
});
$("#download-trip").addEventListener("click", () => {
  const selected = state.offers.find((offer) => offer.id === state.selectedId);
  if (!selected) return;
  const blob = new Blob(
    [
      JSON.stringify(
        {
          schema_version: 1,
          mode: "sample",
          notice:
            "Fictional itinerary. No reservation or payment has been made.",
          trip: state.trip,
          itinerary: selected,
        },
        null,
        2,
      ),
    ],
    { type: "application/json" },
  );
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "chatbot-sample-itinerary.json";
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
});
$("#new-trip").addEventListener("click", () => $("#reset-dialog").showModal());
$("#reset-dialog").addEventListener("close", () => {
  if ($("#reset-dialog").returnValue !== "confirm") return;
  state.trip = emptyTrip();
  state.messages = [{ role: "assistant", text: welcome }];
  state.offers = [];
  state.selectedId = null;
  $("#message").value = "";
  $("#connection-error").hidden = true;
  writeForm();
  showErrors();
  renderMessages();
  renderResults();
  save();
  $("#message").focus();
});

renderMessages();
setBusy(false);
try {
  state.config = await api("/api/config");
  for (const key of ["origin", "destination"])
    for (const airport of state.config.airports) {
      const option = document.createElement("option");
      option.value = airport.code;
      option.textContent = `${airport.city} (${airport.code})`;
      $(`#${key}`).append(option);
    }
  for (const key of ["departure_date", "return_date"]) {
    $(`#${key}`).min = state.config.today;
    $(`#${key}`).max = state.config.max_date;
  }
  state.connected = true;
  writeForm();
  setBusy(false);
  if (readyToSearch(state.trip)) await search(true);
} catch (error) {
  reportError(error);
  $("#connection-status").textContent =
    "Connection unavailable · reload to retry";
}
