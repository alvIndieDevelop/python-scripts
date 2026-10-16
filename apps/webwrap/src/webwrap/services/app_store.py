"""Atomic JSON persistence for WebWrap applications."""

from __future__ import annotations

import json
import os
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from fcntl import LOCK_EX, flock
from pathlib import Path

from webwrap.models import WebApp
from webwrap.validation import ValidationError, validate_app_id


class AppStoreError(RuntimeError):
    """Raised when the application database cannot be read or changed."""


class AppStore:
    """Persist WebApp records in a small versioned JSON document."""

    VERSION = 1

    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self.lock_path = self.path.with_name(f".{self.path.stem}.lock")

    def load(self) -> list[WebApp]:
        """Load and validate all stored applications."""
        return self._load_unlocked()

    def _load_unlocked(self) -> list[WebApp]:
        """Load records without acquiring the mutation lock."""
        try:
            with self.path.open("r", encoding="utf-8") as input_file:
                document = json.load(input_file)
        except FileNotFoundError:
            return []
        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            raise AppStoreError("Application database contains malformed JSON.") from error
        except OSError as error:
            raise AppStoreError(f"Cannot read application database: {error}") from error

        if not isinstance(document, dict) or set(document) != {"version", "apps"}:
            raise AppStoreError("Application database has an invalid schema.")
        if type(document["version"]) is not int or document["version"] != self.VERSION:
            raise AppStoreError("Application database version is not supported.")
        if not isinstance(document["apps"], list):
            raise AppStoreError("Application database has an invalid apps list.")

        try:
            apps = [WebApp.from_dict(record) for record in document["apps"]]
        except (ValidationError, TypeError) as error:
            message = f"Application database contains an invalid record: {error}"
            raise AppStoreError(message) from error
        identifiers = [app.id for app in apps]
        if len(set(identifiers)) != len(identifiers):
            raise AppStoreError("Application database contains duplicate IDs.")
        self._validate_icon_ownership(apps)
        return apps

    def save(self, apps: list[WebApp]) -> None:
        """Atomically replace the database with validated records."""
        with self._exclusive_lock():
            self._load_unlocked()
            self._save_unlocked(apps)

    def _save_unlocked(self, apps: list[WebApp]) -> None:
        """Replace the database while the caller holds the mutation lock."""
        identifiers = [app.id for app in apps]
        if len(set(identifiers)) != len(identifiers):
            raise AppStoreError("Cannot save duplicate application IDs.")
        self._validate_icon_ownership(apps)
        document = {"version": self.VERSION, "apps": [app.to_dict() for app in apps]}
        temporary: Path | None = None
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            descriptor, temporary_name = tempfile.mkstemp(
                dir=self.path.parent,
                prefix=f".{self.path.name}-",
                text=True,
            )
            temporary = Path(temporary_name)
            with os.fdopen(descriptor, "w", encoding="utf-8") as output:
                json.dump(document, output, ensure_ascii=False, indent=2)
                output.write("\n")
                output.flush()
                os.fsync(output.fileno())
            os.replace(temporary, self.path)
        except OSError as error:
            raise AppStoreError(f"Cannot save application database: {error}") from error
        finally:
            if temporary is not None:
                try:
                    temporary.unlink(missing_ok=True)
                except OSError:
                    pass

    def _validate_icon_ownership(self, apps: list[WebApp]) -> None:
        """Ensure persisted icons belong to this store's managed icon directory."""
        managed_dir = (self.path.parent / "icons").resolve(strict=False)
        for app in apps:
            if app.icon is None:
                continue
            icon = Path(app.icon)
            try:
                icon_parent = icon.resolve(strict=False).parent
            except OSError as error:
                raise AppStoreError(f"Cannot validate stored icon path: {error}") from error
            if icon_parent != managed_dir or icon.stem != app.id:
                raise AppStoreError(
                    f"Application '{app.id}' has an icon outside managed storage."
                )

    @contextmanager
    def _exclusive_lock(self) -> Iterator[None]:
        """Hold the stable sibling lock across one complete mutation."""
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.lock_path.open("a+b") as lock_file:
                flock(lock_file.fileno(), LOCK_EX)
                yield
        except OSError as error:
            raise AppStoreError(f"Cannot lock application database: {error}") from error

    def get(self, app_id: str) -> WebApp:
        """Return one application by exact stable ID."""
        validate_app_id(app_id)
        for app in self.load():
            if app.id == app_id:
                return app
        raise AppStoreError(f"Application '{app_id}' does not exist.")

    def create(self, app: WebApp) -> None:
        """Add a new application, rejecting duplicate IDs."""
        with self._exclusive_lock():
            apps = self._load_unlocked()
            if any(existing.id == app.id for existing in apps):
                raise AppStoreError(f"Application '{app.id}' already exists.")
            apps.append(app)
            self._save_unlocked(apps)

    def update(self, app: WebApp) -> None:
        """Replace an existing application by stable ID."""
        with self._exclusive_lock():
            apps = self._load_unlocked()
            for index, existing in enumerate(apps):
                if existing.id == app.id:
                    apps[index] = app
                    self._save_unlocked(apps)
                    return
        raise AppStoreError(f"Application '{app.id}' does not exist.")

    def remove(self, app_id: str) -> WebApp:
        """Remove and return an application by stable ID."""
        validate_app_id(app_id)
        with self._exclusive_lock():
            apps = self._load_unlocked()
            for index, app in enumerate(apps):
                if app.id == app_id:
                    removed = apps.pop(index)
                    self._save_unlocked(apps)
                    return removed
        raise AppStoreError(f"Application '{app_id}' does not exist.")
