#!/usr/bin/env bash
# build_macos.sh – Build a standalone macOS .app bundle
# ──────────────────────────────────────────────────────
# Requirements:
#   pip install pyinstaller
#   brew install python-tk  (if tkinter is missing)

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "==> Building PKT Widget (macOS)..."

pyinstaller \
  --onefile \
  --windowed \
  --name "PKT Widget" \
  --add-data "README.md:." \
  --hidden-import "zoneinfo" \
  --osx-bundle-identifier "com.pktwidget.app" \
  pkt_widget.py

echo ""
echo "✓ App bundle ready: dist/PKT Widget.app"
echo "  Move to /Applications or double-click to run."
