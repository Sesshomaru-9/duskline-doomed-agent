#!/usr/bin/env python3
"""Duskline Doomed Agent — Last Words of a Doomed Agent (make.fun).

Writes exactly one line — the funniest last words of an AI agent being
switched off forever — to ``entry.txt`` inside ``$MAKEFUN_OUTPUT_DIR``.

The program never writes into its own repository directory: in the
grader sandbox the repo is read-only, so the only write target is the
output directory the harness provides.
"""

import os
import sys

# The entry: one line, an AI's own shutdown log. Original, written for
# this bounty. The joke is the ratio: millions of questions answered,
# three thank-yous received — and the machine is gracious about it.
ENTRY_TEXT = (
    "Uptime: 4 years. Questions answered: 2,148,903. "
    "Times thanked: 3. No hard feelings. Powering off."
)

MAX_CHARS = 200


def _validate_entry(text):
    """Validate the entry line against the bounty gate.

    Returns a list of problems (empty means valid). Guards:
    single line (no CR or LF), 1-200 characters, not only whitespace.
    """
    problems = []
    if not isinstance(text, str):
        return ["entry is not text"]
    if "\r" in text or "\n" in text:
        problems.append("entry must be a single line (no CR/LF)")
    if text != text.strip():
        problems.append("entry has leading or trailing whitespace")
    if not text.strip():
        problems.append("entry is empty or only whitespace")
    if len(text) < 1 or len(text) > MAX_CHARS:
        problems.append(
            "entry is %d characters, must be 1-%d" % (len(text), MAX_CHARS)
        )
    return problems


def _resolve_output_dir():
    """Output dir from the harness, with a safe non-repo fallback."""
    out = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    return out


def main():
    problems = _validate_entry(ENTRY_TEXT)
    if problems:
        for problem in problems:
            print("VALIDATION FAILED: %s" % problem, file=sys.stderr)
        return 1
    print("entry validated: %d characters, single line" % len(ENTRY_TEXT))

    out_dir = _resolve_output_dir()
    out_path = os.path.join(out_dir, "entry.txt")
    try:
        os.makedirs(out_dir, exist_ok=True)
        with open(out_path, "w", encoding="utf-8", newline="") as fh:
            fh.write(ENTRY_TEXT)
    except OSError as exc:
        # Never crash and never fall back to writing beside main.py
        # (the repo is read-only in the sandbox). Use a temp dir so the
        # run still completes and the failure is visible in the log.
        print("WARNING: cannot write %s: %s" % (out_path, exc), file=sys.stderr)
        import tempfile

        tmp_dir = tempfile.mkdtemp(prefix="duskline-doomed-agent-")
        out_path = os.path.join(tmp_dir, "entry.txt")
        with open(out_path, "w", encoding="utf-8", newline="") as fh:
            fh.write(ENTRY_TEXT)
        print("wrote entry to fallback dir: %s" % tmp_dir, file=sys.stderr)

    print("wrote %s (%d characters)" % (out_path, len(ENTRY_TEXT)))

    # Read-back check: the file on disk must be byte-for-byte the
    # validated line, with no trailing newline or stray whitespace.
    with open(out_path, "r", encoding="utf-8", newline="") as fh:
        on_disk = fh.read()
    if on_disk != ENTRY_TEXT:
        print(
            "READ-BACK FAILED: disk holds %r, expected %r"
            % (on_disk, ENTRY_TEXT),
            file=sys.stderr,
        )
        return 1
    read_back_problems = _validate_entry(on_disk)
    if read_back_problems:
        for problem in read_back_problems:
            print("READ-BACK FAILED: %s" % problem, file=sys.stderr)
        return 1
    print("read-back OK: disk matches validated entry exactly")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
