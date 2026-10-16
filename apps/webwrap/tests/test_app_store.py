"""Tests for atomic application persistence."""

from __future__ import annotations

import json
import multiprocessing
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from webwrap.models import WebApp
from webwrap.services.app_store import AppStore, AppStoreError


def _create_in_process(
    path: str,
    record: dict[str, object],
    started: multiprocessing.synchronize.Event,
    finished: multiprocessing.synchronize.Event,
) -> None:
    """Create a record in a spawned process for lock serialization tests."""
    started.set()
    AppStore(Path(path)).create(WebApp.from_dict(record))
    finished.set()


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

    def test_save_does_not_replace_malformed_database(self) -> None:
        self.path.parent.mkdir(parents=True)
        self.path.write_text("{bad json", encoding="utf-8")

        with self.assertRaises(AppStoreError):
            self.store.save([self.app])

        self.assertEqual(self.path.read_text(encoding="utf-8"), "{bad json")

    def test_store_rejects_unmanaged_icon_references(self) -> None:
        external = replace(self.app, icon=f"{self.temporary.name}/{self.app.id}.png")
        wrong_stem = replace(
            self.app,
            icon=str(self.path.parent / "icons" / "other-1234abcd.png"),
        )
        for app in (external, wrong_stem):
            with self.subTest(icon=app.icon), self.assertRaises(AppStoreError):
                self.store.create(app)

    def test_loaded_unmanaged_icon_references_are_retained_and_rejected(self) -> None:
        self.path.parent.mkdir(parents=True)
        icons = (
            f"{self.temporary.name}/{self.app.id}.png",
            str(self.path.parent / "icons" / "other-1234abcd.png"),
        )
        for icon in icons:
            document = json.dumps(
                {"version": 1, "apps": [{**self.app.to_dict(), "icon": icon}]}
            )
            with self.subTest(icon=icon):
                self.path.write_text(document, encoding="utf-8")
                with self.assertRaises(AppStoreError):
                    self.store.load()
                self.assertEqual(self.path.read_text(encoding="utf-8"), document)

    def test_missing_managed_icon_is_valid(self) -> None:
        app = replace(
            self.app,
            icon=str(self.path.parent / "icons" / f"{self.app.id}.png"),
        )
        self.store.create(app)
        self.assertEqual(self.store.load(), [app])
        self.assertFalse(Path(app.icon or "").exists())

    def test_mutation_waits_for_lock_and_preserves_records(self) -> None:
        self.store.create(self.app)
        second = WebApp("docs-1234abcd", "Docs", "https://docs.example")
        context = multiprocessing.get_context("spawn")
        started = context.Event()
        finished = context.Event()

        with self.store._exclusive_lock():
            process = context.Process(
                target=_create_in_process,
                args=(str(self.path), second.to_dict(), started, finished),
            )
            process.start()
            self.assertTrue(started.wait(5))
            self.assertFalse(finished.wait(0.2))

        self.assertTrue(finished.wait(5))
        process.join(5)
        self.assertEqual(process.exitcode, 0)
        self.assertEqual(self.store.load(), [self.app, second])
