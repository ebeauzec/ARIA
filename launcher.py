"""
ARIA - Desktop Launcher
=======================
Runs the ARIA server (the same code as server.py: Active IQ sync, cache, reports, optional sign-in) in a background thread and opens the
dashboard in a native window (WebView2 on Windows, WKWebView on macOS). No browser and no Python installation are needed when it is
distributed as a PyInstaller bundle.

Where ARIA keeps its settings, Active IQ tokens, cache and user accounts: the folder that contains the program (ARIA.exe), or, when that folder
cannot be written to, %LOCALAPPDATA%\\ARIA. Set ARIA_DATA_DIR to choose another folder.

Sign-in (off by default for a single user on one machine):
  ARIA.exe --sign-in        turn sign-in on (stored; applies from the next start)
  ARIA.exe --no-sign-in     turn it off again
  or use Settings > Access in the program, or set ARIA_AUTH=local in the environment.
User accounts: ARIA.exe --add-user NAME --role viewer | --set-password NAME | --remove-user NAME | --list-users

Run directly:  python launcher.py        Build Windows: build_windows.bat        Build macOS: ./build_mac.sh
"""
import os
import socket
import sys
import time
from pathlib import Path

APP_NAME = "ARIA — Active IQ Risk Intelligence Advisor"
APP_PORT = int(os.environ.get("ARIA_PORT") or 8080)

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys._MEIPASS)
    EXE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).resolve().parent
    EXE_DIR = BASE_DIR


def _writable(p):
    try:
        p.mkdir(parents=True, exist_ok=True)
        t = p / ".aria_write_test"
        t.write_text("x")
        t.unlink()
        return True
    except Exception:
        return False


def _data_dir():
    if os.environ.get("ARIA_DATA_DIR"):
        return Path(os.environ["ARIA_DATA_DIR"])
    if not getattr(sys, "frozen", False):
        return BASE_DIR
    if _writable(EXE_DIR):
        return EXE_DIR
    return Path(os.environ.get("LOCALAPPDATA") or Path.home()) / "ARIA"


DATA_DIR = _data_dir()
if sys.stdout is None or sys.stderr is None:      # a windowed program has no console: keep the server's messages in a log file
    try:
        _log = open(DATA_DIR / "aria.log", "a", encoding="utf-8", buffering=1)
        sys.stdout = sys.stdout or _log
        sys.stderr = sys.stderr or _log
    except Exception:
        pass
os.environ["ARIA_DATA_DIR"] = str(DATA_DIR)      # server.py reads this when it is imported
os.environ.setdefault("ARIA_BIND", "127.0.0.1")
os.chdir(BASE_DIR)
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "tools"))

import server as aria_server   # noqa: E402  (after the environment above is set)


def _find_free_port(preferred=APP_PORT):
    for port in range(preferred, preferred + 20):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:      # no SO_REUSEADDR: on Windows it would let a second program share a busy port
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    return preferred


def _wait_for_server(port, timeout=20.0):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=1):
                return True
        except OSError:
            time.sleep(0.2)
    return False


def main():
    port = _find_free_port(APP_PORT)
    srv = aria_server.main(block=False, port=port)
    if srv is None or not _wait_for_server(port):
        sys.exit(f"ERROR: the ARIA server did not start on port {port}.")
    url = f"http://127.0.0.1:{port}/"
    try:
        import webview
        webview.create_window(title=APP_NAME, url=url, width=1600, height=960, min_size=(1200, 720), resizable=True, text_select=True, zoomable=True)
        try:
            # keep the session cookie between runs when sign-in is on
            webview.start(debug=False, private_mode=False, storage_path=str(DATA_DIR / "webview"))
        except TypeError:
            webview.start(debug=False)
    except ImportError:
        import webbrowser
        print(f"\n[ARIA] pywebview not found. Opening the browser: {url}\nInstall it with:  pip install pywebview\n")
        webbrowser.open(url)
        try:
            input("Press Enter to stop the server...\n")
        except (KeyboardInterrupt, EOFError):
            pass
    finally:
        try:
            srv.shutdown()
        except Exception:
            pass


if __name__ == "__main__":
    main()
