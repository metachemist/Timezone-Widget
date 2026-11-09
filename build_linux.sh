#!/usr/bin/env bash
# build_linux.sh – Build a standalone Linux binary
# ─────────────────────────────────────────────────
# Requirements:
#   pip install pyinstaller
#   sudo apt install python3-tk tk-dev   (Debian/Ubuntu)
#   sudo dnf install python3-tkinter     (Fedora)

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "==> Building PKT Widget (Linux)..."

pyinstaller \
  --onefile \
  --windowed \
  --name "PKT-Widget" \
  --add-data "README.md:." \
  --hidden-import "zoneinfo" \
  --hidden-import "zoneinfo.tzdata" \
  pkt_widget.py

echo ""
echo "✓ Binary ready: dist/PKT-Widget"
echo "  Run with: ./dist/PKT-Widget"
