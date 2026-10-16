"""Tests for the WebApp model boundary."""

import unittest

from webwrap.models import WebApp
from webwrap.validation import ValidationError


class WebAppTests(unittest.TestCase):
    """Verify serialization, defaults, and strict schema validation."""

    def test_round_trip_and_defaults(self) -> None:
        app = WebApp.from_dict(
            {"id": "chat-1234abcd", "name": "Chat", "url": "https://example.com"}
        )
        self.assertEqual(app.browser, "chromium")
        self.assertFalse(app.isolated_profile)
        self.assertIsNone(app.icon)
        self.assertEqual(WebApp.from_dict(app.to_dict()), app)

    def test_invalid_field_types_and_values_are_rejected(self) -> None:
        base = {"id": "chat-1234abcd", "name": "Chat", "url": "https://example.com"}
        invalid_records = (
            {**base, "id": "../chat"},
            {**base, "name": 1},
            {**base, "url": None},
            {**base, "icon": 1},
            {**base, "icon": ""},
            {**base, "icon": "relative.png"},
            {**base, "icon": "/tmp/bad\nicon.png"},
            {**base, "icon": "/tmp/icon.txt"},
            {**base, "browser": "firefox"},
            {**base, "isolated_profile": 1},
            {**base, "unknown": True},
        )
        for record in invalid_records:
            with self.subTest(record=record), self.assertRaises(ValidationError):
                WebApp.from_dict(record)

    def test_missing_absolute_icon_reference_is_allowed(self) -> None:
        icon = "/missing/chat-1234abcd.PNG"
        app = WebApp("chat-1234abcd", "Chat", "https://example.com", icon=icon)
        self.assertEqual(app.icon, icon)

    def test_missing_required_fields_and_non_objects_are_rejected(self) -> None:
        for record in ({"id": "chat-1234abcd"}, [], None):
            with self.subTest(record=record), self.assertRaises(ValidationError):
                WebApp.from_dict(record)
