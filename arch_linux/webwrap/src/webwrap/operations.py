"""Shared application operations used by the CLI and graphical interface."""

from __future__ import annotations

import logging
import os
from dataclasses import replace
from pathlib import Path
from uuid import uuid4

from webwrap.models import WebApp
from webwrap.paths import WebWrapPaths
from webwrap.services import (
    AppStore,
    AppStoreError,
    BrowserService,
    DesktopEntryError,
    DesktopEntryService,
)
from webwrap.validation import (
    SUPPORTED_ICON_SUFFIXES,
    ValidationError,
    copy_managed_icon,
    generate_app_id,
    validate_icon_path,
    validate_name,
    validate_url,
)


LOGGER = logging.getLogger(__name__)
CREATE_ERRORS = (AppStoreError, DesktopEntryError, ValidationError, OSError)
MUTATION_ERRORS = (AppStoreError, DesktopEntryError, ValidationError, OSError)


def create_web_app(
    name: str,
    url: str,
    paths: WebWrapPaths,
    store: AppStore,
    icon: Path | None = None,
    isolated_profile: bool = False,
) -> WebApp:
    """Create a web app and roll back its artifacts if any step fails."""
    validated_name = validate_name(name)
    validated_url = validate_url(url)
    source_icon = validate_icon_path(icon) if icon else None
    app_id = generate_app_id(validated_name)
    managed_icon = (
        paths.icons_dir / f"{app_id}{source_icon.suffix.lower()}" if source_icon else None
    )
    managed_icon_created = False
    persisted = False
    desktop = DesktopEntryService(paths.applications_dir, paths.profiles_dir)
    try:
        app = WebApp(
            id=app_id,
            name=validated_name,
            url=validated_url,
            icon=str(managed_icon) if managed_icon else None,
            isolated_profile=isolated_profile,
        )
        store.create(app)
        persisted = True
        if source_icon:
            copy_managed_icon(source_icon, paths.icons_dir, app_id)
            managed_icon_created = True
        desktop.create(app)
        return app
    except CREATE_ERRORS:
        record_removed = not persisted
        if persisted:
            try:
                store.remove(app_id)
                record_removed = True
            except (AppStoreError, ValidationError):
                LOGGER.exception("Failed to roll back application record %s", app_id)
        if record_removed and managed_icon_created and managed_icon:
            try:
                managed_icon.unlink(missing_ok=True)
            except OSError:
                LOGGER.exception("Failed to roll back managed icon %s", managed_icon)
        raise


def open_web_app(app_id: str, paths: WebWrapPaths, store: AppStore) -> WebApp:
    """Load and launch a configured web application."""
    app = store.get(app_id)
    BrowserService(paths.profiles_dir).launch(app)
    return app


def update_web_app(
    app_id: str,
    name: str,
    url: str,
    paths: WebWrapPaths,
    store: AppStore,
) -> WebApp:
    """Update an app and restore its record if launcher generation fails."""
    current = store.get(app_id)
    updated = replace(current, name=validate_name(name), url=validate_url(url))
    desktop = DesktopEntryService(paths.applications_dir, paths.profiles_dir)
    store.update(updated)
    try:
        desktop.update(updated)
    except MUTATION_ERRORS:
        try:
            store.update(current)
        except (AppStoreError, ValidationError):
            LOGGER.exception("Failed to roll back application record %s", app_id)
        raise
    return updated


def _managed_icon_path(app: WebApp, paths: WebWrapPaths) -> Path | None:
    if app.icon is None:
        return None
    icon = Path(app.icon)
    try:
        is_managed = icon.parent.resolve() == paths.icons_dir.resolve()
    except OSError:
        is_managed = False
    valid_suffix = icon.suffix.lower() in SUPPORTED_ICON_SUFFIXES
    if not is_managed or icon.stem != app.id or not valid_suffix:
        raise ValidationError("Stored icon path is outside WebWrap-managed storage.")
    return icon


def delete_web_app(app_id: str, paths: WebWrapPaths, store: AppStore) -> WebApp:
    """Delete an app and restore staged artifacts if persistence fails."""
    app = store.get(app_id)
    icon = _managed_icon_path(app, paths)
    staged_icon: Path | None = None
    desktop = DesktopEntryService(paths.applications_dir, paths.profiles_dir)
    desktop_existed = desktop.path_for(app.id).exists()
    desktop_removed = False
    try:
        if icon and icon.exists():
            staged_icon = icon.with_name(f".{icon.name}.deleting-{uuid4().hex}")
            os.replace(icon, staged_icon)
        desktop.delete(app.id)
        desktop_removed = desktop_existed
        store.remove(app.id)
    except MUTATION_ERRORS:
        if staged_icon and staged_icon.exists() and icon:
            try:
                os.replace(staged_icon, icon)
            except OSError:
                LOGGER.exception("Failed to restore managed icon %s", icon)
        if desktop_removed:
            try:
                desktop.create(app)
            except DesktopEntryError:
                LOGGER.exception("Failed to restore desktop entry %s", app.id)
        raise
    if staged_icon:
        try:
            staged_icon.unlink(missing_ok=True)
        except OSError as error:
            message = f"Application deleted, but its icon could not be cleaned up: {error}"
            raise ValidationError(message) from error
    return app
