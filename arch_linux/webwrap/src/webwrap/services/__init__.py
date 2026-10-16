"""Services used by the WebWrap command-line application."""

from webwrap.services.app_store import AppStore, AppStoreError
from webwrap.services.browser import BrowserError, BrowserService
from webwrap.services.desktop_entry import DesktopEntryError, DesktopEntryService

__all__ = [
    "AppStore",
    "AppStoreError",
    "BrowserError",
    "BrowserService",
    "DesktopEntryError",
    "DesktopEntryService",
]
