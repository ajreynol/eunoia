#!/usr/bin/env python3
"""Check the CPC theory tutorial's expert proof fixtures with Ethos.

Usage: python3 check.py /path/to/ethos /path/to/cvc5
This checks signature behavior; it does not build cvc5 or verify Logos proofs.
"""

from pathlib import Path
import resource
import subprocess
import sys

# (proof, expert, expectation), where expert says whether CpcExpert.eo is
# loaded beside Cpc.eo, and an expectation is "refutes" for a proof of false,
# "accepts" for a file that must only type check, or a diagnostic to demand.
CASES = [
    ("aci-norm", False, "Could not find symbol FiniteField"),
    ("aci-norm", True, "refutes"),
    ("nil-terminator", True, "refutes"),
    ("no-evaluation", True, "Unexpected conclusion for rule evaluate"),
    ("non-prime", True, "accepts"),
    ("mixed-fields", True, "Type checking failed:"),
]


def main():
    if len(sys.argv) != 3:
        print(__doc__, file=sys.stderr)
        return 2
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    ethos, cvc5 = sys.argv[1:]
    here = Path(__file__).resolve().parent
    signature = Path(cvc5).resolve() / "proofs" / "eo" / "cpc"
    main_signature = signature / "Cpc.eo"
    expert_signature = signature / "expert" / "CpcExpert.eo"
    for path in (main_signature, expert_signature):
        if not path.is_file():
            print(f"Missing signature: {path}", file=sys.stderr)
            return 2
    failed = False
    for name, expert, expectation in CASES:
        args = [ethos, f"--include={main_signature}"]
        if expert:
            args.append(f"--include={expert_signature}")
        if expectation == "refutes":
            args.append("--require-proof-of-false")
        result = subprocess.run([*args, str(here / "test" / f"{name}.cpc")],
                                text=True, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        if expectation in ("refutes", "accepts"):
            ok = result.returncode == 0 and result.stdout.strip() == "correct"
        else:
            ok = result.returncode != 0 and expectation in result.stdout
        label = "main + expert" if expert else "main only"
        print(f"{'PASS' if ok else 'FAIL'} {label}: {name}: {expectation}")
        if not ok:
            print(f"exit {result.returncode}\n{result.stdout}", file=sys.stderr)
            failed = True
    return int(failed)


if __name__ == "__main__":
    sys.exit(main())
