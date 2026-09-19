# Upstream draft: cvc5's CPC output documentation

**Not a correspondence channel.** A child project opens no topics and answers
none, and this file is not `docs/discussion.md` in the sense the ecosystem's
repository policy gives that name: it carries no topic, no id and no response
gate, because it is not a wire to anybody. Eudaimonia's
[`docs/discussion.md`](../../../docs/discussion.md) is the only one of those in
this tree.

A draft for a person to take upstream, if they agree with it. Nothing here is a
defect report and nothing here was sent to cvc5: the page below is accurate
about everything it says, and the remarks are about what a contributor who is
**changing** the signature, rather than consuming proofs, still has to find
elsewhere. They are the gaps that
[the CPC tutorials](tutorials.md) had to fill from sources while they were
being written, which is the only reason this file exists.

The page is **[Proof format: Cooperating Proof Calculus][page]**, with its
subsections *Checking with Logos*, *Keeping CPC and Logos in sync* and
*Changing the CPC signature*.

## What it already does

It states the format and its options, what `trust` steps mean, and what `ethos`
reports; it introduces Logos, says which fragment of CPC Logos covers and what
`incomplete` means there; and it explains the pin, the `cpc-logos` workflow, and
exactly what the two conditions together do and do not establish. The last of
those is the part hardest to reconstruct from the repository, and the page is
the only place it is written down.

## 1. "Changing the CPC signature" is about rules; a symbol is a different job

> Adding a proof rule to `proofs/eo/cpc`, or removing one, therefore requires a
> matching change to Logos: the Lean proof of that rule is written or removed
> there, and `LOGOS_VERSION` is then moved to the resulting commit […]

A contributor adding a **term** — an operator, a sort, a constant — is changing
the same directory under the same requirement, but the shape of the Logos work
is different, and nothing on the page tells them the section applies to them:

- The term needs a meaning in `install/defs/Cpc.eos`: a name, a `:term`
  translation, or a `:type` entry for a sort. No Lean proof is written for it.
- An operation the target semantics does not have needs an entry in the Eunoia
  compiler's `tools/eoc/semantics/smt.eos`, which also moves the compiler pin in
  Logos's own `install/get-eo-compiler.sh` — a second pin, in the other
  repository, that the page has no reason to mention but that this contributor
  will meet.
- Regeneration produces **no new rule file and therefore no `sorry`**. What
  breaks is an existing rule's proof: for an operator with an evaluation case,
  `evaluate`'s.

All of this is documented in Logos, in
[`install/README.md`](https://github.com/cvc5/logos/blob/main/install/README.md#the-semantics),
two links deep: the page links Logos's README, whose regeneration section is
itself rule-centric and links the installer document at the end.

**Suggested:** one sentence in *Changing the CPC signature* saying that a change
to CPC's vocabulary is also a Logos change, of a different shape, with a direct
link to that section.

## 2. What makes a feature unavailable in safe mode

> - Guard the new cvc5 reasoning that gives rise to the rule so that it is not
>   available in safe mode. Optionally, proof rules that are not yet ready to be
>   run in safe mode can be added to `CpcExpert.eo`.

The two halves of that bullet do very different work, and "Optionally" invites
the reading that moving a declaration into `expert/` *is* the guard. It is not:
where a declaration sits decides what a checker loads, and the guard is in the
solver. For finite fields it is three places — `src/options/ff_options.toml`
(`category = "expert"`), `src/smt/set_defaults.cpp`
(`SET_AND_NOTIFY(ff, ff, false, "safe options")`), and
`src/smt/illegal_checker.cpp`, where the kinds of a theory left unsupported are
rejected with `SafeLogicException`.

**Suggested:** make the guard the requirement and the expert file its
consequence, and name `set_defaults.cpp` as the place experimental theories are
switched off under safe mode.

## 3. The generated checker script includes the expert signature

`contrib/get-ethos-checker` writes `cpc_gen.sh` with both includes:

```bash
echo "(include \"$SIG_DIR/Cpc.eo\")"
echo "(include \"$SIG_DIR/expert/CpcExpert.eo\")"
```

So the workflow the page recommends — a script "for generating proofs with cvc5
and checking them with the Ethos proof checker" — cannot catch an expert symbol
in a proof that is supposed to be safe: the checker it assembles accepts those
symbols by construction. Logos's script does catch it, with the parse error the
page describes, but a contributor testing an expert feature reaches for Ethos.

**Suggested:** say which signatures the generated script loads, and that a proof
from a safe build should also be checked against `Cpc.eo` alone.

## 4. Naming the disclaimer convention would make one pointer usable

> A comprehensive list of these differences can be found in the Eunoia
> definition of CPC, as described below.

The differences are marked in the signature by a convention the page does not
name: a `; disclaimer:` comment on the declaration that departs from SMT-LIB.
`theories/Ints.eo` carries one on `int.pow2` ("This function is not in
SMT-LIB"), `theories/BitVectors.eo` one on `bvand` ("declared to be binary in
SMT-LIB. We declare it with right-assoc-nil to model cvc5's treatment of
variadic functions"), `expert/theories/FiniteFields.eo` one on its sort.

**Suggested:** name the convention. It turns "a comprehensive list" from a read
of the whole signature into one grep.

## Smaller things

- The page names `./configure.sh safe` but not `--safe-mode=safe`, which
  restricts an ordinary build at run time and is the cheaper way for a
  contributor to test that a feature is excluded.
- `contrib/check-logos-compilation` separates "does not compile" (exit 1) from
  "compiles, but the pinned checker was generated from an older signature"
  (exit 2). Its header says so; the page, where a reader arrives from a failing
  `cpc-logos` run, does not.
- Not a page matter, but adjacent: `proofs/eo/cpc/expert/CpcExpert.eo`'s header
  and `src/main/command_executor.h` both name `--safe-options`. The option is
  `--safe-mode`, per `src/options/base_options.toml`.

## What was checked

The page was read on 2026-09-18 in its `docs-main` build. Its text carries every
paragraph of `docs/proofs/output_cpc.rst` at cvc5
`2900761a7c2e2c0e99e2cf669cffa3740ea9a138`, compared word by word, so these
remarks apply to both. Every cvc5 source quoted above was read at that revision,
and the Logos and compiler sources at that revision's pins,
`664c35d6e188a62d5b5dac8fb403d19b9e0f4baa` and
`406b5499f3c83f2a114113107be251f8e58b2d85`. The suggested wording is a
suggestion only: whether any of it is worth a pull request, and in what form, is
a judgement for a person who works on that documentation.

[page]: https://cvc5.github.io/docs-ci/docs-main/proofs/output_cpc.html
