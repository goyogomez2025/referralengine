"""
Yirra Care Agents — Desktop Launcher
Single-instance: double-click always opens the browser (starts once, re-uses after).
Auto-shutdown: exits after 10 minutes of no browser connections.
"""
import os, sys, socket, threading, time, webbrowser, traceback, subprocess
from pathlib import Path

# One file that stores the running server's port  (lives in user home, survives app moves)
PORT_FILE = Path.home() / ".yirracare.port"


def get_base_dir() -> Path:
    if not getattr(sys, "frozen", False):
        return Path(__file__).resolve().parent
    exe = Path(sys.executable).resolve()
    if sys.platform == "darwin":
        resources = exe.parent.parent / "Resources"
        if resources.exists() and (resources / "app").exists():
            return resources
    return exe.parent


def _server_up(port: int) -> bool:
    """Return True if a Streamlit server is responding on this port."""
    try:
        import urllib.request
        r = urllib.request.urlopen(
            f"http://localhost:{port}/_stcore/health", timeout=2
        )
        return r.status == 200
    except Exception:
        return False


def find_free_port(start: int = 8501) -> int:
    for p in range(start, start + 20):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    return start


def _open_browser(port: int) -> None:
    url = f"http://localhost:{port}"
    for _ in range(40):
        time.sleep(1)
        if _server_up(port):
            webbrowser.open(url)
            return
    webbrowser.open(url)


def _idle_watchdog(port: int, idle_minutes: int = 10) -> None:
    """
    Monitor active browser connections.
    If nobody has been connected for idle_minutes, shut the server down.
    """
    idle_secs = 0
    interval  = 30          # check every 30 s
    threshold = idle_minutes * 60
    lsof_env  = {**os.environ, "PATH": "/usr/bin:/bin:/usr/sbin:/sbin"}
    while True:
        time.sleep(interval)
        try:
            r = subprocess.run(
                ["lsof", "-i", f"tcp:{port}", "-n", "-P"],
                capture_output=True, text=True, timeout=5, env=lsof_env
            )
            # ESTABLISHED = active browser connection
            active = r.stdout.count("ESTABLISHED")
            idle_secs = 0 if active > 0 else idle_secs + interval
            if idle_secs >= threshold:
                PORT_FILE.unlink(missing_ok=True)
                os._exit(0)         # force-quit the entire Streamlit process
        except Exception:
            idle_secs = 0           # if we can't check, assume active


def _dialog(title: str, msg: str) -> None:
    if sys.platform == "darwin":
        safe = msg.replace('"', '\\"')
        os.system(
            f'osascript -e \'display dialog "{safe}" '
            f'with title "{title}" buttons {{"OK"}} default button "OK"\''
        )


def main() -> None:
    base_dir = get_base_dir()
    os.chdir(str(base_dir))

    # ── .env guard ───────────────────────────────────────────────────────────
    if not (base_dir / ".env").exists():
        _dialog(
            "Setup Required",
            f"No .env file found in:\\n{base_dir}\\n\\n"
            "Copy .env.template to .env and add your OpenAI key."
        )
        if sys.platform == "darwin":
            os.system(f'open "{base_dir}"')
        return

    # ── Single-instance check ────────────────────────────────────────────────
    # If a server is already running (browser was just closed), re-open the browser
    # instead of launching a second instance → fixes "not open anymore" error.
    if PORT_FILE.exists():
        try:
            port = int(PORT_FILE.read_text().strip())
            if _server_up(port):
                webbrowser.open(f"http://localhost:{port}")
                return          # ← already running, just open browser and exit
        except Exception:
            pass
        PORT_FILE.unlink(missing_ok=True)   # stale file → start fresh

    # ── Start a new server ───────────────────────────────────────────────────
    port = find_free_port(8501)
    PORT_FILE.write_text(str(port))

    threading.Thread(target=_open_browser,    args=(port,), daemon=True).start()
    threading.Thread(target=_idle_watchdog,   args=(port,), daemon=True).start()

    sys.argv = [
        "streamlit", "run",
        str(base_dir / "app" / "ui" / "dashboard.py"),
        f"--server.port={port}",
        "--server.headless=true",
        "--global.developmentMode=false",
        "--browser.gatherUsageStats=false",
        "--server.fileWatcherType=none",
    ]
    from streamlit.web import cli as stcli
    try:
        sys.exit(stcli.main())
    finally:
        PORT_FILE.unlink(missing_ok=True)   # clean up on normal exit


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        tb  = traceback.format_exc()
        log = Path.home() / "Desktop" / "YirraCare_error.log"
        try:
            log.write_text(tb)
        except Exception:
            pass
        _dialog(
            "Yirra Care Agents — Error",
            f"The app failed to start.\\nError log saved to:\\n{log}"
        )
        if sys.platform == "darwin":
            os.system(f'open "{log}"')
