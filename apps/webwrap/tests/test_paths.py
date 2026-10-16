"""Tests for XDG path resolution."""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from webwrap.paths import WebWrapPaths


class WebWrapPathsTests(unittest.TestCase):
    """Verify XDG fallback rules and derived paths."""

    def test_unset_empty_and_relative_xdg_values_use_default(self) -> None:
        home = Path("/home/tester")
        for value in (None, "", "relative/data", "~/data"):
            environment = {} if value is None else {"XDG_DATA_HOME": value}
            with (
                self.subTest(value=value),
                patch.dict(os.environ, environment, clear=True),
                patch("pathlib.Path.home", return_value=home),
            ):
                self.assertEqual(WebWrapPaths.create().data_home, home / ".local/share")

    def test_absolute_xdg_value_is_used(self) -> None:
        with patch.dict(os.environ, {"XDG_DATA_HOME": "/var/tmp/data"}, clear=True):
            self.assertEqual(WebWrapPaths.create().data_home, Path("/var/tmp/data"))

    def test_explicit_roots_and_derived_directories(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            applications = root / "launchers"
            paths = WebWrapPaths.create(root, applications)

            self.assertEqual(paths.data_home, root)
            self.assertEqual(paths.applications_dir, applications)
            self.assertEqual(paths.webwrap_dir, root / "webwrap")
            self.assertEqual(paths.apps_file, root / "webwrap/apps.json")
            self.assertEqual(paths.icons_dir, root / "webwrap/icons")
            self.assertEqual(paths.profiles_dir, root / "webwrap/profiles")
            self.assertFalse(paths.webwrap_dir.exists())
