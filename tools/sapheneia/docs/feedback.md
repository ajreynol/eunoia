# Feedback to the ethos user manual

Candidate feedback found by writing [`manual.md`](manual.md) — a second account
of the same language — and noticing where the second reading could not recover
something from the first: a silence, an ambiguity, or a place the document does
not appear to agree with itself. Some rows below are checkable by reading the
sentence they cite; others are judgement, and those are the ones most likely to
be a defect in our reading rather than in the manual.

**Nothing here has been carried anywhere.** This is a ledger, not a report. Under
[`docs/policy.md`](../../../docs/policy.md), anything that leaves this directory does
so through the host repository's ordinary reporting discipline
(`docs/reports/reporting-workflow.md`), carried by a person who can answer the follow-up,
and only once confirmed. Rows here are *candidates* in the sense of
`docs/reports/reporting-policy.md`: a candidate is published under our own name with the evidence
they have, and explicitly unjudged.

Everything is about the **manual**, never about the language. Where a row
implies a language decision rather than a wording change, it says so and stops
there — proposing the decision is out of this project's charter.

Read against `user_manual.md` at `ethosEoc3` (`3cf1c03`). Section names are the
manual's own headings.

**Rechecked 2026-09-18 against ethos `21fc6c7d`.** Two rows are **fixed** and
six were re-read and **stand**; the remaining seven are judgement rather than
grammar and are unchanged since they were written. The `state` column below
carries the result, and what was actually looked at is in
[the recheck](#the-recheck-2026-09-18) at the bottom — **each fixed row names
the line in the current manual that fixed it**, so disagreeing costs one look.

| id | where | in one line | kind | state |
| --- | --- | --- | --- | --- |
| [EOM-01](#eom-01) | *Full syntax for Eunoia commands* | `<term>` cannot derive a literal | grammar | **fixed** `21fc6c7d` |
| [EOM-02](#eom-02) | *Full syntax for Eunoia commands* | `<datatype-dec>` cannot derive `par` | grammar | **fixed** `21fc6c7d` |
| [EOM-03](#eom-03) | *Full syntax for Eunoia commands* | `(! <term> <attr>+)` is in the grammar and nowhere in the prose | undocumented | stands `21fc6c7d` |
| [EOM-04](#eom-04) | *Overview of Eunoia's features* | `eo::define` is named once and never described | undocumented | stands `21fc6c7d` |
| [EOM-05](#eom-05) | *Command line options*, grammar | `let` appears only as something an option turns off | undocumented | unchanged |
| [EOM-06](#eom-06) | *Full syntax*, *Declaring theory signatures* | `declare-sort` is in the grammar and not in the prose | undocumented | stands `21fc6c7d` |
| [EOM-07](#eom-07) | *Declaring theory signatures* | discriminators and updaters are promised and never described | undocumented | stands `21fc6c7d` |
| [EOM-08](#eom-08) | *Computational Operators* | the strictness rule has more exceptions than it names | inconsistent | unchanged |
| [EOM-09](#eom-09) | *Computational Operators* | "value" carries two unrelated meanings | terminology | unchanged |
| [EOM-10](#eom-10) | *Arithmetic operators* | whether an operator preserves its arguments' literal category is only observable from examples | unstated rule | unchanged |
| [EOM-11](#eom-11) | *Chainable*, *Pairwise* | "neutral element" is used where "nil terminator" is meant | terminology | stands `21fc6c7d` |
| [EOM-12](#eom-12) | *Declaring Parameterized Constants*, *Proofs as terms* | `(Quote u)` and `~>` are two notations for one or two things | inconsistent | unchanged |
| [EOM-13](#eom-13) | six places | the attribute contracts use *must*, *should* and *typically* interchangeably | normative language | unchanged |
| [EOM-14](#eom-14) | *The :opaque annotation* | the rule about opaque argument order is stated as a consequence | unstated rule | unchanged |
| [EOM-15](#eom-15) | *List operators*, *Parametric Nil terminators* | `eo::nil`'s arity is given as two and used as one | inconsistent | stands `21fc6c7d` |

---

### EOM-01

**Where.** *Full syntax for Eunoia commands*.

**What.** `<term> ::= <symbol> | (<symbol> <term>+) | (! <term> <attr>+)` has no
alternative for literals, so `5`, `"abc"` and `#b010` are not derivable as
terms. `<sexpr>` has a `<literal>` alternative, and `<literal>` itself is never
defined; the six categories are defined in *Literal types* as prose.

**Why it matters.** The grammar is the only place a second implementation would
look for what to parse, and literals are the one construct the language's own
computational operators are entirely about.

**Suggested.** Add `| <literal>` to `<term>`, and a production for `<literal>`
over the six categories in *Literal types*.

### EOM-02

**Where.** *Full syntax for Eunoia commands*, versus *Parametric datatypes*.

**What.** `<datatype-dec> ::= (<cons-dec>+)` cannot derive
`(par (X) (((node …) (leaf))))`, which is the form the manual's own parametric
datatype example uses.

**Suggested.** Add the `par` alternative.

### EOM-03

**Where.** *Full syntax for Eunoia commands*.

**What.** `(! <term> <attr>+)` — SMT-LIB's annotated term — is a term
alternative in the grammar and appears nowhere else in the document. What
attributes are legal on a term, whether the annotation survives into the term,
and whether two terms differing only in annotation are equal, are all
unanswered.

**Why it matters.** Term identity is syntactic in Eunoia
(`eo::eq`, pattern matching), so whether an annotation is part of a term is a
question with observable consequences.

### EOM-04

**Where.** *Overview of Eunoia's features*: "The builtin `eo::define` binder can
be used for specifying terms that contain common subterms analogously to `let`
binders in other languages."

**What.** This is the only occurrence of `eo::define` in the manual. It is not
in the operator lists, not in the grammar, and has no example.

**Why it matters.** Sharing is the difference between a proof that checks in a
second and one that does not, at the sizes machine-generated proofs reach, so
this is likely to be load-bearing for exactly the audience the manual is for.

### EOM-05

**Where.** *Command line options of ethos* (`--no-parse-let`), and *Example:
Term evaluator*, which uses `let` in a program body.

**What.** `let` is described only by the option that disables it — "do not treat
`let` as a builtin symbol for specifying a macro" — and is used, without
comment, in one example. Its syntax, scoping and relationship to `eo::define`
are not given. The option is documented as applying to proof and reference files
only, yet the example that uses `let` is a program, which would normally live in
a signature.

### EOM-06

**Where.** `<common-command>` in the grammar.

**What.** `(declare-sort <symbol> <numeral>)` is accepted and never described.
Its SMT-LIB reading — an *n*-ary type constructor, equivalently
`(declare-const S (-> Type … Type))` — is presumably intended, but a reader has
to supply it.

### EOM-07

**Where.** *Declaring theory signatures*: "`(declare-datatype <symbol>
<datatype-dec>)` defines a datatype `<symbol>`, along with its associated
constructors, selectors, discriminators and updaters."

**What.** Constructors and selectors are described and are readable back via
`eo::dt_constructors` and `eo::dt_selectors`. Discriminators and updaters are
named here and never again: no naming convention, no types, no operator that
returns them. Signatures in the wild declare tester predicates by hand — the
manual's own datatype-splitting example declares `is` itself — which suggests
the sentence may be describing SMT-LIB rather than Eunoia.

**Suggested.** Either describe them, or drop them from the sentence and say that
a signature declares its own.

### EOM-08

**Where.** *Computational Operators*: "Apart from `eo::ite`, the evaluation of
all operators assume that their arguments are fully reduced."

**What.** Two further exceptions are documented elsewhere in the same section
and not counted here.

- `eo::requires` does not evaluate its third argument unless the check passes,
  and that argument "may be non-ground" when it is returned. It is as
  non-strict as `eo::ite`.
- `eo::is_ok` is strict but *observes* that its argument is stuck rather than
  becoming stuck — which is what the whole `eo::is_*` family is built on, since
  `eo::is_eq` is defined from it.

**Why it matters.** This sentence is the whole statement of the evaluation
order, and it is the first thing a second implementation would encode.

**Suggested.** "Apart from `eo::ite` and the third argument of `eo::requires`,
… . Note that `eo::is_ok` is strict but does not propagate failure: it reports
whether its argument reduced to a value."

### EOM-09

**Where.** *Computational Operators*, definitions paragraph.

**What.** "We say a term is a _value_ if it is ground and has no occurrences of
builtin operators or programs that failed to evaluate" — under which a declared
constant `x` and the term `(f x 5)` are values. The same section then uses
*arithmetic value*, *numeral value*, *bitwise value* and *32-bit numeral value*
to mean literals of a category, which is a different notion; the two are never
related.

**Why it matters.** Every operator's contract is written with one of these
words, and reading the wrong one gives the wrong contract. "`eo::hash` — if
`t1` is a value, this returns a numeral unique to `t1`" is true of `(f x 5)`,
which is not obvious on a first reading.

**Suggested.** Name the narrow notion something else — *literal* — or state
explicitly that *X value* for a category `X` is not an instance of *value*.

### EOM-10

**Where.** *Arithmetic operators*, and the examples following.

**What.** `(eo::add 2.0 2.5) == 4.5` — decimals in, decimal out. But
`(eo::qdiv 7.0 2.0) == 7/2` — decimals in, rational out. And
`(eo::qdiv 12 6) == 3/1` — numerals in, rational out. So some operators preserve
the literal category of their arguments and some do not, and which is which is
recoverable only by reading the example block.

**Suggested.** One sentence stating the rule per operator group, next to the
"no mixed arithmetic" rule which is stated well.

### EOM-11

**Where.** *Chainable*: "A chainable operator applied to a single argument
reduces to the neutral element of the combining operator when that operator has
a nil terminator". Same phrasing under *Pairwise*.

**What.** The behaviour is defined by the combining operator's **nil
terminator**, not by any neutral element. The manual is careful elsewhere —
under *Right/Left associative with nil terminator* — to note that the nil
terminator *ought* to be neutral and need not be, and gives
`:right-assoc-nil 1` for `+` as the counterexample. Using "neutral element" here
makes the behaviour of `(>= x)` undefined for exactly the operators that
paragraph warns about.

**Suggested.** "reduces to the nil terminator of the combining operator".

### EOM-12

**Where.** *Declaring Parameterized Constants*, note: "`(declare-parameterized-const foo ((T Type)) T)`
defines `foo` to be of 'quote arrow' type, `(~> T T)`". Versus *Proofs as
terms*, which types the same construction as `(-> (Quote u) S)`.

**What.** Two notations. Whether `~>` is a distinct type constructor or a
shorthand for `->` with a `Quote`d domain is not said, and `~>` appears nowhere
else.

**Why it matters.** This is the core of the type system: it is what makes
dependent typing, `eo::quote` programs and proof rule arguments one mechanism
rather than three.

### EOM-13

**Where.** *Right/Left associative* ("must have a type of the form"),
*Right/Left associative with nil terminator* ("must", then "typically"),
*Chainable* ("Note that the type for chainable operators is typically"),
*Pairwise* (same), *Binder* ("should accept a variable number of arguments"),
*Parameterized constants with Attributes* ("are required to have type
`(-> T T T)`").

**What.** Six statements of the same kind — a constraint relating a symbol's
type to its attribute — expressed with *must*, *typically*, *should* and *are
required to*, with no visible pattern to which is which. None is enforced at the
declaration: a `:right-assoc-nil` operator over `Bool` with an `Int` nil is
accepted, and so is a `:chainable` operator with a non-variadic combiner.
*(Both checked against a build of `ethosEoc3`; `docs/notes.md` §3.)*

**Why it matters.** A reader cannot tell which of these a conforming checker may
reject and which are advice. It is the largest single ambiguity found while
writing the second account, and it is a language question the manual could
settle by choosing its words.

**Suggested.** Use *must* for constraints a checker may reject, *should* for
advice, consistently, and say once — where the attributes are introduced — which
of them are checked today.

### EOM-14

**Where.** *The :opaque annotation*: "Opaque arguments should always be expected
before other arguments. Otherwise all applications of the given function will be
ill-typed."

**What.** The rule is given as a prediction about what happens rather than as a
constraint on declarations, so it is not clear whether a declaration with a late
opaque argument is illegal, or legal and useless. The sentence immediately
above — "Return types can never be marked `:opaque` or a type error will be
immediately reported" — is stated the other way round, as a rejection, which
makes the contrast look deliberate without saying what it means.

### EOM-15

**Where.** *List operators*, which gives `(eo::nil f T)`; *Parametric Nil
terminators*, which says `eo::nil` "accepts a type argument in addition to the
operator"; *Parameterized constants with Attributes*, which says it "optionally
accepts two arguments"; and the example `(eo::nil bvor) == (eo::nil bvor)`,
which uses the one-argument form.

**What.** Three statements of the operator's arity and one use of a form the
operator list does not list. The intended reading is presumably that the type
argument is optional and that omitting it is stuck whenever the terminator is
non-ground — but the one-argument form should appear in the operator list if it
is legal.

---

## The recheck, 2026-09-18

**Read against ethos `21fc6c7d`**, the tip of that checkout on the day, by
grepping the manual for each row's own subject. **This is a re-read of the
ledger and not a new pass over the manual**: nothing here looked for rows that
were not already written down, so *no new entry* means nobody searched, not that
there is nothing to find.

**Two are fixed, and the fix is in the grammar block both rows pointed at.**

| id | what it asked for | what `21fc6c7d` has |
| --- | --- | --- |
| `EOM-01` | `\| <literal>` on `<term>`, and a production for `<literal>` | `<term> ::= <symbol> \| <literal> \| (<symbol> <term>+) \| (! <term> <attr>+)`, and `<literal> ::= <numeral> \| <decimal> \| <rational> \| <binary> \| <hexadecimal> \| <string>` — both suggestions taken |
| `EOM-02` | the `par` alternative on `<datatype-dec>` | `<datatype-dec> ::= (<cons-dec>+) \| (par (<symbol>+) (<cons-dec>+))` |

**Neither fix was carried by this project**, which is worth saying because a
ledger that records its own suggestions being taken reads as though it caused
them. Nothing here has been sent anywhere, and the rows are recorded as fixed
because the manual now says something different, not because anybody replied.

**Six were re-read and stand**, with the current evidence beside each:

- **`EOM-03`** — `(! <term> <attr>+)` appears in the manual **once**, in the
  grammar block. No prose describes the annotation form.
- **`EOM-04`** — `eo::define` appears **once**, in *Overview of Eunoia's
  features*: named as a binder analogous to `let`, and described nowhere.
- **`EOM-06`** — `declare-sort` appears **once**, in the command grammar.
- **`EOM-07`** — discriminators and updaters are promised **once**, under
  `declare-datatype`, and appear nowhere else.
- **`EOM-11`** — *neutral element* is still used in *Chainable* and *Pairwise*,
  and **both sentences now read "the neutral element of the combining operator
  when that operator has a nil terminator"** — so the two terms now sit in one
  sentence, which sharpens the row rather than answering it.
- **`EOM-15`** — all three arity statements survive: the operator list gives
  `(eo::nil f T)`; *Parametric Nil terminators* says it "accepts a type argument
  in addition to the operator"; the later text says it "optionally accepts two
  arguments"; and the one-argument form is still used in an example,
  `(eo::nil bvor) == (eo::nil bvor)`.

**Seven were not rechecked and say `unchanged` rather than `stands`**, and the
difference is deliberate. `EOM-05`, `EOM-08`, `EOM-09`, `EOM-10`, `EOM-12`,
`EOM-13` and `EOM-14` are judgement rather than grammar — whether a rule has
unnamed exceptions, whether a word carries two meanings, whether *must* and
*typically* are being used interchangeably. **Confirming one of those means
re-reading the section and forming the same opinion twice**, which is the work
this ledger says is most likely to be a defect in our reading rather than in the
manual, and a grep cannot stand in for it. Recording them as re-confirmed on the
strength of a search would be the inflation the recheck exists to avoid.

**What this does not establish.** That the two fixed rows were the important
ones — they were the two a grammar could decide, which is not the same thing.
That the manual is now correct where these rows are silent. Or that anybody in
ethos has seen this page: they have not, and carrying it upstream is a person's
act.
