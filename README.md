# PyStudioMusic

[![License: GPLv3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE) [![Platform](https://img.shields.io/badge/Platform-Debian%2FUbuntu-orange.svg)](https://www.debian.org/)

Professional GTK3 GUI manager for audio & music-production software on Debian and Ubuntu.

---

## Table of Contents

- [Description](#description)  
- [Features](#features)  
- [Screenshots](#screenshots)  
- [Requirements](#requirements)  
- [Installation](#installation)  
- [Usage](#usage)  
- [Configuration](#configuration)  
- [Custom Applications](#custom-applications)  
- [Contributing](#contributing)  
- [License](#license)  
- [Acknowledgments](#acknowledgments)  

---

## Description

**PyStudioMusic** is a GTK3-based desktop application that lets you easily install, remove, launch and manage your favorite audio and music-production tools. It targets Debian/Ubuntu users who want a polished, intuitive interface for handling DAWs, editors, servers, synthesizers and more.

---

## Features

- Browse a curated catalog of popular audio apps  
- Install, remove or purge applications with one click  
- View real-time status (installed/not-installed)  
- Launch multiple apps simultaneously  
- Add, edit or remove custom applications to suit your workflow  
- Organized by category (DAW, Editor, Server, Synthesizer, etc.)  
- Built-in help & documentation panel  
- Config files stored in `~/.pystudiomusic` for easy backup  

---

## Screenshots

<!-- Replace the URLs below with actual screenshots after capturing them -->

| Main Window | Add Custom App |
| ----------- | -------------- |
| ![Manage Apps tab](docs/screenshots/manage.png) | ![Add App tab](docs/screenshots/add.png) |

| Status & Launch | Help Panel |
| --------------- | ---------- |
| ![Status tab](docs/screenshots/status.png) | ![Help tab](docs/screenshots/help.png) |

---

## Requirements

- Debian 11+ or Ubuntu 20.04+  
- Python 3.8 or higher  
- GTK 3 (gir1.2-gtk-3.0)  
- PyGObject for Python 3 (python3-gi, python3-gi-cairo)  

---

## Installation

1. Clone the repository:  
   ```bash
   git clone https://github.com/yourusername/PyStudioMusic.git
   cd PyStudioMusic
   ```

2. Install system dependencies:  
   ```bash
   sudo apt update
   sudo apt install -y python3-gi python3-gi-cairo gir1.2-gtk-3.0
   ```

3. Make the main script executable:  
   ```bash
   chmod +x PyStudioMusic.py
   ```

4. (Optional) Install a desktop entry for easy launching:

   ```bash
   sudo cp data/PyStudioMusic.desktop /usr/share/applications/
   update-desktop-database
   ```

---

## Usage

Run the application from a terminal or via your desktop menu:

```bash
./PyStudioMusic.py
```

Or, if you installed the desktop entry:

- Search for **PyStudioMusic** in your applications menu and launch.

---

## Configuration

All user data and custom entries are stored under:

```
~/.pystudiomusic/
└── apps.custom      # Custom app definitions
```

You can back up or edit these files by hand if needed. The GUI will reload them on next start.

---

## Custom Applications

1. Go to the **Add App** section in the side menu.  
2. Fill in:
   - **Unique ID:** machine-friendly identifier  
   - **Name:** display name  
   - **Category:** select from the dropdown  
   - **Description:** short summary  
   - **APT Package:** Debian package name  
   - **Launch Command:** the shell command to start the app  
3. Click **Add to Catalog**.  
4. The new entry appears in **Manage Apps** (restart the app if necessary).

---

## Contributing

Contributions are very welcome! Please:

1. Fork the repository  
2. Create a feature branch:  
   ```bash
   git checkout -b feature/YourFeatureName
   ```
3. Commit your changes and push:  
   ```bash
   git commit -m "Add some feature"
   git push origin feature/YourFeatureName
   ```
4. Open a Pull Request describing your work.

Please follow the existing code style and include appropriate comments and tests.

---

## License

This project is licensed under the **GPLv3**. See the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- Thanks to the open-source Linux audio community for maintaining amazing tools  
- Icons by [GNOME Icon Library](https://www.gnome.org)  
- Inspired by the original StudioBand shell script by Luca Bocaletto
