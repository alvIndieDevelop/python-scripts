"""Display-dependent smoke tests for the GTK interface."""

import os
import tempfile
import unittest
from unittest.mock import patch


try:
    import gi

    gi.require_version("Adw", "1")
    gi.require_version("Gdk", "4.0")
    gi.require_version("Gtk", "4.0")
    from gi.repository import Gdk, GLib, Gtk

    Gtk.init()
    HAS_DISPLAY = Gdk.Display.get_default() is not None
except (ImportError, RuntimeError, ValueError):
    HAS_DISPLAY = False


@unittest.skipUnless(HAS_DISPLAY, "GTK and a graphical display are required")
class GuiComponentTests(unittest.TestCase):
    """Verify empty, create, and inline-error interface states."""

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.environment = patch.dict(os.environ, {"XDG_DATA_HOME": self.temporary.name})
        self.environment.start()

    def tearDown(self) -> None:
        self.environment.stop()
        self.temporary.cleanup()

    def test_window_moves_from_empty_state_to_app_list(self) -> None:
        from webwrap.application import WebWrapApplication
        from webwrap.window import WebWrapWindow

        application = WebWrapApplication()
        application.register(None)
        window = WebWrapWindow(application)
        self.assertEqual(window.stack.get_visible_child_name(), "empty")

        self.assertIsNone(window._create_app("Example", "https://example.com"))

        self.assertEqual(window.stack.get_visible_child_name(), "apps")
        self.assertEqual([app.name for app in window.apps], ["Example"])

        app_id = window.apps[0].id
        with patch("webwrap.window.open_web_app") as open_app:
            self.assertIsNone(window._open_app(app_id))
        open_app.assert_called_once_with(app_id, window.paths, window.store)

        self.assertIsNone(
            window._update_app(app_id, "Updated", "https://updated.example")
        )
        self.assertEqual(window.apps[0].name, "Updated")

        with patch("webwrap.window.Adw.AlertDialog") as alert_dialog:
            window._on_delete_action(None, GLib.Variant("s", app_id))
        alert_dialog.assert_called_once()
        alert_dialog.return_value.present.assert_called_once_with(window)

        with patch.object(window, "_delete_app") as delete_app:
            window._on_delete_response(alert_dialog.return_value, "cancel", app_id)
            delete_app.assert_not_called()
            window._on_delete_response(alert_dialog.return_value, "delete", app_id)
            delete_app.assert_called_once_with(app_id)

        self.assertIsNone(window._delete_app(app_id))
        self.assertEqual(window.apps, [])
        self.assertEqual(window.stack.get_visible_child_name(), "empty")
        window.destroy()

    def test_add_dialog_presents_callback_error(self) -> None:
        from webwrap.dialogs import AddWebAppDialog

        dialog = AddWebAppDialog(lambda _name, _url: "Invalid URL")
        dialog.name_entry.set_text("Example")
        dialog.url_entry.set_text("bad")

        dialog._on_create(dialog.create_button)

        self.assertTrue(dialog.error_label.get_visible())
        self.assertEqual(dialog.error_label.get_label(), "Invalid URL")
        self.assertTrue(dialog.create_button.get_sensitive())

    def test_edit_dialog_is_prepopulated(self) -> None:
        from webwrap.dialogs import EditWebAppDialog

        dialog = EditWebAppDialog("Current", "https://example.com", lambda _n, _u: None)

        self.assertEqual(dialog.get_title(), "Edit Web App")
        self.assertEqual(dialog.name_entry.get_text(), "Current")
        self.assertEqual(dialog.url_entry.get_text(), "https://example.com")
        self.assertEqual(dialog.create_button.get_label(), "Save")
