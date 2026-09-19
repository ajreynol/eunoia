# sapheneia

*σαφήνεια — clarity; the lucidity of an account. Aristotle opens his treatment
of style with it: `ὡρίσθω λέξεως ἀρετὴ σαφῆ εἶναι`, let the virtue of style be
defined as being clear (Rhetoric III.2). It is the right word because it names a
property of the **account**, not of the thing accounted for. Eunoia is not
unclear. The description of it can be clearer, and that is the whole of what
this project is for.*

A research project under [`docs/policy.md`](../../docs/policy.md). Started by a human,
read-only, advertised in ecosystem listings, and not part of what this repository
ships. Deleting this directory changes nothing anywhere else.

## The question

**What is Eunoia, as a language, independently of any checker?**

There is one description of Eunoia: `user_manual.md` in the ethos repository. It
is a good document and it is the authority. It is also, by construction, a
manual for a *program* — it opens with how to build the executable, its
normative sentences are about what Ethos does, and the boundary between *the
language requires this* and *this implementation happens to do this* is not
drawn anywhere, because a manual for one implementation has no reason to draw it.

That boundary is exactly what a second implementation, a formal semantics, or an
analyzer needs, and it is what this project tries to supply.

## Goals, in order

1. **The account.** A description of Eunoia written as a language definition:
   ethos-agnostic, with implementation behaviour quarantined and labelled rather
   than mixed in. [`docs/manual.md`](docs/manual.md).

2. **Feedback to the ethos manual.** Writing a second account of something is
   the most reliable way to find the places the first one is silent, ambiguous,
   or contradicts itself. Those go in [`docs/feedback.md`](docs/feedback.md) as a ledger,
   and are carried upstream — if at all — by a person, under the host
   repository's ordinary reporting discipline. Nothing here is filed by machine.

   **Two registers, because a silence and a disagreement are not the same
   thing.** `feedback.md` holds what the manual does not say;
   [`docs/account-vs-manual.md`](docs/account-vs-manual.md) holds what it says
   that we think is not so. The second is the shorter and heavier list, and its
   first row is a correction to this project rather than to the manual.

3. **Wishue: a formal semantics.** Judgement forms and rules for the type
   system, the desugaring, and evaluation, at the level of detail where two
   people could implement from them and agree. [`docs/semantics.md`](docs/semantics.md)
   holds what the shape would have to be and what currently blocks it. This is a
   wishue and is expected to remain one for a while.

4. **The two readings, compared.** Eunoia has a second implementation, reached
   by a different route: logos checks proofs against a Lean package that
   `ethos-eoc` compiled from the signature, so the language is read once by a
   C++ evaluator and once by a compiler, a native layer and a hand-written
   semantics set. Where the two come apart is
   [`docs/ethos-logos.md`](docs/ethos-logos.md), kept as a living register. It
   serves goal 1 the way goal 2 does — a disagreement between two
   implementations is evidence about where the language is undefined, and the
   rows that land in [`docs/manual.md`](docs/manual.md)'s unsettled chapter are the ones
   worth the most.

## What this project does not do

The boundary matters more than the goals, so it is stated first-class.

- **It does not justify any tool.** Not anoieu, not ethos, not the compiler, not
  the Lean development. If a paragraph here reads as an argument for something
  being built, it is off-charter and should be cut. The case for the ecosystem's
  arrangement is argued in `tools/ynoia/docs/why-eunoia.md`, which is a different document
  with a different audience, and this project does not participate in it.
- **It does not propose language changes.** Where the language is underspecified
  this account says so and stops. Proposing the resolution is a change to
  Eunoia, which belongs in the host repository's report to the language's
  maintainers, not in a description of the language as it stands.
- **It does not describe `.eos`.** The semantics-set language read by
  `ethos-eoc` is a second language with its own reference, and folding it in
  would double the scope before the first goal is met. Candidate for later; out
  of scope now.
- **It does not describe how to run, build, install or configure a checker.**
  Command-line options, build flags and streaming behaviour are properties of a
  program. They are cut, not relocated.
- **It is not a specification, and does not claim to be.** The ethos manual is
  the authority, in the sense that it governs and this does not — which is not
  the same as being presumed correct. This is a second account a reader may
  consult and check the first against: additive, never authoritative. Where the two disagree, either may be at fault; the disagreement goes
  to `feedback.md`, or to [`docs/account-vs-manual.md`](docs/account-vs-manual.md)
  where we think the manual asserts something that is not so, as a candidate,
  and stays unjudged until somebody who knows the language rules on it.
- **It says nothing about soundness.** Whether a calculus written in Eunoia
  proves only true things is a question about that calculus. This is a question
  about the language it is written in.

## Method, and what it inherits

The project builds on what writing an analyzer taught this repository, which is
the reason it lives here rather than in a repository of its own — a research
project that does not use the host's evidence should be its own repository.
Three inheritances, each of which must be cited where it is used:

- **Verified behaviour.** `docs/notes.md` §3 records six behaviours checked
  against a real ethos build on `ethosEoc3` — a rule concluding a non-`Bool`
  term, a dormant program case with the wrong return type, an unchecked `define`
  body, a mistyped nil terminator, a `:chainable` operator with a non-variadic
  combiner, a dead program case. Each is a place where the manual's normative
  language and the implementation's behaviour come apart, and each is a place
  this account has to say which one is the language.

- **The unsettled list.** `docs/notes.md` §4 is a list of questions where the
  current answer is "whatever the implementation does". They are reproduced in
  this account's closing chapter rather than resolved, because resolving them is
  a language change and that is out of scope.

- **The reading itself.** `docs/notes.md` §1 is the shape of `.eo` as the
  analyzer's front end had to model it, which is a second reading of the same
  manual made for a different purpose, and disagreements between it and this one
  are worth chasing.

The working rule for the account is a three-way split, applied everywhere:

| label | means |
| --- | --- |
| *(unmarked)* | the language: any conforming implementation must do this |
| **Implementation** | Ethos does this; the language does not appear to require it |
| **Unsettled** | the manual and the implementation disagree, or neither says |

Getting a sentence into the wrong bucket is the characteristic error of this
project, and the reason the buckets are visible in the text rather than in a
convention.

## Layout

[`docs/README.md`](docs/README.md) indexes this project's documents.

## Status

**First cut, drafted 2026-08-31.** Read against `user_manual.md` at
`ethosEoc3` (`3cf1c03`, the commit `scripts/deps.lock` records). Every chapter
exists; the ones on desugaring, evaluation and the type system are the ones
worth reading, and the chapters on files and on the grammar are thin. Nothing
here has been checked by anybody who knows Eunoia. The feedback ledger has
entries and none of them has been carried anywhere.

**The comparison, first cut 2026-09-17.** Twenty rows, read against ethos
`ethosEoc3` (`4d1ba77c`) and logos `main` (`be479120`). Its ethos-side claims
were run against a build; its logos-side claims were read off generated Lean and
not executed. Four of the rows are instances of questions
[`docs/manual.md`](docs/manual.md) §11 already lists as unsettled, which is the part worth
pursuing.

**The disagreements, first cut 2026-09-17.** Ten rows, one of which — that the
manual presents proof checking as type checking where it is closer to program
evaluation — is most of the page and is first of all a correction to
[`docs/manual.md`](docs/manual.md) §8, which repeated the framing without checking it.
That chapter now carries a correction note and is owed a rewrite.

## Is there a paper in this?

**Not yet.** The shape is there — what two independent descriptions of one
language disagree about, and what that says about where the language is actually
undefined — and the evidence is not. A second reading becomes a result when the
disagreements are enumerated, carried to whoever owns the first reading, and
answered; an unfiled disagreement is one project's opinion of another's prose.

**What would change it:** a counted set of divergences between the manual and
this account, with the answers that came back. The ledger is the raw material and
is currently fifteen rows that have gone nowhere.

Stated because [`../../docs/policy.md`](../../docs/policy.md) asks every child
project to say whether a paper exists for it, what the plan is, or that there is
nothing in it worth writing up. This is the second answer.
