"""Compliance rules: ARIA may show and ship only NetApp information that anyone can open without signing in.

Owner's rule (2026-10-17): nothing taken from NetApp's customer-only areas (support bulletins, customer communications and end-of-availability
notices, engineering change ids, pages behind a NetApp Support sign-in) may appear in the code, the documentation, the shipped library, the
deliverables, the change logs or a commit message. This module is the single list of what that means. It is used by

  * tools/guard_sensitive.py   every staged file and commit message (pre-commit), every pushed commit and the new tip (pre-push), --tree, --history
  * tools/playbooks.py         the sources of a procedure (a gated page is refused)
  * tools/dev/sync_library.py  links into those areas are removed from the shipped library
  * app.js                     _dfCompliance(): the same ids are removed from the text of every generated document

A line that has to carry one of these words for a good reason (this file, its tests) is marked with `compliance-ok: <reason>`; the reason is
read by a person at review. Everything else stops the commit.

    python tools/guard_compliance.py --tree HEAD       scan a revision        python tools/guard_compliance.py --file a.md b.md
"""
import re
import sys

# (what it is, regular expression); matched case-insensitively against one line
RULES = [
    ("NetApp support-bulletin id", r"\bSU\d{2,4}\b"),
    ("NetApp customer-notice id", r"\bCPC-\d{3,6}\b"),
    ("NetApp engineering-change id", r"\bECD-\d{3,6}\b"),
    ("NetApp customer-bulletin link", r"(?:Support_" r"Bulletins|Customer_" r"Bulletins)"),
    ("NetApp support-portal article link", r"mysupport\.netapp\.com/(?:site/)?(?:article|info|cpc|bulletins?)\b"),
    ("NetApp customer-only wording", r"\b(?:support|customer) bulletins?\b|\bcustomer communiqu|\bsupport site communications?\b"),
    ("content behind a sign-in", r"\bneeds? a (?:netapp )?(?:support )?sign-?in\b|\bbehind (?:a )?(?:log-?in|sign-?in|paywall)\b|\bnot (?:published )?openly\b|\bnot publicly (?:available|published)\b|\bcontent authenticated\b|(?:netapp support|support site|support portal|mysupport)[^.\n]{0,40}\b(?:sign-?in|log-?in|authenticat\w*)\b"),
    ("marked confidential or internal", r"\bnetapp[ -](?:internal|confidential)\b|\bfor netapp internal use\b|\bunder (?:an? )?nda\b|\bnda-protected\b|\binternal use only\b"),
]
PATTERNS = [(kind, re.compile(rx, re.I)) for kind, rx in RULES]

MARK = "compliance-ok"
# files that must name these things in order to detect them
EXEMPT_PATH = re.compile(r"(^|/)(tools/guard_compliance\.py|tests/test_guard_compliance\.py)(@[0-9a-f]{7})?$")
# hosts a procedure may cite: pages anyone can open
PUBLIC_HOSTS = ("docs.netapp.com", "kb.netapp.com", "security.netapp.com", "www.netapp.com", "netapp.com", "library.netapp.com", "hwu.netapp.com", "imt.netapp.com")
GATED_URL = re.compile(r"(?:Support_" r"Bulletins|Customer_" r"Bulletins|mysupport\.netapp\.com|/login|/signin|/sign-in|/auth/)", re.I)


def scan_line(line):
    """[(kind, matched text)] for one line; empty for a line marked compliance-ok."""
    if MARK in line:
        return []
    out = []
    for kind, rx in PATTERNS:
        m = rx.search(line)
        if m:
            out.append((kind, m.group(0)))
    return out


def exempt(label):
    return bool(EXEMPT_PATH.search(str(label).replace("\\", "/")))


def scan_text(label, text):
    """[(label, line number, kind, matched text)] over a whole text."""
    if exempt(label):
        return []
    out = []
    for i, line in enumerate(text.split("\n"), 1):
        if len(line) > 20000:
            line = line[:20000]
        for kind, hit in scan_line(line):
            out.append((label, i, kind, hit))
    return out


def gated_source(url):
    """Why a procedure may not cite this URL, or '' when it may."""
    u = str(url or "")
    if GATED_URL.search(u):
        return "a page in NetApp's customer-only area or behind a sign-in"
    return ""


def scrub_text(text):
    """The same ids with their wording removed, for text that is generated (documents, exports)."""
    t = re.sub(r"\b(?:KB ID:\s*)?(?:SU\d{2,4}|CPC-\d{3,6}|ECD-\d{3,6})\b", "", str(text))
    return re.sub(r"[ \t]{2,}", " ", t)


_SENT = re.compile(r"(?<=[.!?])\s+(?=[A-Z*(\[`])")


def scrub_sentences(text):
    """Text with every sentence that trips a rule removed (a bullet or line left empty goes too). Used on the shipped library, which is copied from a
    maintainer's notes, so what is shipped is only what passes the rules."""
    out = []
    for line in str(text).split("\n"):
        if not scan_line(line):
            out.append(line)
            continue
        if line.lstrip().startswith("|"):
            continue                                           # a table row cannot be cut by sentence
        parts = _SENT.split(line)
        keep = [x for x in parts if not scan_line(x)]
        rest = " ".join(keep).rstrip()
        if re.sub(r"[\s*\-#>]+", "", rest):
            out.append(rest)
    return "\n".join(out)


def main(argv):
    if "--file" in argv:
        n = 0
        for p in argv[argv.index("--file") + 1:]:
            with open(p, encoding="utf-8", errors="replace") as fh:
                for f in scan_text(p, fh.read()):
                    print("%s:%d  %s  [%s]" % f)
                    n += 1
        return 1 if n else 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
