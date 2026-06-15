"""
Yirra Care Agents — Desktop Launcher
======================================
Entry point when running as a compiled executable (PyInstaller).
Starts the Streamlit server on localhost and opens the browser.

Usage (dev):  python launcher.py
Usage (dist): double-click the .exe / .app
"""
import os
import sys
import socket
import threading
import time
import webbrowser
from pathlib import Path


# ─── Locate the app's base directory ────────────────────────────────────────

def get_base_dir() -> Path:
    """
    Returns the directory containing app/, .streamlit/, prompts/, .env etc.

    • Dev mode (running as .py script) → folder containing this file
    • macOS .app bundle (PyInstaller BUNDLE+COLLECT):
        sys.executable = Contents/MacOS/<exe>
        All bundled files live at Contents/Resources/   ← use this
        sys._MEIPASS is NOT set in --onedir/BUNDLE mode
    • Windows --onedir:
        All files are in the same folder as the .exe
    """
    if not getattr(sys, "frozen", False):
        return Path(__file__).resolve().parent

    exe = Path(sys.executable).resolve()

    if sys.platform == "darwin":
        # Navigate: Contents/MacOS/<exe>  →  Contents/  →  Contents/Resources/
        resources = exe.parent.parent / "Resources"
        if resources.exists() and (resources / "app").exists():
            return resources

    # Windows / fallback: files sit next to the executable
    return exe.parent


# ─── Browser helper ─────────────────────────────────────────────────────────

def _port_open(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        return s.connect_ex(("127.0.0.1", port)) == 0


def _wait_and_open(port: int) -> None:
    """Poll until Streamlit accepts connections, then open the browser."""
    for _ in range(40):          # wait up to 40 s
        time.sleep(1)
        if _port_open(port):
            webbrowser.open(f"http://localhost:{port}")
            return
    webbrowser.open(f"http://localhost:{port}")   # open anyway


# ─── Main ────────────────────────────────────────────────────────────────────

def main() -> None:
    port     = 8501
    base_dir = get_base_dir()

    # All relative paths in the app resolve from here
    os.chdir(str(base_dir))

    # Verify .env exists so the app doesn't crash silently
    if not (base_dir / ".env").exists():
        print("=" * 60)
        print("  Yirra Care Agents — First Run Setup")
        print("=" * 60)
        print(f"\n  No .env file found in:\n  {base_dir}\n")
        print("  Please copy .env.template → .env and fill in your API keys.")
        print("  Then double-click the app again.\n")
        if sys.platform == "win32":
            os.startfile(str(base_dir))   # open folder in Explorer
        input("  Press Enter to exit...")
        return

    # Open browser once Streamlit is ready
    threading.Thread(target=_wait_and_open, args=(port,), daemon=True).start()

    # ── Start Streamlit via its internal CLI ──────────────────────────────
    # Using the CLI directly (not subprocess) is the only reliable way inside
    # a PyInstaller bundle because there is no separate python interpreter.
    sys.argv = [
        "streamlit", "run",
        str(base_dir / "app" / "ui" / "dashboard.py"),
        f"--server.port={port}",
        "--server.headless=true",
        "--global.developmentMode=false",   # required when running inside PyInstaller
        "--browser.gatherUsageStats=false",
        "--server.fileWatcherType=none",
    ]

    from streamlit.web import cli as stcli
    sys.exit(stcli.main())


if __name__ == "__main__":
    main()
