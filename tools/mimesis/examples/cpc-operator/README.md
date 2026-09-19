# CPC operator examples

Worked proofs for
[Extending CPC with a new theory operator](../../docs/extending-cpc-operators.md),
using cvc5's existing `int.pow2`. These fixtures load cvc5's main signature
directly; none of them includes a signature itself.

Run with an Ethos binary and the root of a complete cvc5 checkout:

```bash
python3 check.py /path/to/ethos /path/to/cvc5
```

[`check.py`](check.py) checks the exit status and verdict, or the expected
diagnostic, for five runs against `Cpc.eo`. Positive proofs must derive `false`;
negative tests must fail for the stated reason.

| Proof | Expected outcome | What it shows |
| --- | --- | --- |
| [`evaluate-value.cpc`](test/evaluate-value.cpc) | refutation | `evaluate` computes `(= (int.pow2 3) 8)` |
| [`evaluate-open.cpc`](test/evaluate-open.cpc) | refutation | on a variable argument the evaluator returns the term, so the rule proves `(= t t)` rather than failing |
| [`evaluate-negative.cpc`](test/evaluate-negative.cpc) | refutation | `$arith_eval_int_pow_2` answers `0` below zero, a convention of the signature |
| [`wrong-value.cpc`](test/wrong-value.cpc) | `Unexpected conclusion for rule evaluate` | the rule computes its conclusion; a claimed `9` is rejected at the step |
| [`wrong-type.cpc`](test/wrong-type.cpc) | `Type checking failed:` | `(int.pow2 true)` is rejected by the declaration, before any rule |

The three refutations differ only in the argument, which is the point: an
operator's evaluator has to be right on values, on non-values, and on whatever
cases the SMT-LIB standard leaves open.

All five runs passed on 2026-09-18 with cvc5 signature revision
`2900761a7c2e2c0e99e2cf669cffa3740ea9a138` and Ethos built from
`8dc85c4db8d6cc612f02dc3bb627331732605eff`, cvc5's checker pin at that revision.
These are hand-written proof tests, not proofs emitted by a solver build. No
cvc5 build, Logos generation or Lean proof was run for this example.
