"""Line-ending-safe file edits for patch scripts.

The repository is edited on Windows (git autocrlf on, so the working files have CRLF) and on other machines (LF). A patch script that does
open().read().replace(old, new) either misses its anchor or rewrites every line ending. Use this instead:

    from patchlib import edit, replace_once
    replace_once('app.js', "old text", "new text")            # the old text must occur exactly once, written with \\n line breaks
    edit('README.md', lambda text: text.replace('a', 'b'))     # text arrives with \\n; the file's own line endings are restored on write

Write patch scripts to a file (not a shell heredoc: backslashes and quotes are mangled) and run them from the repository root.
"""
import os


_ROOT = None


def set_root(path):
    """Point the helpers at another tree (the tests do; nothing else needs to)."""
    global _ROOT
    _ROOT = os.path.abspath(path) if path else None


def _root():
    return _ROOT or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _path(p):
    return p if os.path.isabs(p) else os.path.join(_root(), p)


def edit(path, fn):
    """Apply fn(text) -> text to a file, reading and writing it as UTF-8 and keeping its CRLF/LF line endings."""
    full = _path(path)
    with open(full, 'r', encoding='utf-8', newline='') as fh:
        raw = fh.read()
    crlf = '\r\n' in raw
    out = fn(raw.replace('\r\n', '\n'))
    if out is None:
        raise ValueError('the edit function must return the new text')
    with open(full, 'w', encoding='utf-8', newline='') as fh:
        fh.write(out.replace('\n', '\r\n') if crlf else out)


def replace_once(path, old, new):
    """Replace `old` by `new`; fail loudly unless `old` occurs exactly once."""
    def fn(text):
        n = text.count(old)
        if n != 1:
            raise AssertionError(f'{path}: expected the anchor once, found {n} times: {old[:90]!r}')
        return text.replace(old, new)
    edit(path, fn)
