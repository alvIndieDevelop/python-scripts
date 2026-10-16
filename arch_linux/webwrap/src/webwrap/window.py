"""Main GTK window for browsing and creating WebWrap applications."""

from __future__ import annotations

from pathlib import Path
from urllib.parse import urlsplit

import gi

gi.require_version("Adw", "1")
gi.require_version("Gtk", "4.0")

from gi.repository import Adw, Gio, GLib, Gtk

from webwrap.models import WebApp
from webwrap.operations import (
    create_web_app,
    delete_web_app,
    open_web_app,
    update_web_app,
)
from webwrap.paths import WebWrapPaths
from webwrap.services import AppStore, AppStoreError, BrowserError, DesktopEntryError
from webwrap.validation import ValidationError


UI_ERRORS = (AppStoreError, BrowserError, DesktopEntryError, ValidationError, OSError)


class WebWrapWindow(Adw.ApplicationWindow):
    """Display and manage configured web applications."""

    def __init__(self, application: Adw.Application) -> None:
        super().__init__(
            application=application,
            title="WebWrap",
            default_width=680,
            default_height=520,
        )
        self.paths = WebWrapPaths.create()
        self.store = AppStore(self.paths.apps_file)
        self.apps: list[WebApp] = []
        self._install_actions()

        toolbar = Adw.ToolbarView()
        header = Adw.HeaderBar()
        header.set_title_widget(Adw.WindowTitle(title="WebWrap", subtitle="Chromium web apps"))
        toolbar.add_top_bar(header)

        add_button = Gtk.Button(
            icon_name="list-add-symbolic",
            tooltip_text="Add Web App",
        )
        add_button.add_css_class("suggested-action")
        add_button.connect("clicked", self._show_add_dialog)
        header.pack_end(add_button)

        self.toast_overlay = Adw.ToastOverlay()
        self.stack = Gtk.Stack(transition_type=Gtk.StackTransitionType.CROSSFADE)
        self.toast_overlay.set_child(self.stack)
        toolbar.set_content(self.toast_overlay)
        self.set_content(toolbar)

        self.empty_page = Adw.StatusPage(
            icon_name="applications-internet-symbolic",
            title="No web apps yet",
            description="Create a launcher for a website to see it here.",
        )
        empty_add_button = Gtk.Button(label="Add Web App", halign=Gtk.Align.CENTER)
        empty_add_button.add_css_class("suggested-action")
        empty_add_button.connect("clicked", self._show_add_dialog)
        self.empty_page.set_child(empty_add_button)
        self.stack.add_named(self.empty_page, "empty")

        self.list_box = Gtk.ListBox(
            css_classes=["boxed-list"],
            selection_mode=Gtk.SelectionMode.NONE,
        )
        clamp = Adw.Clamp(maximum_size=720, tightening_threshold=500)
        clamp.set_child(self.list_box)
        content = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            margin_top=24,
            margin_bottom=24,
            margin_start=18,
            margin_end=18,
        )
        content.append(clamp)
        scrolled = Gtk.ScrolledWindow(hscrollbar_policy=Gtk.PolicyType.NEVER)
        scrolled.set_child(content)
        self.stack.add_named(scrolled, "apps")

        self._load_apps()

    def _load_apps(self) -> None:
        try:
            self.apps = self.store.load()
        except AppStoreError as error:
            self.apps = []
            self.empty_page.set_title("Applications could not be loaded")
            self.empty_page.set_description(str(error))
        self._render_apps()

    def _render_apps(self) -> None:
        while child := self.list_box.get_first_child():
            self.list_box.remove(child)
        for app in self.apps:
            self.list_box.append(self._create_row(app))
        self.stack.set_visible_child_name("apps" if self.apps else "empty")

    def _create_row(self, app: WebApp) -> Adw.ActionRow:
        host = urlsplit(app.url).hostname or app.url
        row = Adw.ActionRow(title=app.name, subtitle=host, activatable=True)
        row.connect("activated", lambda _row: self._open_app(app.id))
        icon = self._create_icon(app)
        icon.set_size_request(40, 40)
        row.add_prefix(icon)

        open_button = Gtk.Button(label="Open", valign=Gtk.Align.CENTER)
        open_button.connect("clicked", lambda _button: self._open_app(app.id))
        row.add_suffix(open_button)

        menu = Gio.Menu()
        menu.append_item(self._menu_item("Edit", "win.edit", app.id))
        menu.append_item(self._menu_item("Delete", "win.delete", app.id))
        menu_button = Gtk.MenuButton(
            icon_name="view-more-symbolic",
            menu_model=menu,
            tooltip_text="More Actions",
            valign=Gtk.Align.CENTER,
        )
        row.add_suffix(menu_button)
        return row

    def _install_actions(self) -> None:
        parameter_type = GLib.VariantType.new("s")
        edit_action = Gio.SimpleAction.new("edit", parameter_type)
        edit_action.connect("activate", self._on_edit_action)
        self.add_action(edit_action)

        delete_action = Gio.SimpleAction.new("delete", parameter_type)
        delete_action.connect("activate", self._on_delete_action)
        self.add_action(delete_action)

    @staticmethod
    def _menu_item(label: str, action: str, app_id: str) -> Gio.MenuItem:
        item = Gio.MenuItem.new(label, action)
        item.set_attribute_value("target", GLib.Variant("s", app_id))
        return item

    @staticmethod
    def _create_icon(app: WebApp) -> Gtk.Widget:
        if app.icon and Path(app.icon).is_file():
            picture = Gtk.Picture.new_for_filename(app.icon)
            picture.set_content_fit(Gtk.ContentFit.COVER)
            return picture
        return Gtk.Image.new_from_icon_name("applications-internet-symbolic")

    def _show_add_dialog(self, _button: Gtk.Button) -> None:
        from webwrap.dialogs import AddWebAppDialog

        AddWebAppDialog(self._create_app).present(self)

    def _create_app(self, name: str, url: str) -> str | None:
        try:
            app = create_web_app(name, url, self.paths, self.store)
        except UI_ERRORS as error:
            self._sync_apps_after_error()
            return str(error)
        self.apps.append(app)
        self._render_apps()
        self.toast_overlay.add_toast(
            Adw.Toast(title=f"Created {app.name}", use_markup=False, timeout=3)
        )
        return None

    def _open_app(self, app_id: str) -> str | None:
        try:
            open_web_app(app_id, self.paths, self.store)
        except UI_ERRORS as error:
            self._show_error(str(error))
            return str(error)
        return None

    def _on_edit_action(self, _action: Gio.SimpleAction, parameter: GLib.Variant) -> None:
        app_id = parameter.get_string()
        app = self._find_app(app_id)
        if app is None:
            return
        from webwrap.dialogs import EditWebAppDialog

        callback = lambda name, url: self._update_app(app_id, name, url)
        EditWebAppDialog(app.name, app.url, callback).present(self)

    def _update_app(self, app_id: str, name: str, url: str) -> str | None:
        try:
            updated = update_web_app(app_id, name, url, self.paths, self.store)
        except UI_ERRORS as error:
            self._sync_apps_after_error()
            return str(error)
        self.apps = [updated if app.id == app_id else app for app in self.apps]
        self._render_apps()
        self.toast_overlay.add_toast(
            Adw.Toast(title=f"Updated {updated.name}", use_markup=False, timeout=3)
        )
        return None

    def _on_delete_action(self, _action: Gio.SimpleAction, parameter: GLib.Variant) -> None:
        app_id = parameter.get_string()
        app = self._find_app(app_id)
        if app is None:
            return
        dialog = Adw.AlertDialog(
            heading=f"Delete {app.name}?",
            body=(
                "The launcher and managed icon will be removed. "
                "Isolated Chromium profile data will be preserved."
            ),
        )
        dialog.add_response("cancel", "Cancel")
        dialog.add_response("delete", "Delete")
        dialog.set_default_response("cancel")
        dialog.set_close_response("cancel")
        dialog.set_response_appearance("delete", Adw.ResponseAppearance.DESTRUCTIVE)
        dialog.connect("response", self._on_delete_response, app.id)
        dialog.present(self)

    def _on_delete_response(
        self,
        _dialog: Adw.AlertDialog,
        response: str,
        app_id: str,
    ) -> None:
        if response == "delete":
            self._delete_app(app_id)

    def _delete_app(self, app_id: str) -> str | None:
        try:
            deleted = delete_web_app(app_id, self.paths, self.store)
        except UI_ERRORS as error:
            self._sync_apps_after_error()
            self._show_error(str(error))
            return str(error)
        self.apps = [app for app in self.apps if app.id != app_id]
        self._render_apps()
        self.toast_overlay.add_toast(
            Adw.Toast(title=f"Deleted {deleted.name}", use_markup=False, timeout=3)
        )
        return None

    def _find_app(self, app_id: str) -> WebApp | None:
        for app in self.apps:
            if app.id == app_id:
                return app
        self._show_error(f"Application '{app_id}' is no longer available.")
        return None

    def _show_error(self, message: str) -> None:
        self.toast_overlay.add_toast(
            Adw.Toast(title=message, use_markup=False, timeout=5, priority=Adw.ToastPriority.HIGH)
        )

    def _sync_apps_after_error(self) -> None:
        try:
            self.apps = self.store.load()
        except AppStoreError:
            return
        self._render_apps()
