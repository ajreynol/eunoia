# A CPC rule's proof tests

Worked files for [adding a CPC rule](../../docs/adding-a-cpc-rule.md), using the
existing `modus_ponens` rule as the model. These files read the real CPC
signature; they do not define a new calculus or add a duplicate rule.

```bash
bash tools/mimesis/examples/cpc-rule/check.sh \
  /path/to/ethos /path/to/cvc5/proofs/eo/cpc/Cpc.eo
```

| File | Expected result | What it exercises |
| --- | --- | --- |
| [`modus-ponens.cpc`](test/modus-ponens.cpc) | `correct`, exit 0 | Derive `q` from `p` and `p => q`, then contradict `not q` |
| [`wrong-antecedent.cpc`](test/wrong-antecedent.cpc) | rule-application error | The first premise must match the implication's antecedent |
| [`reversed-premises.cpc`](test/reversed-premises.cpc) | rule-application error | Premises are ordered |
| [`wrong-conclusion.cpc`](test/wrong-conclusion.cpc) | conclusion error | The claimed conclusion must equal what the rule computes |
| [`extra-argument.cpc`](test/extra-argument.cpc) | argument error | Pattern variables are not explicit proof arguments |

The negative files end at the application being tested. They are checked
without requiring a refutation, so rejection cannot be explained merely by a
missing final `false`. The script requires a nonzero status and a rule-specific
diagnostic, rather than counting any failure as a successful negative test.

Checked on 2026-09-17 with the signature at cvc5 commit
`2900761a7c2e2c0e99e2cf669cffa3740ea9a138`. All five tests passed. The local
Ethos binary used had SHA-256
`6eb2bd6bac717fea9f0902ea1d5cccfd9e0ee4732bad984fcddf3e1c4abab81c`;
it was an existing build, not a fresh build of cvc5's Ethos pin. These are
Ethos tests; no Logos regeneration or Lean build was run for this example.
See the tutorial's
[validation record](../../docs/adding-a-cpc-rule.md#sources-and-validation).
