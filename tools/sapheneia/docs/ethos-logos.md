# Eunoia in ethos, and Eunoia in logos

**A living comparison.** Two tools read the same Eunoia signature and do not
read it the same way. This page is the register of where they come apart, why,
and whether the language says which is right.

It is part of [sapheneia](../README.md) and inherits its charter: it describes,
it does not adjudicate, and it proposes no change to anything. Where the two
readings disagree and the manual does not settle it, the row says so and stops
— which is the same three-way split [`manual.md`](manual.md) uses, applied to
two implementations instead of to one implementation and a document.

---

## Why there is anything to compare

**ethos reads Eunoia.** A signature is parsed, its declarations are held in a
symbol table, and a proof is checked against them by an evaluator written in
C++. The language and the program are one artifact.

**logos does not read Eunoia at all.** It checks proofs against a Lean package,
and that package is *compiled* from the signature, once, by `ethos-eoc`:

```text
                       ┌──────────────── ethos (C++ evaluator) ──── verdict
  Cpc.eo ──────────────┤
  (the signature)      │
                       └── ethos-eoc ──────────────────────────┐
                            desugar                            │
                            trim-defs      + Cpc.eos           │
                            lean-meta      + lean.eos          │
                                                               ▼
                                                        Cpc/*.lean  ─── logos ─── verdict
```

So "how logos interprets Eunoia" is not a thing anybody wrote down. It is the
composition of four things, none of which is the language:

| the part | what it decides | where it lives |
| --- | --- | --- |
| the **desugar stage** | what the `eo::` operators mean, as Eunoia programs over a deep embedding | `plugins/desugar/eo_desugar*.eo` |
| the **native layer** | what the embedding's 66 primitives are, in Lean | `plugins/lean_meta/lean.eos` |
| the **semantics set** | what CPC's own symbols mean, and the termination measures | `install/defs/Cpc.eos` (logos) |
| the **logos parser** | what a proof file says, re-decided in Lean | `Logos/Parser.lean`, `Cpc/Parser.lean` |

The first two are a second implementation of Eunoia's evaluator. The third is
configuration a person writes by hand. The fourth is a second front end that
never consults the first three. **Every row below is a difference introduced by
one of those four**, and the `kind` column says which sort of difference it is:

| kind | means |
| --- | --- |
| **divergence** | both sides answer, and the answers differ |
| **hole** | Eunoia has a construct the compilation does not reach |
| **closure** | Eunoia leaves something open and the compiled artifact fixes it |
| **front end** | logos's own parser re-decides a question ethos's parser already decided |
| **seam** | nothing checks that the two correspond; the mismatch is the absence of a check |

And `settled?` says whether the ethos manual adjudicates. **No** means the row
is not a defect in either tool — it is a place the language is undefined, and it
belongs to [`manual.md` §11](manual.md) as an instance rather than to
anybody's bug tracker.

---

## The ledger

| id | where | in one line | kind | settled? |
| --- | --- | --- | --- | --- |
| [EL-01](#el-01) | evaluation | decimal collapses into rational, hexadecimal into binary | divergence | yes |
| [EL-02](#el-02) | evaluation | a failed evaluation is a residual term in ethos and a single `Stuck` in logos — mechanism differs, no witness found | divergence | yes |
| [EL-03](#el-03) | evaluation | `eo::extract` clamps to the operand's width in ethos and not in the embedding | divergence | yes |
| [EL-04](#el-04) | evaluation | `eo::cmp` orders terms by two unrelated orders, and `eo::hash` has no Lean at all | divergence + hole | **no** |
| [EL-05](#el-05) | programs | Lean demands a termination argument Eunoia never asks for | hole | **no** |
| [EL-06](#el-06) | types | `eo::typeof` is monomorphised per partial application, with no marker | closure | **no** |
| [EL-07](#el-07) | types | an ill-typed but unambiguous term is rejected by ethos and accepted by logos | divergence | yes |
| [EL-08](#el-08) | lists | the nil predicate of a polymorphic n-ary operator is hand-written and unchecked | seam | yes |
| [EL-09](#el-09) | terms | the Lean term language is closed over one signature | closure | **no** |
| [EL-10](#el-10) | overloading | most-recently-declared-that-types, versus exact-arity-then-first-that-types | divergence | yes |
| [EL-11](#el-11) | coverage | `lambda` and `beta-reduce` are compiled out; the calculus logos checks is a proper subset | closure | n/a |
| [EL-12](#el-12) | commands | an `assume` after the first step is accepted by ethos and refused by logos | front end | yes |
| [EL-13](#el-13) | commands | `include` and `reference` are ignored | front end | yes |
| [EL-14](#el-14) | commands | `declare-datatypes` blocks are reordered, and parametric ones refused | front end | partly |
| [EL-15](#el-15) | commands | `define` with parameters is a macro re-read at each use site | front end | **no** |
| [EL-16](#el-16) | commands | the conclusion written on a `step` is ignored | front end | yes |
| [EL-17](#el-17) | literals | a `\u` escape naming a surrogate is a character in ethos and an error in logos | front end | **no** |
| [EL-18](#el-18) | the seam | logos's package is compiled by an ethos the ethos tree has moved past | seam | n/a |
| [EL-19](#el-19) | the seam | no one checks that the natives a run reaches are the natives a layer implements | seam | n/a |
| [EL-20](#el-20) | verdicts | logos has a third verdict ethos has no counterpart for | closure | n/a |

---

## Evaluation and values

### EL-01

**Decimal collapses into rational, and hexadecimal into binary.**

Eunoia has six literal categories, and ethos keeps decimals apart from
rationals and hexadecimals apart from binaries as *distinct kinds of term* —
`1.0` and `1/1` are not the same term, and neither are `#x1f` and
`#b00011111`. The manual says so directly, under `eo::is_q` ("Note this returns
false for decimal literals") and `eo::is_bin` ("Note this returns false for
hexadecimal literals").

The compiled Lean has four literal constructors, not six:

```lean
-- Cpc/LogosTerm.lean, via the generated Term inductive
Term.Numeral (n : native_Int)  Term.Rational  Term.String  Term.Binary (w n)
```

and the parser maps both forms onto one of them — `#x1f` becomes
`.binary (4 * digits.length) 31`, and a decimal goes through `ofDecimal` to
`.rational` (`Logos/Parser.lean`, `Literal.ofString`). So on the logos side
`1.0` **is** `1/1`, and `#x1f` **is** `#b00011111`.

| term | ethos | logos |
| --- | --- | --- |
| `(eo::is_q 1.0)` | `false` | `true` |
| `(eo::is_bin #x1f)` | `false` | `true` |
| `(eo::is_eq 1.0 1/1)` | `false` | `true` |
| `(eo::is_eq #x1f #b00011111)` | `false` | `true` |

**Evidence.** The ethos column is *run* — see [How to re-check](#how-to-re-check)
for the probe. The logos column is *read* off `Cpc/Logos.lean`
(`__eo_is_q_internal`, `__eo_is_bin_internal`, `__eo_eq`) and
`Logos/Parser.lean`; it has not been executed here.

**Whether it bites.** `eo::is_q` is reached 4 times and `eo::is_bin` 5 times in
the CPC signature logos compiled, so this is live rather than latent. It is
also the mechanism behind sapheneia's existing *category preservation in
arithmetic* question ([`manual.md` §11](manual.md)): `eo::add` on two
decimals gives a decimal in ethos and a `Term.Rational` in logos, and every
predicate downstream inherits the difference.

### EL-02

**A failed evaluation is a residual term in ethos and a single `Stuck` in
logos.**

The manual's phrase for a computational operator that cannot compute is *does
not evaluate*, and it means the application survives as a term: `(BitVec
(eo::add a b))` is a legitimate type when `a` and `b` are not values, and
`(eo::to_z "451")` is a legitimate term that says which computation failed.

The compiled Lean has one failure value, `Term.Stuck`, and the `lean-meta`
stage prepends stuck-propagation cases to every program that matches a
parameter in an argument position whose meta-kind is Eunoia
(`LeanMetaReduce::finalizeProgram`, `plugins/lean_meta/lean_meta_reduce.cpp`):

```lean
def __poly_add : Term -> Term -> Term
  | Term.Stuck , _  => Term.Stuck
  | _ , Term.Stuck  => Term.Stuck
  ...
```

**Evidence.** logos: read, off the generated guard cases (2588 lines of
`Cpc/Logos.lean` name `Term.Stuck`) and the stage that writes them. ethos: the
manual, and run for the negative result below.

**Whether it bites: no witness found, and the obvious one does not work.** The
example to reach for is a program with a catch-all case applied to a residual —
it should match in ethos and go to `Stuck` in Lean. It does not: **ethos does
not invoke a program on an argument that failed to evaluate**, and the manual
says so ("Programs are *not* invoked on terms that fail to evaluate"). Run
against the build below, `(f (eo::to_z "451"))` with `f` a one-case catch-all
program does not evaluate, exactly as the compiled Lean returns `Stuck`. The
same holds for a program applied to a program and for one applied to an `eo::`
operator.

That rule is what closes most of the gap: a residual can be *built*, but a
signature cannot get a program to look at one, so the extra information a
residual carries is mostly unreachable from Eunoia. What is left is two
narrower things, neither yet witnessed changing an answer:

- `eo::is_ok` asks *is this term fully reduced* in ethos
  (`!isEvaluatable`, `src/type_checker.cpp`) and *is this the one failure
  constant* in Lean (`native_not (native_teq x Term.Stuck)`). Every case tried
  here agrees, because `__eo_mk_apply` propagates stuckness out to the whole
  term wherever the compiler could not rule it out statically. Whether the
  compiler's static judgement — `Term.Apply` unguarded versus `__eo_mk_apply`
  guarded, decided by `isEvaluatable()` at compile time — is right everywhere
  is not checked by anything.
- A residual inside a **non-ground** type is how computational type rules work
  at all, and the compiled Lean has no representation for either. That is
  [EL-06](#el-06)'s territory rather than this row's.

**Kept in the ledger anyway**, because the mechanisms genuinely differ and the
reason they agree is a third rule that could be relaxed. If ethos ever invoked
a program on a residual, this row would acquire its witness immediately.

### EL-03

**`eo::extract` clamps to the operand's width in ethos, and does not in the
embedding.**

ethos guards on the operand: an index below zero, or a low index past the
operand's width, gives the empty bit-vector, and a high index past the width is
clamped to the last bit (`Literal::evaluate`, `EVAL_EXTRACT`,
`src/literal.cpp`). The result is therefore never wider than the operand.

The embedding guards only on the *indices*: the result width is `n3 - n2 + 1`
whatever the operand was, and the value is masked to that width by
`$eo_mk_binary`.

```lean
-- Cpc/Logos.lean
def __eo_extract : Term -> Term -> Term -> Term
  | (Term.Binary w n1), (Term.Numeral n2), (Term.Numeral n3) =>
    let _v0 := (native_zplus n3 (native_zneg n2))
    (native_ite (native_or (native_zlt n2 0) (native_zlt _v0 0)) (Term.Binary 0 0)
      (__eo_mk_binary (native_zplus _v0 1) (native_binary_extract w n1 n3 n2)))
```

| term | ethos | logos |
| --- | --- | --- |
| `(eo::extract #b111000 1 10)` | `#b11100`, width 5 | `Term.Binary 10 28`, width 10 |
| `(eo::extract #b111 5 6)` | `#b`, width 0 | `Term.Binary 2 0`, width 2 |

The manual's own example table gives `(eo::extract #b111000 1 10) == #b11100`,
so ethos is the reading the document states and the embedding is the one that
departs from it.

**Evidence.** ethos: run (the width is read off the type, via
`(declare-consts <binary> (BitVec (eo::len eo::self)))`). logos: read.

**Whether it bites.** Latent for CPC as compiled: the only reach of
`__eo_extract` is `__bv_const_to_bitlist_rec`, whose indices come from a list of
positions inside the operand. It is a divergence in the language's evaluator,
not currently in a proof.

The string case of the same operator was checked against ethos's and **agrees**
on every boundary tried (negative low index, high index past the end, crossed
indices, empty operand) — the two are written differently and compute the same
function. That is worth recording precisely because it is the case where a
reader would expect the same defect and there is none.

### EL-04

**`eo::cmp` orders terms by two unrelated orders, and `eo::hash` has no Lean at
all.**

ethos's `eo::hash` is a counter: the first term whose hash is requested gets 1,
the second 2, and so on (`State::getHash`, `src/state.cpp`). `eo::cmp` is
`h1 > h2` over that. The resulting order is total and deterministic within a
run, and it is a function of *the order in which the checker asked*, not of the
terms.

logos's `eo::cmp` is `native_tcmp`, which is `compare` on the derived `Ord` of
the generated `Term` inductive — a structural order, fixed by the order the
constructors were emitted in.

`eo::hash` itself is refused outright by the `lean-meta` stage
(`LeanMetaReduce::finalizeProgram`), on the stated ground that EO leaves what it
returns underconstrained, so a stub would be a claim the signature never made. A
signature that uses it gets Lean naming a definition that was never written, and
Lean is what reports that.

**Settled?** No, and this is the row that most clearly belongs to the language
rather than to either tool. The manual says `eo::cmp` "corresponds to an
arbitrary total order on terms" and says nothing about stability or about
agreement between checkers — which is exactly the open question
[`manual.md` §11](manual.md) already records under *What is `eo::hash`
allowed to be?*. **This row is that question's first concrete instance.**

**Whether it bites.** `$compare_var` is CPC's one use of `eo::cmp`, and it is
live: `$poly_add` and `$mvar_mul_mvar` call it to order monomials. The two
tools therefore build *different normal forms* for the same polynomial. That
does not by itself change a verdict — each side is internally consistent, and a
rule that normalises both of its arguments compares like with like — but it is
the reason a normal form printed by one tool cannot be compared with one printed
by the other, and it is the thing that would break first if a rule ever
published a normal form rather than consuming it.

### EL-05

**Lean demands a termination argument Eunoia never asks for.**

Eunoia places no termination requirement on a program, and ethos does not try
to establish one. The Lean backend compiles every program as a total
definition, so Lean must be told why each recursion terminates whenever it
cannot see it. No measure is derived: the clause is written by hand as Lean
text, in the `:lean` attribute of the semantics set, and appended by the stage
to the program it names.

`install/defs/Cpc.eos` carries **ten** such clauses today, for example:

```lisp
  :lean "termination_by a b => 4 * (sizeOf a + sizeOf b)"
```

This is a hole rather than a divergence: Lean *checks* the measure, so a wrong
one is caught — one full regeneration later, in a language the person editing
the calculus was not writing in. What it bounds is which Eunoia programs can be
compiled at all. A program whose termination no measure expresses has no Lean,
and a Eunoia program that genuinely does not terminate on some input has no
counterpart in a total language.

**Settled?** No. Whether a conforming Eunoia program must terminate is not a
question the manual asks; ethos answers "whatever happens, happens", and the
Lean backend answers "there must be an argument", and the language stands
between them saying nothing.

---

## The type system

### EL-06

**`eo::typeof` is monomorphised per partial application, with no marker.**

The desugar stage builds `$eo_typeof` case by case from the declarations: where
a symbol's type is ground it prints the type, and where it is not it emits a
program per partial application — `(= x)` acquires a type rule, `=` does not.
The generated type system therefore agrees with Eunoia's on the cases the stage
generated and is silent elsewhere, and **nothing in the output distinguishes the
two**: a `Term.Stuck` from `__eo_typeof` may mean *this term has no type* or
*this shape was never generated*.

The stage also may not call `eo::typeof` itself, which is the root cause behind
[EL-08](#el-08).

**Settled?** No. The manual describes `eo::typeof` on values; what the type of a
partial application is, and whether a checker owes an answer, is not written
down. `docs/README.md` §11 in the ethos tree states the approximation in the
compiler's own words.

### EL-07

**An ill-typed but unambiguous term is rejected by ethos and accepted by
logos.**

ethos type checks every application as it parses it. logos's parser uses typing
for one purpose only — choosing between the several things an overloaded name
may denote — and `docs/parser.md` says so outright: *"A name with only one
reading is never rejected this way, so a partially applied operator, which has
no type, still parses."*

So a proof file containing a single ill-typed application is a parse error to
ethos and an ordinary term to logos, which then fails (or does not) on whatever
the rules make of it. This is deliberate on logos's side — the checker's rules
are syntactic manipulations and the soundness theorem is stated about the
assumptions the parser reports, not about their well-typedness — but it means
the two tools do not accept the same set of *files*, quite apart from not
accepting the same set of proofs.

---

## Signature features and their desugaring

### EL-08

**The nil predicate of a polymorphic n-ary operator is hand-written and
unchecked.**

`$eo_is_list_nil f x` answers "is `x` the nil of `f`?", and it is load-bearing
for every list operator in every n-ary calculus. Where the nil is ground the
desugar stage prints it. Where the nil depends on the type — `str.++`, `bvadd`,
`+` — the correct definition needs `eo::typeof`, which the stage declines to
call, so the stage emits a forward declaration and **a human writes the body**,
as an `:is-list-nil` attribute in the semantics set:

```lisp
(define-symbol str.++ (s t)
  :is-list-nil (seq.empty T) true
  :is-list-nil             (eo::eq s ""))
```

Nothing compares the stage's decision to forward-declare with the human's
decision to define. Forget the attribute and an undefined program reaches the
backend; write it wrong and the compiled artifact's list semantics silently
disagree with what ethos does when checking a proof. The ethos tree's own
`docs/README.md` §10 works this through in full and calls it the worst thing in
the compiler; three of its five symptoms have since been fixed and **this one
has not**.

Ten attributes across nine symbols in the development set today, and one more
for every n-ary operator with a polymorphic unit anybody adds.

### EL-09

**The Lean term language is closed over one signature.**

Eunoia's term language is open: a signature declares what it likes, and ethos's
`Expr` accommodates it. The generated Lean's `Term` is an inductive built from
one signature — one `UserOp` constructor per operator, and one `UserOp<n>`
inductive per *index arity the signature actually uses*. An arity no
declaration uses gets no inductive, because `Term` has no constructor that would
name one (`Desugar::printIsClosedUopCases`).

This is not a defect; it is what makes the Lean development possible. It is
recorded because it is the structural reason logos "does not support arbitrary
Eunoia signatures", and because it puts a floor under every other row: a
question about a construct CPC does not use has no logos side to compare.

**Settled?** No — the language has no notion of a well-formed signature at all
(the first entry of [`manual.md` §11](manual.md)), so it has nothing to say
about a reading that fixes one.

### EL-10

**Overload resolution runs in opposite directions.**

ethos, per the manual: *"if a symbol is overloaded, Ethos will use the most
recently declared symbol that results in a well-typed term if applied"*, and an
unapplied symbol is the most recently declared one. The manual builds advice on
this — declare subtraction *before* unary negation, or `(- t)` reads as a
partial application.

logos's parser holds a name's signature declarations in **declaration order**
(`State.ofOps`, `m.getD d.name [] ++ [d]`) and resolves by preferring an
exactly-saturated arity, then the first declaration that admits the argument
count (`resolveOp`); among the several *terms* a name may denote it takes the
first that is well typed and otherwise the first outright (`resolve`). Symbols
the proof file itself declares are prepended, so those are most-recent-first and
match ethos; the signature's own operators are not.

The two rules agree on the manual's example for a reason that is not the
manual's reason (logos gets there by exact arity, not by recency), and they are
constructibly different in general.

### EL-11

**`lambda` and `beta-reduce` are compiled out.**

The semantics set excludes the proof-level binder of CPC and everything that
reduces an application of one — `lambda`, `$get_lambda_type`,
`$beta_reduce_type`, `$beta_reduce`, and the rule `beta-reduce` — on the ground
that SMT-LIB gives them no meaning, so a model would have to invent one.

The consequence is stated plainly: **the calculus logos checks is a proper
subset of the calculus ethos checks**. A proof using `beta-reduce` is a proof
ethos accepts and logos cannot read.

The mechanism carries its own hazard, which the set documents: exclusions are
matched by string, with no existence check and no dependency closure. A typo
excludes nothing, silently, and dropping a symbol means finding its rule and its
helpers by hand — which is why the four companions are listed one by one above.

---

## Commands and the proof file

These are the rows where logos's own front end re-decides something ethos's
parser had already decided. All of them are stated in
[`logos/docs/parser.md`](https://github.com/cvc5/logos/blob/main/docs/parser.md),
which is the source for this section; none of them is inferred here.

### EL-12

**An `assume` after the first step.** logos reads a proof as an assumption set
together with the steps that refute it, so every `assume` must stand before the
first `step`, `assume-push` or `step-pop`. One after is refused. Ethos accepts
one anywhere.

### EL-13

**`include` and `reference`.** Ignored. logos has the signature built in and
does not check the proof against the original input problem, so the
correspondence `reference` asserts is not checked by anything — which the
correctness statement already says: the theorem speaks about the assumptions the
parser reports, not about the file they came from.

### EL-14

**`declare-datatypes`.** Parametric datatypes — a non-zero arity, or a `par`
body — are refused outright, since logos has no representation for them; ethos
has them, and `eo::dt_constructors` is specified over them. And the *order* of a
block matters to logos, because its specification witnesses a datatype only
through entries declared later in the block; the parser reorders a block that
was not written productively, by decreasing rank. A block denotes the same
datatypes however it is sorted — but it is the parser that says so, and the
parser is not verified. The native front end does not go through the parser and
is not normalised: an unproductive block there is reported `incomplete`.

### EL-15

**`define` with parameters.** In logos it is a macro: the body is kept as an
s-expression and re-read wherever the symbol is applied, with the parameters
bound at that site. Three consequences the doc names — a parameter's declared
type is not used, an error in the body is reported at the use site, and a
recursive `define` is rejected.

**Settled?** No, and this one connects to a question sapheneia already has open.
[`manual.md` §11](manual.md) asks whether a `define` body is part of the
language's type discipline, having verified that ethos does not check one. logos
does not check one either, by a different route — it never has a body and a
type in hand at the same time. **Two implementations reaching the same silence
by different mechanisms is evidence about the language, not about either
tool.**

### EL-16

**The conclusion on a `step`.** Ignored — logos recomputes it from the rule and
does not compare. Ethos matches the written conclusion against the rule's
pattern, and a step that provides none fails outright (manual, *Proof rules*).

### EL-17

**A `\u` escape naming a surrogate.** ethos accepts `"\ud800"` and treats it as
a string of one character. logos rejects it, because Lean has no `Char` for a
surrogate code point. A *malformed* escape stands for its own characters in
both.

**Settled?** No. The manual defines the string literal category and the escape
syntax; which code points a character may be is not stated, and the two tools
are answering a question nobody asked them.

---

## The seam itself

### EL-18

**logos's package is compiled by an ethos the ethos tree has moved past.**

logos pins the compiler by commit — `ETHOS_VERSION="406b5499…"`, the head of
`ethosEoc3` when the pin was last advanced — so what the compiler emits changes
only on purpose. The pin is 11 commits behind the local `ethosEoc3` checkout as
this was written.

That is the right design and it has a consequence worth stating: **a divergence
read off the current ethos tree is not necessarily a divergence in the Lean
logos ships**, and a fix to the desugar stage does not reach logos until
somebody runs `scripts/bump-eoc-version.py`. Every row above that cites
`plugins/` is a claim about the compiler; every row that cites `Cpc/Logos.lean`
is a claim about the artifact. Where they could differ the row says which it
read.

Separately: the ethos a *user* runs is a release, and the ethos the compiler is
built from is a development branch. Nothing here has compared the two.

### EL-19

**Nobody checks that the natives a run reaches are the natives a layer
implements.**

The embedding declares 66 natives. A backend's layer implements some of them,
and which it *must* implement depends on what the target language already brings
for free — a fact nothing anywhere writes down. So the coherence of a layer is
unchecked in both directions: a native no layer implements and no language has
surfaces as a Lean or cvc5 error two tools downstream, and a layer entry for a
native the embedding no longer declares is dead text nothing reports.

The Lean layer implements 47 of 47 today, so this is not currently a hole for
logos. It is in the ledger because it is the mechanism by which one would open
without warning.

### EL-20

**logos has a third verdict.**

ethos answers *correct* or it does not. logos answers `correct`, `incorrect`, or
**`incomplete`** — the proof was accepted, but it mentions something the
specification of SMT-LIB semantics does not model, so the correctness theorem
does not apply to it. A sort constructor of non-zero arity is one such thing.

This is not a disagreement about Eunoia. It is recorded because it is the
easiest row to misread as one: a proof that ethos calls correct and logos calls
`incomplete` is not a proof the two tools disagree about, and counting it as a
divergence would overstate the ledger.

---

## What this page does not do

- **It does not say which side is right**, even where the manual does. Where the
  manual settles a row, the row says which reading the manual states; carrying
  that anywhere is a person's job under the host repository's reporting
  discipline, and nothing here has been carried anywhere.
- **It does not describe `.eos`.** The semantics-set language has its own
  reference (`tools/eoc/semantics/README.md` in the ethos tree). Rows cite a set
  where the set is the evidence; the language is out of scope, as it is for
  [`manual.md`](manual.md).
- **It does not compare soundness.** logos proves things about its own checker
  against its own SMT-LIB semantics. Whether that semantics conforms to SMT-LIB
  is [`logos/docs/smt-lib-conformance.md`](https://github.com/cvc5/logos/blob/main/docs/smt-lib-conformance.md),
  and it is a question about SMT-LIB rather than about Eunoia.
- **It does not claim to be complete.** Twenty rows is what one reading found.
  The construct-by-construct sweep that would justify a count has not been done
  — see [Status](#status).

## How to re-check

**This is the part that makes the page living.** Everything above is either
*read* off a tree or *run* against a build, and the two are labelled per row so
that a refresh can redo the right one.

**The trees, and what to read in each:**

| read | for |
| --- | --- |
| `ethos/plugins/desugar/eo_desugar_native.eo` | what an `eo::` operator means to the embedding |
| `ethos/plugins/desugar/natives.eos`, `ethos/plugins/lean_meta/lean.eos` | the primitives and their Lean |
| `ethos/plugins/lean_meta/lean_meta_reduce.cpp` | what the Lean stage refuses, and where stuck cases come from |
| `ethos/src/literal.cpp`, `ethos/src/type_checker.cpp` | what ethos's evaluator does |
| `logos/Cpc/Logos.lean`, `logos/Cpc/LogosTerm.lean` | the artifact — what logos actually runs |
| `logos/install/defs/Cpc.eos` | the hand-written half: nil predicates, termination clauses, exclusions |
| `logos/Logos/Parser.lean`, `logos/docs/parser.md` | the front end |

**The probe.** ethos has no command that prints an evaluated term, and a
`define` body is not type checked, so neither is a way to observe evaluation.
What works is to make the answer decide a *type*, which is checked. The
shortest form is the one the ethos tree uses for its own regressions
(`tests/eo-definitions-test.eo`) — a declaration whose type is an
`eo::requires` that only reduces when the question comes out the way it says:

```lisp
(declare-const probe (eo::requires <THE-QUESTION> true Bool))
```

This checks iff the question evaluates to `true`. Run it again with `false` in
place of `true`, and the three outcomes are distinguished: first file checks =
`true`, second checks = `false`, neither checks = did not evaluate. A failed
`eo::requires` leaves a ground unreduced type, which is what the declaration
rejects.

Where a *width* rather than a truth value is wanted, `(eo::len t)` reads one, so
`(eo::is_eq (eo::len <term>) 5)` asks how wide a bit-vector came out. An earlier
form of the same probe put the answer in a bit-vector width directly —
`(declare-const c (BitVec (eo::ite <Q> 1 2)))` applied to `(-> (BitVec 1) Bool)`
— which works and is longer.

**The builds used.** `eo/ethos/build-eoc/ethos-eoc` is an ethos binary with the
compiler plugins and behaves as the ordinary checker when no `--plugin` is
passed; it was used for every *run* row above. Every such row was also
reproduced against an independent build of a different commit
(`ethos-ai/build/src/ethos` at `292201c2`, branch `anoieu-findings`) and agreed.

**What has not been run at all: logos.** Every logos-side claim here is read off
generated Lean, which is the text Lean compiles, so it is strong evidence — but
it is not execution, and no row above should be quoted as "logos was observed
to". Executing them means building the `Cpc` package and is the obvious next
increment.

## Status

**First cut, 2026-09-17.** Read against:

| tree | at |
| --- | --- |
| kanon (this repository) | `dd4780a` |
| ethos | `ethosEoc3`, `4d1ba77c` |
| logos | `main`, `be479120` |
| the compiler logos pins | ethos `406b5499` — 11 commits behind the above |
| the signature | `logos/install/defs/Cpc.cached.eo`, 6637 lines |

**Nothing here has been checked by anybody who knows Eunoia**, and nothing has
been carried to either repository.

**What would make this a result rather than a list.** The same thing
[`../README.md`](../README.md) says of the feedback ledger: rows that have been
put to the people who own the two readings, and answered. Four of these rows
([EL-04](#el-04), [EL-05](#el-05), [EL-06](#el-06), [EL-15](#el-15)) are
instances of questions [`manual.md` §11](manual.md) already lists as
unsettled, which is the more interesting half — **a second implementation
disagreeing in exactly the places a second *account* found underspecified is
evidence the account found the right places.** That correspondence, counted and
checked, is the paper-shaped thing here; it is not evidence yet.

**Next increments, in order of value:**

1. Build the `Cpc` package and turn the read rows into run rows.
2. Sweep the `eo::` operators construct by construct against the embedding, so
   that a count means something. Rows [EL-01](#el-01) to [EL-04](#el-04) came
   from four operators looked at closely; there are around sixty.
3. Re-read after the next `bump-eoc-version.py`, and record what moved.
