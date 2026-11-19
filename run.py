"""Start the supported Python 3.12 application: python run.py."""

import argparse

from waitress import serve

from chatbot.app import create_app


def main():
    parser = argparse.ArgumentParser(description="Run the flight chatbot prototype.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    print(f"Chatbot workspace: http://{args.host}:{args.port}", flush=True)
    serve(create_app(), host=args.host, port=args.port, threads=4, max_request_body_size=8192)


if __name__ == "__main__":
    main()
