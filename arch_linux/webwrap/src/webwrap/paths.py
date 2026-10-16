"""Centralized XDG paths used by WebWrap."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class WebWrapPaths:
    """Immutable collection of WebWrap data and application paths."""

    data_home: Path
    applications_dir: Path

    @classmethod
    def create(
        cls,
        data_home: Path | None = None,
        applications_dir: Path | None = None,
    ) -> WebWrapPaths:
        """Build paths from explicit roots or the XDG environment."""
        if data_home is None:
            configured_home = os.environ.get("XDG_DATA_HOME")
            data_home = Path(configured_home) if configured_home else Path.home() / ".local/share"
        if applications_dir is None:
            applications_dir = data_home / "applications"
        return cls(data_home=Path(data_home), applications_dir=Path(applications_dir))

    @property
    def webwrap_dir(self) -> Path:
        """Return the managed WebWrap data directory."""
        return self.data_home / "webwrap"

    @property
    def apps_file(self) -> Path:
        """Return the JSON application database path."""
        return self.webwrap_dir / "apps.json"

    @property
    def icons_dir(self) -> Path:
        """Return the managed icon directory."""
        return self.webwrap_dir / "icons"

    @property
    def profiles_dir(self) -> Path:
        """Return the isolated Chromium profile root."""
        return self.webwrap_dir / "profiles"
