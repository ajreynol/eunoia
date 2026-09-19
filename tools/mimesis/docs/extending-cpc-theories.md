# Extending CPC theories

Part of the [Eunoia tutorials](tutorials.md).

A theory is five things: a sort, the values of that sort, the operators over it,
the proof support that reasons about them, and a decision about whether cvc5 may
use any of it in a safe build. This tutorial follows cvc5's finite fields — an
expert theory whose whole CPC declaration is thirty-three lines — through all
five. Read them as the model for your theory; do not add a second copy of them.

Its two neighbours: one operator over sorts that already exist is the shorter
job in [extending CPC with a new theory operator](extending-cpc-operators.md),
which is also where the Logos mechanics this tutorial refers to are worked
through; a new inference is [adding a CPC rule](adding-a-cpc-rule.md).

**Not in scope: implementing the theory in cvc5.** This starts from a theory
cvc5 already solves — its kinds, type rules, rewriter and solver. cvc5's wiki
records [how finite fields were added to the solver][add-theory]; everything
below is the proof side of that same work.

**What was run:** the [six worked proofs](../examples/cpc-theory/README.md)
against cvc5's signature, with Ethos. The cvc5 integration, the safe-mode
behaviour and the Logos requirements are read from sources at the fixed
revisions [recorded below](#sources-and-validation).

## The whole theory, first

This is all of [`expert/theories/FiniteFields.eo`][finite-fields], the complete
CPC declaration of finite fields, with its comments:

```lisp
(include "../../theories/Arith.eo")

; disclaimer: >
;   This sort is not in the SMT-LIB standard. All further function
;   symbols over this sort are also not part of the SMT-LIB standard.
(declare-const FiniteField (-> Int Type))

; program: $ff_size
; args:
; - T Type: The finite field type.
; return: The (integer value) size for a given finite field type.
(program $ff_size ((n Int))
  :signature (Type) Int
  (
  (($ff_size (FiniteField n)) n)
  )
)

; A finite field constant is a term having 2 integer children.
; note: we do not support the native syntax for finite field values.
(declare-parameterized-const ff.value ((p Int)) (-> Int (FiniteField p)))

(declare-parameterized-const ff.add ((p Int :implicit))
    (-> (FiniteField p) (FiniteField p) (FiniteField p))
    :right-assoc-nil (ff.value p 0))
(declare-parameterized-const ff.neg ((p Int :implicit))
    (-> (FiniteField p) (FiniteField p)))
(declare-parameterized-const ff.mul ((p Int :implicit))
    (-> (FiniteField p) (FiniteField p) (FiniteField p))
    :right-assoc-nil (ff.value p 1))
(declare-parameterized-const ff.bitsum ((p Int :implicit))
    (-> (FiniteField p) (FiniteField p) (FiniteField p))
    :right-assoc-nil (ff.value p 0))
```

Every line of it is a decision, and the rest of this tutorial is those decisions
in the order you will make them. What is *not* in the file matters as much: no
evaluation, no rewrites, no rules. Proof support is separate from vocabulary,
and this theory has almost none.

Set the paths the commands below use:

```bash
CVC5=/absolute/path/to/cvc5
ETHOS=/absolute/path/to/ethos
```

`./contrib/get-ethos-checker` in cvc5 builds Ethos at `deps/bin/ethos` if you
need one. Keep the whole `proofs/eo/` subtree: the files include each other by
relative path.

## 1. Choose main or expert

Make this choice first; it decides where the files go and how much work follows.
All paths are relative to `proofs/eo/cpc/`:

| Path | Theory declarations | Rules | Entry point |
| --- | --- | --- | --- |
| Main | `theories/<Theory>.eo` | `rules/<Theory>.eo` | `Cpc.eo` |
| Expert | `expert/theories/<Theory>.eo` | `expert/rules/<Theory>.eo` | `expert/CpcExpert.eo` |

The contract stated in [`CpcExpert.eo`][expert] is that proofs emitted by safe
builds, or by a run restricted with `--safe-mode=safe`, never reference anything
declared in the expert subdirectory. That is the criterion: not whether the theory is in
SMT-LIB, and not whether it is finished. `int.pow2` is nonstandard and main;
finite fields are a real cvc5 theory and expert.

What each path costs:

- **Expert** ends at [step 8](#8-gate-the-theory-in-cvc5). `CpcExpert.eo` is not
  compiled into Logos, so there is no semantics to give, no Lean proof to write
  and no pin to update. Declarations may land while proof-rule support is still
  incomplete. Expert files may include main files; main files must never include
  expert files.
- **Main** additionally owes the theory a meaning in Logos and a soundness proof
  for every rule, described in
  [the last section](#if-the-theory-must-go-to-the-main-signature).

Create the file and include it from the entry point you chose:

```lisp
(include "./theories/MyTheory.eo")
```

Loading that entry point should now reach your new, empty file.

## 2. Declare the sort

```lisp
(include "../../theories/Arith.eo")

(declare-const FiniteField (-> Int Type))
```

A sort is a constant whose result type is `Type`, so `FiniteField` is a function
from an integer to a type and `(FiniteField 7)` is a type. Because the index is
an integer, the file needs integer vocabulary, which is what the include is for.
A sort with no index is simply `(declare-const MySort Type)`.

The declaration gives the index a type and nothing more. `(FiniteField 6)` is a
well-formed CPC type, and the [worked proofs](../examples/cpc-theory/README.md)
include a file that uses one, because Ethos accepts it. cvc5 will never build
that sort — it restricts field sizes to primes where it stores them, in
`src/util/finite_field_value.h` — but a checker reads arbitrary proof files, not
just cvc5's. Write down which restrictions your types enforce and which do not,
and keep the list: it is what [step 6](#6-give-the-theory-proof-support) and the
model both have to account for.

A program can match on a type, which is how the index is read back off one:

```lisp
(program $ff_size ((n Int))
  :signature (Type) Int
  (
  (($ff_size (FiniteField n)) n)
  )
)
```

Nothing in the signature calls `$ff_size`: this theory has no rule that needs
the field size yet. It is written anyway, because a program matching on the type
is the only way to recover an index, and any rule that computes with one — that
reduces a value modulo the field size, say — will start here, from the
`eo::typeof` of a term rather than from the term itself.

## 3. Declare the values

```lisp
; A finite field constant is a term having 2 integer children.
; note: we do not support the native syntax for finite field values.
(declare-parameterized-const ff.value ((p Int)) (-> Int (FiniteField p)))
```

A theory's constants need a CPC spelling, and it need not be the SMT-LIB one.
SMT-LIB writes the element 5 of the field of order 7 as `#f5m7`; CPC writes
`(ff.value 7 5)`, an ordinary application with two integer children. The
parameter `p` is explicit here, not `:implicit`, because nothing in the
application's arguments determines the field.

That choice is half of a decision whose other half is in cvc5's converter, in
[step 5](#5-make-cvc5s-proof-output-agree). Make it once, deliberately: a
value encoding that the converter does not produce, or types the encoding cannot
express, are the two ways this goes wrong, and both show up only when a real
proof is checked.

## 4. Declare the operators

```lisp
(declare-parameterized-const ff.add ((p Int :implicit))
    (-> (FiniteField p) (FiniteField p) (FiniteField p))
    :right-assoc-nil (ff.value p 0))
```

Three decisions, all of them enforced on every application:

**`:implicit`** says the field parameter is recovered from the arguments rather
than written. One consequence is the whole of what the types enforce about
addition: both arguments mention the same `p`, so adding an element of
`(FiniteField 7)` to one of `(FiniteField 11)` fails to type check.

**`:right-assoc-nil`** makes the operator n-ary, with the field's zero as its nil
terminator — and the terminator is itself parameterized, `(ff.value p 0)`. So
`(ff.add x y)` is `(ff.add x (ff.add y (ff.value 7 0)))` underneath, `(ff.add x)`
is a one-element list, and `(ff.add x (ff.value 7 0))` and `x` are the same term.
Anything that treats the operator as a list — normalization, the `eo::list_*`
operators — depends on that choice.

**The terminator is per operator**: `ff.mul` ends in `(ff.value p 1)`, because
the identity of multiplication is one. `ff.neg`, being unary, has neither
attribute.

Declare the operators cvc5 actually prints, with the arities and the argument
order it prints them in, and no others. `ff.bitsum` is in the file because cvc5
has a kind that prints it.

## 5. Make cvc5's proof output agree

The signature now accepts terms. Whether cvc5 emits *those* terms is a separate
question — the solver side is assumed to be in place — and for a new sort it
usually needs work in more than one converter. Here is where finite fields are
handled, and what each place decides:

| cvc5 source | What it decides | Finite fields |
| --- | --- | --- |
| `src/parser/smt2/smt2_state.cpp` | the names and literals the input uses | `addFiniteFieldOperators()`, the `FiniteField` sort, and `#f<value>m<size>` constants |
| `src/printer/smt2/smt2_printer.cpp` | the names cvc5 prints | `(_ FiniteField p)`, `#f5m7`, and `case Kind::FINITE_FIELD_ADD: return "ff.add";` |
| `src/proof/eo/eo_node_converter.cpp` | how a term becomes a CPC term | `CONST_FINITE_FIELD` becomes `mkInternalApp("ff.value", {fs, v}, tn)` |
| `src/proof/eo/eo_dependent_type_converter.cpp` | how an indexed type becomes a CPC type | `d_kindToName[Kind::FINITE_FIELD_TYPE] = "FiniteField"`, plus its abstract-type case |
| `src/proof/eo/eo_list_node_converter.cpp` | n-ary applications and their terminators | `FINITE_FIELD_ADD` and `FINITE_FIELD_MULT` among the n-ary kinds |
| `src/proof/eo/eo_printer.cpp` | the names and arguments of the rules used on these terms | the rules from step 6 |

The node converter is where step 3's decision is honoured, and it is worth
reading closely: a finite-field constant is not printed as a constant at all but
built as an application, size first and value second — the opposite order from
the `#f5m7` literal the SMT-LIB printer produces. Two spellings of one value,
and the converter is the only place that says how they correspond.

Then exercise the theory in your changed cvc5, using the options
[cvc5's CPC documentation][cpc-docs] describes:

```bash
"$CVC5"/build/bin/cvc5 --proof-format-mode=cpc --proof-granularity=dsl-rewrite \
  --dump-proofs /path/to/input.smt2
```

Read the emitted terms against your declarations, and check the proof with
Ethos, giving the checker the CPC commands inside the dump's `unsat` line and
outer proof list. Record every remaining `trust` step: those are the parts of
the theory whose proof support does not exist yet.

## 6. Give the theory proof support

Rules go in `rules/<Theory>.eo` or `expert/rules/<Theory>.eo`, include their
theory with `(include "../theories/<Theory>.eo")`, and are reached from the
entry point of step 1. The [CPC rule tutorial](adding-a-cpc-rule.md) is how to
write one.

Finite fields have no rule file at all. Their entire proof support is two cases
in a program in [`CpcExpert.eo`][expert], which normalize an application of the
two associative-commutative operators:

```lisp
(($get_aci_normal_form_expert (ff.add xf1 xf2))  (@aci.sorted ff.add ($get_a_norm (ff.add xf1 xf2))))
(($get_aci_normal_form_expert (ff.mul xf1 xf2))  (@aci.sorted ff.mul ($get_a_norm (ff.mul xf1 xf2))))
```

with the field-element variables declared in the program's parameter list as
`(m Int) (xf1 (FiniteField m)) (xf2 (FiniteField m) :list)`. That is enough to
prove that addition commutes and that adding the field's zero changes nothing —
the second of those falls out of the nil terminator from step 4, with no rule
about zero anywhere. Two of the worked proofs are exactly these.

**What is missing is silent.** `$run_evaluate` in `Cpc.eo` has no case for any
`ff` operator, so evaluating a finite-field term returns it unchanged and the
`evaluate` rule proves `(= t t)`. Nothing errors. A step that claims the sum of
3 and 5 in the field of order 7 is 1 is rejected not because the arithmetic is
wrong but because the rule computed the term back to itself:

```
Error: no-evaluation.cpc:7.63: Unexpected conclusion for rule evaluate:
    Proves: (eo::define ((_v0 (ff.value 7))) (eo::define ((_v1 (_ (ff.add (_ _v0 3)) (_ (ff.add (_ _v0 5)) (_ _v0 0))))) (_ (= _v1) _v1)))
  Expected: (eo::define ((_v0 (ff.value 7))) (_ (= (_ (ff.add (_ _v0 3)) (_ (ff.add (_ _v0 5)) (_ _v0 0)))) (_ _v0 1)))
```

`Proves` is what the rule computed and `Expected` is what the step claimed. The
computed side binds `_v1` to the whole sum and proves `(= _v1 _v1)`; the sum
itself, printed desugared, is the nil-terminated list from step 4.

Every theory starts here. Decide which rules cvc5 will emit for your theory, add
their support, and test each one; support you did not write is absent rather
than broken, and nothing in the signature will point at it.

## 7. Check the theory with Ethos

Write proofs that use the theory and include neither signature themselves. For
an expert theory, load both:

```bash
"$ETHOS" --include="$CVC5/proofs/eo/cpc/Cpc.eo" \
  --include="$CVC5/proofs/eo/cpc/expert/CpcExpert.eo" \
  --require-proof-of-false /absolute/path/to/proof.cpc
```

A main theory takes `Cpc.eo` alone. Omit `--require-proof-of-false` for a file
that only declares and asserts: you do not need any proof rules to check that
your terms typecheck, which is the first thing to test after step 4.

The [six worked runs](../examples/cpc-theory/README.md) cover what a theory
should be asked:

| Run | What it establishes |
| --- | --- |
| `aci-norm.cpc`, main only | the expert theory is invisible to `Cpc.eo`: `FiniteField` is not a symbol |
| `aci-norm.cpc`, both | `ff.add` commutes, by `aci_norm_expert` |
| `nil-terminator.cpc` | `(ff.add x (ff.value 7 0))` and `x` are one term |
| `no-evaluation.cpc` | the theory has no evaluation, and how that fails |
| `non-prime.cpc` | `(FiniteField 6)` type checks; the sort declaration says nothing about primality |
| `mixed-fields.cpc` | adding across two field sizes does not type check |

```bash
MIMESIS=/absolute/path/to/eudaimonia/tools/mimesis
python3 "$MIMESIS/examples/cpc-theory/check.py" "$ETHOS" "$CVC5"
```

That path is only for these examples; your own theory's tests are your own
files, and nothing in this workflow depends on Mimesis.

The main-only run is not a formality. cvc5's `cpc_gen.sh` helper, installed by
`contrib/get-ethos-checker`, includes both signatures by default, so an expert
symbol that has crept into a safe-mode proof will check happily unless you pass
the includes yourself. Run it explicitly, on every proof that is supposed to be
safe.

## 8. Gate the theory in cvc5

Moving declarations into `expert/` does not make a feature unavailable in a safe
build; three other places do, and a new theory has to join each of them.
Finite fields:

- **`src/options/ff_options.toml`** declares the theory's options with
  `category = "expert"`, including the `--ff` option that enables it.
- **`src/smt/set_defaults.cpp`** disables it whenever safe mode is on, with the
  other experimental theories: `SET_AND_NOTIFY(ff, ff, false, "safe options");`
- **`src/smt/illegal_checker.cpp`** turns that off switch into a rejection: with
  `THEORY_FF` in the logic but `--ff` off, the theory joins
  `unsupportedTheories`, every kind belonging to it becomes illegal, and an
  input using one raises `SafeLogicException` — suggesting `--ff` in builds
  where the option exists.

Check the result from both ends. A restricted cvc5 must reject an input that
uses the theory, and every proof it emits must check against `Cpc.eo` alone.
A normal build tests the first half with one flag, and a safe build tests it as
users get it:

```bash
cvc5 --safe-mode=safe /path/to/input-using-the-theory.smt2
./configure.sh safe && cd build && make
```

**The expert path ends here.** With declarations that cvc5 agrees with, proof
support for the rules it emits, and the safe-mode gate in place, an expert
theory is ready for review even if its proof support is incomplete.

## If the theory must go to the main signature

Then the theory needs a meaning, and every rule over it needs a soundness proof
against that meaning. Finite fields have neither: nothing in Logos mentions
them, which is what being expert means. What follows is the shape of the work,
read from the sources, with bit-vectors as the worked model — the theory Logos
does support that most resembles a field indexed by a number.

**A sort needs a translation.** `install/defs/Cpc.eos` has a section of type
constructors, each saying what a CPC type becomes in the model:

```lisp
(define-symbol BitVec ((! n :raw))
  :type (BitVec (eo.numeral n)) ("ite" ("zleq" 0 n) (BitVec ("z_to_n" n)) none))
```

The `ite` is the whole point of the entry: an index the target has no type for —
here a negative width — is sent to `none`, and a CPC type that translates to
`none` is no type of the model. This is where `(FiniteField 6)` from step 2
would go. The restriction the sort declaration does not make gets made here, in
the one place where making it means something.

**A sort needs a semantic domain.** The target semantics is
`tools/eoc/semantics/smt.eos` in Logos's pinned Ethos compiler. Three additions
are needed there. A value shape, added at the end of the value section because
what is derived from their order depends on it:

```lisp
(declare-constructor Binary ((w <numeral>) (v <numeral>)) :builds SmtValue
  :typeof ("ite" ("and" ("zleq" 0 w) ("zeq" v ("mod_total" v ("z_pow2" w))))
            (BitVec ("z_to_n" w))
            none)
  :canonical ("ite" ("zleq" 0 w)
               ("zeq" v ("mod_total" v ("z_pow2" w)))
               "true"))
```

Read what those two answers are for. `:typeof` says which type a value of this
shape belongs to, and answers `none` for a payload that is not one — a width
below zero, or a value not reduced to it. `:canonical` says whether it is the
one spelling of what it denotes, which for a bit-vector is again being reduced.
A field element would answer both in terms of its own order, and the primality
the sort needs would be part of the first.

The sort itself, answering the three questions asked of every sort — whether its
values are a set at all, whether it is bounded, and what a model reaches for
when it must name a value:

```lisp
(define-sort BitVec ((! w :raw))
  :bounded ("or" ("not" u) ("nateq" w "n_zero"))
  :default (smt.binary ("n_to_z" w) 0))
```

And each operator, with its typing rule and its evaluation:

```lisp
(define-symbol bvadd (x y)
  :typeof ($smtx_typeof_bv_op_2 x y)
  :eval ((smt.binary n x) (smt.binary m y)) (of_width n ("zplus" x y)))
```

Note what the typing rule does: `$smtx_typeof_bv_op_2` is what says two
arguments must be of one width, which is the model's version of the `:implicit`
parameter from step 4. The same restriction is now stated twice, in two
languages, and Logos's type-preservation proofs are where the two have to
agree — which is the general shape of this work, and the reason the semantics
is worth writing before the rules.

**Then the ordinary machinery.** A change to `smt.eos` is a change to the
compiler: land it in Ethos and advance Logos's compiler pin in
`install/get-eo-compiler.sh`. After that, regeneration, the rule proofs and
cvc5's pin are the same steps as for one operator, in
[that tutorial's steps 7 and 8](extending-cpc-operators.md#7-regenerate-logos-and-repair-the-proof),
with one difference of scale: every rule you declared in step 6 arrives as a
generated proof file containing `sorry`, and each is proved against the model
you just wrote.

Two warnings worth having before you start. Mapping the new sort onto an
uninterpreted one is not a meaning: a finite field that the model does not
interpret as a finite field proves nothing about finite-field reasoning. And the
restrictions you listed in step 2 have to be discharged rather than assumed —
the model is where a field of non-prime order stops existing, and any rule whose
soundness depends on that has to say so.

## What it cost, for the ledger

An entry for the [ledger](../README.md#the-ledger), classified the way every
entry is. These are difficulties met while following cvc5's finite fields
through, not defects in anybody's tree.

| what happened | whose |
| --- | --- |
| a field element has two spellings — SMT-LIB's `#f5m7` literal and CPC's `(ff.value 7 5)` application, size first and value second — and one converter is the only place that says how they correspond | **nobody's** — two printers with two jobs; the cost is that the correspondence is findable only by reading `eo_node_converter.cpp`, and a signature written from the literal gets the argument order backwards |
| moving declarations into `expert/` does not gate a feature: three other cvc5 files do, in options, defaults and the illegal-kind checker | **the documentation's** — the directory reads as the gate, and a theory that stopped at it would be experimental in the signature and available in a safe build |
| `cpc_gen.sh`, the convenient way to check a proof, includes both signatures by default — so an expert symbol that has crept into a proof meant to be safe checks happily unless the includes are passed by hand | **nobody's** — the convenient invocation is the permissive one, which is why the worked runs include a main-only run of the same file |
| `$run_evaluate` has no case for any `ff` operator, so evaluating a field term returns it unchanged, and the failure surfaces as a `Proves` / `Expected` pair in which both sides are the same sum rather than as a missing-support message | **nobody's** — the same silence the [operator entry](extending-cpc-operators.md#what-it-cost-for-the-ledger) records, at theory scale and correspondingly harder to read |
| the restriction the sort declaration does not make — `(FiniteField 6)` type checks — is made in the model's type translation, where an index the target has no type for goes to `none` | **nobody's, and the finding.** The signature is a syntax; the model is the one place a restriction becomes a fact, and a rule whose soundness needs primality has to say so there |
| an `:implicit` width and the model's own typing rule state one restriction twice, in two languages, and type preservation is where they are made to agree | **nobody's** — and the reason the tutorial says to write the semantics before the rules |
| the expert route and the main route share almost nothing after step 5: a main theory owes a value shape, a sort, every operator in `smt.eos` and a proof per rule, none of which the expert route needs | **nobody's** — that asymmetry is what the expert route buys, and its cost is that a theory promoted later repeats the second half from scratch |

**And what it does not measure.** No theory was implemented and no cvc5 build was
configured; [Sources and validation](#sources-and-validation) says what was run.
The main-signature section is the shape of the work read from bit-vectors, so its
rows are about what the sources require rather than about what anybody paid —
and finite fields remain outside Logos's calculus, so nobody has paid it.

## Sources and validation

The [six worked runs](../examples/cpc-theory/README.md) were run on 2026-09-18
against cvc5 `2900761a7c2e2c0e99e2cf669cffa3740ea9a138`, the merged
[PR #12891][pr], with Ethos built from that revision's checker pin,
`8dc85c4db8d6cc612f02dc3bb627331732605eff`. All six passed: two refutations and
four rejections or acceptances checked for their expected output. They are
hand-written proof tests against cvc5's existing expert theory, not proofs
emitted by a solver.

No new theory was implemented. The cvc5 integration and safe-mode sources were
read at the revision above; no cvc5 build was configured or run. The Logos
requirements were read at cvc5's pin,
[`664c35d6e188a62d5b5dac8fb403d19b9e0f4baa`][logos] — `install/defs/Cpc.eos` and
its installer — and in that revision's compiler pin,
`406b5499f3c83f2a114113107be251f8e58b2d85`, whose `tools/eoc/semantics/smt.eos`
is the source of the bit-vector model quoted above. No Logos regeneration or
Lean proof was performed, and finite fields remain outside Logos's calculus.

[pr]: https://github.com/cvc5/cvc5/pull/12891
[cpc-docs]: https://cvc5.github.io/docs-ci/docs-main/proofs/output_cpc.html
[add-theory]: https://github.com/cvc5/cvc5/wiki/Adding-a-new-theory-to-cvc5
[expert]: https://github.com/cvc5/cvc5/blob/2900761a7c2e2c0e99e2cf669cffa3740ea9a138/proofs/eo/cpc/expert/CpcExpert.eo
[finite-fields]: https://github.com/cvc5/cvc5/blob/2900761a7c2e2c0e99e2cf669cffa3740ea9a138/proofs/eo/cpc/expert/theories/FiniteFields.eo
[logos]: https://github.com/cvc5/logos/tree/664c35d6e188a62d5b5dac8fb403d19b9e0f4baa
