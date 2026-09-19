#!/usr/bin/env bash
# Check the CPC tutorial's existing-rule examples with Ethos.
# This does not regenerate Logos or check Lean proofs.
set -euo pipefail
ulimit -c 0  # Ethos can abort on an invalid proof; do not leave core files.

if [ "$#" -ne 2 ]; then
  echo "Usage: bash $0 /path/to/ethos /path/to/cvc5/proofs/eo/cpc/Cpc.eo" >&2
  exit 2
fi

ethos="$1"
signature="$2"
here="$(cd "$(dirname "$0")" && pwd)"
failed=0

for name in modus-ponens wrong-antecedent reversed-premises wrong-conclusion extra-argument; do
  options=("--include=$signature")
  if [ "$name" = modus-ponens ]; then
    options+=(--require-proof-of-false)
  fi

  status=0
  output=$("$ethos" "${options[@]}" "$here/test/$name.cpc" 2>&1) || status=$?
  case "$name" in
    modus-ponens) expected='correct' ;;
    wrong-conclusion) expected='Unexpected conclusion for rule modus_ponens:' ;;
    extra-argument) expected='Bad number of arguments provided in function call' ;;
    *) expected='A step of rule modus_ponens failed to check.' ;;
  esac

  if { [ "$name" = modus-ponens ] && [ "$status" -eq 0 ] && [ "$output" = correct ]; } ||
     { [ "$name" != modus-ponens ] && [ "$status" -ne 0 ] &&
       [[ "$output" == *"$expected"* ]] && [[ "$output" == *modus_ponens* ]]; }; then
    echo "PASS $name"
  else
    echo "FAIL $name (exit $status): expected $expected" >&2
    printf '%s\n' "$output" >&2
    failed=1
  fi
done

exit "$failed"
