#!/usr/bin/env bash
# Simple PyInstaller build helper for this project (macOS / Linux)
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

usage() {
  echo "Usage: $0 [gui|web|pyqt]"
  echo "  gui  -> build spx_gui.py (tkinter desktop GUI)"
  echo "  web  -> build spx_gui_web.py (Flask web GUI)"
  echo "  pyqt -> build spx_gui_pyqt.py (PyQt6/PyQt5 GUI)"
  exit 1
}

if [[ ${#} -ne 1 ]]; then
  usage
fi

MODE="$1"
if [[ "$MODE" != "gui" && "$MODE" != "web" ]]; then
  usage
fi

VENV_DIR=".packenv"
if [[ ! -d "$VENV_DIR" ]]; then
  echo "Creating virtualenv in $VENV_DIR..."
  python3 -m venv "$VENV_DIR"
fi

echo "Activating virtualenv..."
# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"

echo "Installing build dependencies..."
pip install --upgrade pip
pip install pyinstaller
if [[ -f requirements.txt ]]; then
  pip install -r requirements.txt || true
fi

if [[ "$MODE" == "gui" ]]; then
  ENTRY="spx_gui.py"
  NAME="spx_gui_app"
elif [[ "$MODE" == "pyqt" ]]; then
  ENTRY="spx_gui_pyqt.py"
  NAME="spx_gui_pyqt"
else
  ENTRY="spx_gui_web.py"
  NAME="spx_gui_web"
fi

echo "Running PyInstaller for $ENTRY..."
# One-file build; change to --onedir if you prefer a folder

# default extra args
EXTRA_ARGS=("--clean" "--onefile" "--name" "$NAME" "--add-data" "spx_sec.py:." )

# If building the PyQt GUI, attempt to locate Qt plugins and include them
if [[ "$MODE" == "pyqt" ]]; then
  echo "Detecting PyQt plugins..."
  PLUGINS_PATH=$(python3 - <<'PY'
import sys, os
try:
    from PyQt6 import QtCore
    p = os.path.join(os.path.dirname(QtCore.__file__), 'Qt', 'plugins')
    print(p)
except Exception:
    try:
        from PyQt5 import QtCore
        p = os.path.join(os.path.dirname(QtCore.__file__), 'Qt', 'plugins')
        print(p)
    except Exception:
        sys.exit(0)
PY
)

  if [[ -n "$PLUGINS_PATH" && -d "$PLUGINS_PATH" ]]; then
    echo "Found Qt plugins at: $PLUGINS_PATH"
    # Include whole plugins directory as binary data; destination inside archive is 'PyQt_plugins'
    EXTRA_ARGS+=("--add-binary" "$PLUGINS_PATH:PyQt_plugins")
  else
    echo "No Qt plugins directory detected; you may need to add platform plugins manually if the app fails at runtime."
  fi
fi

pyinstaller "${EXTRA_ARGS[@]}" "$ENTRY"

echo "Build finished. Dist output is in dist/"
echo "You can run: ./dist/$NAME"

deactivate || true
