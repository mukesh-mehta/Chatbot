"""A stateless Flask API serving the flight-planning workspace."""

import os
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from flask import Flask, jsonify, request, send_from_directory
from werkzeug.exceptions import HTTPException

from . import __version__
from .conversation import respond, result_for
from .providers import SampleFlightProvider
from .trips import AIRPORTS, InputError, Trip

WEB = Path(__file__).resolve().parents[1] / "web"


def create_app(config=None, *, provider=None):
    app = Flask(__name__, static_folder=str(WEB), static_url_path="/assets")
    app.config.update(
        MAX_CONTENT_LENGTH=8192,
        TRUSTED_HOSTS=os.environ.get("CHATBOT_ALLOWED_HOSTS", "localhost,127.0.0.1").split(","),
        TODAY=lambda: datetime.now(ZoneInfo("Asia/Kolkata")).date(),
    )
    app.config.update(config or {})
    provider = provider or SampleFlightProvider()

    @app.before_request
    def same_origin():
        origin = request.headers.get("Origin")
        if (
            request.method == "POST"
            and origin
            and origin.rstrip("/") != request.host_url.rstrip("/")
        ):
            return jsonify(error="Cross-origin requests are not supported."), 403

    @app.after_request
    def security_headers(response):
        response.headers.update(
            {
                "Content-Security-Policy": "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'",
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY",
                "Referrer-Policy": "no-referrer",
                "Cache-Control": "no-store",
            }
        )
        return response

    @app.errorhandler(InputError)
    def invalid_input(exc):
        return jsonify(error=str(exc), errors=exc.errors), 422

    @app.errorhandler(HTTPException)
    def http_error(exc):
        messages = {
            400: "Send valid JSON.",
            413: "Request is too large.",
            415: "Send application/json.",
        }
        return jsonify(error=messages.get(exc.code, exc.name)), exc.code

    def payload(allowed):
        data = request.get_json()
        if not isinstance(data, dict) or set(data) - set(allowed):
            raise InputError("Send a JSON object containing only supported fields.")
        return data

    @app.get("/")
    def index():
        return send_from_directory(WEB, "index.html")

    @app.get("/api/health")
    def health():
        return {"status": "ok", "version": __version__, "mode": "sample"}

    @app.get("/api/config")
    def public_config():
        today = app.config["TODAY"]()
        return {
            "airports": [{key: item[key] for key in ("code", "city", "name")} for item in AIRPORTS],
            "today": today.isoformat(),
            "max_date": (today + timedelta(days=365)).isoformat(),
            "timezone": "Asia/Kolkata",
            "mode": "sample",
            "max_message_length": 500,
        }

    @app.post("/api/chat")
    def chat():
        data = payload(("message", "trip"))
        message = data.get("message")
        if not isinstance(message, str) or not 1 <= len(message.strip()) <= 500:
            raise InputError("Write a message between 1 and 500 characters.")
        trip = Trip.from_payload(data.get("trip", {}))
        return respond(message.strip(), trip, provider, app.config["TODAY"]())

    @app.post("/api/search")
    def search():
        data = payload(("trip",))
        trip = Trip.from_payload(data.get("trip", {}))
        today = app.config["TODAY"]()
        errors = trip.errors(today, require_complete=True)
        if errors:
            raise InputError("Please check your trip details.", errors)
        return result_for(trip, provider, today, search=True)

    return app
