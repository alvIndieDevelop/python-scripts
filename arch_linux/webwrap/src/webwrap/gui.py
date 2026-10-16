"""Dependency-aware entry point for the WebWrap graphical application."""

from __future__ import annotations

import sys


MISSING_DEPENDENCIES = (
    "GTK support is unavailable. On Arch Linux install python-gobject, gtk4, and "
    "libadwaita, then create the virtual environment with --system-site-packages."
)
MINIMUM_GTK_MINOR = 8
MINIMUM_ADW_MINOR = 5


def main(argv: list[str] | None = None) -> int:
    """Run the GTK application or report missing graphical dependencies."""
    try:
        import gi
    except ModuleNotFoundError:
        print(f"webwrap-gui: error: {MISSING_DEPENDENCIES}", file=sys.stderr)
        return 1

    try:
        gi.require_version("Gtk", "4.0")
        gi.require_version("Adw", "1")
    except ValueError as error:
        print(f"webwrap-gui: error: {error}. {MISSING_DEPENDENCIES}", file=sys.stderr)
        return 1

    try:
        from gi.repository import Adw, Gtk
    except (ImportError, OSError, ValueError) as error:
        print(f"webwrap-gui: error: {error}. {MISSING_DEPENDENCIES}", file=sys.stderr)
        return 1

    if Gtk.get_major_version() != 4 or Gtk.get_minor_version() < MINIMUM_GTK_MINOR:
        print("webwrap-gui: error: GTK 4.8 or newer is required.", file=sys.stderr)
        return 1
    if Adw.get_major_version() != 1 or Adw.get_minor_version() < MINIMUM_ADW_MINOR:
        print("webwrap-gui: error: Libadwaita 1.5 or newer is required.", file=sys.stderr)
        return 1

    try:
        from webwrap.application import run
    except (ImportError, OSError, ValueError) as error:
        print(f"webwrap-gui: error: {error}. {MISSING_DEPENDENCIES}", file=sys.stderr)
        return 1

    return run(argv)


if __name__ == "__main__":
    raise SystemExit(main())
