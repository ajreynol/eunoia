# Formalizing Eunoia

*Goal 3 of this project, and a wishue. **Not started.** This file records
what the work would have to be, what already exists to build on, and what
currently blocks it — so that the next person to look at it starts from a
position rather than from a blank page.*

## What this means, and what it does not

**Would be:** judgement forms and inference rules for Eunoia itself, at the
level of detail where two people could implement from them and agree on every
term — a definition against which an implementation is correct or is not.

**Would not be:**

- a proof that any particular calculus is sound. That is a question about a
  signature, not about the language it is written in.
- a Lean development of the embedding, or of the compiler. Those are separate
  pieces of future work under their own names (`tools/ynoia/docs/why-eunoia.md` calls them
  *hermeneia* and *noesis*), with different subjects and different audiences.
- a decision on any of the open questions in
  [`manual.md` §11](manual.md#11-where-the-language-is-unsettled). A
  formalization has to *choose* on each of them; choosing is a change to
  Eunoia, and proposing changes is outside this project's charter. See
  [Blockers](#the-blockers) below for what that implies about the shape of the
  work.

## The four layers

Eunoia is not one semantics; it is four, stacked, and they are usually discussed
as if they were one. Separating them is most of the value a formalization would
add, and it is the same separation
[`manual.md` §1.2](manual.md#12-the-pipeline-and-why-it-matters) draws
informally.

| layer | the judgement, roughly | difficulty |
| --- | --- | --- |
| **1. Desugaring** | `Σ ⊢ s ⇝ t` — source form `s` elaborates to term `t` under signature `Σ` | mechanical, and almost fully specified already |
| **2. Evaluation** | `t ⇓ t'` — a term reduces | mechanical for most operators; `eo::hash` and `eo::nil` are the exceptions |
| **3. Typing** | `Σ ⊢ t : T` | small, and nearly written already |
| **4. Proof checking** | — | *nothing*: it is layer 3 applied to `Proof` types |

Layer 4 collapsing into layer 3 is the language's central design idea, and is
the thing a formalization would make undeniable rather than merely stated. See
[`manual.md` §8](manual.md#8-the-type-system).

### Layer 1 — desugaring

The most under-appreciated layer, and the one where signatures actually go
wrong. A signature-dependent rewrite on source forms, keyed on the head symbol's
declared attribute, defined in
[`manual.md` §4.5](manual.md#45-the-desugaring-algorithm) as an algorithm and
reproducible as a relation directly. It needs:

- `Σ` carrying, per symbol, its attribute and (for the nil forms) its terminator;
- a `:list` marking on parameters, which is a property of the *binding
  occurrence* and must be threaded through;
- the interaction with `eo::list_concat` and `eo::list_singleton_elim`, which is
  where desugaring reaches into layer 2 and produces terms that layer 2 will
  reduce.

It is worth doing first, on its own, for two reasons: it is finishable, and it
is the layer with an existing differential oracle — this repository already has
a desugarer checked against a real checker on a committed battery
(`anoieu/desugar.py`, `scripts/oracle_desugar.py`, `tests/desugar/`). A
formalization of layer 1 could be validated against that battery on the day it
was written, which is not true of any other layer.

### Layer 2 — evaluation

A big-step relation over ground terms. Uniform in shape because of the stuckness
discipline ([`manual.md` §5.1](manual.md#51-one-discipline-stated-once)): every
operator is a partial function on values, lifted to a total function on terms by
returning the application itself where it is undefined. So the whole layer is
one generic rule plus a table of partial functions, with three carve-outs for
the non-strict positions.

The interesting content is not the arithmetic; it is:

- **`eo::nil` is signature-dependent**, and is the only operator that is. It
  cannot be given as a partial function on terms — it is a lookup into `Σ` with
  matching on the type argument, which is precisely why the manual's own
  reconstruction of the operators in pure Eunoia can define every list operator
  *except* this one.
- **`eo::hash` is underspecified** and cannot be given at all without a decision
  (see [Blockers](#the-blockers)).
- **Programs** are user-defined cases of the same relation, with first-match
  semantics over a signature-carried case list, and no termination argument
  anywhere. So layer 2 is a partial relation by construction, and any
  formalization is a definition of a partial function whose domain is not
  characterized.

### Layer 3 — typing

Already close to formal. The manual's *Proofs as terms* appendix gives two
rules, and they are the whole of application typing:

```
    f : (-> U S)        t : T                 f : (-> (Quote u) S)     t : T
    ─────────────────────────  U·σ = T        ──────────────────────────────  u·σ = t
        (f t) : S·σ                               (f t) : S·σ
```

plus the side condition that a well-typed term's type must be non-ground or
fully reduced — which is where layers 2 and 3 are mutually recursive, since
deciding "fully reduced" runs the evaluator, and the evaluator's programs have
no termination argument. That mutual recursion is the one genuine technical
difficulty in the stack, and it is the thing a formalization would have to be
honest about that no informal account has had to be.

What is missing from the two rules: the treatment of `:implicit` (an
elaboration, so arguably layer 1), of `:opaque` (which makes an application not
an application, and so has to be visible to layer 2's matching), of overloading
resolution (which is type-directed, so layer 3 feeds back into layer 1), and of
`eo::self` in `declare-consts`.

## What already exists to build on

Nobody would be starting from nothing.

| | what it is | what it gives |
| --- | --- | --- |
| the manual's *Proofs as terms* appendix | two typing rules and the proof-command correspondence | layer 3, most of the way |
| the manual's *Derived Definitions of Evaluation Operators* (`tests/eo-definitions.eo` in ethos) | every list operator except `eo::nil`, written as ordinary Eunoia programs | a **self-interpretation**: layer 2 partly defined in the object language, and executable |
| the ethos-eoc deep embedding and its `.eos` semantics sets | a compiler's model of the language | an independent reading to disagree with |
| the logos Lean development | a second checker for the same proofs | a second reading, and a place where `eo::hash` was already declined |
| this repository's desugarer battery | layer 1 against a real checker | validation for layer 1, today |

The self-interpretation is the most interesting of these and the least
discussed. A language that can define most of its own evaluator in itself has
already done a large part of the work; what is left is the part that cannot be
done that way, and the manual is explicit that the residue is exactly `eo::nil`.

## The blockers

Each open question in
[`manual.md` §11](manual.md#11-where-the-language-is-unsettled) is a place where
a formalization must choose and this project may not. That is not a reason to
stop; it is a constraint on the *shape* of the result:

> **A formalization here would be parameterized by its choices, and would state
> them as parameters rather than resolving them.**

Which is not a workaround — it is the more useful artifact. A definition that
says "under reading A of the attribute contracts, these signatures are
well-formed; under reading B, these three are not" is a better input to the
people who own the language than a definition that quietly picks one.

The choices, ranked by how much they cost to leave open:

1. **What a well-formed signature is.** The largest. Under the permissive
   reading there is nothing to define — well-formedness is a property of a
   corpus of proofs, not of a file — and the formalization has no top-level
   judgement. Under the strict reading it has one, and existing signatures fail
   it. Everything else on this list is a special case.
2. **`eo::hash`.** Cannot be given a semantics at all without a contract. Every
   choice is observable: any signature that orders terms by `eo::cmp` gets a
   different meaning under a different hash. The honest treatment is to
   parameterize over an injection on values and prove whatever holds for all of
   them, which is what the Lean development effectively did by declining to
   model it.
3. **Attribute contracts.** Determines whether layer 1 is total on all
   signatures or partial on well-formed ones — that is, whether desugaring a
   violating declaration has a definition. Currently it has none.
4. **Program case overlap.** First-match-wins is well defined either way, so
   this is only a question if the language intends coverage or disjointness.
   Cheap to leave open.
5. **File roles.** Literal normalization depends on invocation, so *term
   identity* is not a function of the text. A formalization must either take the
   role as a parameter or define the language for one role and say so.

## A first milestone worth having

Not the whole stack. Layer 1 alone, as a relation, validated against the
existing desugarer battery — because it is finishable, it is checkable the day
it is written, and it is the layer where real signatures actually break. If it
lands, the parts of layers 2 and 3 it forces into the open (`eo::list_concat` in
patterns, the `eo::nil` placeholder, `:list` as a property of a binder) are the
right next thing to look at.

Everything above this line is a plan, and no line of it has been attempted.
