"""
Yirra Care Agents — Desktop Launcher
Starts Streamlit on a free port and opens the browser.
Usage (dev): python launcher.py
Usage (dist): double-click the .exe / .app
"""
import os, sys, socket, threading, time, webbrowser, traceback
from pathlib import Path


def get_base_dir() -> Path:
    if not getattr(sys, "frozen", False):
        return Path(__file__).resolve().parent
    exe = Path(sys.executable).resolve()
    if sys.platform == "darwin":
        resources = exe.parent.parent / "Resources"
        if resources.exists() and (resources / "app").exists():
            return resources
    return exe.parent


def find_free_port(start: int = 8501) -> int:
    for port in range(start, start + 20):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
    return start


def _port_open(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        return s.connect_ex(("127.0.0.1", port)) == 0


def _open_browser(port: int) -> None:
    url = f"http://localhost:{port}"
    for _ in range(40):
        time.sleep(1)
        if _port_open(port):
            webbrowser.open(url)
            return
    webbrowser.open(url)


def _dialog(title: str, msg: str) -> None:
    if sys.platform == "darwin":
        safe = msg.replace('"', '\\"')
        os.system(f'osascript -e \'display dialog "{safe}" with title "{title}" buttons {{"OK"}} default button "OK"\'')


def main() -> None:
    base_dir = get_base_dir()
    os.chdir(str(base_dir))

    if not (base_dir / ".env").exists():
        _dialog("Setup Required", f"No .env file found in:\\n{base_dir}\\n\\nCopy .env.template to .env and fill in your API keys.")
        if sys.platform == "darwin":
            os.system(f'open "{base_dir}"')
        return

    port = find_free_port(8501)
    threading.Thread(target=_open_browser, args=(port,), daemon=True).start()

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
    sys.exit(stcli.main())


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        tb = traceback.format_exc()
        log = Path.home() / "Desktop" / "YirraCare_error.log"
        try:
            log.write_text(tb)
        except Exception:
            pass
        _dialog("Yirra Care Agents Error", f"App failed to start.\\nLog saved to:\\n{log}")
        if sys.platform == "darwin":
            os.system(f'open "{log}"')
