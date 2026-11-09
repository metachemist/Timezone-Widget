@echo off
REM build_windows.bat – Build a standalone Windows .exe
REM ─────────────────────────────────────────────────────
REM Requirements:
REM   pip install pyinstaller tzdata

echo =^> Building PKT Widget (Windows)...

pyinstaller ^
  --onefile ^
  --windowed ^
  --name "PKT-Widget" ^
  --add-data "README.md;." ^
  --hidden-import "zoneinfo" ^
  --hidden-import "tzdata" ^
  --hidden-import "tzdata.zoneinfo" ^
  pkt_widget.py

echo.
echo Done! Binary at: dist\PKT-Widget.exe
