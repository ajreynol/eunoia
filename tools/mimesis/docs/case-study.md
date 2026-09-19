# Case study: BV abstraction

One CPC proof rule, from a published table of lemma schemes into a Eunoia
signature, into Logos — where stating its soundness obligation exposed it as
unsound — then fixed at the source, proved, and finally simplified, with the
Lean proof shrinking by twenty lines for every line the signature lost.

**Why this one.** It is the episode in reach where a signature was written and
something answered back in full: 373 lines of Eunoia, 11,168 lines of Lean, and
seven days of history that say which authoring choices cost what.

**How it was read.** On 2026-09-16, from the commits of two development branches
— `bvAbstract` in Logos and `bvAbstract-pf` in a fork of cvc5 — neither linked
here and both listed by commit in [the appendix](#appendix-the-commits-read). At
that date the work had landed on neither project's `main`. One person authored
both sides, which is why the loop turns in hours below.

**Nothing was built for this account.** Sizes are line counts of committed
files; *compiles* means the history says it compiled. The two counterexamples in
[movement 4](#4-the-unsoundness) were checked by hand, and are the only thing
here verified independently of the trees.

## The rule

`ProofRule::BV_ABSTRACTION` justifies the refinement lemmas of cvc5's bit-vector
arithmetic abstraction: a CEGAR strategy that replaces `bvmul`, `bvudiv` and
`bvurem` terms with fresh constants and constrains those constants with sound
over-approximations instead of bit-blasting the originals. The schemes are a
direct port of Bitwuzla's abstraction module, as described in *Scalable
Bit-Blasting with Abstractions* (Niemetz, Preiner, Zohar, CAV 2024), Table 2 —
71 of them in the signature as it now stands: 19 for `bvmul`, 37 for `bvudiv`,
15 for `bvurem`.

For an abstracted term `(op x s)` with abstraction `t`, each scheme `l[x,s,t]`
satisfies `(=> (= (op x s) t) l)`. The Eunoia rule concludes exactly that
formula:

```
(declare-rule bv_abstraction ((F Bool))
  :args (F)
  :requires ((($bv_abstraction_lemma F) true))
  :conclusion F
)
```

No premises, no structure: a 354-line Eunoia program decides membership in a set
of formulas and the rule says *this one is in it*. Everything hard about the rule
sits inside that program — the part of Eunoia a proof has to take apart case by
case.

## The movements

**Three artifacts, not two repositories.** CPC's Eunoia signature lives in cvc5's
own tree beside the C++, so the middle column below names *what changed* — the
signature, cvc5's C++, or the Lean development in Logos — rather than which
checkout it changed in.

| when (commit's own timestamp) | what changed | what happened |
| --- | --- | --- |
| 2026-08-20 08:34 | cvc5 (C++) | the proof rule and cvc5's own C++ checker for it — **with** the bit-width guard |
| 2026-08-20 09:08 | Eunoia signature | proposed: schemes built and compared, no width guard |
| 2026-08-21 06:53 | Eunoia signature | rewritten toward syntactic matching |
| 2026-08-21 07:47 | Eunoia signature | rewritten again: matching only, no constructed terms |
| 2026-08-21 08:01 | Eunoia signature | split into CPC's layout — program file, rule file |
| 2026-08-21 08:05 | Logos | compiled in: 734 generated lines, obligation stubbed `sorry` |
| 2026-08-21 10:43 | Logos | **unsound** — the width guard hand-patched into the generated file |
| 2026-08-21 11:08 | Eunoia signature | the guard added at its source |
| 2026-08-21 11:32 | Logos | regenerated from the fixed signature; the hand patch discarded |
| 2026-08-21 14:38 → 08-22 17:12 | Logos | the proof: about 11,300 lines added across 24 files, obligation closed |
| 2026-08-24 09:46 | Logos | Lean 4.33 fallout, 5 files, tactics only |
| 2026-08-24 10:01 | Eunoia signature, cvc5 | simplified: six cases become three, and the C++ and its unit test follow |
| 2026-08-24 10:59 → 11:59 | Logos | regenerated (−3 lines), proof follows (−139 lines) |
| 2026-08-27 15:12 | cvc5 (C++) | formatting |

### 0. What the C++ already knew

The first commit of the episode adds the proof rule to cvc5 and, with it, cvc5's
own C++ checker for the rule. That C++ checker contains this, a day before any
Lean proof and half an hour before the signature was written:

```cpp
// Some schemes are not valid for bit-width 1 or 2 (see e.g. MUL5 and MUL9),
// which is why the abstraction module never considers such terms (the
// minimum of --bv-abstraction-size is 3).
if (utils::getSize(n) < 3)
{
  return {};
}
```

Upstream of it, the abstraction module itself — merged five days earlier, by
other people — carries **twelve assertions** naming the schemes that fail at small
widths and the width each one needs: `MUL5`, `MUL6`, `MUL7`, `MUL11`, `MUL12`,
`MUL18`, `UDIV21`, `UDIV32` invalid at width 1; `MUL9` and `UDIV36` invalid at
width 2; `UDIV30` and `UREM13` invalid below 3.

**So the side condition was never unknown.** It was written down twice, in the
language the implementation is written in. What happened next was not a failure
of knowledge but a failure of transcription.

### 1. The signature proposed

Thirty-four minutes later, the first Eunoia draft: 296 lines added to the
bit-vector rules, written in a **constructive** style. For each scheme it builds
the instantiation the scheme would have for `x`, `s` and `t` — under twelve
`eo::define` bindings that name the width and the constants once — and compares
the result to the formula in hand.

The reason for that style is stated in the file itself, and it is the language
pushing back:

> cvc5 treats `bvand`, `bvor`, `bvxor`, `bvadd` and `bvmul` as variadic, so that
> a binary application of these carries a nil terminator that depends on the
> bit-width. Such a terminator is not a legal subterm of a pattern.

A scheme whose shape mentions `(bvand x s)` cannot simply be matched, because the
term cvc5 produces carries a width-dependent nil the author cannot write in a
pattern. The first answer was to stop matching altogether and build instead.

There is no width condition anywhere in this draft.

### 2. Two rewrites before anybody proved anything

The next morning, two rewrites in under an hour, both of them the author
arguing with the same obstacle:

- **06:53** — a hybrid. Schemes that *can* be recognised syntactically become
  patterns; the ones that carry a variadic operator stay constructive, in a
  helper renamed from `_sym` to `_cmp` with a comment explaining which is which.
- **07:47** — the hybrid is abandoned. Everything becomes a pattern, the nil
  terminators are bound as **`:list` variables** and validated on the right-hand
  side of each case: `($bv_is_zero ln1)`, `($bv_is_ones ln2)`, `($bv_is_one cone)`.
  Zero `eo::define` remain.

So `MUL5` ends up as a pattern with three list variables and four right-hand-side
checks:

```
(($bv_abstraction_lemma_mul x s t (not (= s (bvnot (bvor t (bvand cone (bvor x s ln1) ln2) ln3)))))
    (eo::and ($bv_is_one cone) (eo::and ($bv_is_zero ln1) (eo::and ($bv_is_ones ln2) ($bv_is_zero ln3)))))
```

Nobody had proved anything yet, so nothing priced this choice at the time it was
made. It set 56% of the eventual proof; [what it cost](#what-it-cost) arrived two
days later.

At 08:01 the work is split into CPC's conventional layout: the programs into
`programs/BvAbstraction.eo`, the nineteen-line rule into `rules/BitVectors.eo`.

### 3. Compiled, and stubbed

Four minutes later the Logos side begins: the signature is compiled and the
generated Lean lands in Logos's compiled signature file — **734 lines**, or
about one-fifteenth of the entire compiled CPC. The rule is registered, and the
obligation it now owes is created as a stub:

```lean
public theorem cmd_step_bv_abstraction_properties ... := by
  sorry
```

That file is 22 lines, and it is the whole of what Logos owes for this rule. The
framework this repository generates puts the same obligation in the same place
for a calculus of one rule.

### 4. The unsoundness

Two and a half hours later, before a single proof of a scheme exists, the
generated file is **hand-patched** inside Logos:

```lean
-- Bitwuzla generates these schemas only for abstraction widths of at least 3.
def __bv_abstraction_width_ok (x : Term) : Term :=
  __eo_gt (__bv_bitwidth (__eo_typeof x)) (Term.Numeral 2)
```

…and wrapped around every case of the matcher. The commit is called *AI soundness
fix*; the commit that follows it in cvc5's tree, twenty-five minutes later, is
called *Fix unsound based on logos AI*. The signature gains
`$bv_abstraction_width_ok`, a comment recording why, and the two counterexamples
that show it is needed:

> `MUL5` does not hold for `x=1`, `s=0`, `t=0` at width one, and `MUL9` does not
> hold for `x=s=2`, `t=0` at width two.

Both check by hand, and this account checked them:

| | `MUL5` at width 1 | `MUL9` at width 2 |
| --- | --- | --- |
| scheme | `(not (= s (bvnot (bvor t (bvand 1 (bvor x s))))))` | `(bvuge t (bvand 1 (bvlshr (bvand x s) 1)))` |
| values | `x=1`, `s=0`, so `t = x*s = 0` | `x=s=2`, so `t = x*s = 4 mod 4 = 0` |
| guard | `(= (bvmul x s) t)` holds | `(= (bvmul x s) t)` holds |
| body | `bvor x s = 1`; `bvand 1 1 = 1`; `bvor t 1 = 1`; `bvnot 1 = 0`; so the inner `(= s 0)` **holds** and the scheme, which negates it, is false | `bvand x s = 2`; `bvlshr 2 1 = 1`; `bvand 1 1 = 1`; `0 ≥ 1` is **false** |
| verdict | guard true, lemma false: the rule would have accepted an invalid formula | same |

**What was actually at risk, stated precisely.** No cvc5 proof in the wild could
have exercised this: the abstraction module never abstracts below width 3, and
cvc5's C++ checker rejected such lemmas from the first commit. The defect was in
the *rule* — a proof rule must reject what any producer could hand it, not only
what today's producer happens to emit — and it was in the rule for twenty-six
hours, on a branch, and never reached anybody.

Three things about how the fix travelled are worth more than the fix:

1. **It was made in the generated file first.** Logos patched the compiled Lean
   by hand at 10:43, got the signature fixed at its source at 11:08, and
   threw its patch away at 11:32 by regenerating. The hand patch was a diagnosis,
   not a repair, and the history says so: the regeneration commit *deletes* the
   hand-written `def`.
2. **The regenerated form is not the written form.** `(define ...)` in Eunoia is
   a macro; it does not survive compilation as a definition. Where the hand patch
   had a named `__bv_abstraction_width_ok`, the compiler inlined
   `(__eo_gt (__bv_bitwidth (__eo_typeof x)) (Term.Numeral 2))` into all six
   cases — and that inlined form, not the name, is what the eventual proof talks
   about (`width_guard_sound`, which turns it into `3 ≤ w`).
3. **The guard is stronger than any single scheme needs**, and the signature
   says why: twelve schemes carry width caveats of three shapes — at least 2,
   not 2, at least 3 — whose union is "at least 3", and the signature carries the
   union with the two sharpest counterexamples recorded in a comment. A
   signature carrying twelve separate guards would have been more faithful to
   the C++ and considerably worse to prove.

### 5. The proof

Three hours after the regeneration, the proof begins. It arrives in two distinct
phases, and the order is the surprise.

**The mathematics first** (2026-08-21, 14:38 → 16:33; about 5,000 lines). One
theorem per scheme, stated over `BitVec w` for all `w ≥ 3`. `UDIV20`, for
instance, becomes:

```lean
theorem udiv20 {w : Nat} (hw : 3 ≤ w) (x s : BitVec w) :
    s ≠ ~~~(s >>> (x.smtUDiv s >>> 1).toNat)
```

Note that the abstraction `t` has been substituted by `x.smtUDiv s`: the rule's
antecedent `(= (bvudiv x s) t)` is discharged by instantiation, which is why the
schemes can be stated as unconditional facts about two variables.

The technique that makes 71 schemes tractable is a truncation homomorphism:
`low3 x = x.setWidth 3`, plus lemmas saying `low3` commutes with each operation
(`low3_mul`, `low3_add`, `low3_not`, `low3_neg`, `low3_sub`, several of which
carry `3 ≤ w`), plus `ne_of_low3_ne`. A width-generic claim is reduced to a claim
about 3-bit vectors and finished by `bv_decide`. **The bound 3 therefore appears
twice in this episode for two different reasons** — as the validity boundary of
the schemes, and as the constant the proof technique truncates to — and they are
not the same fact, however neatly they coincide.

**The plumbing last** (2026-08-22, one commit, 6,249 lines). And it is *bigger*:

- `BvAbstractionMatcherSupport` (2,604 lines), `…UdivMatcherSupport` (1,579),
  `…MulMatcherSupport` (1,096) — lemmas connecting the compiled program's pattern
  match to a semantic statement. The characteristic theorem is not about
  bit-vectors at all: `validated_zero`, `validated_one`, `validated_ones`,
  `validated_to_bin_literal` turn a right-hand-side check like
  `($bv_is_ones ln2) = true` into *the term really is that literal*;
  `eo_and_eq_true_args` decomposes an `eo::and`; `aliases2` … `aliases6` handle
  the repeated variables a pattern binds.
- `BvAbstractionDslSupport` (358) — a little reflected expression type (`Expr`,
  with `.term` and `.value` interpretations) so that 71 schemes could be handled
  uniformly instead of by 71 bespoke chains.
- `BvAbstractionRuleSupport` (455 at this point) — the rule-level glue, including
  the one lemma that exists purely because of the nil terminator:
  `nested_mul_interprets_of_simple`, which proves that a term `bvmul x (bvmul s 1)`
  interprets like `bvmul x s`, i.e. that the `:list` variable the author had to
  bind is semantically invisible.

The top-level proof is then a `fun_cases` over the compiled program with one case
per Eunoia case, and the obligation's `sorry` gives way to some forty-five lines
of proof — in a 61-line file that never mentions a bit-vector.

### 6. Elegance, and what it refunded

Two days later, in cvc5's tree, the signature is simplified. The guard
equality had been matched in both orientations — `(= (op x s) t)` and
`(= t (op x s))` — giving six cases; the simplification keeps three and requires
the abstracted term on the left. The C++ stops trying both orientations, and a
unit test is flipped from asserting that the reversed form is accepted to
asserting that it is rejected.

Logos follows within two hours, and this is the measurement the whole document
exists for:

| artifact | change |
| --- | --- |
| Eunoia program | −7 lines (six cases to three) |
| generated Lean | −3 lines |
| **hand-written proof** | **−139 lines** |

What went away: `sound_udiv_match_reversed`, `sound_urem_match_reversed`,
`sound_nested_mul_match_reversed`, plus the two symmetry lemmas they needed
(`imp_eq_symm_bool`, `imp_eq_symm_interprets_bv`) — each of which had to establish
that flipping an equality preserves both well-typedness and interpretation, per
operator, by evaluating both sides. And three cases of the top-level `fun_cases`
went with them, along with the negative hypotheses (`hNotMul`, `hNotUdiv`) that
every later case of a Eunoia program inherits from the patterns above it.

**Seven lines of signature were worth 139 lines of proof, at a ratio of about
twenty to one.** An author with no Lean development downstream has no way to see
that number, and would reasonably have judged the two-orientation version the
more accommodating design.

### 7. The toolchain

Between the proof and the simplification sits a Lean 4.33 update: five files,
+31/−20, entirely tactic-level — `dsimp only` calls that had become no-ops
guarded with `try`, a `rw … congr 2` replaced by `omega`, one explicit
`public meta import`. **No statement changed.** For a maintenance estimate that
is the datum that matters: the toolchain bill is paid in tactics, and the
semantic content of the proof was untouched by it.

## What it cost

| | |
| --- | --- |
| Eunoia written | **373 lines** — a 354-line program file and a 19-line rule |
| schemes covered | **71** (19 `bvmul`, 37 `bvudiv`, 15 `bvurem`) |
| Lean generated from it | **734 lines**, in a compiled CPC signature of 11,218 |
| Lean written by hand | **11,168 lines** — 61 in the obligation, 11,107 across 24 support files |
| …of which, the mathematics | **4,842** (44%) |
| …of which, matching and plumbing | **6,265** (56%) |
| ratio, proof to signature | **≈ 30 lines of Lean per line of Eunoia** |
| elapsed, first commit to last | 2026-08-20 08:34 → 2026-08-27 15:12 |
| elapsed, the proof itself | 2026-08-21 14:38 → 2026-08-22 17:12 |

For scale: Logos's CPC proof development is 746,677 lines across 839 files
with **no `sorry`**, and 592 of those files are per-rule obligations — the 591
rules of the trunk, plus this one. One rule here cost about 1.5% of that corpus
— and the hand-written proof of this single rule is roughly the size of the
entire compiled CPC signature it lives beside.

## What it teaches about authoring

The [ledger](../README.md#the-ledger) classifies each difficulty by whose it is
to fix. This episode's entries, in that shape:

| what happened | whose | what it says |
| --- | --- | --- |
| the width caveats lived in twelve C++ assertions and were not carried into the signature | **irreducible, with a mechanizable half** | the side conditions of a calculus are routinely recorded somewhere other than its rule statements — in assertions, in an option's minimum, in a comment. A signature transcribed from the *shapes* of the rules drops them silently, and no amount of care about the shapes recovers them. The mechanizable half is a checklist item, not a tool: *list what the implementation asserts, and account for each* |
| a width-dependent nil terminator is not a legal subterm of a pattern | **the compiler's** | it forced two full rewrites of the signature before any proof existed, and it costs a Lean lemma per affected operator to show the bound list variable is semantically invisible. The compiler tree names the same family of problems from its own side |
| `(define …)` is a macro and does not survive into the generated Lean | **the framework's, to document** | the proof talks about the inlined expression. An author who names a helper for readability should know the obligation will not see the name |
| every case of a Eunoia program is a case of the Lean proof, with negative hypotheses inherited from the cases above | **irreducible, and predictable** | case count is the proof's cost driver, and it is visible in the signature. Three deleted cases were 139 deleted lines |
| the matching style chosen for readability set 56% of the proof burden | **irreducible** | constructive comparison and syntactic matching are both legitimate; they are not equally cheap to prove about, and the difference is invisible at the moment of choosing |
| nothing runnable could have exposed the defect | **irreducible, and the reason the charter says what it says** | it was reachable only at bit-widths the abstraction module never produces and cvc5's own C++ checker already rejected, so no proof, test or fuzzer working from real cvc5 output would have reached it. What found it was somebody having to *state* the obligation |

That last row is why the [ledger](../README.md#the-ledger) refuses soundness
claims. A signature whose proof tests pass is a signature that accepts and
rejects the proofs it was shown. This episode is the strongest
available evidence that the gap between that and soundness is real, is reached by
competent people working carefully, and closes only when somebody states the
obligation in a proof assistant.

## What this project takes from it

Concrete, and to be carried into the route rather than admired:

1. **The route gets a transcription step, before any Eunoia is written.** Read the
   producer's implementation for what it *asserts* and what its options *forbid*,
   list those conditions, and carry each into the signature or record why it does
   not belong there. The rule descriptions are not the whole calculus.
2. **The route states the case-count rule of thumb.** Every case of a program is a
   case of the proof; prefer the formulation with fewer cases even when it reads
   slightly worse, and expect a factor of roughly twenty between a case deleted
   and the proof lines it takes with it.
3. **The route warns about matching style at the point of choosing**, since the
   cost lands two days later in somebody else's file.
4. **A candidate mechanism for goal 5**: a lint over a compiled signature that
   reports, per program, its case count and its right-hand-side validations —
   the two quantities that became matcher lemmas here. It would have given the
   author of movement 2 the number that only arrived in movement 5.
5. **A candidate request**: a diagnostic when a pattern contains a subterm that
   cannot legally appear in one, naming the list-variable idiom as the fix. The
   author found that idiom by rewriting the file twice.

None of these is filed anywhere. Requests leave this island through the parent in
a person's hands, and this document opens no channel.

## What this account cannot tell you

- **How the unsoundness was found.** The tree records the order — the obligation
  created as a stub, then the guard, then the proof — and it records that both
  commit messages credit the Logos-side agent work. It does not record the
  method, and this account does not guess at one.
- **Effort.** Commit timestamps are not working hours, and one person's inner
  loop is not a team's.
- **Whether any of it compiles today.** Nothing was built for this account; the
  claim is that the history says these files were committed as complete, with no
  `sorry` remaining in them.
- **Whether the schemes are stated correctly at all.** That is the CAV 2024 paper's
  and Bitwuzla's, then cvc5's port of them; this account inherits their statement
  of what the schemes are and inspects only what happened downstream.

## Appendix: the commits read

Short identifiers, their own author timestamps, and their subject lines, so that
this account can be re-checked against the trees while they still carry these
branches — and so that it remains a self-contained record of what was read if
they do not. **Identifiers are data here, not links**: a rebase invalidates them
without invalidating anything above, which is why every claim in this document is
stated so that the file contents quoted are the evidence.

| tree | what it changed | commit | timestamp | subject |
| --- | --- | --- | --- | --- |
| cvc5 (upstream) | C++ (the abstraction module) | `36ceff91a0` | 2026-08-15 | bv abstract: Add abstraction lemmas for bvmul, bvudiv, bvurem. (#12782) |
| cvc5 fork | C++ | `b58752770f` | 2026-08-20 08:34 | Proofs for BV abstract |
| cvc5 fork | Eunoia signature | `820fe6a0b3` | 2026-08-20 09:08 | Draft |
| cvc5 fork | Eunoia signature, C++ | `63def358cb` | 2026-08-21 06:53 | Try |
| cvc5 fork | Eunoia signature | `92e5553edc` | 2026-08-21 07:47 | Refactor |
| cvc5 fork | Eunoia signature | `e7dac8f3de` | 2026-08-21 08:01 | Move |
| Logos | generated Lean, obligation stub | `ae6b3e1a` | 2026-08-21 08:05 | Draft of BV abstraction rule |
| Logos | generated Lean (hand-patched) | `cb0e295c` | 2026-08-21 10:43 | AI soundness fix |
| cvc5 fork | Eunoia signature | `879246e0f6` | 2026-08-21 11:08 | Fix unsound based on logos AI |
| Logos | generated Lean (regenerated) | `6cf7559c` | 2026-08-21 11:32 | Fix from updated Eunoia, compiled |
| Logos | Lean proof | `349e75ba` | 2026-08-21 14:38 | In progress |
| Logos | Lean proof | `51d5d461` | 2026-08-21 16:15 | In progress, more |
| Logos | Lean proof | `619c4a77` | 2026-08-21 16:33 | More |
| Logos | Lean proof | `d38f92ca` | 2026-08-22 17:12 | Finish |
| Logos | Lean proof | `af242ff5` | 2026-08-24 09:46 | Updates for 4.33 |
| cvc5 fork | Eunoia signature, C++, unit test | `c68eefe266` | 2026-08-24 10:01 | Simplify proof rule |
| Logos | generated Lean (regenerated) | `a413b4f6` | 2026-08-24 10:59 | Compile simplification |
| Logos | Lean proof | `fb7260a0` | 2026-08-24 11:59 | Fixes to proof from simplification |
| cvc5 fork | C++ | `bc3fbdc495` | 2026-08-27 15:12 | Format |

*Logos* is its `bvAbstract` branch; *cvc5 fork* is the `bvAbstract-pf` branch of
a fork of cvc5, which carries both the C++ and CPC's Eunoia signature. The first
row is upstream cvc5 and reached that branch through an ordinary merge.

## Standing

**Additive, never authoritative.** The people who ran this episode are the
authority on it. Where this reading is wrong about their work, their history is
right and this document is the thing to correct. It reads public commits of
published projects; it reproduces the fragments needed to make its points and no
more; and it reports a defect to nobody, because there is nothing outstanding to
report — the episode fixed itself in twenty-five minutes and went on.

The lessons are drawn for this project's own purposes, which were not the
purposes of the people doing the work. Nobody in that history set out to
demonstrate anything about how signatures should be authored, and nothing here
should be read as their position.
