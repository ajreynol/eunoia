#!/usr/bin/env python3
"""Read a corpus of Eunoia files with the formatter and report what it refused.

    python3 test/corpus.py /path/to/ethos /path/to/cvc5/proofs ...

**Nothing is written.** Each `.eo` and `.eos` file under the given directories
is formatted in memory and thrown away; what is reported is how many the
formatter would not produce a safe result for.

It is separate from `test/run.py` because it needs trees that are not in this
repository, so it cannot run in CI and its result is a dated measurement rather
than a check.  The front page records the last run, the directories it read and
the commits they were at; this is the command that takes the measurement again.

Three ways a file can fail, and each is a defect in the formatter rather than
in the file:

- **refused** — it did not lex or parse, or the safety net found that the
  formatted text had lost a code token or a comment;
- **unsettled** — the layout never stopped changing, so formatting twice says
  something different from formatting once;
- **unreadable** — it is not UTF-8, which is reported separately because that
  is a fact about the file.
"""

import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "eo_format"))

import eo_format as F  # noqa: E402

SUFFIXES = (".eo", ".eos")


def read(root: Path, counts: Counter, formatter: F.Formatter) -> None:
    for path in sorted(root.rglob("*")):
        if path.suffix not in SUFFIXES or not path.is_file():
            continue
        counts["files"] += 1
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError) as err:
            counts["unreadable"] += 1
            print(f"unreadable {path}: {err}")
            continue
        try:
            F.format_text(text, str(path), formatter, F.dialect_for(path))
        except F.FormatError as err:
            key = "unsettled" if "did not settle" in str(err) else "refused"
            counts[key] += 1
            print(f"{key} {path}: {err}")
        except RecursionError:
            counts["refused"] += 1
            print(f"refused {path}: nested too deeply to read")


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__, file=sys.stderr)
        return 2
    formatter = F.Formatter(80, "spaces", 2)
    counts: Counter = Counter()
    for name in argv:
        root = Path(name)
        if not root.is_dir():
            print(f"not a directory: {root}", file=sys.stderr)
            return 2
        before = counts["files"]
        read(root, counts, formatter)
        print(f"-- {root}: {counts['files'] - before} file(s)")
    print(
        f"-- {counts['files']} file(s), {counts['refused']} refused, "
        f"{counts['unsettled']} unsettled, {counts['unreadable']} unreadable"
    )
    return 1 if counts["refused"] or counts["unsettled"] else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
