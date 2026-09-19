# Defining a calculus: propositional resolution

Part of the [Eunoia tutorials](tutorials.md). This is the route for writing a
signature from scratch. To extend cvc5's existing calculus, start with
[adding a CPC rule](adding-a-cpc-rule.md), including its verification in Logos.

A Eunoia signature for propositional resolution, written one decision at a time,
with every step run. You end with a file of about thirty lines of substance that
checks resolution proofs, accepts the empty clause as a refutation, and rejects
the three things a first draft of it accepts by mistake.

**What you need.** An `ethos` binary. Everything below was run; the files are in
[`../examples/resolution/`](../examples/resolution), and `check.sh` re-runs the
whole suite:

```sh
tools/mimesis/examples/resolution/check.sh path/to/ethos
```

**This does not establish that the calculus is sound.** Proof tests show that a
signature accepts and rejects the proofs you showed it, which is a different
thing — see the [ledger](../README.md#the-ledger), and
[what was checked](#what-was-checked-and-what-was-not) for exactly what was run.

## The calculus

Three lines of prose, which is what an author usually starts with:

> A **clause** is a disjunction of literals; a **literal** is a propositional
> variable or its negation. From two clauses `C₁` and `C₂` and a literal `l`
> with `l ∈ C₁` and `¬l ∈ C₂`, **resolution** derives `(C₁ ∖ l) ∪ (C₂ ∖ ¬l)`.
> The **empty clause** is a contradiction.

Everything below is the work of turning that into something a checker can run.

## 1. Decide how a clause is spelled

This decision comes first and everything else rests on it.

```
(declare-const or (-> Bool Bool Bool) :right-assoc-nil false)
(declare-const not (-> Bool Bool))
```

`:right-assoc-nil false` makes `false` the nil terminator of `or`, and buys
three things at once:

- `(or a b)` desugars to `(or a (or b false))`, so a clause **is a list** and
  the `eo::list_*` operators apply to it;
- the **empty clause is exactly `false`** — which is also the term a generated
  checker tests for when it asks whether a proof is a refutation, so the
  calculus needs no encoding of contradiction and no extra rule to reach one;
- `(or a)` is `(or a false)`, a one-element list, while a bare `a` is not a list
  at all. That last consequence costs one operator in §3 and one rejected proof
  in §4.

## 2. Write the rule

A rule with two premises, the pivot as an argument, and a conclusion the
signature *computes* rather than matches:

```
(program $remove ((l Bool) (x Bool) (xs Bool :list))
  :signature (Bool Bool) Bool
  (
    (($remove l false)     false)
    (($remove l (or l xs)) ($remove l xs))
    (($remove l (or x xs)) (eo::cons or x ($remove l xs)))
  )
)

(declare-rule resolution ((C1 Bool) (C2 Bool) (l Bool))
  :premises (C1 C2)
  :args (l)
  :conclusion (eo::list_concat or ($remove l C1) ($remove (not l) C2))
)
```

Two things in `$remove` are worth reading twice. The second case repeats `l`,
which is how a pattern says *this child is the pivot*; case order decides which
of the last two applies. And it removes **every** occurrence, not the first —
which is why the duplicate literals resolution produces disappear without a
factoring rule (§5).

[`test/resolve.proof`](../examples/resolution/test/resolve.proof) checks:

```
(assume @a0 (or p q))
(assume @a1 (or (not p) r))
(step @c0 (or q r) :rule resolution :premises (@a0 @a1) :args (p))
```

```
$ ethos --include=Resolution.eo test/resolve.proof
correct
```

## 3. The first thing that broke: a unit clause

A refutation ends by resolving two unit clauses, so try it —
[`test/unit-empty.proof`](../examples/resolution/test/unit-empty.proof),
assumptions `p` and `(not p)`, concluding `false`:

```
Error: test/unit-empty.proof:7.62: A step of rule resolution failed to check.
Evaluation failed: (eo::define ((_v0 (not p))) (eo::list_concat or (_ $remove p p) (_ $remove _v0 _v0)))
```

`$remove p p` matches none of the three cases: `p` is a bare literal, and every
case of `$remove` expects `false` or an `or`-application. The error prints the
evaluation that got stuck, which names the culprit exactly.

The fix is one operator, applied where the clause enters the rule:

```
:conclusion (eo::list_concat or
              ($remove l (eo::list_singleton_intro or C1))
              ($remove (not l) (eo::list_singleton_intro or C2)))
```

`eo::list_singleton_intro` leaves an `or`-list alone and wraps anything else, so
`p` becomes `(or p)` and `false` stays `false`. The test now passes, and the
empty clause comes out of `eo::list_concat` for free: concatenating two empty
lists is the nil terminator, which is `false`.

## 4. The same distinction, on the way out

[`test/singleton.proof`](../examples/resolution/test/singleton.proof) resolves
`(or p q)` with `(not p)`. The resolvent has one literal, and it has to be
written `(or q)`. Writing `q` is rejected:

```
Error: test/singleton-bare.proof:7.58: Unexpected conclusion for rule resolution:
    Proves: (_ (_ or q) false)
  Expected: q
```

Read the labels carefully, because they are the opposite way round from what the
words suggest: **`Proves` is what the rule computed**, `(or q false)`, and
**`Expected` is what your step claimed**, `q`. Both are printed desugared, with
`_` for application — which is the form to get used to, since it is how every
mismatch in this language is reported.

Coercing the output too, so that a bare literal is accepted as a conclusion,
would be a different calculus: it would make `(or q)` and `q` the same proof
step, and the checker would stop distinguishing a clause from a formula. This
signature keeps the distinction and pays for it with one rejected spelling.

## 5. Duplicates come free

[`test/refutation.proof`](../examples/resolution/test/refutation.proof) is a
whole refutation of `(p ∨ q), (¬p ∨ q), ¬q`:

```
(step @c0 (or q q) :rule resolution :premises (@a0 @a1) :args (p))
(step @c1 false    :rule resolution :premises (@c0 @a2) :args (q))
```

The first step's resolvent has `q` twice, and nothing anywhere removes it — the
proof simply says `(or q q)`, and the second step removes **both** copies
because `$remove` recurses past the first match. A signature whose `$remove`
stopped at the first occurrence would need a factoring rule, and the author
would discover that here rather than when designing.

## 6. Sound, and too generous

Now resolve two clauses that share no complementary pair —
[`test/missing-pivot.proof`](../examples/resolution/test/missing-pivot.proof),
`(or p q)` and `(or q r)` on pivot `p`. The rule as written accepts it: `p` is
removed from the first clause, nothing is removed from the second, and the
result is `(or q q r)`.

**That step is sound.** Whenever one of the two removals does nothing, the
untouched clause survives whole into the conclusion, which is therefore implied
by that premise alone. The version of the rule without any side condition never
concludes something false from something true.

**It is still wrong**, because it is not resolution. A checker that accepts it
accepts proofs whose steps do not mean what their rule name says, and a
downstream reader — a person, or a proof-carrying tool — is entitled to take the
name seriously. So require the occurrences:

```
(program $contains ((l Bool) (x Bool) (xs Bool :list))
  :signature (Bool Bool) Bool
  (
    (($contains l false)     false)
    (($contains l (or l xs)) true)
    (($contains l (or x xs)) ($contains l xs))
  )
)
```

```
  :requires ((($contains l (eo::list_singleton_intro or C1)) true)
             (($contains (not l) (eo::list_singleton_intro or C2)) true))
```

and the step is rejected, with the failing requirement shown as the `eo::requires`
that did not hold:

```
Error: test/missing-pivot.proof:9.67: A step of rule resolution failed to check.
Evaluation failed: (eo::define ((_v0 (_ or q))) (eo::requires false true (_ _v0 (_ _v0 (_ (_ or r) false)))))
```

## 7. The operator the calculus does not use

One more declaration is needed, and nothing in resolution asks for it:

```
(declare-const and (-> Bool Bool Bool) :right-assoc-nil true)
```

The framework's [signature contract](../../../README.md#the-signature-contract)
requires a binary `and` that the semantics sends to `SmtTerm.and`, because what
a generated checker concludes is that the *conjunction* of a proof's assumptions
is unsatisfiable. Resolution's own rules never mention it. `ethos` does not care
— the proofs above check without it — and `install/install-<calc>.sh` refuses to
install without it, which is where an author who skipped the contract meets this.

## 8. The programs you did not have to write

Both programs already exist as list builtins:

| written here | builtin |
| --- | --- |
| `$remove` | `eo::list_erase_all` |
| `$contains` | `eo::list_find`, against `-1` |

[`Resolution-lists.eo`](../examples/resolution/Resolution-lists.eo) is the same
calculus with the programs deleted and the rule stating both side conditions
through builtins. It passes the identical test suite — `check.sh` runs every
test against both files — and it is 20 lines against 50.

Which to ship is a real choice rather than an obvious one: the builtin version is
shorter and the hand-written one is what you can put a name and a comment on, and
[the case study](case-study.md) is about an episode where that kind of choice set
more than half of a proof's size. Writing the programs first is still the right
way to *learn* the language, which is what this file is for.

## What was checked, and what was not

**Checked.** Seven proof tests against both signatures, with two independently
built `ethos` binaries: 28 runs, all matching their `.expected` file. A rejected
proof exits by abort, so a harness should read the exit status rather than only
the output — `check.sh` does.

**Not checked: the semantics.**
[`Resolution.eos`](../examples/resolution/Resolution.eos) is written and is not
compiled here. `ethos` reads the signature and never the semantics; compiling it
needs `ethos-eoc`, and the build available in this environment is newer than the
parent's pinned compiler and rejects the parent's own
`examples/hello/Hello.eos` in the same way it rejects this file. The file is
therefore written to match that shipped example exactly in form, with `or`
added, and is labelled unverified in its own header.

**Not checked: everything downstream of that.** No checker was generated, no
Lean was built, and no soundness obligation was stated — so nothing here says
these rules are sound, only that this signature accepts and rejects the proofs
listed above. To go further:

```sh
mkdir /tmp/res-spec
cp tools/mimesis/examples/resolution/Resolution.eo  /tmp/res-spec/
cp tools/mimesis/examples/resolution/Resolution.eos /tmp/res-spec/
cp tools/mimesis/examples/resolution/profile        /tmp/res-spec/
cp examples/hello/smt.eos                           /tmp/res-spec/   # unchanged
scripts/new-checker.sh --checker Demo --calculus Resolution --spec /tmp/res-spec
```

Those commands were **not** run here, and the spec directory is assembled
outside this repository because a child project writes only inside its own
directory.

## What it cost, for the ledger

This tutorial is also a first-hand entry for the
[ledger](../README.md#the-ledger), classified the way every entry is:

| what happened | whose |
| --- | --- |
| a bare literal is not an `or`-list, so unit clauses got stuck until `eo::list_singleton_intro` was found in the manual's list-operator section | **the documentation's** — the operator is documented; nothing connects *clause representation* to the coercion it implies |
| `Proves` / `Expected` name the computed and the claimed term, in that order, which is the opposite of how the words read | **the compiler's** — a label, and a cheap one to change |
| `and` had to be declared for a calculus that never uses it | **the framework's**, and it is documented in the contract; an author who reads the framework's front page first meets it there rather than at install time |
| two programs were written that the language already provides | **the documentation's** — the list operators are a section of the manual an author has no reason to have read before writing their first program |
| the `.eos` could not be compiled against the pin available here | **the framework's** — a pin is deliberate and moving it is a decision; the cost is that a tutorial cannot verify half of what it ships |

**And what it does not measure.** This was written with the manual open and with
the framework's own examples at hand, by somebody who had just spent a day
reading a CPC rule. It is a *tutorial* — the artifact is meant to be correct and
idiomatic — and the friction above is an informed author's rather than a new
one's. An uninformed first-hand run would need a calculus nobody here has looked
up: this file spends resolution.
