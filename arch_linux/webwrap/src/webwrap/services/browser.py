"""Chromium command construction and launch service."""

from __future__ import annotations

import shutil
import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import Any

from webwrap.models import WebApp
from webwrap.validation import validate_app_id


class BrowserError(RuntimeError):
    """Raised when Chromium cannot be resolved or launched."""


class BrowserService:
    """Build and launch shell-free Chromium application commands."""

    def __init__(
        self,
        profiles_dir: Path,
        which: Callable[[str], str | None] = shutil.which,
        popen: Callable[..., Any] = subprocess.Popen,
    ) -> None:
        self.profiles_dir = Path(profiles_dir)
        self._which = which
        self._popen = popen

    def resolve_executable(self, browser: str) -> str:
        """Resolve the supported browser executable from PATH."""
        if browser != "chromium":
            raise BrowserError("Only the chromium browser is supported.")
        executable = self._which(browser)
        if executable is None:
            raise BrowserError("Chromium is not installed or is not available in PATH.")
        return executable

    def build_arguments(self, app: WebApp, executable: str = "chromium") -> list[str]:
        """Build Chromium arguments without creating files or launching it."""
        validate_app_id(app.id)
        arguments = [executable, f"--app={app.url}"]
        if app.isolated_profile:
            arguments.append(f"--user-data-dir={self.profiles_dir / app.id}")
        return arguments

    def launch(self, app: WebApp) -> Any:
        """Launch an application and create its isolated profile on demand."""
        executable = self.resolve_executable(app.browser)
        if app.isolated_profile:
            try:
                (self.profiles_dir / app.id).mkdir(parents=True, exist_ok=True)
            except OSError as error:
                raise BrowserError(f"Cannot create the Chromium profile: {error}") from error
        arguments = self.build_arguments(app, executable)
        try:
            return self._popen(arguments)
        except (FileNotFoundError, PermissionError, OSError) as error:
            raise BrowserError(f"Cannot launch Chromium: {error}") from error
