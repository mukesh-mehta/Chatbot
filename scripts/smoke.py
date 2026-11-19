"""Check an already running app using only the Python standard library."""

import argparse
import json
import time
from urllib.error import URLError
from urllib.request import Request, urlopen


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:8000")
    args = parser.parse_args()
    for attempt in range(30):
        try:
            with urlopen(args.url + "/api/health", timeout=2) as response:
                assert json.load(response)["status"] == "ok"
            break
        except (URLError, ConnectionError, TimeoutError):
            if attempt == 29:
                raise
            time.sleep(1)
    with urlopen(args.url, timeout=5) as response:
        assert b"Your travel assistant" in response.read()
    request = Request(
        args.url + "/api/chat",
        data=json.dumps({"message": "Delhi to Mumbai tomorrow for 2 adults"}).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urlopen(request, timeout=5) as response:
        data = json.load(response)
    assert data["trip"]["origin"] == "DEL" and data["trip"]["adults"] == 2
    assert len(data["offers"]) == 3 and all(o["is_sample"] for o in data["offers"])
    print("HTTP health, workspace, conversation, and sample search passed.")


if __name__ == "__main__":
    main()
