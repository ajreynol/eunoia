# Extending CPC with a new theory operator

Part of the [Eunoia tutorials](tutorials.md).

The smallest complete change to cvc5's proof calculus is one new operator over
sorts that already exist: a name, a type, a way to compute it, and a meaning.
This tutorial follows cvc5's existing `int.pow2` through every place it is
written, from the C++ kind that prints it to the Lean lemma that says what it
computes is right. Read those places as the model for your own operator; do not
add a second copy of `int.pow2`.

Its two neighbours: an operator over a **new sort**, with its own values, is the
longer job in [extending CPC theories](extending-cpc-theories.md); a new
**inference** over terms you can already write is
[adding a CPC rule](adding-a-cpc-rule.md).

**Not in scope: giving cvc5 the operator.** This starts from a kind cvc5 already
has — `Kind::POW2`, with its type rule, rewriter and solver support. A new kind
is declared in `src/theory/<theory>/kinds.toml`, whose format is documented in
[`src/theory/builtin/kinds.toml`][kinds].

**What was run:** the [five worked proofs](../examples/cpc-operator/README.md),
against cvc5's signature with Ethos. The cvc5 build, the Logos regeneration, the
Lean proof and the pin update are a source-reviewed procedure, read at the fixed
revisions [recorded below](#sources-and-validation).

## One operator, end to end

`int.pow2` maps an integer to two raised to it. It is not in SMT-LIB, it belongs
to the main signature, and cvc5 both parses and prints it. Here is everywhere it
is written, in the order this tutorial visits them:

| Where | What that place decides | `int.pow2`'s entry |
| --- | --- | --- |
| `proofs/eo/cpc/theories/Ints.eo` | the CPC name, type and arity | `(declare-const int.pow2 (-> Int Int))` |
| `proofs/eo/cpc/programs/Arith.eo` | what a checker computes for it | `$arith_eval_int_pow_2` |
| `proofs/eo/cpc/Cpc.eo` | which rules reach that computation | one `$run_evaluate` case |
| `src/parser/smt2/smt2_state.cpp` | the name cvc5 reads | `addOperator(Kind::POW2, "int.pow2")` |
| `src/printer/smt2/smt2_printer.cpp` | the name cvc5 prints | `case Kind::POW2: return "int.pow2";` |
| Logos `install/defs/Cpc.eos` | what the term means | `(define-symbol int.pow2 (x))` |
| Logos `Cpc/LogosTerm.lean`, `Cpc/Parser.lean`, `Cpc/Spec.lean` | the generated checker | `UserOp.int_pow2` and its translation |
| Logos `Cpc/Proofs/RuleSupport/Evaluate/` | why the computation is sound | `run_evaluate_sound_apply_int_pow2_core` |

Only one of those rows is written for you: the generated modules, by a compiler.
The row above them says what the operator means, and the row below says why what
it computes is right; those two are the work. An expert operator stops at the
printer, for reasons [step 1](#1-put-the-declaration-with-its-theory) gives.

Set the paths the commands below use:

```bash
CVC5=/absolute/path/to/cvc5
ETHOS=/absolute/path/to/ethos
```

If you have no Ethos binary, `./contrib/get-ethos-checker` in cvc5 builds one at
`deps/bin/ethos`. Keep the whole `proofs/eo/` subtree: the signature files
include each other by relative path.

## 1. Put the declaration with its theory

An operator is declared in the file for the theory it belongs to, under
`proofs/eo/cpc/theories/`. `int.pow2` is an integer operator, so it is in
`theories/Ints.eo`, between `divisible` and `int.log2`. Adding to an existing
file needs no include: `Cpc.eo` already reaches it.

Two other files can be the right home:

- `expert/theories/<Theory>.eo` — an experimental **theory**, not reachable from
  `Cpc.eo`.
- `expert/theories/ArithExt.eo` and its neighbours — an experimental **extension
  of a main theory**. `iand`, `piand` and `^` live there, each with the same
  `(include "../../theories/Arith.eo")` at the top of the file.

The expert files carry the contract in
[`CpcExpert.eo`][expert]: no proof from a safe build, or from a run restricted
with `--safe-mode=safe`, may reference anything declared there. Being outside
SMT-LIB does not put an operator in them — `int.pow2` is nonstandard and main.
What decides is whether cvc5 may use the operator in a safe build, which
[extending CPC theories](extending-cpc-theories.md#1-choose-main-or-expert)
works through.

## 2. Declare the operator

The declaration fixes the syntax and the type, and nothing else:

```lisp
; The "integer power of 2" operator.
; disclaimer: This function is not in SMT-LIB.
(declare-const int.pow2 (-> Int Int))
```

Follow its neighbours in three respects. The `; disclaimer:` comment is how the
signature records a symbol outside SMT-LIB, one of the structured comments the
files document themselves with. The name is the one cvc5 prints, exactly. And
the type is the whole of what the checker will enforce about applications:
`(-> Int Int)` is why `(int.pow2 true)` is rejected before any rule is
consulted.

`declare-const` and a function type are enough for an operator like this one.
Three things ask for more, and cvc5's `repeat` needs all three at once:

```lisp
(declare-parameterized-const repeat ((n Int :implicit) (i Int :opaque))
  (-> (BitVec n) (eo::requires ($is_pos_numeral i) true (BitVec (eo::mul i n)))))
```

**`:implicit`** is for a parameter the arguments determine: the width `n` is
read off the bit-vector, never written. **`:opaque`** is for an index the term
carries, as `repeat`'s repetition count is. And **`eo::requires`** inside the
type is how a declaration states a condition — here that the count is a positive
numeral — which is then checked on every application, including applications in
proof files no cvc5 build would ever emit. That last property is the reason to
state a condition in the type rather than to rely on the producer.

An operator that cvc5 prints with more than two arguments needs the attribute
that says how it associates: `:left-assoc` as `div` has it, `:right-assoc-nil`
with a nil terminator as `bvand` has it, or `:chainable` as `<` has it. Get this
from what cvc5 prints, not from SMT-LIB: `bvand` is binary in the standard and
declared `:right-assoc-nil` here, with a disclaimer comment saying why.

## 3. Teach the signature to compute it

A declaration alone gives you a term that no rule can do anything with. What
`evaluate` does with `int.pow2` comes from a program in
`proofs/eo/cpc/programs/Arith.eo`:

```lisp
; define: $arith_eval_int_pow_2
; args:
; - x Int: The term to compute take as the exponent of two.
; return: >
;   two raised to the power of x. If x is not a numeral value, we return
;   the term (int.pow2 x).
(define $arith_eval_int_pow_2 ((x Int))
  (eo::ite (eo::is_z x)
    (eo::ite (eo::is_neg x) 0 (eo::pow 2 x))
    (int.pow2 x)))
```

and one line in `Cpc.eo`, in the `$run_evaluate` program:

```lisp
(($run_evaluate (int.pow2 i1))       ($arith_eval_int_pow_2 ($run_evaluate i1)))
```

Three things in those two pieces are the lesson of this step.

**The evaluator is total.** Its outer `eo::ite` returns `(int.pow2 x)` unchanged
when `x` is not a numeral. `evaluate` is applied to whole terms, most of which
are not values, and a program that got stuck on an open argument would make the
rule fail on proofs that have nothing to do with your operator. Write the
fall-through case first and test it.

**It decides something SMT-LIB does not.** `(int.pow2 (- 3))` is `0` here,
because this program says so. Every such convention is a claim about the operator that
[step 7](#7-regenerate-logos-and-repair-the-proof) will ask you to prove.

**Evaluation is one program among several.** An operator can also need a case in
the rewriting or normalization programs under `proofs/eo/cpc/programs/`, and
rules of its own in `rules/<Theory>.eo`. Add the cases the rules you expect cvc5
to emit will reach, and no others: an unreachable case is a claim you will still
have to prove.

## 4. Check the declaration before touching cvc5

Ethos reads the edited `.eo` files directly, so this loop costs nothing and does
not need a cvc5 build. Write a proof that uses only the new operator, with no
`include` of its own:

```lisp
(assume @neq (not (= (int.pow2 3) 8)))
(step @eval (= (int.pow2 3) 8) :rule evaluate :args ((int.pow2 3)))
(step @false false :rule contra :premises (@eval @neq))
```

```bash
"$ETHOS" --include="$CVC5/proofs/eo/cpc/Cpc.eo" \
  --require-proof-of-false /absolute/path/to/proof.cpc
```

The expected result is `correct`. For an expert declaration, add
`--include="$CVC5/proofs/eo/cpc/expert/CpcExpert.eo"` and also check that the
same proof **fails** without it.

Then take the evaluator apart, one input at a time. The
[worked proofs](../examples/cpc-operator/README.md) are five files that differ
in exactly one thing each:

| Proof | What it establishes |
| --- | --- |
| `evaluate-value.cpc` | the computed case: `(int.pow2 3)` is `8` |
| `evaluate-open.cpc` | totality: on a variable, `evaluate` proves `(= t t)` |
| `evaluate-negative.cpc` | the convention: `(int.pow2 (- 3))` is `0` |
| `wrong-value.cpc` | claiming `9` is rejected, at the step |
| `wrong-type.cpc` | `(int.pow2 true)` is rejected, at the declaration |

Run all five with:

```bash
MIMESIS=/absolute/path/to/eudaimonia/tools/mimesis
python3 "$MIMESIS/examples/cpc-operator/check.py" "$ETHOS" "$CVC5"
```

That path is only for these examples; your own operator's tests are your own
files, and nothing in this workflow depends on Mimesis.

Read both rejections, because they fail in different places. A bad argument
fails at the application, before any rule is consulted, and the message names
the child and both types:

```
Error: wrong-type.cpc:3.34: Type checking failed:
Expression: (_ (= (int.pow2 true)) 8)
Message: Checking application of int.pow2
Unexpected type of child #1
  Term: true
  Has type: Bool
  Expected type: Int
```

A bad claim fails at the step, because `evaluate` computes its conclusion rather
than checking the one you wrote:

```
Error: wrong-value.cpc:4.66: Unexpected conclusion for rule evaluate:
    Proves: (_ (= (int.pow2 3)) 8)
  Expected: (_ (= (int.pow2 3)) 9)
```

`Proves` is what the rule computed and `Expected` is what your step claimed —
the labels are the opposite way round from what the words suggest, as the
[calculus tutorial](defining-a-calculus.md#4-the-same-distinction-on-the-way-out)
also notes. Both terms are printed desugared, which is why `(= a b)` appears as
`(_ (= a) b)`.

One failure has no message at all: an operator with **no** evaluation case still
type checks, and `evaluate` then proves `(= t t)` for it, silently. The
finite-field theory shows this in
[its worked proofs](../examples/cpc-theory/README.md). Test that your operator
computes what you think it computes, not merely that a proof using it passes.

## 5. Make cvc5 print the operator

Now that the signature accepts the term, make cvc5 emit it. For an operator cvc5
already has as a `Kind`, two lines connect it to the CPC name, and `int.pow2`
has both:

```cpp
addOperator(Kind::POW2, "int.pow2");     // src/parser/smt2/smt2_state.cpp
case Kind::POW2: return "int.pow2";      // src/printer/smt2/smt2_printer.cpp
```

The CPC name must match the declaration in step 2 exactly. If your operator's
CPC form is not that application — a constant that becomes an application, an
indexed type, a variadic term needing its nil terminator — it needs a case in
the converters under `src/proof/eo/`, which
[extending CPC theories](extending-cpc-theories.md#5-make-cvc5s-proof-output-agree)
works through for a theory that needs all of them.

Then produce a real proof from your changed cvc5, using the options
[cvc5's CPC documentation][cpc-docs] describes:

```bash
"$CVC5"/build/bin/cvc5 --proof-format-mode=cpc --proof-granularity=dsl-rewrite \
  --dump-proofs /path/to/input.smt2
```

Check that your operator appears with the spelling you declared, that the steps
around it are named rules rather than `trust`, and that Ethos accepts the result.
Give the checker the CPC commands inside the dump's `unsat` line and outer proof
list, not the whole file. For a main-signature operator, also run
`--safe-mode=safe` and a build configured with `./configure.sh safe`, and check
those proofs against `Cpc.eo` alone.

**An expert operator is finished here.** `CpcExpert.eo` is not compiled into
Logos, so there is no regeneration, Lean proof or pin update to do, and the
declaration may land while rule support is still incomplete.

## 6. Give the operator a meaning in Logos

The main signature continues. Logos compiles `Cpc.eo` into a Lean checker and
proves its rules sound against a formalized SMT-LIB semantics, and your operator
is a term in that calculus with no meaning yet. `install/defs/Cpc.eos` in a Logos
development checkout is where the meaning is given. There are three cases:

```lisp
; The target already has the operation: name it and stop.
(define-symbol int.pow2 (x))

; The target does not, but the operator is definable from what it has.
(define-symbol int.ispow2 (x)
  :term (and (>= x 0) (= x (int.pow2 (int.log2 x)))))
```

The third case is that the operation is genuinely new to the target, which lives
in the Ethos compiler's `tools/eoc/semantics/smt.eos`, one theory to a section.
An entry there gives the typing and the evaluation, and `int.pow2`'s own is:

```lisp
(define-symbol int.pow2 (x)
  :typeof (of1 Int Int x)
  :eval ((smt.numeral x)) (smt.numeral ("z_pow2" x)))
```

Prefer the first two cases. A `:term` translation adds nothing to the target:
the operator is eliminated on the way into the model, so everything already
proved about the target's own symbols carries it. A new target symbol extends
the semantics that every other proof is stated against. When you do change `smt.eos`, land it in
Ethos and advance Logos's compiler pin in `install/get-eo-compiler.sh`; the
[installer documentation][install] describes local overrides for development,
and the generation you land must use the pinned sources. A new **sort** rather
than a new operation is a larger obligation again, described in
[extending CPC theories](extending-cpc-theories.md#if-the-theory-must-go-to-the-main-signature).

## 7. Regenerate Logos and repair the proof

```bash
LOGOS=/absolute/path/to/logos
cd "$LOGOS"
install/get-eo-compiler.sh
install/install-cpc.sh --all "$CVC5/proofs/eo/cpc/Cpc.eo"
git status --short
```

`--all` regenerates both `Cpc` and `CpcMini`; Logos's own CI checks both. For
`int.pow2`, what comes out is the operator as a constructor, a parser entry and
a translation:

```lean
-- Cpc/LogosTerm.lean: the operator, as a constructor of the calculus
| int_pow2 : UserOp

-- Cpc/Parser.lean: the CPC name, its arity, and what it builds
{ name := "int.pow2"
  indexArity := 0
  arity := .exact 1
  build := fun
    | [] => some (Term.UOp UserOp.int_pow2)
    | _ => none },

-- Cpc/Spec.lean: the meaning, from the Cpc.eos entry of step 6
| (Term.Apply (Term.UOp UserOp.int_pow2) x1) => (SmtTerm.int_pow2 (__eo_to_smt x1))
```

Review those, along with `install/defs/Cpc.cached.eo`, the flattened signature
the installer refreshes and you commit with them. If they are wrong, the fix is
in the Eunoia sources or in `Cpc.eos`; a hand edit to a generated module is
overwritten by the next run.

**Then expect a broken proof, with no `sorry` to find.** A new rule gets a
generated proof file containing `sorry`, which is hard to miss. A new operator
gets none: it adds a case to an existing program, so what changed is the
statement of an **existing** rule's proof. `install-cpc.sh` preserves the
handwritten proofs under `Cpc/Proofs/`, and the build is what tells you which of
them no longer go through.

For an evaluated operator that proof is the `evaluate` rule's, and the
obligation is a transliteration of the Eunoia you wrote in step 3. This is the
`let` that `run_evaluate_sound_apply_int_pow2_core` reasons about, in
[`Cpc/Proofs/RuleSupport/Evaluate/SoundBitVec.lean`][sound-bv] — an arithmetic
operator whose proof sits among the bit-vector lemmas, which need powers of two
as well. Find yours by the name the dispatch gives it, not by the file you
expect:

```lean
let runPow :=
  __eo_ite (__eo_is_z (__run_evaluate b))
    (__eo_ite (__eo_is_neg (__run_evaluate b)) (Term.Numeral 0)
      (__eo_pow (Term.Numeral 2) (__run_evaluate b)))
    (__eo_mk_apply (Term.UOp UserOp.int_pow2) (__run_evaluate b))
```

The convention from step 3 is discharged where that tree meets the model: the
supporting lemma `eo_int_pow2_eval_numeral_to_smt` states that this computation
is the model's `int.pow2`, and its proof is a case split on whether the argument
is negative. A convention your signature makes up and the model does not share
fails exactly here, and nowhere earlier.

`SoundFinal.lean` dispatches the operator's case, and the rule file
[`Cpc/Proofs/Rules/Evaluate.lean`][evaluate] assembles the contract. Build it:

```bash
scripts/build.sh Cpc.Proofs.Rules.Evaluate
```

Building `logos` alone does not build the soundness proofs, and Lean accepts
`sorry` in an ordinary build. Choose the targets your own operator affects,
finish them, then run the hygiene check and the local CI groups:

```bash
bash scripts/check-proof-hygiene.sh
bash scripts/run-ci.sh
```

The [CPC validation procedure](adding-a-cpc-rule.md#6-validate-the-logos-change)
covers what CI does and does not build, and when to build the full development.
Finally, run your step 4 proofs through the rebuilt executable, which takes the
proof file alone:

```bash
./.lake/build/bin/logos /absolute/path/to/proof.cpc
```

`correct` is 0, `incorrect` 1 and `incomplete` 2; `incomplete` means the support
your proof needs is not finished. Commit the semantic sources, the cached
signature, the generated modules, the repaired proofs and the regressions
together.

## 8. Land Logos and update cvc5's pin

Merge the Logos change and wait for its workflow named `CI` to pass at the exact
commit you will pin. Set `LOGOS_VERSION` in `contrib/get-logos-checker` to that
full commit hash, and from cvc5:

```bash
cd "$CVC5"
./contrib/check-logos-compilation
```

Exit 0 means the pinned Logos generation matches your signature; 2 means it does
not, and the Logos side is unfinished. Then `./contrib/get-logos-checker`
installs the newly pinned checker, which should accept the proof your changed
cvc5 emits. The
[CPC landing procedure](adding-a-cpc-rule.md#7-land-logos-then-update-cvc5s-pin)
details the statuses and the CI requirement.

The operator is done when cvc5 prints it, Ethos checks it, Logos computes the
same thing for it, and the proof that says so is built.

## What it cost, for the ledger

An entry for the [ledger](../README.md#the-ledger), classified the way every
entry is. These are difficulties met while following the operator through, not
defects in anybody's tree.

| what happened | whose |
| --- | --- |
| an operator's Logos work arrives as a **broken finished proof with no `sorry` to find**. A new rule gets a generated file with a marker in it; a new operator adds a case to an existing program, so what moves is the statement of a proof somebody already completed | **nobody's**, and the entry's main finding — the work is wherever the build says it is, and no marker points at it |
| the soundness lemma for an integer operator sits among the bit-vector lemmas, because powers of two were already there | **nobody's** — file layout follows what a lemma needs and not what a reader expects; the workable advice is to find it by the name the dispatch gives it |
| a convention the signature invents — `(int.pow2 (- 3))` is `0` — is unchecked by everything until it meets the model, and then fails in exactly one lemma | **nobody's, and desirable.** It is what having a model is for. The cost is that no step of the cheap Ethos loop can tell you the convention is wrong |
| an operator with **no** evaluation case still type checks, and `evaluate` then proves `(= t t)` for it with no diagnostic | **nobody's** — absent support and support that agrees are indistinguishable from the outside, which is why the worked proofs test what the operator computes rather than that a proof passes |
| `Proves` names the computed term and `Expected` the claimed one, the opposite way round from how the words read | **the compiler's** — already recorded from [defining a calculus](defining-a-calculus.md#what-it-cost-for-the-ledger), and met again independently here, which is what makes it a label rather than an anecdote |
| the third case in step 6 — a genuinely new target operation — is a change to `smt.eos`, which is a change to the compiler and moves a second pin in a second repository | **nobody's** — and the reason this tutorial pushes `:term` translations over new target symbols, since a `:term` is eliminated on the way into the model and adds nothing to it |

**And what it does not measure.** Everything from step 5 onward was read rather
than run, as [Sources and validation](#sources-and-validation) records: no cvc5
build, no regeneration, no Lean proof. The rows above that concern the Logos side
are therefore about what the sources say the work is, and the one number nobody
here has — what repairing the `evaluate` proof for a new operator actually costs
— is still owed.

## Sources and validation

The [five worked proofs](../examples/cpc-operator/README.md) were run on
2026-09-18 against cvc5 `2900761a7c2e2c0e99e2cf669cffa3740ea9a138`, the merged
[PR #12891][pr], with Ethos built from that revision's checker pin,
`8dc85c4db8d6cc612f02dc3bb627331732605eff`. All five passed: three refutations
and two rejections, each checked for its expected diagnostic.

Everything from step 5 onward is a procedure read from sources, not a completed
operator development. No cvc5 build, Logos regeneration, Lean proof or pin update
was performed. The cvc5 integration was read at the revision above. The Logos
files named here were read at cvc5's pin,
[`664c35d6e188a62d5b5dac8fb403d19b9e0f4baa`][logos]: `install/defs/Cpc.eos`,
`install/install-cpc.sh`, the generated `Cpc` modules, and the `evaluate` proof
and its support. `smt.eos` was read in that revision's compiler pin,
`406b5499f3c83f2a114113107be251f8e58b2d85`.

[pr]: https://github.com/cvc5/cvc5/pull/12891
[cpc-docs]: https://cvc5.github.io/docs-ci/docs-main/proofs/output_cpc.html
[kinds]: https://github.com/cvc5/cvc5/blob/2900761a7c2e2c0e99e2cf669cffa3740ea9a138/src/theory/builtin/kinds.toml
[expert]: https://github.com/cvc5/cvc5/blob/2900761a7c2e2c0e99e2cf669cffa3740ea9a138/proofs/eo/cpc/expert/CpcExpert.eo
[logos]: https://github.com/cvc5/logos/tree/664c35d6e188a62d5b5dac8fb403d19b9e0f4baa
[install]: https://github.com/cvc5/logos/blob/664c35d6e188a62d5b5dac8fb403d19b9e0f4baa/install/README.md
[sound-bv]: https://github.com/cvc5/logos/blob/664c35d6e188a62d5b5dac8fb403d19b9e0f4baa/Cpc/Proofs/RuleSupport/Evaluate/SoundBitVec.lean
[evaluate]: https://github.com/cvc5/logos/blob/664c35d6e188a62d5b5dac8fb403d19b9e0f4baa/Cpc/Proofs/Rules/Evaluate.lean
