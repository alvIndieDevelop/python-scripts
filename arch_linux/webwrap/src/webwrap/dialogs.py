"""Dialogs used by the WebWrap graphical interface."""

from __future__ import annotations

from collections.abc import Callable

import gi

gi.require_version("Adw", "1")
gi.require_version("Gtk", "4.0")

from gi.repository import Adw, Gtk


SubmitCallback = Callable[[str, str], str | None]


class WebAppDialog(Adw.Dialog):
    """Collect and validate the editable fields of a web application."""

    def __init__(
        self,
        title: str,
        description: str,
        submit_label: str,
        submit_callback: SubmitCallback,
        name: str = "",
        url: str = "",
    ) -> None:
        super().__init__(title=title, content_width=480, content_height=360)
        self._submit_callback = submit_callback

        toolbar = Adw.ToolbarView()
        header = Adw.HeaderBar()
        header.set_show_end_title_buttons(False)
        toolbar.add_top_bar(header)

        cancel_button = Gtk.Button(label="Cancel")
        cancel_button.connect("clicked", lambda _button: self.close())
        header.pack_start(cancel_button)

        self.create_button = Gtk.Button(label=submit_label)
        self.create_button.add_css_class("suggested-action")
        self.create_button.connect("clicked", self._on_create)
        header.pack_end(self.create_button)

        page = Adw.PreferencesPage()
        group = Adw.PreferencesGroup(
            title="Website",
            description=description,
        )
        page.add(group)

        self.name_entry = Adw.EntryRow(title="Name")
        self.name_entry.set_text(name)
        self.name_entry.connect("entry-activated", self._on_create)
        group.add(self.name_entry)

        self.url_entry = Adw.EntryRow(title="URL")
        self.url_entry.set_text(url)
        self.url_entry.set_input_purpose(Gtk.InputPurpose.URL)
        self.url_entry.connect("entry-activated", self._on_create)
        group.add(self.url_entry)

        self.error_label = Gtk.Label(
            css_classes=["error"],
            margin_top=12,
            visible=False,
            wrap=True,
            xalign=0,
        )
        group.add(self.error_label)

        toolbar.set_content(page)
        self.set_child(toolbar)

    def _on_create(self, _source: object) -> None:
        self.create_button.set_sensitive(False)
        error = self._submit_callback(self.name_entry.get_text(), self.url_entry.get_text())
        if error is None:
            self.close()
            return
        self.error_label.set_label(error)
        self.error_label.set_visible(True)
        self.create_button.set_sensitive(True)


class AddWebAppDialog(WebAppDialog):
    """Collect the fields required to create a web application."""

    def __init__(self, create_callback: SubmitCallback) -> None:
        super().__init__(
            title="Add Web App",
            description="Create a launcher that opens this site in Chromium.",
            submit_label="Create",
            submit_callback=create_callback,
        )


class EditWebAppDialog(WebAppDialog):
    """Edit the name and URL of an existing web application."""

    def __init__(
        self,
        name: str,
        url: str,
        update_callback: SubmitCallback,
    ) -> None:
        super().__init__(
            title="Edit Web App",
            description="Update the launcher name and website address.",
            submit_label="Save",
            submit_callback=update_callback,
            name=name,
            url=url,
        )
