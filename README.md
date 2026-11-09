# 🇵🇰 PKT Time Zone Converter Widget

A lightweight, cross-platform, **frameless desktop widget** that shows the live
Pakistan Standard Time (PKT · UTC+5) clock and converts any global IANA time
zone into PKT — built with pure Python + Tkinter (no Electron, no browser).

---

## ✨ Features

| Feature | Detail |
|---|---|
| **Live PKT Clock** | Updates every second in 12-hour (AM/PM) format |
| **400+ Timezones** | All IANA zones loaded from Python's `zoneinfo` stdlib |
| **Fuzzy Search** | Type city, country, or region name — matches filtered in real time |
| **Time Converter** | 12h spinbox input with AM/PM selector → instant PKT result |
| **Day Offset** | Shows ▲ Next Day / ▼ Prev Day / Same Day |
| **Frameless UI** | Dark-mode floating widget, click-and-drag to reposition |
| **Always-on-Top** | Pin (📌) toggle to keep widget above other windows |
| **Low RAM** | ~25 MB; no browser, no Electron |
| **Cross-platform** | Windows 10+, macOS 12+, Ubuntu/Fedora/Arch |

---

## 🚀 Quick Start (Run from Source)

### Prerequisites

#### All Platforms
- **Python 3.9+** — [python.org/downloads](https://www.python.org/downloads/)
- **Tkinter** — usually bundled, see platform notes below
- **tzdata** — required on Windows (see below)

#### Linux (Debian/Ubuntu)
```bash
sudo apt update
sudo apt install python3-tk tk-dev
# zoneinfo is in stdlib, tzdata is the system timezone db
```

#### Linux (Fedora/RHEL)
```bash
sudo dnf install python3-tkinter
```

#### Linux (Arch)
```bash
sudo pacman -S tk
```

#### macOS
```bash
# Tkinter comes with python.org builds
# If you used Homebrew Python and tkinter is missing:
brew install python-tk
```

#### Windows 10/11
Tkinter ships with the official python.org installer.
You **must** also install the `tzdata` package (Windows lacks a system tz database):
```powershell
pip install tzdata
```

---

### Run the Widget
```bash
# Clone or download the project, then:
cd pkt-widget
python pkt_widget.py
```

---

## 🖱️ Usage

| Action | How |
|---|---|
| **Move widget** | Click-and-drag anywhere on the dark background or title bar |
| **Search timezone** | Click the search box, type a city/country/region name |
| **Select timezone** | Click a result in the dropdown, or press ↑/↓ then Enter |
| **Set time** | Use the spinbox arrows or type directly in the H / MM fields |
| **Toggle AM/PM** | Click the AM/PM dropdown |
| **Pin on top** | Click 📌 to toggle Always-on-Top |
| **Close** | Click ✕ |

### Search Examples

| You type | Matches |
|---|---|
| `new york` | `America/New_York` |
| `london` | `Europe/London` |
| `tokyo` | `Asia/Tokyo` |
| `dubai` | `Asia/Dubai` |
| `pak` | `Asia/Karachi`, `Asia/Qyzylorda`… |
| `america` | All Americas zones |
| `utc` | `UTC` |

---

## 📦 Build Standalone Executables

Install PyInstaller first:
```bash
pip install pyinstaller
```

### Linux Binary
```bash
chmod +x build_linux.sh
./build_linux.sh
# → dist/PKT-Widget   (single self-contained binary)
```

### macOS `.app` Bundle
```bash
chmod +x build_macos.sh
./build_macos.sh
# → dist/PKT Widget.app   (drag to /Applications)
```

### Windows `.exe`
```powershell
pip install tzdata pyinstaller
.\build_windows.bat
# → dist\PKT-Widget.exe   (double-click to run)
```

> **Note for Windows builds:** The `--hidden-import tzdata` flag in
> `build_windows.bat` bundles the timezone database inside the `.exe` so it
> works on machines without Python installed.

---

## 🏗️ Project Structure

```
widget/
├── pkt_widget.py        # Main application (single file)
├── pyproject.toml       # Package metadata
├── build_linux.sh       # Linux PyInstaller build script
├── build_macos.sh       # macOS PyInstaller build script
├── build_windows.bat    # Windows PyInstaller build script
└── README.md            # This file
```

---

## 🔧 Customisation

All colours, fonts, and dimensions are defined as constants near the top of
`pkt_widget.py`:

```python
W, H = 360, 300          # widget size in pixels
BG_DARK  = "#1a1a2e"     # background colour
ACCENT   = "#e94560"     # red accent (AM/PM labels)
GREEN    = "#00d4aa"     # PKT result colour
```

Change `W` / `H` to resize, or swap any hex colour to retheme.

---

## 🐛 Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError: No module named 'tkinter'` | Install `python3-tk` (Linux) or `python-tk` via Homebrew (macOS) |
| `ZoneInfoNotFoundError` on Windows | `pip install tzdata` |
| Widget appears behind all windows | Click the 📌 pin button to enable Always-on-Top |
| Dropdown doesn't appear | Click inside the search box first |

---

## 📄 License

MIT — free to use, modify, and distribute.
