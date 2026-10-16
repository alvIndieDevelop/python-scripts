"""Tests for the dependency-aware graphical launcher."""

import contextlib
import io
import sys
import unittest
from unittest.mock import patch

import context  # noqa: F401

from webwrap import gui


class GuiLauncherTests(unittest.TestCase):
    """Verify a useful error when PyGObject is unavailable."""

    def test_missing_gi_returns_failure_without_traceback(self) -> None:
        stderr = io.StringIO()
        with patch.dict(sys.modules, {"gi": None}), contextlib.redirect_stderr(stderr):
            self.assertEqual(gui.main([]), 1)

        self.assertIn("python-gobject", stderr.getvalue())
        self.assertNotIn("Traceback", stderr.getvalue())
