# Resolution — the tutorial's signature

The end state of [defining a calculus](../../docs/defining-a-calculus.md): a Eunoia
signature for propositional resolution, its semantics, and the proof tests the
tutorial builds one at a time.

| file | what it is |
| --- | --- |
| [`Resolution.eo`](Resolution.eo) | the signature: `or` as a clause list, two programs, one rule. **Checked** — `check.sh` runs the suite against it |
| [`Resolution-lists.eo`](Resolution-lists.eo) | the same calculus with both programs replaced by list builtins. **Checked**, on the same tests |
| [`Resolution.eos`](Resolution.eos) | the semantics. **Not compiled here** — see the tutorial's [what was checked](../../docs/defining-a-calculus.md#what-was-checked-and-what-was-not) |
| [`profile`](profile) | the calculus profile a `--spec` run records |
| `test/` | seven proofs, each with an `.expected` of `correct` or `rejected` |

```sh
./check.sh path/to/ethos
```

`ethos` checks a proof against a signature. It is not the framework's generated
checker, it does not produce the framework's four verdicts, and nothing here
establishes that these rules are sound.
