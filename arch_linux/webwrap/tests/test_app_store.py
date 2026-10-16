"""Tests for atomic application persistence."""

import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

import context  # noqa: F401

from webwrap.models import WebApp
from webwrap.services.app_store import AppStore, AppStoreError


class AppStoreTests(unittest.TestCase):
    """Verify CRUD behavior and corrupt-data handling."""

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.path = Path(self.temporary.name) / "nested" / "apps.json"
        self.store = AppStore(self.path)
        self.app = WebApp("chat-1234abcd", "Chat", "https://example.com")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_missing_database_returns_empty_without_creating_it(self) -> None:
        self.assertEqual(self.store.load(), [])
        self.assertFalse(self.path.exists())

    def test_create_update_remove_round_trip(self) -> None:
        self.store.create(self.app)
        self.assertEqual(self.store.get(self.app.id), self.app)
        updated = replace(self.app, name="Updated")
        self.store.update(updated)
        self.assertEqual(self.store.load(), [updated])
        self.assertEqual(self.store.remove(updated.id), updated)
        self.assertEqual(self.store.load(), [])
        with self.path.open(encoding="utf-8") as input_file:
            self.assertEqual(json.load(input_file), {"version": 1, "apps": []})

    def test_duplicate_and_missing_records_fail(self) -> None:
        self.store.create(self.app)
        with self.assertRaises(AppStoreError):
            self.store.create(self.app)
        with self.assertRaises(AppStoreError):
            self.store.update(WebApp("other-1234abcd", "Other", "https://other.test"))
        with self.assertRaises(AppStoreError):
            self.store.remove("missing-1234abcd")

    def test_malformed_and_invalid_documents_are_retained(self) -> None:
        self.path.parent.mkdir(parents=True)
        documents = (
            "{bad json",
            json.dumps({"version": 2, "apps": []}),
            json.dumps({"version": 1, "apps": "bad"}),
            json.dumps({"version": 1, "apps": [self.app.to_dict(), self.app.to_dict()]}),
            json.dumps({"version": 1, "apps": [{**self.app.to_dict(), "id": "../bad"}]}),
        )
        for document in documents:
            with self.subTest(document=document):
                self.path.write_text(document, encoding="utf-8")
                with self.assertRaises(AppStoreError):
                    self.store.load()
                self.assertEqual(self.path.read_text(encoding="utf-8"), document)
