#!/usr/bin/env python3
"""Run this repository's own tests.

    python3 test/run.py

Everything here is about `eo_format/`, which is the only program in this tree.
It reads nothing under `tools/`: the child projects are islands, and a test
suite that opened one of their signatures would make deleting a child change
what this says.

Two kinds of case, and the second is the one that matters.  A **golden** case
is an input beside the output the formatter must produce for it.  An
**invariant** is a property every case has to have whatever the layout rules
say: the formatted text holds the same code tokens and the same comment words
as the text it came from, and formatting it again changes nothing.  A layout
rule can be argued with; losing a comment cannot, and the invariants are what
noticed that the rules were doing it.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "eo_format"))

import eo_format as F  # noqa: E402

CASES = ROOT / "test" / "eo_format" / "cases"


class Failures:
    def __init__(self) -> None:
        self.count = 0

    def check(self, ok: bool, what: str, detail: str = "") -> None:
        print(f"{'ok  ' if ok else 'FAIL'} {what}")
        if not ok:
            self.count += 1
            if detail:
                print("     " + detail.replace("\n", "\n     "))


def lexes_to(text: str, dialect: str) -> list[str]:
    return [tok.text for tok in F.Lexer(text, "<case>", dialect).tokenize()]


def dialect_cases(fail: Failures) -> None:
    """The two languages quote strings differently, and reading one with the
    other's rule is how the formatter used to fail on `.eos` outright."""
    fail.check(
        lexes_to('"a""b"', "eo") == ['"a""b"'],
        "eo reads a doubled quote as an escape",
    )
    fail.check(
        lexes_to('"a""b"', "eos") == ['"a"', '"b"'],
        "eos reads a doubled quote as two strings",
    )
    fail.check(
        lexes_to(r'"x\"y"', "eos") == [r'"x\"y"'],
        "eos reads a backslash as an escape",
    )
    fail.check(
        F.decode_eunoia_string('"a""b"', "eo") == 'a"b',
        "eo decodes a doubled quote",
    )
    fail.check(
        F.decode_eunoia_string(r'"x\"y"', "eos") == 'x"y',
        "eos decodes a backslash escape",
    )
    fail.check(
        F.dialect_for(Path("a.eos")) == "eos"
        and F.dialect_for(Path("a.eo")) == "eo"
        and F.dialect_for(Path("included")) == "eo",
        "a file's dialect comes from its suffix",
    )


def golden_cases(fail: Failures) -> None:
    formatter = F.Formatter(80, "spaces", 2)
    inputs = sorted(CASES.glob("*.in.*"))
    fail.check(bool(inputs), f"there are cases in {CASES.relative_to(ROOT)}")
    for path in inputs:
        name = path.name.split(".in.")[0]
        expected_path = path.with_name(path.name.replace(".in.", ".expected."))
        dialect = F.dialect_for(path)
        source = path.read_text(encoding="utf-8")
        if not expected_path.is_file():
            fail.check(False, f"{name}: has an expected output")
            continue
        expected = expected_path.read_text(encoding="utf-8")
        try:
            got = F.format_text(source, str(path), formatter, dialect)
        except F.FormatError as err:
            fail.check(False, f"{name}: formats", str(err))
            continue
        fail.check(got == expected, f"{name}: matches {expected_path.name}", diff(expected, got))
        try:
            again = F.format_text(expected, str(expected_path), formatter, dialect)
        except F.FormatError as err:
            fail.check(False, f"{name}: the expected output formats", str(err))
            continue
        fail.check(
            again == expected,
            f"{name}: the expected output is a fixed point",
            diff(expected, again),
        )
        fail.check(
            F.code_tokens(source, name, dialect) == F.code_tokens(got, name, dialect),
            f"{name}: keeps every code token",
        )
        fail.check(
            F.comment_words(source, name, dialect)
            == F.comment_words(got, name, dialect),
            f"{name}: keeps every comment word, in order",
        )


def refusal_cases(fail: Failures) -> None:
    """The safety net is the claim the front page makes, so it is tested:
    a rule that dropped a comment must stop the write rather than reach disk."""
    formatter = F.Formatter(80, "spaces", 2)
    try:
        F.verify_reformat("; kept\n(a)\n", "(a)\n", "<case>", "eo")
    except F.FormatError:
        fail.check(True, "a lost comment is refused")
    else:
        fail.check(False, "a lost comment is refused")
    try:
        F.verify_reformat("(a b)\n", "(a)\n", "<case>", "eo")
    except F.FormatError:
        fail.check(True, "a lost token is refused")
    else:
        fail.check(False, "a lost token is refused")
    for bad in ["(a", "a)", '"unterminated']:
        try:
            F.format_text(bad, "<case>", formatter, "eo")
        except F.FormatError:
            fail.check(True, f"{bad!r} is refused")
        else:
            fail.check(False, f"{bad!r} is refused")


def cli_cases(fail: Failures) -> None:
    """Exit 1 means `--check` found something to change, so nothing else may
    exit 1: a file that cannot be read is exit 2 with a message, not a
    traceback.  Everything here is written to a temporary directory."""
    import contextlib
    import io
    import tempfile

    def run(*argv: str) -> int:
        with contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(
            io.StringIO()
        ):
            try:
                return F.main(list(argv))
            except SystemExit as exit:
                return int(exit.code or 0)

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "dir").mkdir()
        (root / "bad.eo").write_bytes(b"\xff(a)\n")
        (root / "deep.eo").write_text("(" * 5000 + ")" * 5000 + "\n")
        (root / "ok.eo").write_text("(a)\n")
        (root / "loose.eo").write_text("(a  b)\n")
        (root / "inc.eo").write_text('(include "dir")\n\n(a)\n')
        fail.check(run("--check", str(root / "ok.eo")) == 0, "cli: --check, no change, exits 0")
        fail.check(run("--check", str(root / "loose.eo")) == 1, "cli: --check, a change, exits 1")
        fail.check(run("--check", str(root / "nope.eo")) == 2, "cli: a missing file exits 2")
        fail.check(run("--check", str(root / "dir")) == 2, "cli: a directory exits 2")
        fail.check(run("--check", str(root / "bad.eo")) == 2, "cli: a non-UTF-8 file exits 2")
        fail.check(run("--check", str(root / "deep.eo")) == 2, "cli: deep nesting exits 2")
        fail.check(
            run("--check", str(root / "inc.eo")) == 0,
            "cli: an include naming a directory is skipped",
        )
        fail.check(
            run("--width", "0", "--check", str(root / "ok.eo")) == 2
            and run("--indent-size", "0", "--check", str(root / "ok.eo")) == 2,
            "cli: a width or indent below 1 is refused",
        )
        # The safety net refusing the second file must leave the first as it
        # was, so the refusal is forced on it here.
        verify = F.verify_reformat

        def refuse_late(original: str, formatted: str, name: str, dialect: str) -> None:
            if name.endswith("late.eo"):
                raise F.FormatError(f"{name}: refused")
            verify(original, formatted, name, dialect)

        (root / "late.eo").write_text("(c  d)\n")
        F.verify_reformat = refuse_late
        try:
            code = run(str(root / "loose.eo"), str(root / "late.eo"))
        finally:
            F.verify_reformat = verify
        fail.check(
            code == 2 and (root / "loose.eo").read_text() == "(a  b)\n",
            "cli: nothing is written when any file is refused",
        )


def diff(expected: str, got: str) -> str:
    import difflib

    return "".join(
        difflib.unified_diff(
            expected.splitlines(keepends=True),
            got.splitlines(keepends=True),
            "expected",
            "got",
        )
    )


def main() -> int:
    fail = Failures()
    dialect_cases(fail)
    golden_cases(fail)
    refusal_cases(fail)
    cli_cases(fail)
    print()
    if fail.count:
        print(f"-- eo_format: {fail.count} failure(s)")
        return 1
    print("-- eo_format: every case passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
