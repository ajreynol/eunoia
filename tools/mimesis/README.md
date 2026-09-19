# Mimesis

**Where to learn how to write Eunoia and maintain its verification in Logos.**
A child project of the Eudaimonia build framework, in two strands:

- **Case studies** read an episode that already happened — a signature somebody
  wrote, and whatever answered back: a stated proof obligation, a generated
  checker, a producer's own checker, a test suite. Each says what was decided,
  what was got wrong, and what caught it. The supply is real history: 75 commits
  touched CPC's signature on cvc5's trunk in the twelve months to 2026-09-16.
- **Tutorials** cover different jobs: adding a CPC rule, adding an operator to a
  theory CPC already has, extending CPC with a whole theory, or defining a new
  calculus's signature. Main CPC changes continue through Logos; expert additions
  end with their CPC declarations and checks. Worked files are kept, and each
  tutorial distinguishes what was run from instructions for the reader's own
  change.

Mimesis provides optional advice and examples. Creating a Eunoia signature,
generating a checker, and verifying rules in Logos require no Mimesis checkout
or tooling; the tutorials describe those projects' workflows.

**[Choose a tutorial](docs/tutorials.md).** If you are changing cvc5, start with
**[adding a rule to `Cpc.eo`](docs/adding-a-cpc-rule.md)**. Updating and proving
the rule in Logos is part of that job.

| document | strand | what it is |
| --- | --- | --- |
| [`docs/adding-a-cpc-rule.md`](docs/adding-a-cpc-rule.md) | tutorial | **Start here if you want to add a rule to Cpc.eo in cvc5.** Signature, proof tests, Logos regeneration and Lean proof, then the cvc5 pin and CI |
| [`docs/case-study.md`](docs/case-study.md) | case study | **BV abstraction.** One CPC rule from a paper's lemma schemes into a Eunoia signature, into Logos as 11,168 lines of Lean — where stating the obligation exposed it as unsound — then fixed, proved, and simplified, with the proof shrinking twenty lines for every line the signature lost |
| [`docs/defining-a-calculus.md`](docs/defining-a-calculus.md) | tutorial | **Defining a calculus: propositional resolution.** Write a signature from scratch, with worked proof tests |
| [`docs/extending-cpc-operators.md`](docs/extending-cpc-operators.md) | tutorial | **Extending CPC with a new theory operator.** One operator over existing sorts, followed end to end: `int.pow2`'s declaration, its evaluator, cvc5's printed name, and the Lean lemma that justifies what it computes |
| [`docs/extending-cpc-theories.md`](docs/extending-cpc-theories.md) | tutorial | **Extending CPC theories.** A sort, its values and operators, taken from cvc5's expert finite fields: the main-or-expert decision, cvc5's proof output, the safe-mode gate, and what a main theory owes Logos |
| [`docs/tutorials.md`](docs/tutorials.md) | tutorial | **The router.** One row per job — add a rule, define a calculus, add an operator, add a theory — and which tutorial each starts in. It is the index of that strand, not a tutorial itself |
| [`docs/upstream-draft.md`](docs/upstream-draft.md) | draft | **cvc5's CPC output documentation.** Four things a contributor changing the signature has to find elsewhere, written as a draft for a person to take upstream; nothing in it was sent to cvc5 |

## What each strand owes

**A case study names its sources precisely enough to be re-checked, and is
written so that it survives the branches it was read from.** It reads public
history and reports no defects: anything still wrong in a live tree is a finding
and leaves through the parent in a person's hands, never through an entry here.

**A tutorial ships what works.** Every claim in one is something that was run,
and anything that was not run says so — in the tutorial and in the file itself.

**A draft is a draft, not a dispatch.** Where writing an entry here turned
up something another project might want to hear, it is written down for a person
to send or to drop; sending it is not this project's to do. It is not
correspondence and this project has no channel: a child project is addressed
through the repository that carries it, and the only `docs/discussion.md` in
this tree is Eudaimonia's.

**Both are additive.** The Eunoia [manual][manual] is the authority on the
language, the framework's [front page](../../README.md) on what a signature must
provide, and the compiler's output on what a signature means. Where an entry
here disagrees with any of them, they are right and the disagreement is this
project's to explain.

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
make a calculus sound — it shows that a signature accepts and rejects the proofs
it was shown, and a freshly generated checker's soundness proofs are unfinished
by construction, as the parent's
[limitations](../../docs/limitations.md#nothing-is-proven-yet) say.

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

The name is reserved in [ynoia's register][names], in kanon's tree, and nothing
here edits it; a reader who finds it listed as *not started* should read that as
an edit that is owed.

## An island

It reads the parent, its neighbours and the compiler's tree, and writes only
inside `tools/mimesis/`. Nothing in Eudaimonia links here, imports from here or
runs anything here — deleting this directory changes nothing else. Files a
framework run would produce are written outside the repository, never here.

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

[names]: https://github.com/ajreynol/kanon/blob/5545d5cd20578ec890100810aa59165bb782c6e1/tools/ynoia/names.md#reserved-for-an-intended-launch
[manual]: https://github.com/cvc5/ethos/blob/main/user_manual.md
