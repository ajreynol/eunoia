# eunoia

*One word, two spellings: **Eunoia** is the language and **eunoia** is this
tree, and where the difference matters below the capital says which. Why they
share a word is [the name](#the-name).*

**This is where Eunoia is studied, its semantics configuration language is
maintained, and its files are laid out: what the languages are, how they are
written, and one program that reads them.**
Eunoia is the logical framework and language the [Ethos][ethos] checker reads
natively — calculi are defined in it and solver proofs are checked against those
definitions. Understanding it and authoring in it are two different jobs, and
this repository keeps a project for each.

| project | the question it asks | start at |
| --- | --- | --- |
| [**sapheneia**](tools/sapheneia/README.md) | *What is Eunoia, as a language, independently of any checker?* The language account, and the maintained definition of Eunoia semantics (`.eos`) configuration files | [the account](tools/sapheneia/docs/manual.md); [the `.eos` reference](tools/sapheneia/docs/eos.md) |
| [**mimesis**](tools/mimesis/README.md) | *How is a Eunoia signature written, and how does it stay verified?* Case studies of episodes that already happened, and tutorials for the jobs an author actually has | [choose a tutorial](tools/mimesis/README.md#tutorials) |

Beside them is [**`eo_format`**](#the-formatter), the one program in this tree:
it lays out a `.eo` or `.eos` file and is what the projects above learned the
two languages are lexed differently enough to need.

The two projects read the same manual for opposite purposes — one has to say what the
language *requires*, the other what to *type* — and each keeps a ledger of what
that cost: sapheneia's of what the manual does not settle or appears to get
wrong, mimesis's of what an author had to reconstruct and whose it is to fix.
Neither ledger has been carried anywhere, and carrying one is a person's.

## The formatter

`eo_format/eo_format.py` reads a Eunoia file and writes it out again: two-space
indentation, a line the given width, and program bodies laid out so that the
one-line cases of a group line their returns up. It takes files, writes them in
place, and follows `include` unless told not to.

```sh
python3 eo_format/eo_format.py --check path/to/Signature.eo   # would it change?
python3 eo_format/eo_format.py --diff  path/to/Signature.eo   # show what it would do
python3 eo_format/eo_format.py path/to/Signature.eo           # do it
```

**The two languages are lexed differently, and the suffix picks which.** In a
`.eo` string a doubled quote is the escape and a backslash is an ordinary
character, which is SMT-LIB 2.6 and what ethos's lexer implements. In a `.eos`
string a backslash escapes the character after it and a doubled quote is two
strings, which is what lets a `:lean-impl` body hold its own strings.
`--dialect` overrides the suffix. Whether that difference is the language or an
accident is [`docs/discussion.md`](docs/discussion.md) `D1`.

**It refuses rather than guesses.** Rewriting a file in place destroys the only
copy of anything it drops, so every result is read back and compared with the
file it came from: same code tokens, same comment words in the same order. A
mismatch is reported as the formatter's defect and nothing is written. Layout
also runs to a fixed point, so a file it has just written passes `--check`.

**What it is not.** There is no Eunoia formatter standard and this does not
propose one: the shared policy holds that `.eo` and `.eos` are laid out by hand
and that a difference in layout is not a finding, and nothing here asks anybody
to run this or reformats a file it had another reason to touch. It is not a
checker and says nothing about whether a signature is well-formed — only ethos
decides that. Its comment rules are the weakest part: a comment written after a
form that will not fit beside it is moved onto a line of its own above that
form, which is a judgement about where the comment belongs.

**Measured 2026-09-19** with `test/corpus.py` over every `.eo` and `.eos` file
in four checkouts — ethos `8d8e028`, cvc5 `dbf176d`'s `proofs/`, eudaimonia
`b465b9d`, and the two logos `c8165b2` does not vendor from ethos —
**297 files, none refused and none unsettled**. The same corpus before the same
day's fixes: two files refused outright, 26 whose comment text the formatter
dropped, one whose comments it reordered, and three that changed again on a
second run. Nothing was written to any of those trees, and logos's vendored
copy of ethos was read as well, to the same result and on the same files.

## What is here, and what is not

**One program, and the rest is documents.** This repository ships no checker, no
compiler and no signature anybody depends on. Beside the formatter it holds
documents, worked signatures and the proof files those are checked against. The
checkers, compilers and signatures it talks about — [ethos][ethos], [cvc5][cvc5],
[logos][logos] and the Eunoia compiler — live in their own repositories, are
named where they are used, and are pinned to a commit where a claim depends on
one.

**The `.eo` account is a second reading.** ethos's
[`user_manual.md`][manual] remains the authority on Eunoia itself. Where that
manual and the account here disagree either may be at fault, and the
disagreement goes into a ledger rather than into a correction of the manual.

**Sapheneia maintains the `.eos` definition.** Its
[`Eunoia semantics` reference](tools/sapheneia/docs/eos.md) is the authoritative
definition maintained here for those configuration files. It was copied from
Ethos's Eunoia compiler documentation on 2026-09-19, with its source revision
recorded. Corrections and future definition updates belong there; the compiler
implementation and individual semantics sets remain with their own projects.

**The `.eo` account does not propose language changes.** Where Eunoia is
underspecified, the work here says where and stops. Proposing the resolution is
a change to Eunoia and belongs with the language's maintainers.

**Nothing leaves by machine.** Anything this repository or a project in it
wants to say to ethos, cvc5 or logos is carried by a person, under the
receiving project's own reporting discipline, and only once somebody who can
answer the follow-up has agreed to carry it. A topic staged in
[`docs/discussion.md`](docs/discussion.md) is a draft for that person and is
not a message.

**Nothing here is a soundness claim.** Whether a calculus written in Eunoia
proves only true things is a question about that calculus. These are questions
about the language it is written in and about how one is authored.

## Running things

Most of this is read rather than run. Three things are not.

```sh
python3 test/run.py                                    # the formatter's own cases
python3 test/corpus.py path/to/ethos path/to/logos     # read a corpus, write nothing
tools/mimesis/examples/resolution/check.sh path/to/ethos
```

`test/run.py` is what runs on every push, and green means the formatter
produced every expected output in `test/eo_format/cases` and that each one kept
the tokens and comments of the file it came from. It reads nothing under
`tools/`: the projects there are islands, and a suite that opened one of their
signatures would make deleting a project change what this says. `test/corpus.py`
takes the measurement on [the formatter](#the-formatter) again, against trees
that are not in this repository and so cannot be in CI.

mimesis's worked examples carry check scripts that take the tools as arguments
rather than building them; each example's README says what its script checks and
what it does not. No project here is a build dependency: writing a Eunoia
signature, generating a checker and proving rules in Lean all happen without a
checkout of this tree.

## Documents

The projects carry their own indexes — [sapheneia's][sapheneia-docs] and
[mimesis's](tools/mimesis/README.md). This repository's own documents are this
front page and [`docs/discussion.md`](docs/discussion.md).

## The name

*εὔνοια* — goodwill, and literally "well-minded": the disposition to read
something in the best sense it will bear. The language took the word first and
this repository takes it from the language, because the language is the whole of
its subject.

The word also describes the work rather than only the subject. A second account
of somebody else's manual earns its place only if it reads the first in the best
sense it will bear, and the test of that is what happens on a disagreement: what
this tree produces is a ledger row saying where the two part, not a correction
to the document that governs.

## The ecosystem

This tree is arranged by the Eunoia ecosystem's shared policy, which
[kanon][kanon] maintains in [`docs/policy.md`][policy]: one front page, every
document indexed, each project under `tools/` an island that reads what it likes
and writes only inside itself. kanon's [`docs/glossary.md`][glossary] is the
authoritative register of the ecosystem's names, including the ones used here.

## Status

**Opened 2026-09-19**, with the two projects as its contents. Each arrived with
its own history and keeps its own status section; read those rather than this
one for what has been checked and against which commits.

**The formatter is the newest thing here and the least exercised.** Its layout
rules have been read against 297 files and its own cases, and by nobody who
writes Eunoia for a living. It has no consumer outside this tree: nothing
elsewhere runs it, no repository has been asked to, and the honest statement of
what it is for today is that it made the two languages' difference visible
enough to ask about.

**The name register is kanon's.** As of 2026-09-19 its
[glossary][glossary] entries for both projects name this repository as their
parent and give their charters here. Editing the register is kanon's and
nothing here does it.

## How this repository is maintained

This repository is part of the **Eunoia ecosystem** and follows its shared
repository policy, kept by [kanon](https://github.com/ajreynol/kanon) in
[`docs/policy.md`](https://github.com/ajreynol/kanon/blob/main/docs/policy.md).

**Human maintainers:** [the current list in policy.md](https://github.com/ajreynol/kanon/blob/main/docs/policy.md#human-maintainers).

**The checker runs here on every push**, as `anoieu / policy`. This repository
names a policy contract rather than pinning a checker commit, so what is held
still is the obligations and not the implementation: a build here can turn red
with nothing committed, and when it does, a violation already in this tree has
started being reported.

**Written by AI agents, under light human supervision.** A human directs the
work, reads what is published and decides what is filed. **What that does not
cover:** nobody vets the internal design of anything here, no claim in these
documents has been checked by somebody who writes Eunoia for a living, and
nothing said about another project's tree has been read by that project. An
agent holds no footing and makes no decision here: starting a project under
`tools/`, changing what one is chartered to do, ending one, and carrying
anything to another repository are all a person's.

[ethos]: https://github.com/cvc5/ethos
[manual]: https://github.com/cvc5/ethos/blob/main/user_manual.md
[cvc5]: https://github.com/cvc5/cvc5
[logos]: https://github.com/cvc5/logos
[kanon]: https://github.com/ajreynol/kanon
[policy]: https://github.com/ajreynol/kanon/blob/main/docs/policy.md
[glossary]: https://github.com/ajreynol/kanon/blob/main/docs/glossary.md
[sapheneia-docs]: tools/sapheneia/docs/README.md
