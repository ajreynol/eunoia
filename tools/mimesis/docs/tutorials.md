# Eunoia tutorials

These tutorials offer advice and optional worked examples. Mimesis is not a
dependency of signature creation or checker development. Choose the job you
are doing:

| I want to… | Start here | What you will work on |
| --- | --- | --- |
| Add a proof rule to cvc5's CPC signature | **[Start here if you want to add a rule to Cpc.eo in cvc5](adding-a-cpc-rule.md)** | The rule's interface and tests, its generated Lean and soundness proof in Logos, and the cvc5 version pin |
| Define my own proof calculus | [Define a calculus: propositional resolution](defining-a-calculus.md) | Terms, premises, arguments, computed conclusions, side conditions, and proof tests |
| Add an operator to a theory cvc5's CPC signature already has | [Extending CPC with a new theory operator](extending-cpc-operators.md) | One declaration, the program that computes it, cvc5's printed name, and its meaning, generated checker and soundness proof in Logos |
| Add a whole theory to cvc5's CPC signature | [Extending CPC theories](extending-cpc-theories.md) | A sort, its values and operators, the main or expert decision, cvc5's proof output and safe options, and what a main theory owes Logos |

For a concrete example of why the Logos proof matters, read the
[BV abstraction case study](case-study.md): stating the obligation exposed a
missing condition in a rule that cvc5's own proof output did not exercise.

Each tutorial records what was tested and what remains a procedure for the
reader to run. cvc5's own [CPC documentation](https://cvc5.github.io/docs-ci/docs-main/proofs/output_cpc.html) is the upstream authority on
the proof format, its two checkers, and the signature-and-pin requirement; the
[Eunoia manual](https://github.com/cvc5/ethos/blob/main/user_manual.md)
is the language reference. Return to [Mimesis](../README.md) for the case studies
and the project's scope.
