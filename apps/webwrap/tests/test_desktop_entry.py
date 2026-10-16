"""Tests for freedesktop launcher generation."""

import stat
import tempfile
import unittest
from pathlib import Path

from webwrap.models import WebApp
from webwrap.services.desktop_entry import DesktopEntryService
from webwrap.validation import ValidationError


class DesktopEntryServiceTests(unittest.TestCase):
    """Verify filenames, fields, escaping, and file operations."""

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.service = DesktopEntryService(self.root / "applications", self.root / "profiles")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_render_contains_required_fields_and_no_default_icon(self) -> None:
        app = WebApp("chat-1234abcd", "Chat App", "https://example.com/a%20path?q=100%25")
        rendered = self.service.render(app)
        self.assertIn("Name=Chat App\n", rendered)
        self.assertIn('Exec="chromium" "--app=https://example.com/a%%20path?q=100%%25"', rendered)
        self.assertNotIn("\nIcon=", rendered)
        for field in (
            "Terminal=false",
            "Type=Application",
            "Categories=Network;",
            "StartupNotify=true",
        ):
            self.assertIn(field, rendered)

    def test_render_escapes_strings_and_isolated_arguments(self) -> None:
        app = WebApp(
            "chat-1234abcd",
            'Chat "Back\\slash"',
            'https://example.com/a?quote="yes"&price=$5&code=`x`',
            icon="/tmp/an icon\\file.png",
            isolated_profile=True,
        )
        rendered = self.service.render(app)
        self.assertIn(r'Name=Chat "Back\\slash"', rendered)
        self.assertIn(r'Icon=/tmp/an icon\\file.png', rendered)
        self.assertIn(r'quote=\"yes\"&price=\$5&code=\`x\`', rendered)
        self.assertIn(f'"--user-data-dir={self.root / "profiles" / app.id}"', rendered)

    def test_create_update_delete_and_safe_filename(self) -> None:
        app = WebApp("chat-1234abcd", "Chat", "https://example.com")
        destination = self.service.create(app)
        self.assertEqual(destination.name, "webwrap-chat-1234abcd.desktop")
        self.assertEqual(stat.S_IMODE(destination.stat().st_mode), 0o644)
        updated = WebApp(app.id, "Updated", app.url)
        self.service.update(updated)
        self.assertIn("Name=Updated", destination.read_text(encoding="utf-8"))
        self.service.delete(app.id)
        self.service.delete(app.id)
        self.assertFalse(destination.exists())
        with self.assertRaises(ValidationError):
            self.service.path_for("../escape")
