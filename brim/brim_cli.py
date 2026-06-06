import argparse
import json
import sys

import requests


def create_user(base_url, username, password):
    response = requests.post(
        f"{base_url.rstrip('/')}/api/users/",
        json={"username": username, "password": password},
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def main():
    parser = argparse.ArgumentParser(description="Brim administrative CLI")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    subparsers = parser.add_subparsers(dest="command", required=True)

    create_user_parser = subparsers.add_parser("create-user")
    create_user_parser.add_argument("username")
    create_user_parser.add_argument("password")

    args = parser.parse_args()

    if args.command == "create-user":
        result = create_user(args.base_url, args.username, args.password)
        print(json.dumps(result, indent=2))
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
