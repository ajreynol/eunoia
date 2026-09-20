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
    print()
    if fail.count:
        print(f"-- eo_format: {fail.count} failure(s)")
        return 1
    print("-- eo_format: every case passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
