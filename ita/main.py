#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
StudioBand v1.0.0
Gestore completo e professionale per applicazioni audio e produzione musicale
Compatibile con Debian/Ubuntu (GTK3)
Autore: Luca Bocaletto
Licenza: GPLv3
Data: 2025-08-02
"""

import gi
import os
import subprocess
from pathlib import Path

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, Pango

# -------------------------------------------------------------------
# Costanti e configurazione
# -------------------------------------------------------------------

VERSIONE     = "1.0.0"
HOME          = Path.home()
CONFIG_DIR    = HOME / ".studioband"
CUSTOM_FILE   = CONFIG_DIR / "apps.custom"

# Categorie possibili
CATEGORIE = [
    "DAW", "Editor", "Server", "Sintetizzatore",
    "Host Plugin", "Looper", "DJ", "Patchbay",
    "Suite", "Utility"
]

# Catalogo built-in: 
# id → (Nome, Categoria, Descrizione breve, pacchetto APT, comando di avvio)
BUILTIN_APPS = {
    "ardour":      ("Ardour",         "DAW",             "DAW professionale",      "ardour",       "ardour"),
    "lmms":        ("LMMS",           "DAW",             "Produzione pattern",     "lmms",         "lmms"),
    "qtractor":    ("Qtractor",       "DAW",             "DAW JACK-centric",       "qtractor",     "qtractor"),
    "rosegarden":  ("Rosegarden",     "DAW",             "MIDI e notazione",       "rosegarden",   "rosegarden"),
    "musescore":   ("MuseScore",      "Editor",          "Notazione musicale",     "musescore3",   "musescore3"),
    "audacity":    ("Audacity",       "Editor",          "Editor audio",           "audacity",     "audacity"),
    "jackd2":      ("JACK2",          "Server",          "Server audio a bassa latenza","jackd2",  "jackd"),
    "pipewire":    ("PipeWire",       "Server",          "Server audio moderno",   "pipewire",     "pipewire"),
    "pulseaudio":  ("PulseAudio",     "Server",          "Server audio tradizionale","pulseaudio",  "pulseaudio"),
    "hydrogen":    ("Hydrogen",       "Sintetizzatore",  "Drum machine avanzata",  "hydrogen",     "hydrogen"),
    "fluidsynth":  ("FluidSynth",     "Sintetizzatore",  "Sintetizzatore SoundFont","fluidsynth", "fluidsynth"),
    "qsynth":      ("Qsynth",         "Sintetizzatore",  "GUI per FluidSynth",     "qsynth",       "qsynth"),
    "carla":       ("Carla",          "Host Plugin",     "Host plugin VST/LV2",    "carla",        "carla"),
    "sooperlooper":("SooperLooper",   "Looper",          "Looping live",           "sooperlooper","sooperlooper"),
    "mixxx":       ("Mixxx",          "DJ",              "Software per DJ",        "mixxx",        "mixxx"),
    "patchage":    ("Patchage",       "Patchbay",        "Patch bay LV2/JACK",     "patchage",     "patchage"),
    "cadence":     ("Cadence",        "Suite",           "Suite KXStudio",         "cadence",      "cadence"),
    "ffmpeg":      ("FFmpeg",         "Utility",         "Framework multimediale", "ffmpeg",       "ffmpeg"),
    "sox":         ("SoX",            "Utility",         "Toolkit audio",          "sox",          "sox"),
    "ecasound":    ("Ecasound",       "Utility",         "Registratore multitraccia","ecasound",   "ecasound"),
    "alsa-utils":  ("ALSA Utils",     "Utility",         "Mixer e strumenti MIDI", "alsa-utils",   "alsamixer"),
}

# Runtime state
class AppEntry:
    def __init__(self, uid, nome, categoria, descrizione, pkg, cmd, custom=False):
        self.uid         = uid
        self.nome        = nome
        self.categoria   = categoria
        self.descrizione = descrizione
        self.pkg         = pkg
        self.cmd         = cmd
        self.custom      = custom
        self.installed   = False
        self.desired     = False

apps: dict = {}   # uid → AppEntry

# -------------------------------------------------------------------
# Funzioni di utilità
# -------------------------------------------------------------------

def run_cmd(*cmd, check=False):
    return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=check)

def is_installed(pkg: str) -> bool:
    res = run_cmd("dpkg-query", "-W", "-f=${Status}", pkg)
    return res.stdout.decode().startswith("install ok installed")

def apt_install(pkgs: list):
    run_cmd("sudo", "apt-get", "update", "-qq", check=True)
    run_cmd("sudo", "apt-get", "install", "-y", *pkgs, check=True)

def apt_remove(pkgs: list):
    run_cmd("sudo", "apt-get", "remove", "-y", *pkgs, check=True)

def apt_purge(pkgs: list):
    run_cmd("sudo", "apt-get", "purge", "-y", *pkgs, check=True)

def ensure_config():
    CONFIG_DIR.mkdir(exist_ok=True)

def load_apps():
    """Carica catalogo built-in più personalizzate e aggiorna stati."""
    apps.clear()
    # built-in
    for uid, (nome, cat, desc, pkg, cmd) in BUILTIN_APPS.items():
        apps[uid] = AppEntry(uid, nome, cat, desc, pkg, cmd, custom=False)
    # personalizzate
    if CUSTOM_FILE.exists():
        for line in CUSTOM_FILE.read_text(encoding="utf-8").splitlines():
            parts = line.split("|")
            if len(parts) == 6:
                uid, nome, cat, desc, pkg, cmd = parts
                apps[uid] = AppEntry(uid, nome, cat, desc, pkg, cmd, custom=True)
    # aggiorna stati
    for a in apps.values():
        a.installed = is_installed(a.pkg)
        a.desired   = a.installed

def save_custom():
    """Salva solo le app custom sul file."""
    lines = []
    for a in apps.values():
        if a.custom:
            line = "|".join((a.uid, a.nome, a.categoria, a.descrizione, a.pkg, a.cmd))
            lines.append(line)
    CUSTOM_FILE.write_text("\n".join(lines), encoding="utf-8")

# -------------------------------------------------------------------
# Interfaccia GTK
# -------------------------------------------------------------------

class MainWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="StudioBand")
        self.set_default_size(800, 500)
        self.set_border_width(6)
        self._setup_headerbar()
        ensure_config()
        load_apps()
        self._build_ui()
        self.show_all()

    def _setup_headerbar(self):
        hb = Gtk.HeaderBar()
        hb.props.show_close_button = True
        hb.props.title            = "StudioBand"
        hb.props.subtitle         = f"v{VERSIONE}"
        self.set_titlebar(hb)

    def _build_ui(self):
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        self.add(hbox)

        # Menu laterale con Gtk.StackSwitcher
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.stack.set_transition_duration(200)

        switcher = Gtk.StackSwitcher()
        switcher.set_stack(self.stack)
        switcher.set_margin_bottom(10)
        switcher.set_hexpand(True)

        menu = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        menu.pack_start(switcher, False, False, 0)

        hbox.pack_start(menu, False, False, 0)
        hbox.pack_start(self.stack, True, True, 0)

        # Pagine
        self.stack.add_titled(self._page_manage(),   "manage",   "Gestione App")
        self.stack.add_titled(self._page_status(),   "status",   "Stato App")
        self.stack.add_titled(self._page_launch(),   "launch",   "Avvio App")
        self.stack.add_titled(self._page_add(),      "add",      "Aggiungi App")
        self.stack.add_titled(self._page_help(),     "help",     "Guida & Info")

    # -------------------------------------------------------------------
    # Pagina 1: Gestione App (install/remove, modifica catalogo)
    # -------------------------------------------------------------------
    def _page_manage(self):
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        # TreeView catalogo
        cols = ["Installa", "Nome", "Categoria", "Descrizione", "Installato", "Azione"]
        self.store = Gtk.ListStore(bool, str, str, str, str, object)
        self._populate_store()

        tree = Gtk.TreeView(model=self.store)
        tree.set_hexpand(True)
        tree.set_vexpand(True)
        # col 0: checkbox desired
        renderer_toggle = Gtk.CellRendererToggle()
        renderer_toggle.connect("toggled", self.on_toggle_desired)
        col0 = Gtk.TreeViewColumn("Installa", renderer_toggle, active=0)
        tree.append_column(col0)
        # col 1-4: testo
        for i, title in enumerate(cols[1:5], start=1):
            renderer = Gtk.CellRendererText()
            col = Gtk.TreeViewColumn(title, renderer, text=i)
            tree.append_column(col)
        # col 4: stato installato
        # col 5: pulsante Azione (Elimina custom)
        renderer_btn = Gtk.CellRendererText()
        col5 = Gtk.TreeViewColumn("Azione", renderer_btn, text=5)
        tree.append_column(col5)

        sw = Gtk.ScrolledWindow()
        sw.add(tree)
        vbox.pack_start(sw, True, True, 0)

        btn_apply = Gtk.Button(label="Applica modifiche")
        btn_apply.connect("clicked", self.on_apply_manage)
        vbox.pack_start(btn_apply, False, False, 0)
        return vbox

    def _populate_store(self):
        self.store.clear()
        for uid, a in sorted(apps.items(), key=lambda x: x[1].nome.lower()):
            stato = "✔" if a.installed else "✖"
            azione = "Elimina" if a.custom else ""
            self.store.append([a.desired, a.nome, a.categoria, a.descrizione, stato, azione])

    def on_toggle_desired(self, widget, path):
        uid = list(sorted(apps.keys(), key=lambda x: apps[x].nome.lower()))[int(path)]
        apps[uid].desired = not apps[uid].desired
        self.store[path][0] = apps[uid].desired

    def on_apply_manage(self, _btn):
        to_install, to_remove = [], []
        for a in apps.values():
            if a.desired and not a.installed:
                to_install.append(a.pkg)
            if not a.desired and a.installed:
                to_remove.append(a.pkg)
        if to_remove:
            dlg = Gtk.MessageDialog(self, 0, Gtk.MessageType.QUESTION,
                Gtk.ButtonsType.NONE,
                "Vuoi rimuovere o eliminare (purge) le app selezionate?")
            dlg.add_buttons("Rimuovi", 1, "Purge", 2, "Annulla", 0)
            resp = dlg.run(); dlg.destroy()
            if resp == 1:
                apt_remove(to_remove)
            elif resp == 2:
                apt_purge(to_remove)
        if to_install:
            apt_install(to_install)
        load_apps()
        self._populate_store()

    # -------------------------------------------------------------------
    # Pagina 2: Stato App
    # -------------------------------------------------------------------
    def _page_status(self):
        tv = Gtk.TextView()
        tv.set_editable(False)
        buf = tv.get_buffer()
        testo = []
        for a in sorted(apps.values(), key=lambda x: x.nome.lower()):
            mark = "✔" if a.installed else "✖"
            testo.append(f"{mark} {a.nome} — {a.categoria}")
        buf.set_text("\n".join(testo))
        sw = Gtk.ScrolledWindow()
        sw.add(tv)
        return sw

    # -------------------------------------------------------------------
    # Pagina 3: Avvio App
    # -------------------------------------------------------------------
    def _page_launch(self):
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        grid = Gtk.Grid(row_spacing=4, column_spacing=4)

        self.launch_checks = {}
        row = 0
        for a in sorted(apps.values(), key=lambda x: x.nome.lower()):
            if a.installed:
                cb = Gtk.CheckButton(label=f"{a.nome} ({a.categoria})")
                grid.attach(cb, 0, row, 1, 1)
                self.launch_checks[a.uid] = cb
                row += 1

        sw = Gtk.ScrolledWindow()
        sw.add(grid)
        vbox.pack_start(sw, True, True, 0)
        btn = Gtk.Button(label="Avvia selezionate")
        btn.connect("clicked", self.on_launch)
        vbox.pack_start(btn, False, False, 0)
        return vbox

    def on_launch(self, _btn):
        for uid, cb in self.launch_checks.items():
            if cb.get_active():
                cmd = apps[uid].cmd.split()
                subprocess.Popen(cmd)
        dlg = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO,
            Gtk.ButtonsType.OK, "Applicazioni avviate.")
        dlg.run(); dlg.destroy()

    # -------------------------------------------------------------------
    # Pagina 4: Aggiungi App personalizzata
    # -------------------------------------------------------------------
    def _page_add(self):
        grid = Gtk.Grid(row_spacing=4, column_spacing=6, margin=12)
        labels = ["ID unico", "Nome", "Categoria", "Descrizione", "Pacchetto APT", "Comando di avvio"]
        self.entries = []
        for i, txt in enumerate(labels):
            grid.attach(Gtk.Label(label=txt), 0, i, 1, 1)
            ent = Gtk.Entry()
            if txt == "Categoria":
                combo = Gtk.ComboBoxText()
                for c in CATEGORIE:
                    combo.append_text(c)
                combo.set_active(0)
                grid.attach(combo, 1, i, 1, 1)
                self.entries.append(combo)
                continue
            grid.attach(ent, 1, i, 1, 1)
            self.entries.append(ent)
        btn = Gtk.Button(label="Aggiungi alla lista")
        btn.connect("clicked", self.on_add_custom)
        grid.attach(btn, 0, len(labels), 2, 1)
        return grid

    def on_add_custom(self, _btn):
        uid      = self.entries[0].get_text().strip()
        nome     = self.entries[1].get_text().strip()
        categoria= self.entries[2].get_active_text()
        descr    = self.entries[3].get_text().strip()
        pkg      = self.entries[4].get_text().strip()
        cmd      = self.entries[5].get_text().strip()
        if not uid or not pkg or not nome:
            dlg = Gtk.MessageDialog(self, 0, Gtk.MessageType.WARNING,
                Gtk.ButtonsType.OK, "ID, Nome e Pacchetto APT sono obbligatori.")
            dlg.run(); dlg.destroy()
            return
        if uid in apps:
            dlg = Gtk.MessageDialog(self, 0, Gtk.MessageType.WARNING,
                Gtk.ButtonsType.OK, "ID già esistente.")
            dlg.run(); dlg.destroy()
            return
        apps[uid] = AppEntry(uid, nome, categoria, descr, pkg, cmd, custom=True)
        save_custom()
        load_apps()
        self._populate_store()
        dlg = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO,
            Gtk.ButtonsType.OK, "Applicazione personalizzata aggiunta.")
        dlg.run(); dlg.destroy()

    # -------------------------------------------------------------------
    # Pagina 5: Guida & Info
    # -------------------------------------------------------------------
    def _page_help(self):
        tv = Gtk.TextView()
        tv.set_editable(False)
        buf = tv.get_buffer()
        testo = f"""
StudioBand v{VERSIONE}

Navigazione:
• Gestione App — installa, rimuovi o purge delle applicazioni.
• Stato App     — overview rapida delle installazioni.
• Avvio App     — avvia più applicazioni contemporaneamente.
• Aggiungi App  — aggiungi software personalizzato al catalogo.
• Guida & Info  — questa pagina.

Come funziona:
1. In Gestione App spunta le caselle per definire quali app installare o rimuovere.
2. Clicca Applica modifiche per eseguire apt-get.
3. In Aggiungi App inserisci i dettagli e salva; le app custom vengono mantenute in ~/.studioband/apps.custom.
4. Riavvia StudioBand per vedere le modifiche al catalogo.

File di configurazione:
{CUSTOM_FILE}

© 2025 Luca Bocaletto — GPLv3
"""
        buf.set_text(testo.strip())
        sw = Gtk.ScrolledWindow()
        sw.add(tv)
        return sw

# -------------------------------------------------------------------
# Avvio applicazione
# -------------------------------------------------------------------

def main():
    win = MainWindow()
    win.connect("destroy", Gtk.main_quit)
    Gtk.main()

if __name__ == "__main__":
    main()
