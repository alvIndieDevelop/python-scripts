"""Tests for Chromium launch behavior."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from webwrap.models import WebApp
from webwrap.services.browser import BrowserError, BrowserService


class BrowserServiceTests(unittest.TestCase):
    """Verify shell-free arguments and profile creation timing."""

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.profiles = Path(self.temporary.name) / "profiles"
        self.shared = WebApp("chat-1234abcd", "Chat", "https://example.com/a?x=1")
        self.isolated = WebApp(
            "mail-1234abcd",
            "Mail",
            "https://mail.example.com",
            isolated_profile=True,
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_build_arguments_has_no_side_effects(self) -> None:
        service = BrowserService(self.profiles)
        self.assertEqual(
            service.build_arguments(self.shared, "/usr/bin/chromium"),
            ["/usr/bin/chromium", "--app=https://example.com/a?x=1"],
        )
        isolated_arguments = service.build_arguments(self.isolated, "chromium")
        self.assertEqual(
            isolated_arguments,
            [
                "chromium",
                "--app=https://mail.example.com",
                f"--user-data-dir={self.profiles / self.isolated.id}",
            ],
        )
        self.assertFalse(self.profiles.exists())

    def test_launch_resolves_binary_creates_profile_and_passes_a_list(self) -> None:
        popen = Mock(return_value=object())
        service = BrowserService(self.profiles, which=lambda _: "/usr/bin/chromium", popen=popen)
        service.launch(self.isolated)
        popen.assert_called_once_with(
            [
                "/usr/bin/chromium",
                "--app=https://mail.example.com",
                f"--user-data-dir={self.profiles / self.isolated.id}",
            ]
        )
        self.assertTrue((self.profiles / self.isolated.id).is_dir())

    def test_missing_browser_does_not_create_profile(self) -> None:
        service = BrowserService(self.profiles, which=lambda _: None)
        with self.assertRaises(BrowserError):
            service.launch(self.isolated)
        self.assertFalse(self.profiles.exists())

    def test_launch_os_errors_are_translated(self) -> None:
        popen = Mock(side_effect=PermissionError("denied"))
        service = BrowserService(self.profiles, which=lambda _: "/bin/chromium", popen=popen)
        with self.assertRaises(BrowserError):
            service.launch(self.shared)
