"""Freedesktop desktop entry rendering and persistence."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

from webwrap.models import WebApp
from webwrap.services.browser import BrowserService
from webwrap.validation import validate_app_id


class DesktopEntryError(RuntimeError):
    """Raised when a desktop entry cannot be written or removed."""


def _escape_value(value: str) -> str:
    return (
        value.replace("\\", "\\\\")
        .replace("\n", "\\n")
        .replace("\r", "\\r")
        .replace("\t", "\\t")
    )


def _quote_exec_argument(argument: str) -> str:
    escaped = argument.replace("%", "%%")
    for character in ("\\", '"', "`", "$"):
        escaped = escaped.replace(character, f"\\{character}")
    return f'"{escaped}"'


class DesktopEntryService:
    """Create and delete safe desktop entries for managed applications."""

    def __init__(self, applications_dir: Path, profiles_dir: Path) -> None:
        self.applications_dir = Path(applications_dir)
        self.browser = BrowserService(profiles_dir)

    def path_for(self, app_id: str) -> Path:
        """Return the launcher path for a validated ID."""
        validate_app_id(app_id)
        return self.applications_dir / f"webwrap-{app_id}.desktop"

    def render(self, app: WebApp) -> str:
        """Render a standards-compatible desktop entry."""
        arguments = self.browser.build_arguments(app, app.browser)
        lines = [
            "[Desktop Entry]",
            f"Name={_escape_value(app.name)}",
            f"Exec={' '.join(_quote_exec_argument(argument) for argument in arguments)}",
        ]
        if app.icon:
            lines.append(f"Icon={_escape_value(app.icon)}")
        lines.extend(
            [
                "Terminal=false",
                "Type=Application",
                "Categories=Network;",
                "StartupNotify=true",
            ]
        )
        return "\n".join(lines) + "\n"

    def create(self, app: WebApp) -> Path:
        """Atomically create or replace an application's desktop entry."""
        destination = self.path_for(app.id)
        temporary: Path | None = None
        try:
            self.applications_dir.mkdir(parents=True, exist_ok=True)
            descriptor, temporary_name = tempfile.mkstemp(
                dir=self.applications_dir,
                prefix=f".{destination.name}-",
                text=True,
            )
            temporary = Path(temporary_name)
            with os.fdopen(descriptor, "w", encoding="utf-8") as output:
                output.write(self.render(app))
                output.flush()
                os.fsync(output.fileno())
            temporary.chmod(0o644)
            os.replace(temporary, destination)
            return destination
        except OSError as error:
            raise DesktopEntryError(f"Cannot write desktop entry: {error}") from error
        finally:
            if temporary is not None:
                try:
                    temporary.unlink(missing_ok=True)
                except OSError:
                    pass

    def update(self, app: WebApp) -> Path:
        """Replace an application's desktop entry."""
        return self.create(app)

    def delete(self, app_id: str) -> None:
        """Remove an application's desktop entry if it exists."""
        try:
            self.path_for(app_id).unlink(missing_ok=True)
        except OSError as error:
            raise DesktopEntryError(f"Cannot remove desktop entry: {error}") from error
