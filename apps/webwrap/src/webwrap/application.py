"""GTK application lifecycle for WebWrap."""

from __future__ import annotations

import sys

import gi

gi.require_version("Adw", "1")
gi.require_version("Gtk", "4.0")

from gi.repository import Adw, Gio

from webwrap.window import WebWrapWindow


APPLICATION_ID = "io.github.alvIndieDevelop.WebWrap"


class WebWrapApplication(Adw.Application):
    """Own the WebWrap process and present a single main window."""

    def __init__(self) -> None:
        super().__init__(
            application_id=APPLICATION_ID,
            flags=Gio.ApplicationFlags.DEFAULT_FLAGS,
        )

    def do_activate(self) -> None:
        """Create the main window once and present it on every activation."""
        window = self.get_active_window()
        if window is None:
            window = WebWrapWindow(self)
        window.present()


def run(argv: list[str] | None = None) -> int:
    """Run the graphical application and return its process status."""
    return WebWrapApplication().run(argv if argv is not None else sys.argv)
