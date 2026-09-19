# CPC theory examples

Worked proofs for [Extending CPC theories](../../docs/extending-cpc-theories.md),
using cvc5's expert finite-field theory. These fixtures load cvc5's signatures
directly; none of them includes a signature itself.

Run with an Ethos binary and the root of a complete cvc5 checkout:

```bash
python3 check.py /path/to/ethos /path/to/cvc5
```

[`check.py`](check.py) checks the exit status and verdict, or the expected
diagnostic, for six runs. Positive proofs must derive `false`; negative tests
must fail for the stated reason.

| Proof | Signature | Expected outcome | What it shows |
| --- | --- | --- | --- |
| [`aci-norm.cpc`](test/aci-norm.cpc) | `Cpc.eo` only | `Could not find symbol FiniteField` | an expert theory is invisible to the main signature |
| Same proof | main and expert | refutation | `aci_norm_expert` proves that `ff.add` commutes |
| [`nil-terminator.cpc`](test/nil-terminator.cpc) | main and expert | refutation | `(ff.add x (ff.value 7 0))` and `x` are one term, because the field's zero is the operator's nil terminator |
| [`no-evaluation.cpc`](test/no-evaluation.cpc) | main and expert | `Unexpected conclusion for rule evaluate` | the theory has no evaluation, so `evaluate` proves `(= t t)` instead of computing in the field |
| [`non-prime.cpc`](test/non-prime.cpc) | main and expert | checks | `(FiniteField 6)` is a well-typed CPC type; the declaration says nothing about primality |
| [`mixed-fields.cpc`](test/mixed-fields.cpc) | main and expert | `Type checking failed:` | `ff.add` infers one field parameter, so adding across two field sizes fails |

The [tutorial commands](../../docs/extending-cpc-theories.md#7-check-the-theory-with-ethos)
show the individual Ethos invocations. The explicit main-only run matters:
cvc5's `cpc_gen.sh` helper includes both signatures by default, so it would not
catch an expert symbol in a proof that is supposed to be safe.

All six runs passed on 2026-09-18 with cvc5 signature revision
`2900761a7c2e2c0e99e2cf669cffa3740ea9a138` and Ethos built from
`8dc85c4db8d6cc612f02dc3bb627331732605eff`, cvc5's checker pin at that revision.
These are hand-written proof tests, not proofs emitted by a solver build. No
Logos generation or Lean proof was run for this example, and the finite-field
theory is not part of Logos's main-signature compilation.
