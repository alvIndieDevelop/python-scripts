"""Tests for the WebWrap command-line interface."""

import contextlib
import io
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from webwrap.main import build_parser, main
from webwrap.paths import WebWrapPaths
from webwrap.services import AppStore


class MainTests(unittest.TestCase):
    """Verify parser behavior and lifecycle output without launching Chromium."""

    def test_parser_builds_expected_subcommands(self) -> None:
        parser = build_parser()
        create = parser.parse_args(
            ["create", "--name", "Chat", "--url", "https://example.com"]
        )
        self.assertEqual(create.command, "create")
        self.assertEqual(create.name, "Chat")
        self.assertFalse(create.isolated_profile)
        self.assertEqual(parser.parse_args(["list"]).command, "list")
        self.assertEqual(parser.parse_args(["open", "chat-1234abcd"]).id, "chat-1234abcd")
        self.assertEqual(
            parser.parse_args(["delete", "chat-1234abcd"]).id,
            "chat-1234abcd",
        )

    def test_parser_rejects_missing_subcommand_and_required_values(self) -> None:
        parser = build_parser()
        for arguments in (
            [],
            ["create", "--name", "Chat"],
            ["create", "--name", "Chat", "--url", "https://example.com", "--isolated-p"],
        ):
            with self.subTest(arguments=arguments), self.assertRaises(SystemExit) as raised:
                parser.parse_args(arguments)
            self.assertEqual(raised.exception.code, 2)

    def test_create_list_delete_lifecycle_uses_temporary_xdg_data(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = io.StringIO()
            with (
                patch.dict(os.environ, {"XDG_DATA_HOME": temporary}, clear=False),
                contextlib.redirect_stdout(output),
            ):
                self.assertEqual(
                    main(["create", "--name", "Test", "--url", "https://example.com"]),
                    0,
                )
                paths = WebWrapPaths.create()
                app = AppStore(paths.apps_file).load()[0]
                self.assertEqual(main(["list"]), 0)
                self.assertEqual(main(["delete", app.id]), 0)

            rendered = output.getvalue()
            self.assertIn(f"Created {app.id}\n", rendered)
            self.assertIn(f"{app.id}\tTest\thttps://example.com\n", rendered)
            self.assertIn(f"Deleted {app.id}\n", rendered)
            self.assertEqual(AppStore(paths.apps_file).load(), [])

    def test_invalid_input_returns_concise_error(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            errors = io.StringIO()
            with (
                patch.dict(os.environ, {"XDG_DATA_HOME": temporary}, clear=False),
                contextlib.redirect_stderr(errors),
            ):
                status = main(
                    ["create", "--name", "Test", "--url", "file:///tmp/example"]
                )

            self.assertEqual(status, 1)
            self.assertIn("webwrap: error:", errors.getvalue())
            self.assertNotIn("Traceback", errors.getvalue())
