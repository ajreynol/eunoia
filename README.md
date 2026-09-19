# eunoia

*εὔνοια — goodwill, and literally "well-minded": the disposition to read
something in the best sense it will bear. The language took the word first and
this repository takes it from the language, because the language is the whole of
its subject. Where the two need telling apart below, **Eunoia** is the language
and **eunoia** is this tree.*

**This is where Eunoia is studied: what the language is, and how it is written.**
Eunoia is the logical framework and language the [Ethos][ethos] checker reads
natively — calculi are defined in it and solver proofs are checked against those
definitions. Understanding it and authoring in it are two different jobs, and
this repository keeps a project for each.

| project | the question it asks | start at |
| --- | --- | --- |
| [**sapheneia**](tools/sapheneia/README.md) | *What is Eunoia, as a language, independently of any checker?* A description written as a language definition, with implementation behaviour quarantined and labelled rather than mixed in | [the account](tools/sapheneia/docs/manual.md) |
| [**mimesis**](tools/mimesis/README.md) | *How is a Eunoia signature written, and how does it stay verified?* Case studies of episodes that already happened, and tutorials for the jobs an author actually has | [choose a tutorial](tools/mimesis/README.md#tutorials) |

The two read the same manual for opposite purposes — one has to say what the
language *requires*, the other what to *type* — and each keeps a ledger of what
that cost: sapheneia's of what the manual does not settle or appears to get
wrong, mimesis's of what an author had to reconstruct and whose it is to fix.
Neither ledger has been carried anywhere, and carrying one is a person's.

## What is here, and what is not

**Nothing here is a program.** This repository ships no checker, no compiler and
no signature anybody depends on. It holds documents, worked signatures and the
proof files those are checked against. The checkers, compilers and signatures it
talks about — [ethos][ethos], [cvc5][cvc5], [logos][logos] and the Eunoia
compiler — live in their own repositories, are named where they are used, and
are pinned to a commit where a claim depends on one.

**Nothing here is authoritative.** ethos's [`user_manual.md`][manual] is the
authority on Eunoia: it governs, which is not the same as being presumed
correct. Everything written here is a second reading a person may consult and
check the first against. Where the two disagree either may be at fault, and the
disagreement goes into a ledger rather than into a correction of the manual.

**Nothing here proposes changes to the language.** Where Eunoia is
underspecified, the work here says where and stops. Proposing the resolution is
a change to Eunoia and belongs with the language's maintainers.

**Nothing leaves by machine.** This repository keeps no discussion file, so
there is no wire into it and none out of it. Anything a project here wants to
say to ethos, cvc5 or logos is carried by a person, under the receiving
project's own reporting discipline, and only once somebody who can answer the
follow-up has agreed to carry it.

**Nothing here is a soundness claim.** Whether a calculus written in Eunoia
proves only true things is a question about that calculus. These are questions
about the language it is written in and about how one is authored.

## Running things

Almost everything here is read rather than run. The exception is mimesis's
worked examples, which carry check scripts that take the tools as arguments
rather than building them:

```sh
tools/mimesis/examples/resolution/check.sh path/to/ethos
```

Each example's README says what its script checks and what it does not. No
project here is a dependency of anything: writing a Eunoia signature, generating
a checker and proving rules in Lean all happen without a checkout of this tree.

## The ecosystem

This tree is arranged by the Eunoia ecosystem's shared policy, which
[kanon][kanon] maintains in [`docs/policy.md`][policy]: one front page, every
document indexed, each project under `tools/` an island that reads what it likes
and writes only inside itself. kanon's [`docs/glossary.md`][glossary] is the
authoritative register of the ecosystem's names, including the ones used here.

## Status

**Opened 2026-09-19**, with the two projects as its contents. Each arrived with
its own history and keeps its own status section; read those rather than this
one for what has been checked and against which commits. This repository has no
documents of its own yet — the front page is the whole of it, and the projects
carry their own indexes.

**The name register is kanon's.** As of 2026-09-19 its glossary entries for both
projects name the repositories they were written in rather than this one.
Editing the register is kanon's and nothing here does it.

## How this repository is maintained

This repository is part of the **Eunoia ecosystem** and follows its shared
repository policy, kept by [kanon](https://github.com/ajreynol/kanon) in
[`docs/policy.md`](https://github.com/ajreynol/kanon/blob/main/docs/policy.md).

**The checker runs here on every push**, as `anoieu / policy`. This repository
names a policy contract rather than pinning a checker commit, so what is held
still is the obligations and not the implementation: a build here can turn red
with nothing committed, and when it does, a violation already in this tree has
started being reported.

**Written by AI agents under light supervision.** The human maintainer is
`ajreynol` — Andrew Reynolds, University of Iowa and AWS — who is the authority
over this repository and the answer to *who do I take this up with*. An agent
holds no footing and makes no decision here: starting a project under `tools/`,
changing what one is chartered to do, ending one, and carrying anything to
another repository are all a person's.

[ethos]: https://github.com/cvc5/ethos
[manual]: https://github.com/cvc5/ethos/blob/main/user_manual.md
[cvc5]: https://github.com/cvc5/cvc5
[logos]: https://github.com/cvc5/logos
[kanon]: https://github.com/ajreynol/kanon
[policy]: https://github.com/ajreynol/kanon/blob/main/docs/policy.md
[glossary]: https://github.com/ajreynol/kanon/blob/main/docs/glossary.md
