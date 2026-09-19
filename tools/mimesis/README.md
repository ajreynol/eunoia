# Mimesis

**Where to learn how to write Eunoia and maintain its verification in Logos.**
A child project of [eunoia](../../README.md), the repository for language
research, in two strands: tutorials for the job you are doing, and case studies
of episodes that already happened.

Mimesis provides optional advice and examples. Creating a Eunoia signature,
generating a checker, and verifying rules in Logos require no Mimesis checkout
or tooling; the tutorials describe those projects' workflows.

## Tutorials

One per job. **If you are changing cvc5, start with [adding a rule to
`Cpc.eo`](tutorials/adding-a-cpc-rule.md)** — updating and proving the rule in
Logos is part of that job. Main CPC changes continue through Logos; expert
additions end with their CPC declarations and checks. Worked files are kept with
each tutorial, and every one distinguishes what was run from instructions for
the reader's own change.

| the job | tutorial | what you work on |
| --- | --- | --- |
| Add a proof rule to cvc5's CPC signature | [**Adding a rule to `Cpc.eo`**](tutorials/adding-a-cpc-rule.md) | The rule's interface and its proof tests, its generated Lean and soundness proof in Logos, then the cvc5 pin and CI |
| Add an operator to a theory CPC already has | [**Extending CPC with a new theory operator**](tutorials/extending-cpc-operators.md) | One declaration, the program that computes it, cvc5's printed name, and the Lean lemma that justifies what it computes — `int.pow2`, end to end |
| Add a whole theory to CPC | [**Extending CPC theories**](tutorials/extending-cpc-theories.md) | A sort, its values and operators, the main-or-expert decision, cvc5's proof output, the safe-mode gate, and what a main theory owes Logos — cvc5's expert finite fields |
| Define a proof calculus of your own | [**Defining a calculus: propositional resolution**](tutorials/defining-a-calculus.md) | A signature written from scratch: terms, premises, arguments, computed conclusions, side conditions, and worked proof tests |

## Case studies

A case study reads an episode that already happened — a signature somebody
wrote, and whatever answered back: a stated proof obligation, a generated
checker, a producer's own checker, a test suite. Each says what was decided,
what was got wrong, and what caught it.

| case study | the episode | what it shows |
| --- | --- | --- |
| [**BV abstraction**](docs/case-study.md) | One CPC rule, from a paper's lemma schemes into a Eunoia signature and into Logos as 11,168 lines of Lean | Stating the obligation exposed the rule as unsound — then the fix, the proof, and the simplification that followed, with the proof shrinking twenty lines for every line the signature lost |

**One so far**, and accumulating them is this project's main goal. The supply is
real history: 75 commits touched CPC's signature on cvc5's trunk in the twelve
months to 2026-09-16.

## The upstream draft

[`docs/upstream-draft.md`](docs/upstream-draft.md) belongs to neither strand.
Writing the CPC tutorials meant reconstructing four things from cvc5's sources
that a contributor **changing** the signature would expect to find on cvc5's own
CPC documentation page: what a change to CPC's vocabulary owes Logos, what
actually makes a feature unavailable in safe mode, which signatures the
generated checker script loads, and the `; disclaimer:` convention that marks
departures from SMT-LIB. Each is written up with the sources quoted, the
revisions recorded, and a suggested wording — a draft for a person to take
upstream if they agree with it. Nothing in it was sent to cvc5.

## What each strand owes

**A case study names its sources precisely enough to be re-checked, and is
written so that it survives the branches it was read from.** It reads public
history and reports no defects: anything still wrong in a live tree is a finding
and leaves through the parent in a person's hands, never through an entry here.

**A tutorial ships what works.** Every claim in one is something that was run,
and anything that was not run says so — in the tutorial and in the file itself.

**A draft is a draft, not a dispatch.** Where writing an entry here turned up
something another project might want to hear, it is written down for a person
to send or to drop; sending it is not this project's to do. It is not
correspondence and this project has no channel: a child project is addressed
through the repository that carries it, and the repository that carries this
one keeps no `docs/discussion.md` at all. Where there is no discussion file
there is no wire, in either direction, and what is said is carried by a person.

**All three are additive.** The Eunoia [manual][manual] is the authority on the
language, the [signature contract][contract] of [eudaimonia][eudaimonia] — the
checker-build framework, *the framework* wherever a ledger row below says it —
on what a signature must provide, and the compiler's output on what a signature
means. Where an entry here disagrees with any of them, they are right and the
disagreement is this project's to explain.

## The ledger

What the entries accumulate into: each difficulty recorded with whose it is to
fix — **the compiler's**, **the framework's**, **the documentation's**, or
**nobody's**, a judgement about the calculus that no tool can make. Counts by
category across entries are the point; one entry is a story.

**It is a convention rather than a file.** Every entry ends with its own rows,
under *What it cost, for the ledger* or, in the case study, *What it teaches
about authoring*; there is nothing to keep in step and nothing that can go stale
against the entries. Entries spell **nobody's** as *irreducible* where that reads
better, and it is the same category: not that the difficulty is unimportant, but
that no tool or page could remove it.

**A row is a difficulty, not a defect.** Anything still wrong in a live tree is a
finding and leaves through the parent in a person's hands. Where a row says *the
documentation's*, what it names is a place a reader has to reconstruct something
— and where that is somebody else's page, the draft is
[upstream-draft.md](docs/upstream-draft.md) and sending it is a person's.

Nothing in a ledger entry is a soundness claim. Passing proof tests does not
make a calculus sound — it shows that a signature accepts and rejects the
proofs it was shown, and a freshly generated checker's soundness proofs are
unfinished by construction, as eudaimonia's [limitations][limitations] say.

**No paper.** A reading of somebody's history is not a result. That changes if
there are enough entries for counts to mean something, at least one of them
written first-hand.

## The name

*Mimesis* (Greek **μίμησις**, "imitation") is Aristotle's word for learning by
representing — a craft picked up from worked instances before it can be stated
as a rule. Both strands are that word taken literally: the doing of somebody who
has already done it, set down in enough detail to be imitated and argued with.
Learning from an existing CPC rule and designing a new signature are different
starting points; the tutorials give each its own route.

The name is registered in [kanon's glossary][names], and nothing here edits it;
a reader who finds that entry naming a different repository should read it as
an edit that is owed.

## An island

It reads the parent, its neighbours and the compiler's tree, and writes only
inside `tools/mimesis/`. Nothing outside imports from here or runs anything
here, and deleting this directory changes nothing else. Files a framework run
would produce are written outside the repository, never here.

**One named exception.** In one respect this project is **not an island**:
eunoia's front page names and advertises it, a link inward that a reader meets
before this page. That is the parent's choice, recorded here so that it is a
named exception rather than drift. What has been delivered is four tutorials,
one case study and the upstream draft — nothing of it carried anywhere. The
promotion decision is therefore open, and it is the human maintainer's.

## Status

**Started 2026-09-16 by the maintainer, in an explicit instruction**, and
reoriented the same day and the same way: it had led with writing one calculus
ourselves, and the main goal now is accumulating case studies, with tutorials as
the second strand. On 2026-09-17, the tutorial collection gained a CPC contributor
entry point, with the Logos update at its center. On 2026-09-18 the theory
tutorial became two: one operator over sorts CPC already has, followed from
`int.pow2`'s declaration to the Lean lemma that justifies it, and a whole theory,
followed through cvc5's expert finite fields. A person decides whether it
**graduates** into its own repository, is **folded** into the parent, or is **retired in
place** with a note saying what was learned; going quiet is not one of those.

[names]: https://github.com/ajreynol/kanon/blob/main/docs/glossary.md#mimesis
[manual]: https://github.com/cvc5/ethos/blob/main/user_manual.md
[eudaimonia]: https://github.com/ajreynol/eudaimonia
[contract]: https://github.com/ajreynol/eudaimonia/blob/main/README.md#the-signature-contract
[limitations]: https://github.com/ajreynol/eudaimonia/blob/main/docs/limitations.md#nothing-is-proven-yet
