#!/usr/bin/env python3
"""Check the CPC operator tutorial's proof fixtures with Ethos.

Usage: python3 check.py /path/to/ethos /path/to/cvc5
Every case uses the main signature alone, which is where int.pow2 is declared.
This checks signature behavior; it does not build cvc5 or verify Logos proofs.
"""

from pathlib import Path
import resource
import subprocess
import sys

# (proof, expectation), where an expectation is "refutes" for a proof of false,
# "accepts" for a file that must only type check, or a diagnostic to demand.
CASES = [
    ("evaluate-value", "refutes"),
    ("evaluate-open", "refutes"),
    ("evaluate-negative", "refutes"),
    ("wrong-value", "Unexpected conclusion for rule evaluate"),
    ("wrong-type", "Type checking failed:"),
]


def main():
    if len(sys.argv) != 3:
        print(__doc__, file=sys.stderr)
        return 2
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    ethos, cvc5 = sys.argv[1:]
    here = Path(__file__).resolve().parent
    signature = Path(cvc5).resolve() / "proofs" / "eo" / "cpc" / "Cpc.eo"
    if not signature.is_file():
        print(f"Missing signature: {signature}", file=sys.stderr)
        return 2
    failed = False
    for name, expectation in CASES:
        args = [ethos, f"--include={signature}"]
        if expectation == "refutes":
            args.append("--require-proof-of-false")
        result = subprocess.run([*args, str(here / "test" / f"{name}.cpc")],
                                text=True, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        if expectation in ("refutes", "accepts"):
            ok = result.returncode == 0 and result.stdout.strip() == "correct"
        else:
            ok = result.returncode != 0 and expectation in result.stdout
        print(f"{'PASS' if ok else 'FAIL'} {name}: {expectation}")
        if not ok:
            print(f"exit {result.returncode}\n{result.stdout}", file=sys.stderr)
            failed = True
    return int(failed)


if __name__ == "__main__":
    sys.exit(main())
