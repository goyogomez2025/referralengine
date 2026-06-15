"""
Yirra Care Agents — Desktop Launcher
======================================
TWO-PROCESS ARCHITECTURE (fixes the macOS double-click bug):

  LAUNCHER mode (default, double-click):
    - Checks if Streamlit is already running (via ~/.yirracare.port)
    - If YES  -> opens browser -> exits immediately  <- macOS sees app as "closed"
    - If NO   -> writes port file, spawns DETACHED server subprocess -> waits for
                server to be ready -> opens browser -> exits immediately

  SERVER mode (env YIRRA_SERVER=1, spawned by launcher):
    - Runs Streamlit inline (blocking)
    - Idle watchdog: auto-shuts down after 10 min with no browser connections
    - Cleans up port file on exit

Because the launcher ALWAYS exits quickly, macOS never blocks a second
double-click. The Streamlit server is just a background process.
"""
import os, sys, socket, threading, time, webbrowser, traceback, subprocess
from pathlib import Path

PORT_FILE = Path.home() / ".yirracare.port"
LOG_FILE  = Path.home() / "Library" / "Logs" / "YirraCare.log"
IDLE_SECS = 10 * 60


def get_base_dir() -> Path:
    env = os.environ.get("YIRRA_BASEDIR")
    if env:
        return Path(env)
    if not getattr(sys, "frozen", False):
        return Path(__file__).resolve().parent
    exe = Path(sys.executable).resolve()
    if sys.platform == "darwin":
        resources = exe.parent.parent / "Resources"
        if resources.exists() and (resources / "app").exists():
            return resources
    return exe.parent


def _server_up(port: int) -> bool:
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


def _dialog(title: str, msg: str) -> None:
    if sys.platform == "darwin":
        safe = msg.replace("\\", "\\\\").replace('"', '\\"')
        os.system(
            "osascript -e 'display dialog \"" + safe + "\" "
            "with title \"" + title + "\" buttons {\"OK\"} default button \"OK\"'"
        )


# ---- SERVER MODE ------------------------------------------------------------

def _idle_watchdog(port: int) -> None:
    idle = 0
    step = 30
    env  = {**os.environ, "PATH": "/usr/bin:/bin:/usr/sbin:/sbin"}
    while True:
        time.sleep(step)
        try:
            r = subprocess.run(
                ["lsof", "-i", f"tcp:{port}", "-n", "-P"],
                capture_output=True, text=True, timeout=5, env=env,
            )
            idle = 0 if r.stdout.count("ESTABLISHED") > 0 else idle + step
            if idle >= IDLE_SECS:
                PORT_FILE.unlink(missing_ok=True)
                os._exit(0)
        except Exception:
            idle = 0


def run_server_mode(base_dir: Path) -> None:
    try:
        port = int(PORT_FILE.read_text().strip())
    except Exception:
        return

    threading.Thread(target=_idle_watchdog, args=(port,), daemon=True).start()

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
        stcli.main()
    finally:
        PORT_FILE.unlink(missing_ok=True)


# ---- LAUNCHER MODE ----------------------------------------------------------

def run_launcher_mode(base_dir: Path) -> None:
    if not (base_dir / ".env").exists():
        _dialog(
            "Setup Required",
            f"No .env file found in: {base_dir}. Copy .env.template to .env and add your OpenAI key.",
        )
        if sys.platform == "darwin":
            os.system(f'open "{base_dir}"')
        return

    if PORT_FILE.exists():
        try:
            port = int(PORT_FILE.read_text().strip())
            for _ in range(5):
                if _server_up(port):
                    webbrowser.open(f"http://localhost:{port}")
                    return
                time.sleep(1)
        except Exception:
            pass
        PORT_FILE.unlink(missing_ok=True)

    port = find_free_port(8501)
    PORT_FILE.write_text(str(port))

    exe = str(Path(sys.executable).resolve())
    cmd = [exe] if getattr(sys, "frozen", False) else [exe, str(Path(__file__).resolve())]

    env = {**os.environ, "YIRRA_SERVER": "1", "YIRRA_BASEDIR": str(base_dir)}
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    log_fd = open(str(LOG_FILE), "w")
    subprocess.Popen(
        cmd,
        env=env,
        start_new_session=True,
        stdout=log_fd,
        stderr=log_fd,
        cwd=str(base_dir),
    )
    log_fd.close()

    for _ in range(40):
        time.sleep(1)
        if _server_up(port):
            webbrowser.open(f"http://localhost:{port}")
            return

    PORT_FILE.unlink(missing_ok=True)
    _dialog("Yirra Care Agents", f"Server did not start in 40 seconds. Check log: {LOG_FILE}")


# ---- ENTRY POINT ------------------------------------------------------------

def main() -> None:
    base_dir = get_base_dir()
    os.chdir(str(base_dir))
    if os.environ.get("YIRRA_SERVER") == "1":
        run_server_mode(base_dir)
    else:
        run_launcher_mode(base_dir)


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
        _dialog("Yirra Care Agents — Error", f"The app failed to start. Error log: {log}")
        if sys.platform == "darwin":
            os.system(f'open "{log}"')
