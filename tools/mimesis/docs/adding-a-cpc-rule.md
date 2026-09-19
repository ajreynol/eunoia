# Start here if you want to add a rule to Cpc.eo in cvc5

Part of the [Eunoia tutorials](tutorials.md).

Adding a CPC rule means updating **both cvc5 and Logos**. In cvc5 you describe
which proof steps the rule accepts. In Logos you regenerate that description
into Lean and prove that those accepted steps preserve truth under its
formalized SMT-LIB semantics. Then cvc5 pins the verified Logos revision.
The rule is ready when those pieces agree.

This is the contributor workflow introduced by [cvc5 PR #12891][pr]. It uses
the existing `modus_ponens` rule as a small worked model, with
[runnable proof files](../examples/cpc-rule/README.md) and an existing Lean
proof to read. Do not add a second copy of that rule; apply the same steps to
your new inference. For a new term rather than a new inference, use
[extending CPC with a new theory operator](extending-cpc-operators.md) or
[extending CPC theories](extending-cpc-theories.md); for a whole new calculus,
the separate [signature-from-scratch tutorial](defining-a-calculus.md).

**What was run:** the example proof tests against the merged PR's CPC
signature. The commands for regenerating, proving, and merging your new rule
are a source-reviewed procedure, not a completed new rule development. Exact
sources and validation are [recorded below](#sources-and-validation).

## 1. Set up the two working trees

You need a cvc5 checkout containing your signature change and a Logos checkout
for its corresponding proof. Keep the complete `proofs/eo/` subtree:
`Cpc.eo` includes other files by relative path. You do not need to build cvc5
to compile its signature into Logos.

Set these paths once, using absolute paths to your own checkouts:

```bash
CVC5=/absolute/path/to/cvc5
LOGOS=/absolute/path/to/logos

cd "$CVC5"
./contrib/get-logos-checker --version
```

That last command prints the commit in `LOGOS_VERSION`, in
`contrib/get-logos-checker`. Record it as your starting point and compare it
with the Logos branch on which you will develop. Use a development checkout
for that work: the downloaded `deps/logos-checker/` is replaced when its pin
changes.

For the proof tests, use an Ethos binary, or install one from cvc5:

```bash
cd "$CVC5"
./contrib/get-ethos-checker
ETHOS="$CVC5/deps/bin/ethos"
```

Ethos reads your edited `.eo` files directly. Logos embeds the compiled rules;
installing the currently pinned Logos binary does not teach it your new rule.
The compiler setup in step 4 needs CMake, a C++17 compiler, GMP development
headers, Python 3, tar, and wget or curl. Building the Lean proof also needs
Lake and the version in Logos's `lean-toolchain`; see [Logos installation][install].

## 2. Specify exactly what cvc5 will print

Write down the ordered premises, explicit arguments, conclusion, and every
side condition before writing the declaration. Match cvc5's proof API and
printed CPC terms, including types, list representations, and argument order.
For an internal `ProofRule`, inspect its documentation in
`include/cvc5/cvc5_proof_rule.h` and its handling in
`src/proof/eo/eo_printer.cpp`. A new C++ inference also needs its own producer
and checking support; a signature declaration alone does not make cvc5 emit it.

`Cpc.eo` is the entry point, but many rules live in included theory files.
The model here lives in `proofs/eo/cpc/rules/Booleans.eo`:

```lisp
(declare-rule modus_ponens ((F1 Bool) (F2 Bool))
    :premises (F1 (=> F1 F2))
    :conclusion F2
)
```

Read this as a checking algorithm. Match the first premise to `F1`, match the
second to `(=> F1 F2)`, and return `F2`. Reusing `F1` requires the antecedent
to be the same term. There are **no explicit arguments**: the variables are
recovered from the premises, so proof steps supply no `:args`.

For your rule, follow neighboring declarations and their documentation comments
(`rule`, `implements`, `premises`, `args`, `conclusion`). Put the declaration
in the relevant included file, or add its include to `Cpc.eo`. Use `:args` for
data the proof supplies, `:requires` for conditions the checker must enforce,
and a program when the conclusion needs computation. A condition guaranteed
by cvc5's current producer still belongs in the signature if soundness requires
it: arbitrary proof files can call the rule too.

That last distinction is the point of the [BV abstraction case study](case-study.md):
the producer enforced a bit-width restriction that the signature initially
omitted, and the Logos proof exposed the omission.

## 3. Exercise the rule before compiling it

Here is a complete refutation using the model rule:

```lisp
(declare-const p Bool)
(declare-const q Bool)
(assume @p p)
(assume @imp (=> p q))
(assume @nq (not q))
(step @q q :rule modus_ponens :premises (@p @imp))
(step @false false :rule contra :premises (@q @nq))
```

You can save those commands as a proof file and run it against the signature
you are editing. To use the optional example files kept with this tutorial,
set `MIMESIS` to their location:

```bash
MIMESIS=/absolute/path/to/eudaimonia/tools/mimesis
"$ETHOS" --include="$CVC5/proofs/eo/cpc/Cpc.eo" --require-proof-of-false \
  "$MIMESIS/examples/cpc-rule/test/modus-ponens.cpc"
```

That path is only for these examples. Your signature and Logos development
use your own files and do not depend on Mimesis.

The expected result is `correct`. The
[worked files](../examples/cpc-rule/README.md) also change one thing at a time:
the antecedent, premise order, claimed conclusion, or explicit arguments.
Each malformed application must fail **at the rule application**. An unrelated
parse error is not evidence that a side condition works.

Run all five examples with:

```bash
bash "$MIMESIS/examples/cpc-rule/check.sh" \
  "$ETHOS" "$CVC5/proofs/eo/cpc/Cpc.eo"
```

Adapt these tests to your new rule. Include boundary cases for every side
condition, especially conditions your current producer always satisfies.
Tests establish the behavior of the declaration on those inputs; the universal
soundness argument is the work in Logos.

Also produce a regression proof from your changed cvc5, with
`--proof-format-mode=cpc --proof-granularity=dsl-rewrite --dump-proofs`.
Check that it actually uses your named rule rather than `trust`, and check it
with Ethos. The dump includes an `unsat` result and outer proof-list delimiters;
give the checker the CPC commands inside those delimiters, as in the example
above. For a safe-mode feature, exercise a cvc5 build configured with
`./configure.sh safe` as well.

## 4. Regenerate Logos from the edited signature

In the Logos development checkout:

```bash
cd "$LOGOS"
install/get-eo-compiler.sh
install/install-cpc.sh --all "$CVC5/proofs/eo/cpc/Cpc.eo"
git status --short
git diff --stat
```

Use Logos's pinned compiler, installed by its own script. The Ethos binary
used for direct proof checking and the `ethos-eoc` compiler are different
tools; an arbitrary newer compiler can also change the generated output or
semantics. Compiler upgrades are separate changes to review.

`--all` regenerates both `Cpc` and `CpcMini`. A plain invocation regenerates
only `Cpc`, while Logos's regeneration CI checks both packages. The installer
also refreshes `install/defs/Cpc.cached.eo`, the flattened signature that lets
Logos reproduce the result without a cvc5 checkout. Review and commit that
snapshot along with the generated changes.

Expect three kinds of work:

| Files | What to do |
| --- | --- |
| Generated modules such as `Cpc/Logos.lean`, `Cpc/LogosTerm.lean`, `Cpc/Parser.lean`, `Cpc/Spec.lean`, and `Cpc/Proofs/RuleLemmas.lean` | Review the changes; repair their Eunoia sources and regenerate if wrong |
| A new `Cpc/Proofs/Rules/<Rule>.lean` | Replace the generated `sorry` with the rule's Lean proof |
| Existing rule proofs and handwritten support modules | Repair any proofs affected by the changed generated definitions |

Existing per-rule proof files are preserved by the installer. Consequently,
`--check` is a regeneration comparison, **not a check that those proofs still
typecheck**. Build affected proofs after regeneration, including when changing
an existing rule rather than adding one. Do not use `--rules` against the main
`Cpc` package to refresh a single proof: it selects a reduced calculus.

A rule using existing operators may need no new semantic declarations. A new
operator needs its meaning specified in `install/defs/Cpc.eos`, and possibly
an extension to the compiler's `tools/eoc/semantics/smt.eos`. Generated
`Spec.lean` and the model modules reflect those inputs; a hand edit to them
will be overwritten. See [the installer documentation][install] for this case,
and [extending CPC with a new theory operator](extending-cpc-operators.md) for
that job on its own.

## 5. Prove the generated rule obligation

Open the new rule file first. For the model rule, read the complete
[`Cpc/Proofs/Rules/Modus_ponens.lean`][mp-proof]. Its public theorem is
`cmd_step_modus_ponens_properties`. The corresponding generated definitions
are `__eo_prog_modus_ponens` and the `CRule.modus_ponens` branch of
`__eo_cmd_step_proven`.

For an ordinary step, the [checker/rule contract][contract] asks for
`StepRuleProperties`: the computed conclusion follows from the premise
evidence in a well-formed model, and the conclusion has an SMT translation.
The theorem supplies hypotheses about command translation, the premises'
translated Boolean types, and the result's Eunoia type. Rules that discharge
assumptions have a different contract; use their generated obligation and a
neighboring proof as the guide.

The `modus_ponens` proof shows how to connect those requirements to the code:

1. Analyze the command's argument and premise lists. A valid application has
   no explicit arguments and exactly two premises; other shapes get stuck.
2. Unfold the generated rule program enough to expose the implication pattern
   and the check equating its antecedent with the first premise.
3. Establish the result's translated Boolean type and truth, using the semantic
   implication-elimination lemma.
4. Assemble those facts into the generated public theorem.

For your rule, prove the obligation about the **actual generated program**.
A theorem about an idealized mathematical rule misses mistakes in the Eunoia
encoding. If the proof needs a hypothesis the signature does not check, return
to the signature, add the condition, add a negative test, and regenerate.

Build the new proof explicitly. For the worked model the command is:

```bash
cd "$LOGOS"
scripts/build.sh Cpc.Proofs.Rules.Modus_ponens
```

Replace that target with the module the installer created for your rule.
Building `logos` alone does not build every soundness proof, and Lean accepts
`sorry` during an ordinary build. Complete the proof and run proof hygiene:

```bash
bash scripts/check-proof-hygiene.sh
```

The regeneration result and an executable that prints `correct` are both
useful milestones. Neither discharges the new `sorry`.

## 6. Validate the Logos change

Run the local CI groups after setting up the compiler, so regeneration is
included:

```bash
cd "$LOGOS"
bash scripts/run-ci.sh
```

If you are following the optional worked example, check the same proof against
the newly built executable:

```bash
./.lake/build/bin/logos "$MIMESIS/examples/cpc-rule/test/modus-ponens.cpc"
```

For your change, add and run a refutation that uses your new rule and tests
that reject its invalid applications. Logos takes the proof file alone; do
not pass `Cpc.eo` to it. Check the verdict and exit status: `correct` is 0,
`incorrect` is 1, and `incomplete` is 2. Parse errors also exit 1, so inspect
the diagnostic for negative tests.

At the reviewed revision, Logos CI builds a representative subset of CPC
proofs and textually rejects proof placeholders; it does not build every rule
proof. This is why step 5 explicitly builds yours. For a regeneration that
can affect other rules, follow Logos's guidance and build the full development:

```bash
scripts/build-all-cpc-rules.sh
scripts/build.sh Cpc.ApiCorrect
```

The full rule build can take hours. Record which proof targets you built in
the Logos PR rather than treating a passing executable build or CI subset as
evidence that all rule proofs compile. Keep the cached signature, generated
modules, completed proof, and regressions together in that PR.

## 7. Land Logos, then update cvc5's pin

Prepare linked cvc5 and Logos PRs. Merge the Logos change, and wait for Logos's
workflow named `CI` to pass at the **exact commit you will pin**, normally the
resulting commit on Logos's main branch. A successful run for an earlier PR
head does not establish success for a different merge or squash commit.

In the cvc5 PR, set `LOGOS_VERSION` in `contrib/get-logos-checker` to that full
40-character commit hash. It is the single pin: `check-logos-compilation`
reads it too. Then run from cvc5:

```bash
cd "$CVC5"
./contrib/check-logos-compilation
```

| Exit | Meaning | Next step |
| --- | --- | --- |
| 0 | The CPC regeneration comparison matches the pinned Logos | Check the Logos CI result and the cvc5 PR's remaining checks |
| 1 | Compilation or setup failed | Read the error; fix the signature, environment, or compiler support as appropriate |
| 2 | The signature compiled but differs from the pinned Logos | Finish the matching Logos change and pin its tested commit |

These are the **cvc5 wrapper's** statuses. Logos's own
`install/install-cpc.sh --check` uses 1 for both a mismatch and a compile
failure.

The [cvc5 `cpc-logos` workflow][cvc-ci] requires both the regeneration match
and an already-recorded successful Logos CI run at that pin. It queries the
Logos result; it does not build Logos or run its Lean proofs itself. The
combined assurance is limited by what Logos CI actually checks, which is why
the proof-build evidence above matters. This cvc5 comparison checks `Cpc`;
Logos's own regeneration CI checks `Cpc` and `CpcMini`.

Finally, `./contrib/get-logos-checker` installs the newly pinned executable.
Use it to check the regression proof produced by your cvc5 change. Both PRs
should identify the corresponding signature and Logos revision, the new rule's
proof target, test results, and any intentional limitation of its coverage.

## If the rule cannot yet be proved in Logos

The [cvc5 documentation][cvc-doc] gives two explicit ways to proceed:

- Keep the new reasoning out of safe mode; rules outside that fragment can
  live in `proofs/eo/cpc/expert/CpcExpert.eo`. Guard the reasoning in cvc5 as
  well: moving a declaration alone does not make a feature unavailable in a
  safe build. Expert rules are outside Logos's calculus and cause parse errors.
- Keep the reasoning in safe mode, but explicitly exclude the rule from Logos's
  correctness coverage in `install/defs/Cpc.eos`, following its existing
  `(define-rule beta-reduce :exclude)` example. Regenerate, test that a proof
  using it reports `incomplete`, land that Logos change, and update the pin.

Exclusion records a limitation; it does not prove the rule. It still requires
the coordinated Logos update. Nor is it a `trust` step: safe-mode proof
completeness and Logos's semantic coverage are separate checks. An Ethos result
of `correct` need not imply that Logos reports `correct` for the same proof.

## What it cost, for the ledger

An entry for the [ledger](../README.md#the-ledger), classified the way every
entry is. What is recorded is what cost time while the tutorial was assembled,
not a defect in anybody's tree.

| what happened | whose |
| --- | --- |
| the job spans two repositories and a pin, and no one page carries it end to end: this tutorial was assembled from cvc5's `output_cpc.rst`, two contrib scripts, one workflow file and Logos's `install/README.md` | **the documentation's** — and the four specific gaps are written out in [upstream-draft.md](upstream-draft.md), as a draft for a person to take upstream |
| `install-cpc.sh --check` compares regenerated output and does **not** typecheck the proofs it preserved, so a green `--check` after a signature change says nothing about whether the rule proofs still go through | **the documentation's** — the installer says so; the cost is that a reader meets the flag at the moment they would otherwise draw the opposite conclusion |
| a plain `install-cpc.sh` regenerates `Cpc` alone, while Logos's regeneration CI checks `Cpc` and `CpcMini`: the invocation that matches CI is the flagged one | **nobody's** — regenerating less than CI checks is a defensible default, and the cost lands on whoever forgets `--all` |
| `--rules` reads as a way to refresh one proof and selects a reduced calculus instead | **the documentation's** — a flag whose name suggests a filter over the package it is run against |
| two exit vocabularies for one question: cvc5's `check-logos-compilation` distinguishes mismatch (2) from failure (1), Logos's own `--check` returns 1 for both | **nobody's** — two tools with two audiences; the cost is that a reader has to know which one they ran before reading the number |
| `ethos` and `ethos-eoc` are different programs built from one tree, and *the checker* names either — as does *the pin*, of which there are three in play | **nobody's** — one tree, several artifacts, and no spelling fixes it; the tutorial spends a paragraph on it because nothing else does |
| `correct` from Ethos need not mean `correct` from Logos | **nobody's** — it is what two checkers of different strength means, and it is the fact in this workflow most likely to be read as a contradiction |

**And what it does not measure.** Nothing was regenerated here, no Lean proof was
written, and no pin was moved: [Sources and validation](#sources-and-validation)
says exactly what was run. So the friction above is a careful reader's and a
reviewer's rather than an implementer's, and an implementer's entry — the one
that would say what proving an unfamiliar rule actually costs — is still owed.

## Sources and validation

Reviewed on 2026-09-17 against these fixed revisions:

- cvc5 PR #12891, merged as
  [`2900761a7c2e2c0e99e2cf669cffa3740ea9a138`][cvc-doc]:
  `docs/proofs/output_cpc.rst`, the two Logos contrib scripts, the
  `cpc-logos` workflow, and the CPC signature and printer sources.
- Its Logos pin,
  [`664c35d6e188a62d5b5dac8fb403d19b9e0f4baa`][logos-readme]:
  `README.md`, `install/README.md`, the installer and CI scripts, the rule
  contract, and the completed `Modus_ponens.lean` proof.

The five [example proof files](../examples/cpc-rule/README.md) were run against
that cvc5 signature with Ethos: one accepted refutation and four rule-application
errors. No new cvc5 inference was implemented, no Logos package was regenerated,
and no Lean proof, complete CI run, or pin update was performed for this tutorial.
The instructions for those steps were checked against the sources above.

For current requirements, consult [cvc5's CPC documentation][current-cvc-doc]
and [Logos's regeneration instructions][current-install].

[pr]: https://github.com/cvc5/cvc5/pull/12891
[cvc-doc]: https://github.com/cvc5/cvc5/blob/2900761a7c2e2c0e99e2cf669cffa3740ea9a138/docs/proofs/output_cpc.rst
[cvc-ci]: https://github.com/cvc5/cvc5/blob/2900761a7c2e2c0e99e2cf669cffa3740ea9a138/.github/workflows/cpc_logos.yml
[logos-readme]: https://github.com/cvc5/logos/blob/664c35d6e188a62d5b5dac8fb403d19b9e0f4baa/README.md
[install]: https://github.com/cvc5/logos/blob/664c35d6e188a62d5b5dac8fb403d19b9e0f4baa/install/README.md
[mp-proof]: https://github.com/cvc5/logos/blob/664c35d6e188a62d5b5dac8fb403d19b9e0f4baa/Cpc/Proofs/Rules/Modus_ponens.lean
[contract]: https://github.com/cvc5/logos/blob/664c35d6e188a62d5b5dac8fb403d19b9e0f4baa/Cpc/Proofs/RuleSupport/Contract.lean
[current-cvc-doc]: https://cvc5.github.io/docs-ci/docs-main/proofs/output_cpc.html
[current-install]: https://github.com/cvc5/logos/tree/main/install
