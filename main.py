#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PyStudioMusic v1.0.0
Professional GTK3 GUI manager for audio/music-production software on Debian/Ubuntu

Repository: https://github.com/yourusername/PyStudioMusic
Author: Luca Bocaletto
License: GPLv3
Date: 2025-08-02
"""

import subprocess
from pathlib import Path

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

# -------------------------------------------------------------------
# Configuration constants
# -------------------------------------------------------------------

VERSION = "1.0.0"
HOME = Path.home()
CONFIG_DIR = HOME / ".pystudiomusic"
CUSTOM_FILE = CONFIG_DIR / "apps.custom"

# Categories for user‐custom applications
CATEGORIES = [
    "DAW", "Editor", "Server", "Synthesizer",
    "Plugin Host", "Looper", "DJ", "Patchbay",
    "Suite", "Utility"
]

# Built‐in catalog of known audio/music apps:
#   uid -> (Name, Category, Short description, apt package, launch command)
BUILTIN_APPS = {
    "ardour":       ("Ardour",         "DAW",           "Professional DAW",              "ardour",        "ardour"),
    "lmms":         ("LMMS",           "DAW",           "Pattern-based music creation", "lmms",          "lmms"),
    "qtractor":     ("Qtractor",       "DAW",           "JACK-centric sequencer",        "qtractor",      "qtractor"),
    "rosegarden":   ("Rosegarden",     "DAW",           "MIDI & notation editor",       "rosegarden",    "rosegarden"),
    "musescore":    ("MuseScore",      "Editor",        "Music notation software",      "musescore3",    "musescore3"),
    "audacity":     ("Audacity",       "Editor",        "Audio editor",                 "audacity",      "audacity"),
    "jackd2":       ("JACK2",          "Server",        "Low-latency audio server",      "jackd2",        "jackd"),
    "pipewire":     ("PipeWire",       "Server",        "Modern audio server",          "pipewire",      "pipewire"),
    "pulseaudio":   ("PulseAudio",     "Server",        "Sound server",                 "pulseaudio",    "pulseaudio"),
    "hydrogen":     ("Hydrogen",       "Synthesizer",   "Advanced drum machine",        "hydrogen",      "hydrogen"),
    "fluidsynth":   ("FluidSynth",     "Synthesizer",   "SoundFont software synth",     "fluidsynth",    "fluidsynth"),
    "qsynth":       ("Qsynth",         "Synthesizer",   "GUI for FluidSynth",           "qsynth",        "qsynth"),
    "carla":        ("Carla",          "Plugin Host",   "VST/LV2 plugin host",          "carla",         "carla"),
    "sooperlooper": ("SooperLooper",   "Looper",        "Live looping tool",            "sooperlooper",  "sooperlooper"),
    "mixxx":        ("Mixxx",          "DJ",            "DJ mixing software",           "mixxx",         "mixxx"),
    "patchage":     ("Patchage",       "Patchbay",      "LV2/JACK patchbay",            "patchage",      "patchage"),
    "cadence":      ("Cadence",        "Suite",         "KXStudio tools suite",         "cadence",       "cadence"),
    "ffmpeg":       ("FFmpeg",         "Utility",       "Multimedia framework",         "ffmpeg",        "ffmpeg"),
    "sox":          ("SoX",            "Utility",       "Sound processing toolkit",     "sox",           "sox"),
    "ecasound":     ("Ecasound",       "Utility",       "Multitrack audio recorder",    "ecasound",      "ecasound"),
    "alsa-utils":   ("ALSA Utils",     "Utility",       "Mixer & MIDI tools",           "alsa-utils",    "alsamixer"),
}


class AppEntry:
    """
    Represents one audio/music application in our catalog:
      - uid         : unique identifier
      - name        : display name
      - category    : one of CATEGORIES
      - description : short text
      - pkg         : Debian package name
      - cmd         : shell command to launch
      - custom      : True if user‐added
      - installed   : updated at load time
      - desired     : user selection for install/remove
    """

    def __init__(self, uid, name, category, description, pkg, cmd, custom=False):
        self.uid = uid
        self.name = name
        self.category = category
        self.description = description
        self.pkg = pkg
        self.cmd = cmd
        self.custom = custom
        self.installed = False
        self.desired = False


# Global in‐memory catalog: uid -> AppEntry
apps = {}


# -------------------------------------------------------------------
# System utility functions
# -------------------------------------------------------------------

def run_cmd(*cmd, check=False):
    """Run a subprocess command, capture output silently."""
    return subprocess.run(cmd, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, check=check)


def is_installed(pkg: str) -> bool:
    """Return True if Debian package ‘pkg’ is currently installed."""
    result = run_cmd("dpkg-query", "-W", "-f=${Status}", pkg)
    return result.stdout.decode().startswith("install ok installed")


def apt_install(pkgs: list):
    """Install packages via apt-get."""
    run_cmd("sudo", "apt-get", "update", "-qq", check=True)
    run_cmd("sudo", "apt-get", "install", "-y", *pkgs, check=True)


def apt_remove(pkgs: list):
    """Remove packages (leave config files)."""
    run_cmd("sudo", "apt-get", "remove", "-y", *pkgs, check=True)


def apt_purge(pkgs: list):
    """Purge packages (delete config files)."""
    run_cmd("sudo", "apt-get", "purge", "-y", *pkgs, check=True)


def ensure_config_dir():
    """Create ~/.pystudiomusic directory if it does not exist."""
    CONFIG_DIR.mkdir(exist_ok=True)


def load_apps():
    """
    Populate the global `apps` dict from built‐in + custom file.
    Update 'installed' and 'desired' flags.
    """
    apps.clear()

    # Load built‐in entries
    for uid, (name, cat, desc, pkg, cmd) in BUILTIN_APPS.items():
        apps[uid] = AppEntry(uid, name, cat, desc, pkg, cmd, custom=False)

    # Load user‐custom entries from apps.custom
    if CUSTOM_FILE.exists():
        for line in CUSTOM_FILE.read_text(encoding="utf-8").splitlines():
            parts = line.split("|")
            if len(parts) == 6:
                uid, name, cat, desc, pkg, cmd = parts
                apps[uid] = AppEntry(uid, name, cat, desc, pkg, cmd, custom=True)

    # Check installation status
    for entry in apps.values():
        entry.installed = is_installed(entry.pkg)
        entry.desired = entry.installed  # default checkbox = current state


def save_custom_apps():
    """Write only custom AppEntry objects back to apps.custom."""
    lines = []
    for entry in apps.values():
        if entry.custom:
            fields = [entry.uid, entry.name, entry.category,
                      entry.description, entry.pkg, entry.cmd]
            lines.append("|".join(fields))
    CUSTOM_FILE.write_text("\n".join(lines), encoding="utf-8")


# -------------------------------------------------------------------
# Main GTK window
# -------------------------------------------------------------------

class MainWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="PyStudioMusic")
        self.set_default_size(800, 500)
        self.set_border_width(8)

        # Configure header bar with title and version
        self._setup_headerbar()

        # Ensure config and load catalogs
        ensure_config_dir()
        load_apps()

        # Build the stacked UI
        self._build_ui()

        # Show window
        self.connect("destroy", Gtk.main_quit)
        self.show_all()

    def _setup_headerbar(self):
        """Create a modern header bar displaying the app name/version."""
        header = Gtk.HeaderBar()
        header.props.show_close_button = True
        header.props.title = "PyStudioMusic"
        header.props.subtitle = f"v{VERSION}"
        self.set_titlebar(header)

    def _build_ui(self):
        """Compose the main layout: side menu + stack of pages."""
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.add(hbox)

        # Sidebar with stack switcher
        sidebar = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.stack = Gtk.Stack(transition_type=Gtk.StackTransitionType.SLIDE_LEFT_RIGHT,
                               transition_duration=200)
        switcher = Gtk.StackSwitcher()
        switcher.set_stack(self.stack)
        sidebar.pack_start(switcher, False, False, 0)

        # Main content area
        hbox.pack_start(sidebar, False, False, 0)
        hbox.pack_start(self.stack, True, True, 0)

        # Add pages to the stack
        self.stack.add_titled(self._page_manage(), "manage", "Manage Apps")
        self.stack.add_titled(self._page_status(), "status", "Status")
        self.stack.add_titled(self._page_launch(), "launch", "Launch Apps")
        self.stack.add_titled(self._page_add(), "add", "Add App")
        self.stack.add_titled(self._page_help(), "help", "Help & Info")

    # -------------------------------------------------------------------
    # Page 1: Manage Apps (install/remove, modify catalog)
    # -------------------------------------------------------------------

    def _page_manage(self) -> Gtk.Box:
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        # ListStore for TreeView: desired, name, category, description, installed, action
        self.store = Gtk.ListStore(bool, str, str, str, str, object)
        self._refresh_store()

        tree = Gtk.TreeView(model=self.store)
        tree.set_vexpand(True)
        tree.set_hexpand(True)

        # Checkbox column for desired install state
        renderer_toggle = Gtk.CellRendererToggle()
        renderer_toggle.connect("toggled", self._on_toggle_desired)
        col_toggle = Gtk.TreeViewColumn("Install", renderer_toggle, active=0)
        tree.append_column(col_toggle)

        # Text columns: Name, Category, Description
        for idx, title in enumerate(["Name", "Category", "Description"], start=1):
            renderer_text = Gtk.CellRendererText()
            col = Gtk.TreeViewColumn(title, renderer_text, text=idx)
            tree.append_column(col)

        # Installed status column
        renderer_status = Gtk.CellRendererText()
        col_status = Gtk.TreeViewColumn("Installed", renderer_status, text=4)
        tree.append_column(col_status)

        # Action column (e.g. "Delete" for custom entries)
        renderer_action = Gtk.CellRendererText()
        col_action = Gtk.TreeViewColumn("Action", renderer_action, text=5)
        tree.append_column(col_action)

        scroll = Gtk.ScrolledWindow()
        scroll.add(tree)
        vbox.pack_start(scroll, True, True, 0)

        btn_apply = Gtk.Button(label="Apply Changes")
        btn_apply.connect("clicked", self._on_apply_manage)
        vbox.pack_start(btn_apply, False, False, 0)

        return vbox

    def _refresh_store(self):
        """Reload ListStore from `apps` dict, sorted by name."""
        self.store.clear()
        for uid, entry in sorted(apps.items(), key=lambda kv: kv[1].name.lower()):
            installed_mark = "✔" if entry.installed else "✖"
            action_text = "Delete" if entry.custom else ""
            self.store.append([
                entry.desired,
                entry.name,
                entry.category,
                entry.description,
                installed_mark,
                action_text
            ])

    def _on_toggle_desired(self, widget, path):
        """Toggle the 'desired' flag when user clicks a checkbox."""
        key_list = sorted(apps.keys(), key=lambda k: apps[k].name.lower())
        uid = key_list[int(path)]
        apps[uid].desired = not apps[uid].desired
        self.store[path][0] = apps[uid].desired

    def _on_apply_manage(self, _btn):
        """Install or remove packages based on user selection."""
        to_install, to_remove = [], []
        for entry in apps.values():
            if entry.desired and not entry.installed:
                to_install.append(entry.pkg)
            if not entry.desired and entry.installed:
                to_remove.append(entry.pkg)

        # If any removals, ask remove vs purge
        if to_remove:
            dlg = Gtk.MessageDialog(
                transient_for=self,
                flags=0,
                message_type=Gtk.MessageType.QUESTION,
                buttons=Gtk.ButtonsType.NONE,
                text="Remove or purge selected applications?"
            )
            dlg.add_buttons("Remove", 1, "Purge", 2, "Cancel", 0)
            choice = dlg.run()
            dlg.destroy()
            if choice == 1:
                apt_remove(to_remove)
            elif choice == 2:
                apt_purge(to_remove)

        if to_install:
            apt_install(to_install)

        # Reload states and update UI
        load_apps()
        self._refresh_store()

    # -------------------------------------------------------------------
    # Page 2: Status (readonly list of installed apps)
    # -------------------------------------------------------------------

    def _page_status(self) -> Gtk.ScrolledWindow:
        textview = Gtk.TextView()
        textview.set_editable(False)
        buffer = textview.get_buffer()

        lines = []
        for entry in sorted(apps.values(), key=lambda e: e.name.lower()):
            mark = "✔" if entry.installed else "✖"
            lines.append(f"{mark} {entry.name} — {entry.category}")

        buffer.set_text("\n".join(lines))
        scroll = Gtk.ScrolledWindow()
        scroll.add(textview)
        return scroll

    # -------------------------------------------------------------------
    # Page 3: Launch Apps (checkbox list)
    # -------------------------------------------------------------------

    def _page_launch(self) -> Gtk.Box:
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        grid = Gtk.Grid(row_spacing=4, column_spacing=4)
        self.launch_checks = {}

        row = 0
        for entry in sorted(apps.values(), key=lambda e: e.name.lower()):
            if entry.installed:
                cb = Gtk.CheckButton(label=f"{entry.name} ({entry.category})")
                grid.attach(cb, 0, row, 1, 1)
                self.launch_checks[entry.uid] = cb
                row += 1

        scroll = Gtk.ScrolledWindow()
        scroll.add(grid)
        vbox.pack_start(scroll, True, True, 0)

        btn_launch = Gtk.Button(label="Launch Selected")
        btn_launch.connect("clicked", self._on_launch_selected)
        vbox.pack_start(btn_launch, False, False, 0)

        return vbox

    def _on_launch_selected(self, _btn):
        """Spawn subprocesses to launch each checked application."""
        for uid, cb in self.launch_checks.items():
            if cb.get_active():
                cmd = apps[uid].cmd.split()
                subprocess.Popen(cmd)
        dlg = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="Applications launched."
        )
        dlg.run()
        dlg.destroy()

    # -------------------------------------------------------------------
    # Page 4: Add Custom App
    # -------------------------------------------------------------------

    def _page_add(self) -> Gtk.Grid:
        grid = Gtk.Grid(row_spacing=4, column_spacing=6, margin=12)
        labels = ["Unique ID", "Name", "Category", "Description", "APT Package", "Launch Command"]
        self.entries = []

        # Build form fields
        for i, title in enumerate(labels):
            grid.attach(Gtk.Label(label=title), 0, i, 1, 1)
            if title == "Category":
                combo = Gtk.ComboBoxText()
                for c in CATEGORIES:
                    combo.append_text(c)
                combo.set_active(0)
                grid.attach(combo, 1, i, 1, 1)
                self.entries.append(combo)
            else:
                entry = Gtk.Entry()
                grid.attach(entry, 1, i, 1, 1)
                self.entries.append(entry)

        btn_add = Gtk.Button(label="Add to Catalog")
        btn_add.connect("clicked", self._on_add_custom)
        grid.attach(btn_add, 0, len(labels), 2, 1)

        return grid

    def _on_add_custom(self, _btn):
        """Validate form and append new custom AppEntry."""
        uid = self.entries[0].get_text().strip()
        name = self.entries[1].get_text().strip()
        category = self.entries[2].get_active_text()
        description = self.entries[3].get_text().strip()
        pkg = self.entries[4].get_text().strip()
        cmd = self.entries[5].get_text().strip()

        # Basic validation
        if not uid or not name or not pkg:
            dlg = Gtk.MessageDialog(
                transient_for=self,
                flags=0,
                message_type=Gtk.MessageType.WARNING,
                buttons=Gtk.ButtonsType.OK,
                text="ID, Name, and APT Package are required."
            )
            dlg.run()
            dlg.destroy()
            return

        if uid in apps:
            dlg = Gtk.MessageDialog(
                transient_for=self,
                flags=0,
                message_type=Gtk.MessageType.WARNING,
                buttons=Gtk.ButtonsType.OK,
                text="An application with this ID already exists."
            )
            dlg.run()
            dlg.destroy()
            return

        # Create and persist custom entry
        apps[uid] = AppEntry(uid, name, category, description, pkg, cmd, custom=True)
        save_custom_apps()
        load_apps()
        self._refresh_store()

        dlg = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="Custom application added. Restart to see changes."
        )
        dlg.run()
        dlg.destroy()

    # -------------------------------------------------------------------
    # Page 5: Help & Info
    # -------------------------------------------------------------------

    def _page_help(self) -> Gtk.ScrolledWindow:
        textview = Gtk.TextView()
        textview.set_editable(False)
        buffer = textview.get_buffer()

        help_text = f"""
PyStudioMusic v{VERSION}

Welcome to PyStudioMusic, the professional GUI manager for audio 
and music‐production software. Navigate the sections on the left:

• Manage Apps — install, remove or purge your catalog.
• Status      — quick overview of installed software.
• Launch Apps — run multiple applications at once.
• Add App     — add your own entries to the catalog.
• Help & Info — you’re here.

Configuration directory:
    {CONFIG_DIR}
Custom applications file:
    {CUSTOM_FILE}

© 2025 Luca Bocaletto — GPLv3
"""
        buffer.set_text(help_text.strip())
        scroll = Gtk.ScrolledWindow()
        scroll.add(textview)
        return scroll


def main():
    """Application entry point."""
    win = MainWindow()
    Gtk.main()


if __name__ == "__main__":
    main()
