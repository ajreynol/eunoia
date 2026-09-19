# Where our account disagrees with the ethos manual

**A living register of what we think the manual gets wrong.** Not what it leaves
out, and not how it words things — those are [`feedback.md`](feedback.md).
This page is the shorter and heavier list: sentences that appear to say
something that is not so.

The ethos manual is the authority, in the sense that it governs and this does
not — which is not the same as being presumed correct. **Every row is a
candidate and none is judged.** Where our reading and the manual's disagree,
either may be at fault, and nothing here is settled until somebody who knows
Eunoia rules on it. Nothing here has been carried anywhere, and nothing leaves
this directory by machine.

| this page | [`feedback.md`](feedback.md) |
| --- | --- |
| the manual **asserts** something we believe is not the case | the manual is **silent**, ambiguous, or inconsistent in its wording |
| fixed by changing what it says | fixed by adding a sentence |
| the first row is fixed by changing **how the language is explained** | no row is that large |

**The first row is also a correction to us.** [`manual.md`](manual.md) §8
opens *"a proof is a term and proof checking is type checking"*, which we took
from the manual rather than derived. We now think that account is the wrong way
round, and [MD-01](#md-01) is the argument. A second account that repeats the
first one's framing has not checked it, which is the characteristic failure of
this whole project and is worth saying out loud.

---

## The ledger

| id | where | in one line | kind |
| --- | --- | --- | --- |
| [MD-01](#md-01) | *Proofs as terms*, *Declaring Proof Rules* | **proof checking is presented as type checking; it is evaluation** | framing |
| [MD-02](#md-02) | *Declaring Proof Rules* vs *Explicit Conclusions* | the well-definedness condition is stated without the exception the manual itself then introduces | contradicted |
| [MD-03](#md-03) | *Proofs as terms* | the correspondence's caveat names two fields that break it; a third does | incomplete |
| [MD-04](#md-04) | *Proofs as terms* | `Proof` and `Quote` are not symbols the language has, so the equivalences are not writable | not expressible |
| [MD-05](#md-05) | *Declaring Proof Rules* | `Proof`'s stated kind is not enforced where a typed reading says it must be | contradicted |
| [MD-06](#md-06) | *String operators* | `eo::extract` states one guard, four are in force, and the manual's own examples need the missing ones | wrong spec |
| [MD-07](#md-07) | *Derived Definitions of Evaluation Operators* | "all list operators with the exception of `eo::nil`" — `eo::list_repeat` has no definition | wrong claim |
| [MD-08](#md-08) | *Ambiguous Functions* | "all uses must use `as`" — a bare use is accepted, and is a different term | wrong claim |
| [MD-09](#md-09) | *Core operators* | the two meanings of *value* make two operator specifications wrong, not merely ambiguous | wrong spec |
| [MD-10](#md-10) | *The :type attribute for definitions* | types are compared "identical" after an evaluation the sentence does not mention | incomplete |

**Read against** `user_manual.md` on `ethosEoc3` at `4d1ba77c`. Every *run* claim
was checked against `eo/ethos/build-eoc/ethos-eoc`, built from that commit; the
probe is at the [end](#how-to-re-check).

---

## MD-01

**Proof checking is presented as type checking. It is evaluation.**

**Where.** *Proofs as terms* (appendix), and the closing note of *Declaring
Proof Rules*.

**What the manual says.** The appendix opens:

> This section overviews the semantics of proofs in the Eunoia language. Proof
> checking can be seen as a special instance of type checking terms involving
> the `Proof` and `Quote` types.

and gives two application rules, a side condition on each, a note that a
well-typed term's type must be "either non-ground, or fully reduced", and three
equivalences: a rule is a parameterized constant, an `assume` is a
`declare-const`, a `step` is a `define` with `:type`.

**This is the only place the manual explains what checking a proof *is*.** There
is no other section that says, step by step, what happens when a checker reads a
proof. So this is not a remark in an appendix; it is the semantics, and the
manual says so in its first sentence.

**What we think is wrong.** Not that the correspondence is false — it is a real
and useful analogy, and [what it gets right](#what-the-typed-reading-gets-right)
is below. What is wrong is that it is offered *as the account*, and it is the
wrong shape for the thing: **checking a Eunoia proof is running a program, and
the typed presentation hides every part of that.** Six specifics, each checked.

### 1. The account is written in a vocabulary the language does not have

`Proof` and `Quote` are not symbols a signature can name. Run:

```lisp
(declare-const p (Proof (= a a)))   ; Error: Could not find symbol Proof
(declare-const f (-> (Quote 1) Int)) ; Error: Could not find symbol Quote
```

So `(assume s f)` ≡ `(declare-const s (Proof f))` is not a rewriting anybody
could perform, check, or test; the right-hand side is not a command in the
language the left-hand side belongs to. That is fine for an analogy and fatal
for a semantics: there is nothing to be right or wrong *about*. See
[MD-04](#md-04).

### 2. It covers four of the seven things a rule can say

`declare-rule` has `:assumption`, `:premises`, `:premise-list`, `:args`,
`:requires`, `:conclusion` and `:conclusion-explicit`. The correspondence covers
`:premises`, `:args`, `:requires` and `:conclusion`. The manual's own caveat
names two of the three it does not:

> Notice the correspondence above assumes the declaration of `r` does not
> involve `:assumption` or `:premise-list`.

`:conclusion-explicit` also breaks it and is not named — [MD-03](#md-03).

**The three it cannot express are exactly the operational ones.**
`:assumption`/`step-pop` is a *stack discipline* over the sequence of commands;
`:premise-list` is a *fold over however many premises were actually supplied*;
`:conclusion-explicit` *matches against an input the checker was handed* and
binds parameters from it. None of the three is a property of a term. All three
are properties of a run.

### 3. All the computation is inside the `=`

The two rules are

```
f : (-> U S)   t : T                f : (-> (Quote u) S)   t : T
────────────────────── if U·σ = T   ────────────────────────────── if u·σ = t
   (f t) : S·σ                             (f t) : S·σ
```

and `=` here is not syntactic equality. It is equality *after evaluation* — and
the manual says as much a paragraph later, by requiring that a well-typed term's
type be "fully reduced, i.e. contains no irreducible applications of programs or
evaluation operators".

So computing a type means **running the signature's programs to a fixpoint**,
and `program` is defined by the manual itself as "an ordered list of rewrite
rules" evaluated by first-match-wins. The dependency runs

```text
typing  ──needs──▶  evaluation  ──is──▶  ordered rewriting
```

and the appendix presents the top of that stack as the meaning of the bottom of
it. Everything a reader wants to know — when a side condition runs, what happens
when it gets stuck, why a step fails — lives in the `=` and is not discussed.

### 4. `Quote` is pattern matching, not typing

In the quoted rule the argument's type `T` is written down and then never used.
What the rule actually does is *match the term `t` against the pattern `u` and
bind*. That is a `program` case. Calling the thing that performs it a type
system means the type system contains a term matcher, which is the part of the
machinery that does the work.

### 5. `Proof`'s kind is not enforced where the typed reading says it must be

The manual states:

> `Proof` is a type whose kind is `(-> Bool Type)`

Under the typed reading a rule concluding an `Int` builds `(Proof a)` with
`a : Int`, which is ill-kinded, and `declare-rule` should refuse it. It does not:

```lisp
(declare-const Int Type) (declare-const a Int)
(declare-rule silly () :conclusion a)   ; ACCEPTED
(step @p0 a :rule silly)                ; Error: Expected: Bool
```

The declaration goes through, and the failure arrives later, at the *step*, and
as a check on the term the step produced. This is what an evaluator does and not
what a kind system does. (It is also
[`manual.md` §11](manual.md)'s *rule that could conclude a non-`Bool` term*,
reached here from a different direction.)

### 6. Typing is demand-driven and order-dependent

A type system assigns a type to a term. Ethos assigns one *when something asks*,
and whether anything asks is a fact about the file, not about the term:

```lisp
(declare-const or (-> Bool Bool Bool) :right-assoc-nil 0)   ; Int nil, Bool operator
(define P () (or a b))            ; ACCEPTED
(define P () (or a b) :type Bool) ; the same body: Type checking failed
```

A program case with the wrong return type is accepted and lies dormant until a
proof reaches it. And overload resolution takes "the most recently declared
symbol that results in a well-typed term", so what a name denotes depends on
declaration order. The host repository reached the same place from the analyzer
side and put it in one sentence — `docs/notes.md` §1, *"Ethos is demand-driven:
it types a term only when something asks"*, and *"a signature is not a thing it
validates; it is the vocabulary a proof is checked against"*.

A property of a run is not a type discipline. It is an evaluation order.

### What we think the account should be

**A signature is a rewrite system, and a proof is a program run against it.**

- The *state* is a stack of what has been assumed and what has been proven.
- A *command* transforms the state: `assume` and `assume-push` push, `step`
  applies a rule and pushes what came out, `step-pop` discharges back to the
  nearest pushed assumption.
- A *step* is three operations in order: **match** the premise, argument and
  (for `:conclusion-explicit`) conclusion patterns, binding a substitution;
  **evaluate** the requirements and any programs the conclusion names; **produce**
  a term.
- *Failure* is a computation that got stuck, not a judgement that did not hold.
  A failed `:requires` leaves a residual term, and the step then fails because
  what it computed is not what was written.
- Checking a proof is folding the command list over the state and asking what
  the final state holds.

**The strongest evidence that this is the account an implementer needs is that
the ethos project wrote it.** `plugins/desugar/eo_desugar_checker.eo` is Eunoia's
proof layer re-expressed in Eunoia, for the compiler to compile, and it is an
abstract machine:

```lisp
(declare-const $emb_s.nil  $eo_State)          ; the state is a stack
(declare-const $emb_s.Stuck $eo_State)         ; ... with a failure state
(declare-parameterized-const $emb_so.assume      ((F Bool :opaque)) $eo_StateObj)
(declare-parameterized-const $emb_so.assume_push ((F Bool :opaque)) $eo_StateObj)
(declare-parameterized-const $emb_so.proven      ((F Bool :opaque)) $eo_StateObj)

(program $eo_invoke_cmd ...                    ; one command, one state transition
  (
  (($eo_invoke_cmd $s_stuck c) $s_stuck)
  (($eo_invoke_cmd S ($cmd_assume_push proven)) ($eo_push_assume_check ... proven S))
  (($eo_invoke_cmd S ($cmd_step r args premises))
    ($eo_push_proven ($eo_cmd_step_proven S r args premises) S))
  (($eo_invoke_cmd S ($cmd_step_pop r args premises))
    ($eo_invoke_cmd_step_pop S S r args premises))
  )
)
```

`$eo_invoke_cmd_list` folds that over a command list. There is no `Proof` type
in it and no `Quote`. When the same project had to write this language down a
second time, in a form something else would execute, what it wrote was a machine
— and the Lean that `ethos-eoc` generates from it is the same machine again.

### What the typed reading gets right

Stated because a row that only attacks is not a reading.

- **Dependency.** It is the clearest explanation of why a rule's `:args` may
  appear in its conclusion: the argument's *term* is bound, so the result can
  mention it. Nothing in an operational account says that as economically.
- **Premise matching is not a separate mechanism.** Seeing a premise as an
  argument whose type is a `Proof` correctly predicts that premise matching and
  argument matching are one operation.
- **`:requires` as part of the return type** is exactly right, and it is why a
  failed requirement is a stuck term rather than an error.

Our position is that these belong in the manual as *an analogy that explains the
dependency*, kept, and that they cannot carry the sentence "this section
overviews the semantics of proofs" — which needs the machine.

### What it costs a reader

A second implementer reads *Proofs as terms* looking for the semantics, and
finds a type system whose vocabulary the language lacks, whose side conditions
are an unexplained `=`, and which does not reach three of the seven things a
rule can say. What they need — the state, the command transitions, the order of
match/evaluate/produce, and what failure is — is in no section of the manual and
has to be recovered from `plugins/` or from the implementation.

**We propose nothing.** Whether the manual should carry an operational account,
and what it should look like, is a decision for whoever owns the manual.

---

## MD-02

**The well-definedness condition is stated without the exception the manual
itself then introduces.**

*Declaring Proof Rules* says, without qualification:

> A proof rule is only well defined if the free parameters of the requirements
> and conclusion term are also contained in the arguments and premises.

It is enforced, and the error is specific:

```lisp
(declare-rule bad ((x Int) (y Int)) :premises ((= x x)) :conclusion (= y y))
;; Error: Unexpected free parameter in expression
```

A hundred lines later, *Explicit Conclusions* introduces a feature whose whole
purpose is to violate it — `F` occurs in neither the premises nor the arguments:

```lisp
(declare-rule split ((F Bool)) :conclusion-explicit (or F (not F)))
(step @p0 (or true (not true)) :rule split)     ; ACCEPTED
```

The same rule written with a plain `:conclusion` is refused, with a *third*
condition that appears nowhere in the manual:

```lisp
(declare-rule split ((F Bool)) :conclusion (or F (not F)))
;; Error: Nullary proof rule must have ground reduced conclusion
```

So there are two well-definedness rules, one per conclusion form, and the manual
states one of them as though it were unconditional. **Run.**

## MD-03

**The correspondence's caveat names two fields that break it; a third does.**

> Notice the correspondence above assumes the declaration of `r` does not
> involve `:assumption` or `:premise-list`.

`:conclusion-explicit` breaks it too, and for a reason worth naming: under the
correspondence a step is `(define s () (r …) :type (Proof f))`, in which the
conclusion `f` is *checked against* the computed type. With
`:conclusion-explicit` the conclusion is *matched to bind* a parameter, which a
`:type` annotation cannot do — the binding has to happen before the rule can be
applied at all. See [MD-01 §2](#md-01).

## MD-04

**`Proof` and `Quote` are not symbols the language has, so the equivalences are
not writable.**

```lisp
(declare-const p (Proof (= a a)))     ; Error: Could not find symbol Proof
(declare-const f (-> (Quote 1) Int))  ; Error: Could not find symbol Quote
```

The manual presents three equivalences (`declare-rule`, `assume`, `step`) whose
right-hand sides are not commands anybody can write, and does not say so.
*Declaring Proof Rules* does say "By design, the user cannot declare terms
involving type `Proof`" — which is the same fact, stated two thousand lines
earlier, and is not connected to the appendix that goes on to use it. A reader
who tries the appendix's translation gets an unknown-symbol error with no
indication that the manual already knew. **Run.**

## MD-05

**`Proof`'s stated kind is not enforced where a typed reading says it must be.**

Covered in [MD-01 §5](#md-01) and kept as its own row because it is checkable on
its own terms: `Proof : (-> Bool Type)` predicts that `declare-rule` refuses a
non-`Bool` conclusion, and it does not. **Run.**

## MD-06

**`eo::extract` states one guard; four are in force; and the manual's own
examples need the missing ones.**

*String operators* says, for the binary case:

> this returns the binary value corresponding to the bits in `t1` from position
> `t2` through `t3` if `0<=t2`, or the empty binary value otherwise

The implementation (`Literal::evaluate`, `src/literal.cpp`) returns the empty
value when **any** of four things holds — `t2 < 0`, `t3 < 0`, `t2 >` the
operand's width, or the operand is empty — and then **clamps `t3` down to the
last bit** before extracting, and returns empty again if the low index now
exceeds the high one.

The stated rule accounts for one of the manual's four binary examples. The other
three need parts that are not stated:

| the manual's example | needs |
| --- | --- |
| `(eo::extract #b10 -1 2) == #b` | the stated guard `0<=t2` |
| `(eo::extract #b111000 1 10) == #b11100` | the clamp of `t3` to the width |
| `(eo::extract #b11100 2 1) == #b` | the low-above-high guard |
| `(eo::extract #b11100 2 4) == #b111` | — |

and behaviour that is in neither the prose nor the examples:

| term | ethos |
| --- | --- |
| `(eo::extract #b111 5 6)` | `#b`, width 0 — `t2` past the width |
| `(eo::extract #b111 3 4)` | `#b`, width 0 — `t2` equals the width |

The string case is specified in the same shape and has the same gaps. **Run** —
widths read with `eo::len`.

This is the row most likely to be a defect in *our* reading, in this sense: the
prose may be intended as a sketch with the examples as the specification. If so
the two are the wrong way round, since a second implementation has to write the
guards and cannot read four of them off four examples.

## MD-07

**"All list operators with the exception of `eo::nil`" — `eo::list_repeat` has
no definition either.**

*Derived Definitions of Evaluation Operators* says:

> It is possible to define programs for *all* list operators with the exception
> of `eo::nil`.

The manual's own *List operators* section lists seventeen, `eo::list_repeat`
among them. `tests/eo-definitions.eo`, the file this paragraph points at,
defines sixteen: there is no `$eo_list_repeat` and no note saying why.

Whether `eo::list_repeat` *can* be defined as an ordinary program is a separate
question this page does not answer — it may simply be an omission from the file.
Either way the sentence and the artifact do not agree. **Read.**

## MD-08

**"All uses of ambiguous functions must use `as`" — a bare use is accepted, and
means something else.**

*Ambiguous Functions* says:

> All uses of ambiguous functions must use the SMT-LIB syntax `as`, which
> expects the symbol to annotate and the return type of that instance.

A bare use is not refused. It is accepted in a checked position, inside a proof:

```lisp
(declare-const Set (-> Type Type))
(declare-parameterized-const set.empty ((T Type :implicit)) (Set T))
(declare-parameterized-const = ((T Type :implicit)) (-> T T Bool))
(assume a (= set.empty set.empty))                 ; ACCEPTED
```

and it denotes a *different term* from the ascribed one:

| term | result |
| --- | --- |
| `(eo::is_eq set.empty (as set.empty (Set Int)))` | `false` |
| `(eo::is_eq set.empty set.empty)` | `true` |
| `(eo::is_eq (as set.empty (Set Int)) (as set.empty (Set Real)))` | `false` |

which follows from the manual's own note — the symbol is internally extended
with an opaque type argument, so the bare name is the uninstantiated constant
and the `as` form is an opaque application of it. The "must" therefore describes
neither a check nor a parse rule but a convention, and breaking it produces a
term that silently matches nothing written with `as` rather than an error.
**Run.**

## MD-09

**The two meanings of *value* make two operator specifications wrong, rather
than merely ambiguous.**

[`feedback.md` EOM-09](feedback.md) records that the manual uses *value* for
both *literal* and *fully reduced ground term*. Two specifications are not just
unclear under that ambiguity — they are false under one reading and silent under
the other.

**`eo::is_ok`.** "If `t` is ground, this returns true if `t` is a value, and
false otherwise." With `+` an ordinary declared constant, `(eo::is_ok (+ 1 2))`
is **`true`**, and `(+ 1 2)` is not a literal. The implementation is
`!isEvaluatable(t)` — *is this term fully reduced* — which is the second reading
and is what the sentence should say.

**`eo::is_eq`.** "If `t1` and `t2` are ground values, this returns `true` if
`t1` is (syntactically) equal to `t2` and `false` otherwise. If either `t1` or
`t2` is non-ground, it does not evaluate." Neither sentence covers a ground
argument that is *not* fully reduced, which is the common case, and there the
operator returns **`false`**: `(eo::is_eq (eo::to_z "451") (eo::to_z "451"))` is
`false`, not stuck and not true. The exact rule is written in the ethos source
beside the code, and is a sentence the manual could have used:

> `(eo::is_eq t s)` is equivalent to
> `(eo::ite (eo::and (eo::is_ok t) (eo::is_ok s)) (eo::eq s t) false)`

Note that this also separates `eo::is_eq` from `eo::eq`, which *does* go
unevaluated on an unreduced argument — a distinction the manual's two entries do
not draw. **Run.**

## MD-10

**Types are compared "identical" after an evaluation the sentence does not
mention.**

*The :type attribute for definitions*: "This instructs the checker to compare
the type it computed for the term with the specified type. An error will be
thrown if the two types are not identical."

The manual's own bit-vector example has a computed type of
`(BitVec (eo::add 2 3))` and a written type of `(BitVec 5)`, which are identical
only after evaluating the first. Small on its own, and in the ledger because it
is the same substitution as [MD-01 §3](#md-01): a word that means *equal* is
carrying a call to the evaluator, and every place the manual does that is a
place a second implementation has to guess.

---

## What this page does not do

- **It does not propose wording.** [`feedback.md`](feedback.md) does, because
  a silence has an obvious repair and a disagreement does not. Here we say what
  we think is not so and stop; [MD-01](#md-01) in particular proposes no
  replacement text, only that a replacement is needed.
- **It does not claim the manual is unreliable.** Ten rows against a
  2362-line document that is the only description of the language, and nine of
  them are local. The one that is not is a framing question on which reasonable
  people differ.
- **It is not a bug report about ethos.** Every row is about the *document*.
  Where the implementation does something the manual does not describe, the row
  says the manual does not describe it — not that the implementation is wrong.

## How to re-check

The probe is the one the ethos tree uses for its own regressions
(`tests/eo-definitions-test.eo`): a declaration whose type only reduces when the
question comes out as stated.

```lisp
(declare-const probe (eo::requires <THE-QUESTION> true Bool))
```

Accepted iff the question evaluates to `true`; run it again with `false` to
distinguish `false` from *did not evaluate*. For the rows about what a command
accepts, the file itself is the probe and the exit status is the answer. Widths
are read with `(eo::len t)`.

Built from `ethosEoc3` at `4d1ba77c`:
`eo/ethos/build-eoc/ethos-eoc` is an ethos binary carrying the compiler plugins
and behaves as the ordinary checker when no `--plugin` is passed.

## Status

**First cut, 2026-09-17.** Ten rows, one of which is most of the page. Nothing
has been checked by anybody who knows Eunoia and nothing has been carried
anywhere.

**What is owed to [`manual.md`](manual.md).** Its §8 asserts the framing
[MD-01](#md-01) rejects, and currently carries a pointer here rather than a
rewrite. Rewriting that chapter around the machine — state, commands,
match/evaluate/produce, stuckness — with the typed reading kept as the
explanation of dependency, is the next substantial piece of work in this
project.

**Where this meets the other register.** Three rows of
[`ethos-logos.md`](ethos-logos.md) are the same facts seen from the compilation
side: EL-02 is what stuckness looks like when a machine has to represent it,
EL-06 is the type system being an approximation because it is really an
evaluator, and EL-05 is what happens when an evaluator with no termination
requirement meets a language that has one. **A framing error in a manual and a
mismatch between two implementations are not separate subjects** — the second is
where the first becomes observable, which is the argument for keeping both
registers in one project.
