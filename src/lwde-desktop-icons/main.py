#!/usr/bin/env python
import configparser
import os
import subprocess
import sys
from posixpath import expanduser

import gi

gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")
gi.require_version("GtkLayerShell", "0.1")
from gi.repository import Gdk, Gio, GLib, Gtk, GtkLayerShell

if "--help" in sys.argv:
    print("--show-dotfiles         - show dotfiles on the desktop")
    print("--help                  - show this help message")
    print("--enable-no-matter-what - enable desktop icons no matter what")
    sys.exit(0)

if (
    os.path.exists(expanduser("~/.config/disable-lwde-desktop-icons"))
    and not "--enable-no-matter-what" in sys.argv
):
    print("icons disabled: use --enable-no-matter-what to enable for sure")
    sys.exit(0)


def parse_desktop_file(path):
    config = configparser.ConfigParser(interpolation=None)
    config.read(path)
    section = "Desktop Entry"
    if not config.has_section(section):
        return None
    return {
        "name": config.get(section, "Name", fallback=os.path.basename(path)),
        "icon": config.get(section, "Icon", fallback="application-x-executable"),
        "exec": config.get(section, "Exec", fallback=""),
        "type": config.get(section, "Type", fallback="Application"),
    }


def clean_exec(exec_str):
    return " ".join(part for part in exec_str.split() if not part.startswith("%"))


def load_desktop_icons():
    global lot_of_items
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    if not os.path.isdir(desktop):
        os.makedirs(desktop)
        return []

    icons = []
    for fname in sorted(os.listdir(desktop)):
        path = os.path.join(desktop, fname)

        if fname.endswith(".desktop"):
            entry = parse_desktop_file(path)
            if entry and entry["type"] == "Application" and entry["exec"]:
                icons.append((entry["name"], entry["icon"], entry["exec"], path))
        else:
            if fname.startswith(".") and "--show-dotfiles" not in sys.argv:
                continue
            gio_file = Gio.File.new_for_path(path)
            info = gio_file.query_info(
                "standard::icon,standard::content-type",
                Gio.FileQueryInfoFlags.NONE,
                None,
            )
            gio_icon = info.get_icon()
            icon_name = gio_icon.get_names()[0] if gio_icon else "application-x-generic"
            icons.append((fname, icon_name, f'xdg-open "{path}"', path))

    return icons


class DesktopIcon(Gtk.Button):
    def __init__(self, name, icon_name, exec_cmd, path):
        super().__init__()
        self.exec_cmd = exec_cmd
        self.path = path

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)

        icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.DIALOG)
        if icon.get_storage_type() == Gtk.ImageType.EMPTY:
            icon = Gtk.Image.new_from_icon_name(
                "application-x-generic", Gtk.IconSize.DIALOG
            )

        lbl = Gtk.Label(label=name)
        lbl.set_max_width_chars(12)
        lbl.set_line_wrap(True)
        lbl.set_justify(Gtk.Justification.CENTER)

        box.pack_start(icon, False, False, 0)
        box.pack_start(lbl, False, False, 0)
        self.add(box)
        self.get_style_context().add_class("flat")
        self.connect("button-press-event", self.on_click)

    def on_click(self, widget, event):
        if event.button == 1 and event.type == Gdk.EventType.DOUBLE_BUTTON_PRESS:
            self.launch()
            return True
        elif event.button == 3:
            self.show_context_menu(event)
            return True
        return False

    def launch(self):
        if self.exec_cmd:
            subprocess.Popen(clean_exec(self.exec_cmd), shell=True)

    def show_context_menu(self, event, reload_cb):
        menu = Gtk.Menu()

        open_item = Gtk.MenuItem(label="Open")
        open_item.connect("activate", lambda _: self.launch())
        menu.append(open_item)

        copy_item = Gtk.MenuItem(label="Copy path")
        copy_item.connect("activate", self.copy_path)
        menu.append(copy_item)

        trash_item = Gtk.MenuItem(label="Move to Trash")
        trash_item.connect("activate", lambda _: self.trash(reload_cb))
        menu.append(trash_item)

        menu.show_all()
        menu.popup_at_pointer(event)

    def copy_path(self, *_):
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        clipboard.set_text(self.path, -1)

    def trash(self, reload_cb):
        Gio.File.new_for_path(self.path).trash(None)
        reload_cb()


class Desktop(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app)

        GtkLayerShell.init_for_window(self)
        GtkLayerShell.set_layer(self, GtkLayerShell.Layer.BOTTOM)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.LEFT, True)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.TOP, True)
        GtkLayerShell.set_exclusive_zone(self, -1)

        self.set_app_paintable(True)
        visual = self.get_screen().get_rgba_visual()
        if visual:
            self.set_visual(visual)

        self.grid = Gtk.Grid(
            row_spacing=8, column_spacing=8, margin_top=16, margin_start=16
        )

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        vbox.pack_start(self.grid, True, True, 0)
        self.add(vbox)
        self.show_all()

        self._last_icons = None
        self.refresh()
        GLib.timeout_add_seconds(3, self.refresh)

    def columns(self, icon_count):
        screen_height = self.get_screen().get_height()
        icon_height = 80
        max_rows = max(1, screen_height // icon_height)
        return max(1, (icon_count + max_rows - 1) // max_rows)

    def refresh(self):
        icons = load_desktop_icons()
        if icons == self._last_icons:
            return True

        self._last_icons = icons

        for child in self.grid.get_children():
            self.grid.remove(child)

        cols = self.columns(len(icons))
        for i, (name, icon, cmd, path) in enumerate(icons):
            btn = DesktopIcon(name, icon, cmd, path)
            btn.show_context_menu = lambda event, b=btn: b.__class__.show_context_menu(
                b, event, self.refresh
            )
            self.grid.attach(btn, i % cols, i // cols, 1, 1)

        self.grid.show_all()
        return True


app = Gtk.Application(application_id="com.example.desktop")
app.connect("activate", lambda a: Desktop(a))
app.run()
