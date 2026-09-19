#!/bin/sh
# Run the tutorial's proof tests against both signatures in this directory.
#
#   ./check.sh [path-to-ethos]
#
# `ethos` checks a proof against a Eunoia signature; it is not the framework's
# generated checker and does not produce the framework's four verdicts. Here a
# test either prints `correct` or is rejected with an error, and each
# test/<name>.expected says which of the two it must be.
#
# Rejection is how three of these tests pass, and `ethos` reaches it by
# aborting, so two things have to be arranged or a passing run looks broken.
# `ulimit -c 0` stops the aborts leaving core files behind. Running into a file
# rather than into `$(...)` stops the shell announcing each one: a command
# substitution whose child dies on a signal is reported as `Aborted (core
# dumped)` by some shells, on this script's own stderr, interleaved with the
# `ok` lines.
set -e
ulimit -c 0
ETHOS=${1:-ethos}
here=$(dirname "$0")
status=0
log=$(mktemp "${TMPDIR:-/tmp}/resolution-check.XXXXXX")
trap 'rm -f "$log"' EXIT

for sig in "$here"/Resolution.eo "$here"/Resolution-lists.eo; do
  echo "== $(basename "$sig")"
  for proof in "$here"/test/*.proof; do
    name=$(basename "$proof" .proof)
    want=$(cat "$here/test/$name.expected")
    if "$ETHOS" --include="$sig" "$proof" > "$log" 2>&1; then
      got=$(tail -n 1 "$log")
    else
      got=rejected
    fi
    case "$got" in
      "$want") echo "   ok   $name ($want)" ;;
      *)       echo "   FAIL $name: wanted $want, got $got"; status=1 ;;
    esac
  done
done

exit $status
