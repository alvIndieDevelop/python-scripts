"""Command-line interface for WebWrap."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from webwrap.operations import create_web_app, delete_web_app, open_web_app
from webwrap.paths import WebWrapPaths
from webwrap.services import (
    AppStore,
    AppStoreError,
    BrowserError,
    DesktopEntryError,
)
from webwrap.validation import ValidationError


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())
KNOWN_ERRORS = (AppStoreError, BrowserError, DesktopEntryError, ValidationError)
OPERATION_ERRORS = KNOWN_ERRORS + (OSError,)


def build_parser() -> argparse.ArgumentParser:
    """Build the WebWrap command-line parser."""
    parser = argparse.ArgumentParser(description="Create and launch Chromium web applications.")
    commands = parser.add_subparsers(dest="command", required=True)

    create = commands.add_parser("create", help="Create a web application")
    create.add_argument("--name", required=True, help="Application name")
    create.add_argument("--url", required=True, help="HTTP or HTTPS URL")
    create.add_argument("--icon", type=Path, help="Optional image file")
    create.add_argument(
        "--isolated-profile",
        action="store_true",
        help="Use a dedicated Chromium profile",
    )

    commands.add_parser("list", help="List configured web applications")
    open_command = commands.add_parser("open", help="Open a web application")
    open_command.add_argument("id", help="Stable application ID")
    delete = commands.add_parser("delete", help="Delete a web application")
    delete.add_argument("id", help="Stable application ID")
    return parser


def _create(args: argparse.Namespace, paths: WebWrapPaths, store: AppStore) -> None:
    app = create_web_app(
        args.name,
        args.url,
        paths,
        store,
        icon=args.icon,
        isolated_profile=args.isolated_profile,
    )
    print(f"Created {app.id}")


def _list(store: AppStore) -> None:
    apps = store.load()
    if not apps:
        print("No web apps configured.")
        return
    print("ID\tNAME\tURL")
    for app in apps:
        print(f"{app.id}\t{app.name}\t{app.url}")


def _open(app_id: str, paths: WebWrapPaths, store: AppStore) -> None:
    open_web_app(app_id, paths, store)


def _delete(app_id: str, paths: WebWrapPaths, store: AppStore) -> None:
    app = delete_web_app(app_id, paths, store)
    print(f"Deleted {app.id}")


def main(argv: list[str] | None = None) -> int:
    """Run the WebWrap CLI and return its process status."""
    parser = build_parser()
    args = parser.parse_args(argv)
    paths = WebWrapPaths.create()
    store = AppStore(paths.apps_file)
    try:
        if args.command == "create":
            _create(args, paths, store)
        elif args.command == "list":
            _list(store)
        elif args.command == "open":
            _open(args.id, paths, store)
        elif args.command == "delete":
            _delete(args.id, paths, store)
    except OPERATION_ERRORS as error:
        LOGGER.exception("WebWrap command failed")
        print(f"webwrap: error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
