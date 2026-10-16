"""Tests for operations shared by the CLI and graphical interface."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import context  # noqa: F401

from webwrap.operations import create_web_app, delete_web_app, open_web_app, update_web_app
from webwrap.paths import WebWrapPaths
from webwrap.services import AppStore, AppStoreError, DesktopEntryError


class CreateWebAppTests(unittest.TestCase):
    """Verify successful creation and multi-artifact rollback."""

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        root = Path(self.temporary.name)
        self.paths = WebWrapPaths(root, root / "applications")
        self.store = AppStore(self.paths.apps_file)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_create_persists_record_and_desktop_entry(self) -> None:
        app = create_web_app("Example", "https://example.com", self.paths, self.store)

        self.assertEqual(self.store.load(), [app])
        desktop = self.paths.applications_dir / f"webwrap-{app.id}.desktop"
        self.assertTrue(desktop.is_file())
        self.assertIn("Name=Example", desktop.read_text(encoding="utf-8"))

    def test_desktop_failure_rolls_back_record(self) -> None:
        error = DesktopEntryError("desktop failed")
        with patch("webwrap.operations.DesktopEntryService.create", side_effect=error):
            with self.assertRaisesRegex(DesktopEntryError, "desktop failed"):
                create_web_app("Example", "https://example.com", self.paths, self.store)

        self.assertEqual(self.store.load(), [])
        self.assertEqual(list(self.paths.applications_dir.glob("*.desktop")), [])

    def test_id_collision_preserves_existing_artifacts(self) -> None:
        first_icon = Path(self.temporary.name) / "first.png"
        first_icon.write_bytes(b"first")
        existing = create_web_app(
            "Existing",
            "https://existing.example",
            self.paths,
            self.store,
            icon=first_icon,
        )
        desktop = self.paths.applications_dir / f"webwrap-{existing.id}.desktop"
        original_desktop = desktop.read_text(encoding="utf-8")
        managed_icon = Path(existing.icon or "")

        second_icon = Path(self.temporary.name) / "second.png"
        second_icon.write_bytes(b"second")
        with patch("webwrap.operations.generate_app_id", return_value=existing.id):
            with self.assertRaisesRegex(AppStoreError, "already exists"):
                create_web_app(
                    "Collision",
                    "https://collision.example",
                    self.paths,
                    self.store,
                    icon=second_icon,
                )

        self.assertEqual(self.store.load(), [existing])
        self.assertEqual(desktop.read_text(encoding="utf-8"), original_desktop)
        self.assertEqual(managed_icon.read_bytes(), b"first")

    def test_failed_record_rollback_preserves_referenced_icon(self) -> None:
        source_icon = Path(self.temporary.name) / "source.png"
        source_icon.write_bytes(b"icon")
        desktop_error = DesktopEntryError("desktop failed")
        remove_error = AppStoreError("rollback failed")

        with (
            patch("webwrap.operations.DesktopEntryService.create", side_effect=desktop_error),
            patch.object(self.store, "remove", side_effect=remove_error),
            self.assertLogs("webwrap.operations", level="ERROR"),
        ):
            with self.assertRaisesRegex(DesktopEntryError, "desktop failed"):
                create_web_app(
                    "Example",
                    "https://example.com",
                    self.paths,
                    self.store,
                    icon=source_icon,
                )

        stored = self.store.load()
        self.assertEqual(len(stored), 1)
        self.assertEqual(Path(stored[0].icon or "").read_bytes(), b"icon")

    def test_update_preserves_identity_and_regenerates_desktop(self) -> None:
        app = create_web_app("Original", "https://example.com", self.paths, self.store)

        updated = update_web_app(
            app.id,
            "Updated",
            "https://updated.example",
            self.paths,
            self.store,
        )

        self.assertEqual(updated.id, app.id)
        self.assertEqual(self.store.load(), [updated])
        desktop = self.paths.applications_dir / f"webwrap-{app.id}.desktop"
        rendered = desktop.read_text(encoding="utf-8")
        self.assertIn("Name=Updated", rendered)
        self.assertIn("--app=https://updated.example", rendered)

    def test_update_failure_restores_original_record_and_desktop(self) -> None:
        app = create_web_app("Original", "https://example.com", self.paths, self.store)
        desktop = self.paths.applications_dir / f"webwrap-{app.id}.desktop"
        original_desktop = desktop.read_text(encoding="utf-8")

        with patch(
            "webwrap.operations.DesktopEntryService.update",
            side_effect=DesktopEntryError("update failed"),
        ):
            with self.assertRaisesRegex(DesktopEntryError, "update failed"):
                update_web_app(
                    app.id,
                    "Updated",
                    "https://updated.example",
                    self.paths,
                    self.store,
                )

        self.assertEqual(self.store.load(), [app])
        self.assertEqual(desktop.read_text(encoding="utf-8"), original_desktop)

    def test_open_uses_browser_service(self) -> None:
        app = create_web_app("Example", "https://example.com", self.paths, self.store)

        with patch("webwrap.operations.BrowserService.launch") as launch:
            self.assertEqual(open_web_app(app.id, self.paths, self.store), app)

        launch.assert_called_once_with(app)

    def test_delete_removes_managed_artifacts_but_preserves_profile(self) -> None:
        source_icon = Path(self.temporary.name) / "source.png"
        source_icon.write_bytes(b"icon")
        app = create_web_app(
            "Example",
            "https://example.com",
            self.paths,
            self.store,
            icon=source_icon,
            isolated_profile=True,
        )
        profile = self.paths.profiles_dir / app.id
        profile.mkdir(parents=True)
        (profile / "data").write_text("keep", encoding="utf-8")

        self.assertEqual(delete_web_app(app.id, self.paths, self.store), app)

        self.assertEqual(self.store.load(), [])
        self.assertFalse(Path(app.icon or "").exists())
        self.assertFalse(
            (self.paths.applications_dir / f"webwrap-{app.id}.desktop").exists()
        )
        self.assertEqual((profile / "data").read_text(encoding="utf-8"), "keep")

    def test_delete_failure_does_not_create_previously_missing_desktop(self) -> None:
        app = create_web_app("Example", "https://example.com", self.paths, self.store)
        desktop = self.paths.applications_dir / f"webwrap-{app.id}.desktop"
        desktop.unlink()

        with patch.object(self.store, "remove", side_effect=AppStoreError("remove failed")):
            with self.assertRaisesRegex(AppStoreError, "remove failed"):
                delete_web_app(app.id, self.paths, self.store)

        self.assertEqual(self.store.load(), [app])
        self.assertFalse(desktop.exists())
