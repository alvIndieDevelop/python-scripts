"""Tests for untrusted input validation."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import context  # noqa: F401

from webwrap.validation import (
    ValidationError,
    copy_managed_icon,
    generate_app_id,
    validate_app_id,
    validate_icon_path,
    validate_name,
    validate_url,
)


class ValidationTests(unittest.TestCase):
    """Exercise names, URLs, IDs, and icon handling."""

    def test_name_is_trimmed_and_controls_are_rejected(self) -> None:
        self.assertEqual(validate_name("  Chat GPT  "), "Chat GPT")
        for invalid in ("", "   ", "bad\nname", "bad\x00name"):
            with self.subTest(invalid=invalid), self.assertRaises(ValidationError):
                validate_name(invalid)

    def test_valid_urls_are_preserved(self) -> None:
        for url in ("https://example.com/a?b=1", "http://localhost:8080"):
            with self.subTest(url=url):
                self.assertEqual(validate_url(url), url)

    def test_invalid_urls_are_rejected(self) -> None:
        invalid_urls = (
            "ftp://example.com",
            "https:///missing-host",
            "https://example.com/a b",
            "https://example.com:invalid",
            "https://example.com:70000",
        )
        for url in invalid_urls:
            with self.subTest(url=url), self.assertRaises(ValidationError):
                validate_url(url)

    def test_generated_ids_use_slug_fallback_and_unique_suffix(self) -> None:
        with patch("webwrap.validation.uuid.uuid4") as mocked_uuid:
            mocked_uuid.return_value.hex = "a1b2c3d4ffff"
            self.assertEqual(generate_app_id("Café Chat"), "cafe-chat-a1b2c3d4")
            self.assertEqual(generate_app_id("聊天"), "app-a1b2c3d4")
        self.assertNotEqual(generate_app_id("Chat"), generate_app_id("Chat"))

    def test_unsafe_ids_are_rejected(self) -> None:
        self.assertEqual(validate_app_id("chat-a1b2c3d4"), "chat-a1b2c3d4")
        for app_id in ("../chat", "Chat", "chat_1", "-chat", "chat/"):
            with self.subTest(app_id=app_id), self.assertRaises(ValidationError):
                validate_app_id(app_id)

    def test_icons_are_validated_and_copied_atomically(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source.PNG"
            source.write_bytes(b"image")
            self.assertEqual(validate_icon_path(source), source)
            copied = copy_managed_icon(source, root / "icons", "chat-1234abcd")
            self.assertEqual(copied.name, "chat-1234abcd.png")
            self.assertEqual(copied.read_bytes(), b"image")
            unsupported = root / "icon.txt"
            unsupported.write_text("not an image", encoding="utf-8")
            with self.assertRaises(ValidationError):
                validate_icon_path(unsupported)
