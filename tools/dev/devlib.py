"""Shared helpers for the development scripts in this folder: start/stop a test server, open the fleet in a browser, run node.

Nothing here is used by ARIA itself. Outputs go to data/dev/ (git-ignored; it sits in the shared folder, so another workstation sees them too, but treat them as
scratch). Customer names are never written in these scripts: pass them on the command line.

Rules the helpers keep (they come from hard lessons, see CLAUDE.md):
  * the test server runs on port 8091 only, one at a time, with authentication off, and is stopped by the PID it was started with, never by name;
  * the page is opened with the 'what's new' modal suppressed, and waited for until the fleet is loaded.
"""
import json
import os
import subprocess
import sys
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, 'data', 'dev')
PORT = 8091
URL = f'http://127.0.0.1:{PORT}/'
PIDFILE = os.path.join(OUT, 'server.pid')


def version():
    with open(os.path.join(ROOT, 'version.json'), encoding='utf-8') as fh:
        return json.load(fh)['version']


def port_open():
    try:
        urllib.request.urlopen(URL, timeout=2).read(1)
        return True
    except Exception:
        return False


def start_server(wait=40):
    """Start server.py on 8091 (auth off). Returns the PID, or the PID of the one already started by these helpers."""
    os.makedirs(OUT, exist_ok=True)
    if port_open():
        return int(open(PIDFILE).read()) if os.path.exists(PIDFILE) else None
    env = dict(os.environ, ARIA_AUTH='none', ARIA_PORT=str(PORT))
    log = open(os.path.join(OUT, 'server.log'), 'w')
    p = subprocess.Popen([sys.executable, os.path.join(ROOT, 'server.py')], cwd=ROOT, env=env, stdout=log, stderr=log, stdin=subprocess.DEVNULL)
    with open(PIDFILE, 'w') as fh:
        fh.write(str(p.pid))
    t0 = time.time()
    while time.time() - t0 < wait:
        if port_open():
            return p.pid
        time.sleep(1)
    raise RuntimeError('the test server did not answer on port %d in %d s; see data/dev/server.log' % (PORT, wait))


def stop_server():
    """Stop the server these helpers started, by its PID. Does nothing to any other process."""
    if not os.path.exists(PIDFILE):
        return False
    pid = int(open(PIDFILE).read())
    try:
        if os.name == 'nt':
            subprocess.run(['taskkill', '/PID', str(pid), '/F', '/T'], capture_output=True)
        else:
            os.kill(pid, 15)
    except Exception:
        pass
    os.remove(PIDFILE)
    return True


def open_fleet(pw, min_systems=100, settle=12000, width=1400, height=1000):
    """(browser, page) with the fleet loaded. Needs `pip install playwright` and `playwright install chromium`."""
    b = pw.chromium.launch()
    ctx = b.new_context(viewport={'width': width, 'height': height})
    ctx.add_init_script("try{localStorage.setItem('aiq_seen_version','%s')}catch(e){}" % version())
    pg = ctx.new_page()
    pg.goto(URL)
    pg.wait_for_function('window.state && state.systems && state.systems.length > %d' % min_systems, timeout=240000)
    pg.wait_for_timeout(settle)
    pg.evaluate("(()=>{const m=document.getElementById('whatsNewModal'); if(m) m.remove();})()")
    return b, pg


def node_available():
    try:
        return subprocess.run(['node', '--version'], capture_output=True, text=True).returncode == 0
    except OSError:
        return False
