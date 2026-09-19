# Eunoia

*An account of the language, independent of any checker.*

> **This is not the specification.** The specification is `user_manual.md` in the
> [ethos](https://github.com/cvc5/ethos) repository. That document governs and
> this one does not, and nothing here is offered as established fact about
> Eunoia.
>
> Where the two disagree, **either may be the one at fault.** The disagreement
> is itself the useful thing — two independent descriptions of the same language
> come apart exactly where the language is unclear — so what we do with one is
> record it in [`feedback.md`](feedback.md) as a candidate and leave it
> unjudged. What we do not do is assume it settles in either direction. See
> [`../README.md`](../README.md) for why this exists.
>
> Read against `user_manual.md` at `ethosEoc3` (`3cf1c03`).

## How to read this

Eunoia has exactly one implementation today — **Ethos**, a proof checker written
in C++ — and one description, which is that checker's manual. Nothing in the
language's design requires this, and several things in the ecosystem assume it
will not stay that way: a compiler emits Lean from Eunoia signatures, a Lean
development checks the same proofs, and a fuzzer compares two checkers against
each other on the same file. All of that needs a line between *what the language
requires* and *what one program happens to do*, and no such line is currently
drawn. Drawing it is what this document is for.

So every claim here sits in one of three buckets, and the bucket is visible:

| | |
| --- | --- |
| *(unmarked prose)* | **The language.** Any implementation must behave this way, and a program that does not is wrong |
| > **Implementation.** | **Ethos does this**, and the language does not appear to require it. A second implementation could reasonably differ. Signatures in the wild may nevertheless depend on it |
| > **Unsettled.** | **Nobody has decided.** The manual and the implementation disagree, or the manual is normative and nothing enforces it, or neither says anything at all. Listed again in [chapter 11](#11-where-the-language-is-unsettled) |

Which bucket a claim lands in is this document's own judgement, in all three
cases, and is the most likely thing here to be wrong. Where a claim rests on a
behaviour that was actually run against a checker rather than read out of a
document, it is cited as **[verified]** with a pointer to where.

Examples use SMT-LIB syntax and are written the way a signature would be. Where
an example shows what a term becomes, `⇝` is desugaring and `==` is evaluation.

---

## 1. What Eunoia is

Eunoia is a **logical framework**: a language for defining logics rather than a
logic. You write down a *signature* — the symbols of a theory, their types, the
proof rules that may be applied to them — and the language gives you a notion of
what it means for a proof in that theory to check.

It is aimed at one job in particular, which is recording and checking the proofs
that SMT solvers emit. That shows in three places:

- **The syntax is SMT-LIB version 3.0.** Not a resemblance: terms, types,
  declarations and literals are SMT-LIB's, so that the formulas in a proof can
  be written the same way they were written in the query the solver was given.
- **There are no builtin theories.** `Int`, `+`, `and`, `distinct` and the rest
  are not in the language. Every one of them is declared in a signature, which
  is what makes the framework a framework and not a solver.
- **Proofs are data.** A proof is a sequence of commands in a file, in a format
  close to Alethe's, that a checker reads once.

A Eunoia file is a sequence of **commands**. There are no expressions at the top
level, no module system beyond textual inclusion, and no separate compilation:
the state of a checker is a symbol table that commands extend, and the meaning
of a command depends on everything declared before it.

### 1.1 Three file roles

The same syntax is read in three roles, and the role is decided by *how the file
arrives*, not by anything written in it:

| role | how it arrives | what it may contain |
| --- | --- | --- |
| **signature** | named on the command line with a `.eo` extension, or pulled in by `include` | Eunoia commands |
| **proof** | named on the command line without a `.eo` extension, or streamed | Eunoia commands |
| **reference** | pulled in by `reference` | SMT-LIB 2.6 commands |

Signatures and proofs accept the same commands; the distinction between them is
that literal-normalization options apply to proofs and reference files and never
to signatures ([§3.5](#35-literal-categories)). Convention puts declarations,
programs and rules in signatures and `assume`/`step` in proofs, but the language
does not enforce it — a signature may contain a proof and a proof may declare
constants.

> **Unsettled.** A role is not a property of a file, so the same text is
> well-formed or not depending on how it was invoked. Nothing in a file records
> the role it was written for.

### 1.2 The pipeline, and why it matters

Almost every surprising behaviour in Eunoia is a *stage confusion*, so the
stages are worth having in mind before anything else. Reading a term goes
through four of them:

```
    source text
        │
        ├─ 1. parse ─────────  s-expressions
        │
        ├─ 2. desugar ───────  attribute-directed elaboration of (f t1 ... tn),
        │                      driven by how the symbol f was declared
        │
        ├─ 3. expand ────────  defined symbols replaced by their bodies
        │
        └─ 4. evaluate ──────  ground applications of eo:: operators and
                               programs reduced, eagerly and bottom-up
                                    │
                                    └─ the term

    typing happens on demand, over the term, and is a separate question
```

Three consequences, each of which accounts for a family of confusions:

**Desugaring is a property of the written symbol, not of the value it denotes.**
Stage 2 looks at the head of the application *as written in the source* and at
the attributes that symbol was declared with. If the head is a parameter that
happens to be bound to a variadic operator, or if the application is written
with the explicit application operator `_`, no desugaring happens
([§4.1](#41-what-sugar-is-and-where-it-stops)).

**Desugaring runs once, at parse time, and is not re-run.** A `define` is a
macro; its body was desugared when the `define` was parsed, and substituting it
somewhere else does not desugar it again.

**Evaluation is part of building a term, not a step you can observe.** A ground
application of a computational operator is reduced as it is constructed, so
`(eo::add 1 1)` and `2` are *the same term*, everywhere, and no context can tell
them apart. There is no unevaluated `(eo::add 1 1)` for anything to hold.

Typing is deliberately outside the pipeline. A term exists whether or not
anything has asked for its type, and in general nothing does ask until a proof
step needs it — see [chapter 8](#8-the-type-system).

---

## 2. Terms

### 2.1 One grammar, three levels

Terms, types and kinds are written in the same grammar and are the same kind of
object. `Int` is a term, and so is `Type`, and so is `(-> Int Int)`. What
distinguishes them is only what their *type* is:

```smt
5           : Int          ; a term whose type is a type
Int         : Type         ; a type, whose type is a kind
Type                       ; the kind of all types
```

The word **term** in this document means any of the three unless something says
otherwise, which follows the ethos manual's own convention.

There is no separate syntax for type application, function types, or
quantification over types. `(-> Int Int)` is an application of the constant `->`
to two arguments, `(Array Int Bool)` is an application of a declared constant
`Array`, and a polymorphic function's type parameter is an ordinary argument
whose type is `Type` ([§3.3](#33-declare-parameterized-const)).

### 2.2 Everything is unary; everything is curried

Every function in Eunoia takes exactly one argument. Multi-argument syntax is
notation:

```smt
(-> Int Int Int)     ≡  (-> Int (-> Int Int))
(f a b)              ≡  ((f a) b)  ≡  (_ (_ f a) b)
```

`->` is a right-associative binary type constructor, and `_` is the explicit
higher-order application operator. Writing `(f a b)` and writing
`(_ (_ f a) b)` produce the same term *unless* `f` has an attribute, because the
attribute is consulted only for the first form — which is the single most
important consequence of currying in this language and is treated in
[§4.1](#41-what-sugar-is-and-where-it-stops).

A consequence worth stating on its own: **partial application is always
available and never an error.** `(f a)` for a binary `f` is a term of type
`(-> Int Int)`. Combined with pattern matching this is what makes the generic
programs in [chapter 6](#6-programs) possible — the pattern `(f a)` with both
`f` and `a` parameters matches *any* application whatsoever.

### 2.3 The four kinds of atomic term

| | introduced by | notes |
| --- | --- | --- |
| **constant** | `declare-const`, `declare-parameterized-const`, `declare-datatype(s)`, `declare-sort` | globally scoped; the ordinary case |
| **parameter** | a `<typed-param>` in a `define`, `program`, `declare-rule` or `declare-parameterized-const` | scoped to that command; what patterns match against and substitutions replace |
| **variable** | `(eo::var <string> <type>)`, or a binder's variable list ([§4.9](#49-binder)) | intended for object-level bound variables |
| **literal** | written directly: `5`, `1/2`, `1.3`, `#b010`, `#xf`, `"abc"` | typed by `declare-consts` ([§3.5](#35-literal-categories)) |

The distinction that does the work is **constant versus parameter**. A parameter
is a matching hole: it is what a program case binds, what a proof rule's
substitution fills in, and what makes a term *non-ground*. Constants and
variables are not holes — nothing ever binds `x` declared by `declare-const`,
and a program pattern containing it matches only that exact constant.

Variables are identified by the pair of their name and their type: two
occurrences of `(eo::var "x" Int)` anywhere in a run are the same term. This is
what makes two separately-parsed binder terms over `x` syntactically equal.

### 2.4 Ground, value, stuck

Three words that carry the whole of the evaluation story. They are worth
learning before the operators, because the operators are all defined in terms of
them.

- A term is **ground** if it contains no parameters. `(f x 5)` is ground when
  `f` and `x` are declared constants; `(f x n)` is not, when `n` is a parameter.
- An application is **stuck** if it is an application of a computational
  operator or a program whose arguments did not meet its preconditions, so it
  reduced to itself. `(eo::add 2 1/3)` is stuck: there is no mixed arithmetic,
  so it is a perfectly good term that denotes nothing in particular.
- A term is a **value** if it is ground and contains no stuck subterms.

> **This is the language's most misleading piece of vocabulary.** "Value" here
> does *not* mean "literal". A declared constant `x` is a value. `(f x 5)` is a
> value. What "value" excludes is holes (parameters) and failures (stuck
> applications), so it means something closer to *finished*: a term nothing more
> is going to happen to. The manual does use "value" in the narrow, literal
> sense as well, in the phrases *numeral value*, *arithmetic value*, *bitwise
> value* and *32-bit numeral value*, which name literal categories and not this
> notion at all. This document keeps both usages because signatures in the wild
> are written against them, and marks the narrow ones by always naming the
> category.

The three combine into the only failure mode evaluation has: **nothing errors,
things get stuck.** An operator applied to arguments it does not handle is not a
type error and does not stop the checker. It is a term, and it propagates: any
enclosing operator sees a non-value argument and gets stuck in turn. A signature
can therefore be wrong in a way that produces no diagnostic at all, and shows up
much later as a proof step that does not check, or as a term that fails to match
a pattern. This is the single most common way to get a Eunoia signature wrong.

### 2.5 The builtin constants

The language's entire builtin vocabulary at the term level:

| | |
| --- | --- |
| `Type` | the kind of all types |
| `->` | the function type constructor, right-associative |
| `_` | higher-order function application |
| `Bool` | the Boolean type |
| `true`, `false` | its two values |

Plus two builtin declarations that behave as if a signature had made them:

```smt
(declare-consts <boolean> Bool)          ; true and false are Bool values

(declare-const eo::List Type)            ; the list used by the datatype operators
(declare-const eo::List::nil eo::List)
(declare-parameterized-const eo::List::cons ((T Type :implicit))
  (-> T eo::List eo::List) :right-assoc-nil eo::List::nil)
```

`eo::List` is heterogeneous — its `cons` takes an element of any type — and is
*not* itself a datatype in the sense of [§3.6](#36-datatypes), so the datatype
operators do not apply to it. It exists to be the return type of
`eo::dt_constructors` and `eo::dt_selectors` ([§5.6](#56-datatype-operators)).

Two further types, `Proof` and `Quote`, exist in the type system and cannot be
named in a signature. They are what proof checking is made of; see
[chapter 8](#8-the-type-system).

Everything else spelled `eo::` is an operator rather than a constant, and lives
in [chapter 5](#5-evaluation).

---

## 3. Declaring a signature

Seven commands introduce symbols. Three are SMT-LIB 3.0's; four are Eunoia's
own.

| command | introduces | from |
| --- | --- | --- |
| `declare-const <symbol> <type> <attr>*` | a constant | SMT-LIB |
| `declare-datatype`, `declare-datatypes` | a datatype and its constructors, selectors, discriminators and updaters | SMT-LIB |
| `declare-sort <symbol> <numeral>` | an *n*-ary type constructor | SMT-LIB |
| `declare-parameterized-const <symbol> (<typed-param>*) <type> <attr>*` | a constant with named, possibly implicit, possibly opaque arguments | Eunoia |
| `declare-consts <lit-category> <type>` | a type for a whole syntactic category of literals | Eunoia |
| `define <symbol> (<typed-param>*) <term> <attr>*` | a macro | Eunoia |
| `program <symbol> (<typed-param>*) :signature (<type>+) <type> …` | a program ([chapter 6](#6-programs)) | Eunoia |

`declare-rule` introduces a proof rule and is [chapter 7](#7-proof-rules-and-proofs).

### 3.1 `declare-const`

```smt
(declare-const Int Type)
(declare-const c Int)
(declare-const f (-> Int Int Int))
(declare-const g (-> Int (-> Int Int)))
```

`f` and `g` have the same type, `->` being right-associative. Types are
themselves terms, so `(declare-const Int Type)` is not a special form: it
declares a constant whose type is the kind `Type`, and thereafter `Int` may be
used wherever a type is expected. Type constructors are the same idea one level
up:

```smt
(declare-const Array (-> Type Type Type))
(declare-const a (Array Int Bool))
```

`declare-sort` is SMT-LIB's spelling for the arity-only case:
`(declare-sort S 2)` is `(declare-const S (-> Type Type Type))`.

> **Unsettled.** The manual lists `declare-sort` in the grammar and never
> describes it. The reading above is the SMT-LIB one and is almost certainly
> right, but it is inference rather than documentation.

The optional attributes are the variadic annotations, and are
[chapter 4](#4-application-sugar).

### 3.2 `define` is a macro

```smt
(define <symbol> (<typed-param>*) <term> <attr>*)
```

This is not a function definition. It binds `<symbol>` to the term, and every
later occurrence of `<symbol>` is replaced by it — hygienically, so a parameter
name in the body cannot capture anything at the use site. With an empty
parameter list it names a term; with parameters it names a lambda that is
applied at expansion time.

Because expansion happens at stage 3 of the pipeline, a defined symbol never
survives into a term. There is no `notId` in the result of parsing
`(define notId ((x Bool)) (not (id x)))` — there is only what its body expands
to, `(lambda ((x Bool)) (not x))`, and applications of it are substituted away.

**No return type is given, and by default nothing is checked.** The optional
`:type <term>` attribute is what asks for the body to be type checked against a
stated type:

```smt
(declare-const not (-> Bool Bool))
(define notTrue () (not true) :type Bool)      ; checked
(define notTrue () (not true))                 ; not checked
```

> **Implementation. [verified]** Without `:type`, an Ethos `define` body is not
> type checked at all — a body that cannot be typed is accepted silently and the
> error surfaces at some later term that happens to ask. `docs/notes.md` §3
> records the case. This is a direct consequence of typing being on demand
> ([chapter 8](#8-the-type-system)) rather than a decision about `define`, but
> the effect is that `:type` is the only thing standing between a signature and
> an unchecked term, and it is optional.

### 3.3 `declare-parameterized-const`

The general declaration form. It gives the arguments *names*, which lets later
arguments and the return type mention earlier ones — dependent types — and lets
arguments be marked.

```smt
(declare-parameterized-const <symbol> (<typed-param>*) <type> <attr>*)
```

```smt
(declare-parameterized-const eq ((T Type)) (-> T T Bool))
(define P ((x Int) (y Int)) (eq Int x y))          ; T given explicitly
```

The named arguments are called the **parameters** of the declaration, and they
are in scope for the rest of the command — including for the return type and for
the value of an attribute such as a nil terminator
([§4.10](#410-parametric-nil-terminators)).

**`:implicit`** drops an argument from the surface syntax; it is recovered by
matching against the types of the arguments that are supplied.

```smt
(declare-parameterized-const = ((T Type :implicit)) (-> T T Bool))
(define P ((x Int) (y Int)) (= x y))               ; T inferred as Int
```

An argument can be implicit when its value is determined by the type of some
later, explicit argument. If it is not — if a free parameter of the return type
occurs in no explicit argument — the constant is **ambiguous**
([§3.4](#34-ambiguous-functions)).

**`:opaque`** marks an argument as an *index* rather than a child. A function
with opaque arguments is a family of constants indexed by them:

```smt
(declare-parameterized-const @array_diff
  ((T Type :implicit) (U Type :implicit)
   (t (Array T U) :opaque) (u (Array T U) :opaque))
  T)
```

`(@array_diff A B)` is an atomic term of type `T` — not an application, and in
particular **not a function application for the purposes of pattern matching**.
A generic traversal written against the pattern `(f a)` will not descend into
it, and a substitution will not rewrite inside it. That is the whole point:
opaque arguments are how you introduce a symbol that is *about* some terms
without being *built from* them, which is what purification and Skolem symbols
need. [§6.2](#62-patterns) has the matching consequences.

Opaque arguments must come before ordinary ones, and the return type may not be
marked opaque.

> **Unsettled.** "Opaque arguments should always be expected before other
> arguments. Otherwise all applications of the given function will be ill-typed."
> The manual states the consequence rather than the rule, so it is not clear
> whether a declaration with a late opaque argument is *illegal* or merely
> *useless*. An implementation could reject it; the current one does not.

### 3.4 Ambiguous functions

If a free parameter of the return type occurs in no explicit argument, nothing
in an application determines it, and the constant is **ambiguous**. Every use
must be annotated with SMT-LIB's `as`:

```smt
(declare-const Set (-> Type Type))
(declare-parameterized-const set.empty ((T Type :implicit)) (Set T))

(define f () (as set.empty (Set Int)) :type (Set Int))
```

The annotation is not a coercion and not a hint: it is *the argument*. An
ambiguous constant's type is extended with a leading opaque argument carrying
the return type, and `(as c T)` is the application of `c` to `T`. So
`(as set.empty (Set Int))` is an atomic, opaque-indexed constant, exactly like
`@array_diff` above.

The same treatment applies to datatype constructors whose return type has a
parameter that appears in no field ([§3.6](#36-datatypes)).

### 3.5 Literal categories

Literals are not builtin. A signature says what a whole syntactic category of
them means:

```smt
(declare-const Int Type)
(declare-consts <numeral> Int)      ; 0, 1, -7, … are terms of type Int
```

The six categories, with their surface syntax:

| category | syntax | examples |
| --- | --- | --- |
| `<numeral>` | `-?<digit>+` | `0`, `42`, `-7` |
| `<decimal>` | `-?<digit>+.<digit>+` | `1.5`, `-10.25` |
| `<rational>` | `-?<digit>+/<digit>+` | `1/2`, `-1/3` |
| `<binary>` | `#b<0\|1>+` | `#b0`, `#b1010` |
| `<hexadecimal>` | `#x<hex-digit>+` | `#xf`, `#x1A` |
| `<string>` | `"<char>*"` | `"abc"`, `""` |

Two things follow that catch people out.

**Negative literals are literals.** `-1` is a numeral, not an application of a
`-` symbol, and `1/2` is a rational literal rather than a division. Both differ
from SMT-LIB 2.

**Literals are normalized within their category, always.** `2/4` and `1/2` are
the same term; `1.300` and `1.3` are the same term. This is not optional and not
a checker setting.

**A literal's category is fixed at parse time and is independent of its type.**
`#b1010` is a binary literal whether or not any `declare-consts <binary>` has
been seen; what `declare-consts` supplies is the type rule. The computational
operators dispatch on the *category*, never on the type, which is why the
arithmetic operators in [§5.4](#54-arithmetic-boolean-string-and-conversion)
behave the same in every signature.

**Type rules that depend on the literal.** For categories whose type varies with
the content — bitvectors being the motivating case — `declare-consts` may use
the distinguished parameter `eo::self`, which stands for the literal being
typed:

```smt
(declare-const BitVec (-> Int Type))
(declare-consts <binary> (BitVec (eo::len eo::self)))

(define x () #b000 :type (BitVec 3))
```

Typing `#b000` substitutes it for `eo::self`, giving `(BitVec (eo::len #b000))`,
which evaluates to `(BitVec 3)`.

**Cross-category normalization is a parser option, and applies to proofs only.**
In proof and reference files, decimals are read as rationals and hexadecimals as
binaries by default, and numerals can optionally be read as rationals. In
signature files none of this happens. So in a signature `#xf` and `#b1111` are
different terms of different categories, and `(eo::add #x1 #b0001)` is stuck.

> **Unsettled.** The same text therefore denotes different terms depending on
> which role the file was given ([§1.1](#11-three-file-roles)). This is
> deliberate — a signature must be able to talk about hexadecimal literals as
> such — but it means literal identity is not a property of the language alone.

### 3.6 Datatypes

```smt
(declare-datatypes ((Tree 0)) (((node (left Tree) (right Tree)) (leaf))))
```

declares the type `Tree` with constructors `node` and `leaf`, selectors `left`
and `right`, and — per the manual's summary of the command — discriminators and
updaters. Parametric datatypes use SMT-LIB 2.6's `par`:

```smt
(declare-datatypes ((Tree 1))
  ((par (X) (((node (left Tree) (data X) (right Tree)) (leaf))))))
```

A constructor is **ambiguous** when a free parameter of its return type occurs
in none of its fields — `leaf` above, which is a `(Tree X)` for every `X`. As
with ambiguous functions ([§3.4](#34-ambiguous-functions)) every use must be
written `(as leaf (Tree Int))`, and the result is an opaque-indexed atomic
constant.

What datatypes buy over ordinary declarations is that their structure can be
*read back* by the operators in [§5.6](#56-datatype-operators), which is what
makes a proof rule that splits on constructors writable once for all datatypes
rather than once per datatype.

> **Unsettled.** The manual says the command defines "constructors, selectors,
> discriminators and updaters" and then documents only constructors and
> selectors. How a discriminator or updater is named, what its type is, and
> whether `eo::dt_selectors` relates to it are not stated anywhere. Signatures
> in the wild declare their own tester predicates by hand, which suggests the
> sentence may be aspirational.

> **Unsettled.** `par` does not appear in the grammar in the manual's appendix,
> which gives `<datatype-dec> ::= (<cons-dec>+)` and so cannot derive the
> parametric form the manual's own example uses.

### 3.7 Overloading

A symbol may be declared more than once. The declarations coexist; an
application selects among them.

```smt
(declare-const - (-> Int Int Int))       ; binary subtraction, declared first
(declare-const - (-> Int Int))           ; unary negation, declared second
```

The rule is **most recently declared that types**: given an application, the
latest declaration under which the term is well-typed wins. An *unapplied*
occurrence of an overloaded symbol resolves to the most recent declaration
outright. Hence the ordering convention above — declaring subtraction first
means `(- t)` still reaches unary negation, whereas the opposite order would
make `(- t)` a partial application of subtraction and never an error.

No warning is issued when several declarations would fit. Selection is silent
and order-dependent, and the order is the order of the declarations in the file.

`eo::as` forces the choice:

```smt
(eo::as - (-> Int Int Int))              ; the binary one
```

`(eo::as t (-> T1 … Tn T))` evaluates to the atomic term `s` sharing `t`'s name
for which `(s k1 … kn)` has type `T`, with `ki` fresh of type `Ti`; the most
recent such `s` if several, and stuck if none. Note that this is a *computational
operator* and takes a full function type, which is not the same thing as
SMT-LIB's `as` in [§3.4](#34-ambiguous-functions) — `as` supplies an argument,
`eo::as` picks a declaration.

### 3.8 The remaining commands

| | |
| --- | --- |
| `(include <string>)` | read that file as a signature, path relative to the including file |
| `(reference <string> <term>?)` | read that file as a reference input; [chapter 9](#9-files) |
| `(set-option <attr>)` | set a parser option from within a file |
| `(echo <string>?)` | print |
| `(reset)` | discard all declarations and definitions |
| `(exit)` | stop |

---

## 4. Application sugar

A declaration may carry one attribute that changes how *applications of that
symbol written in the source* are read. This is where most of Eunoia's
expressiveness for SMT-LIB lives — it is how `(or a b c d)` becomes a
right-nested binary term, how `(>= x y z)` becomes a conjunction of two
comparisons, and how `(forall ((x Int)) …)` becomes an ordinary application.

It is also where most of the language's characteristic bugs live, for one
reason: the sugar is a **parse-time rewrite keyed on a written symbol**, and
every mistake is a case of it applying when it was not expected to, or not
applying when it was.

### 4.1 What sugar is, and where it stops

Desugaring happens at stage 2 of the pipeline ([§1.2](#12-the-pipeline-and-why-it-matters)):
the parser sees `(f t1 … tn)`, looks up how the symbol `f` was declared, and if
`f` carries an attribute, rewrites the application accordingly. Four
consequences, and every one of them has bitten somebody:

**Only the written head counts.** If `f` is a parameter that happens to be bound
to a variadic operator, `(f a b)` is an ordinary application. There is no
"variadic value" — variadicity is a property of a declaration, not of a term.

**`_` opts out.** `(_ or a b)` is the ordinary curried application
`(_ (_ or a) b)`. It is not an `or`-list of any kind, and no nil is inserted.

**Macro expansion does not re-desugar.** A `define`'s body was desugared when it
was parsed. Substituting it elsewhere inserts the already-desugared term.

```smt
(declare-const or (-> Bool Bool Bool) :right-assoc-nil false)
(define apply-f-to-ab ((f (-> Bool Bool Bool))) (f a b))

(apply-f-to-ab or)   ⇝  (_ (_ or a) b)              ; head was a parameter
(or a b)             ⇝  (_ (_ or a) (_ (_ or b) false))
(_ or a b)           ⇝  (_ (_ or a) b)              ; explicit application
```

**At most one attribute.** A symbol carrying two of the attributes below is an
error at the declaration.

### 4.2 Associativity without a nil

```smt
(declare-const or (-> Bool Bool Bool) :right-assoc)
(declare-const and (-> Bool Bool Bool) :left-assoc)
```

For `n ≥ 3`, the application is re-nested; for `n ≤ 2` the attribute does
nothing at all.

```
(or x y z)   ⇝  (or x (or y z))
(and x y z)  ⇝  (and (and x y) z)
(or x y)     ⇝  (or x y)
(or x)       ⇝  (or x)        ; a partial application, of type (-> Bool Bool)
```

The resulting terms are **ambiguous**: `(or x (or y z))` and `(or x y z)` are the
same term, so nothing downstream can tell a two-element list from a nested
application. This is why the nil-terminated variants exist, and why real
signatures use them.

### 4.3 Associativity with a nil terminator

```smt
(declare-const or (-> Bool Bool Bool) :right-assoc-nil false)
```

Now every application, down to one argument, is closed off with the terminator:

```
(or x y z)  ⇝  (or x (or y (or z false)))
(or x y)    ⇝  (or x (or y false))
(or x)      ⇝  (or x false)
```

and left-associative is the mirror image, with the nil at the far left:
`(or x y z) ⇝ (or (or (or false x) y) z)`.

The terms are now unambiguous: an `or`-list of *k* elements has a shape no
other list has, and `(or x (or y z))` written by hand differs from `(or x y z)`
because the inner one gets its own nil.

This is what makes the list operators of [§5.5](#55-list-operators) meaningful.
Define: a term is an **`f`-list with children `t1 … tn`** if it is `(f t1 … tn)`
for `n > 0`, or `nil` for `n = 0`. Every list operator is defined on `f`-lists
and stuck on anything else.

> The nil terminator ought to be an identity element of the operator, and
> nothing requires it. `(declare-const + (-> Int Int Int) :right-assoc-nil 1)`
> is accepted, and makes `(+ x y z)` and `(+ x (+ y z))` denote arithmetically
> different terms. This is a modelling error rather than a language violation,
> but it is invisible.

A nil terminator may be any term of the right type, including one built from
symbols declared earlier:

```smt
(declare-const re.all RegLan)
(declare-const re.inter (-> RegLan RegLan RegLan) :right-assoc-nil re.all)
```

It may *not* mention the type parameters of the operator — with `declare-const`,
because `declare-const` has no parameters to mention. That restriction is what
`declare-parameterized-const` lifts; see
[§4.10](#410-parametric-nil-terminators).

### 4.4 `:list` — a parameter that is a tail

The one attribute that goes on a *parameter* rather than a declaration. It says:
where this parameter appears as an argument of a nil-terminated associative
operator, it stands for the **tail** of the list, not for an element of it.

```smt
(declare-const or (-> Bool Bool Bool) :right-assoc-nil false)
(define P ((x Bool) (y Bool))       (or x y))    ; ⇝ (or x (or y false))
(define Q ((x Bool) (y Bool :list)) (or x y))    ; ⇝ (or x y)
```

`P` builds a two-element list. `Q` conses `x` onto whatever list `y` is. Applied
to the same arguments `a` and `(or a b)`:

```
(P a (or a b))   ≡  (or a (or a b))     ; two elements, the second a nested list
(Q a (or a b))   ≡  (or a a b)          ; three elements
```

This is the mechanism that makes it possible to write a program case that
matches a list of *any* length ([chapter 6](#6-programs)), and forgetting the
annotation is the most common program bug in the language: `((contains (or l xs) l) true)`
with an unmarked `xs` matches `or`-terms of exactly two children and silently
fails on everything longer.

### 4.5 The desugaring algorithm

Stated once, for right-associative `f` with nil terminator `nil`. Left-associative
is the mirror image throughout.

To desugar `(f t1 … tn)`:

1. Let `N` be the nil term: `nil` itself when `nil` is ground, and
   `(eo::nil f (eo::typeof t1))` when it is not
   ([§4.10](#410-parametric-nil-terminators)).
2. If `tn` is marked `:list`, set `r := tn` and let `i` run from `n-1` down to 1.
   Otherwise set `r := N` and let `i` run from `n` down to 1.
3. For each `i`: `r := (f ti r)` if `ti` is not marked `:list`, and
   `r := (eo::list_concat f ti r)` if it is.
4. The result is `r`.

Worked, with `z` and `w` marked `:list` and `x`, `y` not:

```
(or x y)      ⇝  (or x (or y false))
(or x z)      ⇝  (or x z)
(or x z y)    ⇝  (or x (eo::list_concat or z (or y false)))
(or x)        ⇝  (or x false)
(or z)        ⇝  z
(or z y w x)  ⇝  (eo::list_concat or z (or y (eo::list_concat or w (or x false))))
```

`(or z)` is worth staring at: a single `:list` argument desugars to *itself*, no
application of `or` is built at all. And `(or x z y)` produces an
`eo::list_concat`, which is a computational operator, which means the result is
not a legal pattern — see [§6.2](#62-patterns).

### 4.6 `:right-assoc-non-singleton-nil`

Identical to the nil-terminated form except that a one-element list collapses to
its element.

```smt
(declare-const or (-> Bool Bool Bool) :right-assoc-non-singleton-nil false)
```

Formally: desugar as in [§4.5](#45-the-desugaring-algorithm) to get `t`; if at
least two of `t1 … tn` are unmarked, return `t`; otherwise return
`(eo::list_singleton_elim f t)`.

```smt
(define or_3 ((x Bool :list) (y Bool) (z Bool :list)) (or x y z))
  ⇝ (eo::list_singleton_elim or (eo::list_concat or x (or y z)))

(or_3 (or a b) a false)  ≡  (or a (or b (or a false)))    ; three elements
(or_3 false a false)     ≡  a                             ; collapsed
```

The collapse is a *desugaring* behaviour only. It does not change what the list
operators do at run time: `(eo::list_repeat or a 1)` still returns a
one-element `or`-list even for a non-singleton-nil operator.

### 4.7 `:chainable` and `:pairwise`

Both take a combining operator and both fold a relation over several arguments.

```smt
(declare-const and (-> Bool Bool Bool) :right-assoc-nil true)
(declare-const >= (-> Int Int Bool) :chainable and)
(declare-parameterized-const distinct ((T Type :implicit)) (-> T T Bool) :pairwise and)
```

```
(>= x y z)        ⇝  (and (>= x y) (>= y z))              ; adjacent pairs
(distinct x y z)  ⇝  (and (distinct x y) (distinct x z) (distinct y z))
```

For `n ≤ 2` neither attribute does anything. For `n = 1` both reduce to the
combining operator's nil terminator — `(>= x)` is `true` above — and are a parse
error if the combiner has no nil.

`:pairwise` produces quadratically many terms, which is what `:arg-list` exists
to avoid.

### 4.8 `:arg-list`

Instead of folding, collect the arguments into a single list and hand it over:

```smt
(declare-parameterized-const @cons ((T Type :implicit)) (-> T @List @List)
  :right-assoc-nil @nil)
(declare-parameterized-const distinct ((xs @List)) Bool :arg-list @cons)
```

```
(distinct x y z)  ⇝  (distinct (@cons x y z))
                  ⇝  (distinct (@cons x (@cons y (@cons z @nil))))
```

The annotated symbol is unary: it takes the list. One exception, so that
already-built lists can be passed through: if there is exactly one argument and
it is marked `:list`, it is handed over as-is rather than wrapped.

```smt
(define distinct-of  ((xs @List :list))               (distinct xs))
  ⇝ (distinct xs)                                     ; not (distinct (@cons xs))
(define distinct-of2 ((T Type :implicit) (x T) (xs @List :list)) (distinct x xs))
  ⇝ (distinct (@cons x xs))
```

### 4.9 `:binder`

Lets a symbol accept SMT-LIB's variable-list syntax as its first argument.

```smt
(declare-const forall (-> @List Bool Bool) :binder @cons)

(forall ((x Int)) (P x))   ⇝  (forall (@cons x) (P x))   where x ≡ (eo::var "x" Int)
```

The variable list is turned into an application of the named constructor, and
the symbols in it are bound — as variables, not parameters — while the remaining
arguments are parsed. The constructor should be variadic, since it is applied to
however many variables were written.

Because a variable is identified by its name and type ([§2.3](#23-the-four-kinds-of-atomic-term)),
`(forall ((x Int)) (P x))` written twice gives the same term, and writing
`(forall (@cons x) (P x))` by hand with `x` defined as `(eo::var "x" Int)` gives
that same term again. There is no α-renaming and no scope-sensitive identity:
binding is a matter of which constructor was applied, and the language does not
distinguish a bound occurrence from a free one.

> **Unsettled.** Nothing in the language relates a binder's variable list to the
> variables occurring in its body. `(forall (@cons x) (P y))` is an ordinary
> well-typed term. Capture, shadowing and freshness are entirely the signature
> author's problem, and no operator reports on them.

### 4.10 Parametric nil terminators

`declare-parameterized-const` has parameters in scope for the whole command, so
the nil terminator may depend on them:

```smt
(define bvzero ((m Int)) (eo::to_bin m 0))
(declare-parameterized-const bvor ((m Int :implicit))
  (-> (BitVec m) (BitVec m) (BitVec m))
  :right-assoc-nil (bvzero m))
```

An operator whose nil is non-ground must have type `(-> T T T)`, so that the
first argument alone determines the parameters. Desugaring then inserts the
*placeholder* `(eo::nil f (eo::typeof t1))` in place of the nil, which reduces
to the real terminator once the type is ground:

```
(bvor x y)   ⇝  (bvor x (bvor y (eo::nil bvor (eo::typeof x))))
             ==  (bvor x (bvor y #b0000))         ; x : (BitVec 4)
(bvor z w)   ⇝  (bvor z (bvor w (eo::nil bvor (eo::typeof z))))
             ==  itself                            ; z : (BitVec n), n a parameter
```

`eo::nil` therefore takes the operator and, optionally, the type it is wanted
at: `(eo::nil bvor (BitVec 4))` is `#b0000`, `(eo::nil bvor (BitVec 5))` is
`#b00000`, and `(eo::nil bvor)` is stuck because nothing determines which.

Conceptually `eo::nil` is a program with one case per nil-terminated declaration
in the signature, `(($eo_nil f T) nil)`, matching on both the operator and the
type. That is exactly how the manual's appendix says to reconstruct it in pure
Eunoia, and it is the reason the type argument exists.

When the nil is ground, none of this machinery appears: the terminator is
substituted directly at desugaring time.

### 4.11 The declaration contracts

Each attribute constrains the type of the symbol it is on. Collected, because
they are stated in six different places in the manual and enforced in none:

| attribute | required shape | and |
| --- | --- | --- |
| `:right-assoc` | `(-> T1 T2 T2)` | |
| `:left-assoc` | `(-> T1 T2 T1)` | |
| `:right-assoc-nil n` | `(-> T1 T2 T2)` | `n : T2` |
| `:left-assoc-nil n` | `(-> T1 T2 T1)` | `n : T1` |
| `:right-assoc-nil n`, `n` non-ground | `(-> T T T)` | |
| `:chainable c` | `(-> T T S)` | `c : (-> S S S)`, and `c` variadic |
| `:pairwise c` | `(-> T T S)` | `c : (-> S S S)`, and `c` variadic |
| `:arg-list c` | unary, taking `c`'s list type | `c` variadic |
| `:binder c` | first argument `c`'s list type | `c` variadic |

> **Implementation. [verified]** None of these is checked at the declaration.
> A `:right-assoc-nil` operator over `Bool` with an `Int` nil is accepted, and
> so is a `:chainable` operator whose combiner is a plain binary function. The
> error appears later — at the first application whose type is asked for, or,
> for the chainable case, only at four or more arguments — or does not appear at
> all if no proof exercises the operator. `docs/notes.md` §3 records both cases
> against a real build.

> **Unsettled.** The manual writes these with a mixture of *must*, *should* and
> *typically*, and one implementation enforces none of them. Either they are
> requirements on a well-formed signature, in which case a conforming checker
> may reject a signature that violates them, or they are advice, in which case
> the desugaring of a violating declaration needs a definition and does not have
> one. Both readings are defensible; only one can be the language.

---

## 5. Evaluation

Eunoia has a built-in evaluator over literals, terms and lists, spelled with the
reserved prefix `eo::`. It is what lets a signature *compute* — bitwidths in a
type rule, the side conditions of a proof rule, the normal form of a formula —
without any of that computation having to be proved.

### 5.1 One discipline, stated once

Every operator in this chapter obeys the same rule, and it is not the rule most
languages use:

> **An operator applied to arguments it does not handle reduces to itself.**

There is no error, no exception, no failure value. `(eo::add 2 1/3)` — mixed
categories — is a term. `(eo::to_str -1)` — not a code point — is a term. Such a
term is **stuck** ([§2.4](#24-ground-value-stuck)), and stuckness propagates:
an enclosing operator sees an argument that is not a value and gets stuck in
turn.

So the whole of this chapter can be read as: *here are the cases in which each
operator does something; in every other case it does nothing.* The per-operator
tables below therefore list only the cases that reduce.

Two further facts complete the picture:

**Evaluation is eager, and part of building the term.** A ground application of
a computational operator is reduced as it is constructed. `(eo::add 1 1)` and
`2` are the same term in every context; there is no way to hold the unevaluated
one.

**Evaluation is bottom-up.** Arguments are evaluated before the operator is
applied, with the exceptions in [§5.2](#52-strictness-and-its-three-exceptions).
This includes positions a lazy language would skip: in `(eo::or A B)` both `A`
and `B` are evaluated even when `A` is `true`.

### 5.2 Strictness, and its three exceptions

| operator | evaluated eagerly | held back |
| --- | --- | --- |
| `(eo::ite c a b)` | `c` | `a` and `b`, until the branch is selected |
| `(eo::requires a b c)` | `a`, `b` | `c`, until the check has passed |
| `(eo::is_ok t)` | `t` | nothing — but it does not inherit `t`'s failure |

`eo::ite` and `eo::requires` are genuinely lazy in the held-back positions, and
this is load-bearing: it is what lets a recursive program have a base case, and
what lets a proof rule's requirement guard a conclusion that would otherwise not
be well formed. Note also that both may *return a non-value*: `eo::requires`
explicitly may return a non-ground `t3`, and `(eo::ite true Bool Int)` returns a
type.

`eo::is_ok` is different and is the reason the manual's "apart from `eo::ite`"
is not the whole story. It is strict, but it is the one operator that can
*observe* that its argument got stuck rather than getting stuck itself — which
is what makes stuckness testable from inside the language at all, and hence what
`eo::is_eq` and the whole `eo::is_*` family are built from.

### 5.3 Core operators

| | reduces when | to |
| --- | --- | --- |
| `(eo::is_ok t)` | `t` ground | `true` if `t` is a value, else `false` |
| `(eo::ite c a b)` | `c` is `true` / `false` | `a` / `b` |
| `(eo::eq t1 t2)` | both ground values | `true` if syntactically identical, else `false` |
| `(eo::is_eq t1 t2)` | always, if ground | as `eo::eq`, but `false` when either is stuck |
| `(eo::requires t1 t2 t3)` | `(eo::is_eq t1 t2)` is `true` | `t3` |
| `(eo::hash t)` | `t` a value | a numeral unique to `t` |
| `(eo::typeof t)` | `t` a value with ground type | its type |
| `(eo::nameof t)` | `t` a variable | its name, as a string |
| `(eo::cmp t1 t2)` | both values | `(eo::gt (eo::hash t1) (eo::hash t2))` |
| `(eo::as t T)` | see [§3.7](#37-overloading) | the selected declaration |
| `(eo::var s T)` | — | *not* an operator: an ordinary term, the variable named `s` of type `T` |

**`eo::eq` and `eo::is_eq` are syntactic.** `(eo::eq x y)` for distinct declared
constants is `false` — a statement about the two terms, not about whether some
model could equate them. This is the single most important thing to keep
straight when writing side conditions: the evaluator has no notion of semantic
equality and never will.

The difference between them is only stuckness: on a stuck argument `eo::eq` gets
stuck and `eo::is_eq` answers `false`. Use `eo::is_eq` when a `false` is wanted
for "this did not compute", and `eo::eq` when it is not.

```smt
(eo::eq x x)                         == true
(eo::eq 2 (eo::add 1 1))             == true
(eo::eq (eo::neg "a") x)             == (eo::eq (eo::neg "a") x)   ; stuck
(eo::is_eq (eo::neg "a") x)          == false
(eo::requires x x Int)               == Int
(eo::requires x 0 true)              == itself                     ; guard failed
```

> **Implementation.** `eo::hash` assigns numerals to values, and the only stated
> property is that the assignment is injective. Nothing says it is stable across
> runs, across checkers, or across the order in which terms were built. Since
> `eo::cmp` is defined from it, the total order on terms it induces is equally
> unspecified, and any signature that depends on a *particular* order is
> depending on an implementation. The Lean development declines to model
> `eo::hash` for exactly this reason.

The derived predicates, all definable in terms of the above:

| | equivalent to |
| --- | --- |
| `(eo::is_z t)` | `(eo::is_eq (eo::to_z t) t)` |
| `(eo::is_q t)` | `(eo::is_eq (eo::to_q t) t)` — `false` for decimals |
| `(eo::is_bin t)` | `(eo::is_eq (eo::to_bin (eo::len t) t) t)` — `false` for hexadecimals |
| `(eo::is_str t)` | `(eo::is_eq (eo::to_str t) t)` |
| `(eo::is_bool t)` | `(eo::or (eo::is_eq t true) (eo::is_eq t false))` |
| `(eo::is_var t)` | `(eo::is_eq (eo::var (eo::nameof t) (eo::typeof t)) t)` |

### 5.4 Arithmetic, Boolean, string and conversion

These dispatch on the **literal category** of their arguments
([§3.5](#35-literal-categories)), never on their declared type. Two groupings
recur:

- an **arithmetic value** is a numeral, decimal or rational literal;
- a **bitwise value** is a binary or hexadecimal literal.

and the governing rule is that **there is no mixed arithmetic**: both arguments
must be of the *same* category, and for bitwise values of the same bitwidth.
`(eo::add 2 1/3)` is stuck; `(eo::add 2/1 1/3)` is `7/3`. Binary values are
little-endian, and bitwise arithmetic is modulo the width.

| | on arithmetic values | on bitwise values | on strings |
| --- | --- | --- | --- |
| `eo::add`, `eo::mul` | same category | same width, modular | — |
| `eo::neg` | arithmetic negation | signed negation | — |
| `eo::pow t1 t2` | `t2` a non-negative 32-bit numeral | — | — |
| `eo::log t1 t2` | `t1` numeral: `⌊log_t1 t2⌋`, clamped at 0 | — | — |
| `eo::qdiv` | rational division, `t2 ≠ 0` | — | — |
| `eo::zdiv`, `eo::zmod` | numerals, `t2 ≠ 0` | total: `/0` gives max, `mod 0` gives `t1` | — |
| `eo::is_neg` | `true` iff strictly negative | — | — |
| `eo::gt` | `(eo::is_neg (eo::add (eo::neg t1) t2))` | compares as unsigned numerals | — |
| `eo::and`, `eo::or`, `eo::xor`, `eo::not` | on `true`/`false` | bitwise, same width | — |
| `eo::len` | — | bitwidth | length |
| `eo::concat` | — | bit concatenation | string concatenation |
| `eo::extract t i j` | — | bits `i..j`, empty if `i < 0` | characters `i..j` inclusive, empty if `i < 0` |
| `eo::find t1 t2` | — | — | least index of `t2` in `t1`, or `-1` |

Conversions:

| | |
| --- | --- |
| `(eo::to_z t)` | numeral → itself; rational → floor; binary → its value; length-one string → code point |
| `(eo::to_q t)` | rational → itself; numeral → the integral rational |
| `(eo::to_bin w t)` | `w` a 32-bit numeral; `t` binary or non-negative numeral → width-`w` binary, modulo `2^w` |
| `(eo::to_str t)` | string → itself; numeral in `0…196607` → the one-character string |

`eo::and`, `eo::or`, `eo::xor`, `eo::add`, `eo::mul` and `eo::concat` accept any
number of arguments `≥ 2`.

Sanity checks worth internalizing, all of which are stuck:

```smt
(eo::add 2 1/3)          ; different categories
(eo::add 2.0 1/3)        ; likewise: decimal is not rational, before normalization
(eo::add #x1 #b0001)     ; likewise: hexadecimal is not binary
(eo::qdiv 7 0)           ; division by zero
(eo::pow 2 -1)           ; negative exponent
(eo::to_z "451")         ; string is not length one
(eo::to_str -1)          ; not a code point
```

> **Unsettled.** `eo::qdiv` on two *decimals* returns a rational
> (`(eo::qdiv 7.0 2.0) == 7/2`), while `eo::add` on two decimals returns a
> decimal. So the arithmetic operators are not uniform in whether they preserve
> the category of their arguments, and which ones do is not stated as a rule —
> only observable from the examples.

### 5.5 List operators

Defined over `f`-lists ([§4.3](#43-associativity-with-a-nil-terminator)) for a
nil-terminated associative `f`. Every one of them is stuck when `f` is not such
an operator, or when an argument that should be an `f`-list is not — including
when it is a *different* operator's list.

| | |
| --- | --- |
| `(eo::nil f T?)` | the nil terminator of `f`, at type `T` if parametric ([§4.10](#410-parametric-nil-terminators)) |
| `(eo::cons f t l)` | `(f t l)`, requiring `l` to be an `f`-list |
| `(eo::list_len f l)` | number of children |
| `(eo::list_concat f l1 l2)` | append |
| `(eo::list_nth f l i)` | the `i`th child, `0`-based, stuck if out of range |
| `(eo::list_find f l t)` | least index of `t`, or `-1` |
| `(eo::list_rev f l)` | reverse |
| `(eo::list_erase f l t)` | drop the first occurrence of `t` |
| `(eo::list_erase_all f l t)` | drop every occurrence, order preserved |
| `(eo::list_setof f l)` | drop repeats after the first, order preserved |
| `(eo::list_minclude f l1 l2)` | multiset inclusion of `l1` in `l2` |
| `(eo::list_meq f l1 l2)` | multiset equality |
| `(eo::list_diff f l1 l2)` | multiset difference |
| `(eo::list_inter f l1 l2)` | multiset intersection |
| `(eo::list_singleton_elim f l)` | a one-element list becomes its element; others unchanged |
| `(eo::list_singleton_intro f t)` | an `f`-list is unchanged; anything else becomes a singleton |
| `(eo::list_repeat f t n)` | the list of `n` copies of `t`, `n` a non-negative 32-bit numeral |

Written in list notation (so `(or a b)` means the two-element `or`-list):

```smt
(eo::cons or a (or a b))                    == (or a a b)
(eo::cons or a b)                           == itself          ; b is not an or-list
(eo::list_len or (or (or a a) b))           == 2               ; nesting is not flattening
(eo::list_concat or (or a b) (or b))        == (or a b b)
(eo::list_concat or (and a b) false)        == itself          ; wrong operator
(eo::list_diff or (or a b a c a) (or a a))  == (or b c a)
(eo::list_inter or (or a b a c a) (or a a)) == (or a a)
(eo::list_singleton_elim or (or a))         == a
(eo::list_repeat or a 0)                    == false
```

The multiset operators respect multiplicity and preserve the order of whichever
list they are traversing; they are not set operations despite the name of
`eo::list_setof`.

All of these except `eo::nil` are expressible as ordinary Eunoia programs, and
the manual's appendix gives a signature that does so. `eo::nil` is not, because
its behaviour depends on the declarations in scope — which is the sharpest
statement of how it differs from the rest.

### 5.6 Datatype operators

| | |
| --- | --- |
| `(eo::dt_constructors T)` | the `eo::List` of `T`'s constructors, if `T` is a datatype |
| `(eo::dt_selectors c)` | the `eo::List` of `c`'s selectors, if `c` is a constructor |

For a fully instantiated parametric datatype, ambiguous constructors come back
already annotated; unambiguous ones come back bare. Selectors are returned the
same way whether or not the constructor was annotated.

```smt
(eo::dt_constructors (Tree Int))  == (eo::List::cons node
                                       (eo::List::cons (as leaf (Tree Int))
                                          eo::List::nil))
(eo::dt_selectors leaf)           == eo::List::nil
(eo::dt_constructors (Pair Int))  == itself          ; partially applied
```

These two operators are what make generic reasoning about datatypes possible:
a proof rule can recurse over the constructors of whatever type it was given,
so one rule covers every datatype a signature declares
([§7.6](#76-a-worked-rule-splitting-on-a-datatype)).

---

## 6. Programs

A **program** is an ordered list of rewrite rules. It is Eunoia's mechanism for
side conditions: computation a proof rule needs, expressed in the language
rather than assumed of the checker.

```smt
(program <symbol> (<typed-param>*) :signature (<type>+) <type> ((<term> <term>)*)?)
```

The parameter list introduces the parameters used in the body; they are implicit
and are not the program's arguments. `:signature` gives the argument types and
the return type. The body, if present, is a non-empty list of
`(pattern replacement)` pairs. Without a body the command is a forward
declaration, which is how mutual recursion is written.

```smt
(declare-const or (-> Bool Bool Bool) :right-assoc-nil false)
(program contains ((l Bool) (x Bool) (xs Bool :list))
  :signature (Bool Bool) Bool
  (
    ((contains false l)     false)
    ((contains (or l xs) l) true)
    ((contains (or x xs) l) (contains xs l))
  )
)
```

### 6.1 How a program evaluates

For a ground application `(f s1 … sn)`: take the cases in order, find the first
whose pattern matches for some substitution `S`, and return `S` applied to that
case's replacement. If no case matches, the application is **stuck**
([§5.1](#51-one-discipline-stated-once)) — like any other operator, it reduces
to itself and nothing is reported.

**First match wins**, so the order of cases is part of the program's meaning. A
general pattern placed before a specific one makes the specific one unreachable.

Four situations in which a program is *not* invoked at all, and its application
is stuck instead:

- an argument is stuck — programs never see failed computations;
- an argument is another program, a computational operator, or an oracle;
- the body has no cases;
- the application is not ground.

The second is worth noting: programs are not higher-order over programs. A
program expecting a function argument may be applied to an ordinary declared
constant, but not to another program.

> **Implementation. [verified]** Because matching is first-match-wins and
> nothing checks coverage, an unreachable case is accepted silently: there is no
> notion of a dead case, so shadowing is well defined and invisible.
> `docs/notes.md` §3 records the case.

### 6.2 Patterns

A pattern is an ordinary term, containing parameters where the case will bind.
Matching is **syntactic** — over the desugared term, after
[§4.5](#45-the-desugaring-algorithm) has run.

Three restrictions, all checked at the declaration:

1. Each case's pattern must be an application of the program itself.
2. A pattern may not contain a computational operator.
3. The free parameters of a replacement must be contained in those of its
   pattern.

Restriction 2 is the one that surprises people, because desugaring can
*introduce* an operator into something that looked like a pattern. Two
adjacent `:list` parameters under an associative operator desugar to an
`eo::list_concat` ([§4.5](#45-the-desugaring-algorithm)), and the case is then
rejected:

```smt
(program contains ((l Bool) (x Bool :list) (xs Bool :list))  ; both :list
  :signature (Bool Bool) Bool
  ( … ((contains (or x xs) l) (contains xs l)) )
)
;; (or x xs) ⇝ (eo::list_concat or x xs), which is not a legal pattern
```

And the mirror-image error, forgetting `:list` entirely, is accepted and simply
means something else — `(or l xs)` with an unmarked `xs` matches an `or`-list of
*exactly two* children, so the program works on `(or a b)` and silently fails to
evaluate on `(or a b c)`. Neither the declaration nor the failing call reports
anything.

Currying makes very general patterns available. `(f a)` with both `f` and `a`
parameters matches **any** function application, which is what a generic
traversal is built from:

```smt
(program substitute ((T Type) (U Type) (S Type) (x S) (y S) (f (-> T U)) (a T) (z U))
  :signature (S S U) U
  (
    ((substitute x y x)     y)                                        ; found it
    ((substitute x y (f a)) (_ (substitute x y f) (substitute x y a))) ; any application
    ((substitute x y z)     z)                                        ; anything else
  )
)
```

This also shows what opaque arguments ([§3.3](#33-declare-parameterized-const))
buy: `(@array_diff A B)` is not an application, so the second case does not
match it and the traversal does not descend into `A` and `B`. A program that
*does* want to descend must name `@array_diff` in a case of its own.

> **Implementation.** Matching does not appear to consult types: a case is
> selected on shape alone, and the argument types in `:signature` are not used
> to rule one out. Nothing in the manual says either way.

### 6.3 What a program body is not

> **Implementation. [verified]** Program bodies are not type checked. The manual
> states this outright — *"Terms in program bodies are not statically type
> checked. Evaluating a program may introduce non-well-typed terms if the
> program body is malformed."* A case whose replacement has a type unrelated to
> the program's declared return type is accepted, and is discovered only if some
> proof reaches that case:
>
> ```smt
> (program $mk ((x Int) (F Bool)) :signature (Bool) Bool
>   ( (($mk (not F)) F)
>     (($mk F)       (+ 1 1)) ))    ; Int, where Bool was declared — accepted
> ```
>
> A proof taking the first branch checks. A proof taking the second fails with a
> type error. Nothing between the two says the signature was already wrong.
> `docs/notes.md` §3 records the case.

> **Unsettled.** Whether this is the language or an implementation is exactly
> the question of what a *well-formed signature* is, and Eunoia has no such
> notion — see [chapter 11](#11-where-the-language-is-unsettled). Under the
> permissive reading a signature is well-formed when the proofs people happen to
> write against it check, which makes well-formedness a property of a corpus
> rather than of a file.

### 6.4 Dependent programs: `eo::quote`

A program's return type may mention its arguments, by naming one in the
signature with `eo::quote`:

```smt
(program repeat_zero ((n Int))
  :signature ((eo::quote n)) (BitVec n)
  (
    ((repeat_zero 0) @bv_empty)
    ((repeat_zero n) (eo::requires (eo::is_neg n) false
                        (concat #b0 (repeat_zero (eo::add n -1)))))
  )
)

(define foo () (repeat_zero 7) :type (BitVec 7))
```

`(eo::quote n)` in argument position says: bind this argument to the parameter
`n`, so that `n` may be used in the return type. Quoted and ordinary arguments
may be mixed freely, and the argument of `eo::quote` must be a parameter from
the program's own parameter list.

```smt
(program repeat_term ((m Int) (n Int) (x (BitVec m)))
  :signature ((BitVec m) (eo::quote n)) (BitVec (eo::mul m n))
  …)
```

This is the same `Quote` that the type system uses for proof rule arguments
([chapter 8](#8-the-type-system)); a dependent program and a proof rule are the
same construction seen from two sides.

The `eo::requires` in `repeat_zero` is doing real work: it guards the recursive
case against a negative `n`, which would otherwise recurse forever. Termination
of programs is not checked by anything.

---

## 7. Proof rules and proofs

### 7.1 The shape of it

A proof is a sequence of steps, each naming a rule, its premises and its
arguments. Checking a step means finding a substitution that makes the rule's
patterns fit what was supplied.

```smt
(declare-rule <symbol> (<typed-param>*)
   <assumption>?      ; :assumption <term>
   <premises>?        ; :premises (<term>*)  |  :premise-list <term> <term>
   <arguments>?       ; :args (<term>*)
   <reqs>?            ; :requires ((<term> <term>)*)
   <conclusion>       ; :conclusion <term>  |  :conclusion-explicit <term>
   <attr>*)
```

Applying a rule to concrete premises and arguments succeeds when there is a
substitution `S` such that

- each premise proof proves the corresponding premise pattern under `S`,
- each supplied argument matches the corresponding argument pattern under `S`,
- each requirement pair evaluates to the same term under `S`,

and the step then proves `S` applied to the conclusion.

A rule is only well defined if every free parameter of its requirements and its
conclusion also occurs in its arguments or premises — otherwise `S` does not
determine what it proves.

```smt
(declare-rule symm ((T Type) (t T) (s T))
    :premises ((= t s))
    :conclusion (= s t))
```

Given a premise proving `(= a b)`, matching gives `{t ↦ a, s ↦ b}` and the step
proves `(= b a)`. Note that `T` appears in no premise or argument *pattern*
directly; it is determined by the implicit type argument of `=`.

### 7.2 Requirements

`:requires ((r1 s1) … (rk sk))` asks that each pair evaluate to the same term.
It is exactly sugar for wrapping the conclusion:

```smt
(declare-rule leq-contra ((x Int))
    :premises ((>= x 0))
    :requires (((eo::is_neg x) true))
    :conclusion false)

;; identical to
(declare-rule leq-contra ((x Int))
    :premises ((>= x 0))
    :conclusion (eo::requires (eo::is_neg x) true false))
```

Which means requirements inherit `eo::requires`'s discipline: a failed
requirement leaves a stuck term, and the step fails because what it proves is
not what it claimed, not because anything raised an error.

### 7.3 Premise lists

`:premise-list <pattern> <op>` takes any number of premises, combines the
formulas they prove into a single term with `op`, and matches that against the
pattern.

```smt
(declare-const and (-> Bool Bool Bool) :right-assoc-nil true)
(declare-rule and-intro ((F Bool))
    :premise-list F and
    :conclusion F)
```

Given premises proving `F1 … Fn`, `F` is bound to `(and F1 … Fn)`. `op` must be
a variadic operator ([chapter 4](#4-application-sugar)).

### 7.4 Explicit conclusions

`:conclusion-explicit <pattern>` inverts the direction: instead of computing
what is proved, the rule matches against a conclusion the step *supplies*.

```smt
(declare-rule split ((F Bool))
  :conclusion-explicit (or F (not F)))

(step @p0 (or true (not true)) :rule split)
```

A step using such a rule must give a conclusion, and the step is valid only if
that conclusion matches. This is how a rule with a large or non-computable space
of conclusions is written: let the proof say which one, and check it.

### 7.5 Proof commands, and local assumptions

| | |
| --- | --- |
| `(assume <symbol> <term>)` | `<symbol>` is a proof of `<term>` |
| `(step <symbol> <term>? :rule r :premises (…)? :args (…)?)` | apply `r`; if `<term>` is given, check that it is what was proved |
| `(assume-push <symbol> <term>)` | as `assume`, but scoped |
| `(step-pop <symbol> <term>? :rule r …)` | apply `r`, discharging the innermost pushed assumption |

`assume-push` and `step-pop` are how a rule with an `:assumption` field is used:
the assumption is available as a proof inside the scope, and consumed when the
scope closes.

```smt
(declare-rule implies-intro ((F Bool) (G Bool))
  :assumption F
  :premises (G)
  :conclusion (=> F G))

(assume-push @p1 false)
(step     @p2 true :rule contra :premises (@p1) :args (true))
(step-pop @p3 (=> false true) :rule implies-intro :premises (@p2))
```

After the `step-pop`, `@p1` is out of scope. Scopes nest.

Omitting the conclusion term from a `step` is allowed: the step then proves
whatever the rule computes, unchecked against any stated intent. Supplying it
is what turns a proof into something a reader can follow, and is required for
`:conclusion-explicit` rules.

### 7.6 A worked rule: splitting on a datatype

Putting programs, datatype operators and rules together — one rule that works
for every datatype in the signature:

```smt
(declare-parameterized-const is ((C Type :implicit) (D Type :implicit)) (-> C D Bool))
(declare-const or (-> Bool Bool Bool) :right-assoc-nil false)

(program $mk_dt_split ((D Type) (x D) (T Type) (c T) (xs eo::List :list))
  :signature (eo::List D) Bool
  (
    (($mk_dt_split eo::List::nil x)         false)
    (($mk_dt_split (eo::List::cons c xs) x) (eo::cons or (is c x) ($mk_dt_split xs x)))
  )
)

(declare-rule dt-split ((D Type) (x D))
  :args (x)
  :conclusion ($mk_dt_split (eo::dt_constructors (eo::typeof x)) x))
```

```smt
(declare-datatypes ((Tree 0)) (((node (left Tree) (right Tree)) (leaf))))
(step @p0 (or (is node x) (is leaf x)) :rule dt-split :args (x))

(declare-datatypes ((Color 0)) (((red) (green) (blue))))
(step @p1 (or (is red y) (is green y) (is blue y)) :rule dt-split :args (y))
```

The conclusion is not a term; it is a *computation* that produces one. This is
the characteristic shape of a Eunoia proof rule, and the reason the evaluator
exists.

### 7.7 `:sorry`, and what a checker answers

A rule may be marked `:sorry`, meaning it has no justification. Using one does
not fail; it changes the answer.

After reading a file without error, a checker reports one of:

| | |
| --- | --- |
| `incomplete` | some step used a rule marked `:sorry` |
| `correct` | otherwise |

`correct` says only that every step checked. It carries no claim about *what*
was proved — a proof of nothing in particular is `correct`. Requiring the final
step to prove `false` at assumption level zero is available as an option, and
is off by default.

> **Implementation.** The response vocabulary, and the fact that there are two
> words rather than an exit code, is a property of a checker's interface rather
> than of the language. It is recorded here because signatures in the wild — and
> every CI job that runs one — depend on it.

---

## 8. The type system

> **Correction, 2026-09-17.** This chapter opens by repeating the ethos manual's
> framing — that proof checking is a special instance of type checking — which
> this account took over rather than checked. We no longer think it is the right
> account: checking a Eunoia proof is *running a program*, and the typed
> presentation reaches neither `:assumption`, `:premise-list` nor
> `:conclusion-explicit`, states a kind for `Proof` that is not enforced, and
> hides the evaluator inside the `=` of its side conditions. The argument, with
> what was run to establish it, is
> [`docs/account-vs-manual.md` MD-01](account-vs-manual.md). **The chapter
> below is accurate as a description of the typing rules and wrong as an
> account of proof checking**; rewriting it around the state, the commands and
> the match/evaluate/produce order — keeping the typed reading as the
> explanation of dependency, which is what it is good for — is outstanding work.

Everything in [chapter 7](#7-proof-rules-and-proofs) is notation. Underneath,
**a proof is a term and proof checking is type checking**, in a type system with
two types a signature cannot name:

| | |
| --- | --- |
| `Proof` | of kind `(-> Bool Type)`. `(Proof F)` is the type of proofs of `F` |
| `Quote` | marks an argument position whose *term* is bound, not just its type |

Taking `t : S` as an axiom for every atomic term declared with type `S`, the
whole of application typing is two rules:

```
    f : (-> U S)        t : T
    ─────────────────────────────  if U·σ = T,  U not a Quote
        (f t) : S·σ

    f : (-> (Quote u) S)     t : T
    ──────────────────────────────  if u·σ = t
        (f t) : S·σ
```

The first is ordinary dependent application: match the argument's *type* against
the expected one and carry the substitution into the result type. The second is
what makes dependent types usable in practice: match the argument *term* against
a pattern, so the result type can mention the argument itself. `eo::quote` in a
program signature ([§6.4](#64-dependent-programs-eoquote)) is this rule, and so
is a proof rule's `:args`.

**One further condition, and it is the one that bites.** A term is well-typed
only if its type is either non-ground, or fully reduced — containing no stuck
application of a program or a computational operator.

```smt
(declare-const x (BitVec 2))
(declare-const y (BitVec 3))
(define z () (concat x y) :type (BitVec 5))     ; (BitVec (eo::add 2 3)) reduces

(declare-const a Int) (declare-const b Int)
(declare-const x2 (BitVec a)) (declare-const y2 (BitVec b))
(define z2 () (concat x2 y2))                   ; type error
```

`z2`'s type is `(BitVec (eo::add a b))`. `a` and `b` are declared constants, so
the type is ground; `eo::add` is stuck on them, so it is not reduced; so the
term is ill-typed. Had `a` and `b` been *parameters*, the type would be
non-ground and the term would be fine. This is why computational type rules work
inside a program or a rule and not at the top level.

### 8.1 The proof commands as sugar

```smt
(declare-rule s ((v1 T1) … (vi Ti))
    :premises (p1 … pn) :args (t1 … tm)
    :requires ((r1 s1) … (rk sk)) :conclusion t)
```

is

```smt
(declare-parameterized-const s ((v1 T1 :implicit) … (vi Ti :implicit))
    (-> (Quote t1) … (Quote tm)
        (Proof p1) … (Proof pn)
        (eo::requires r1 s1 … (eo::requires rk sk
            (Proof t)))))
```

and correspondingly

```smt
(assume s f)                    ≡  (declare-const s (Proof f))
(step s f :rule r :premises (p1 … pn) :args (t1 … tm))
                                ≡  (define s () (r t1 … tm p1 … pn) :type (Proof f))
```

with the `:type` omitted when the step gives no conclusion. Reading these three
lines is the fastest way to understand the proof layer:

- **A rule is a constant.** Its arguments are `Quote`d so the conclusion can
  mention them; its premises are ordinary arguments whose types are `Proof`s.
- **Requirements are `eo::requires` in the return type.** A failed requirement
  leaves the return type stuck, so the `define`'s `:type` check fails.
- **A step is a `define` with `:type`** — which is why a step's optional
  conclusion is exactly the optional `:type` of [§3.2](#32-define-is-a-macro),
  and why omitting it means nothing is checked.
- **Matching premises against patterns is unification of `Proof` types**, not a
  separate mechanism.

The correspondence assumes a rule with neither `:assumption` nor
`:premise-list`; those two need scope tracking that the sugar does not express.

> **Unsettled.** The manual writes the quoted argument type as `(-> (Quote u) S)`
> in the appendix and as a distinct "quote arrow" `(~> T T)` in a note earlier
> on. Whether these are two notations for one thing, or `~>` is a separate
> constructor, is not stated. A formalization has to pick.

---

## 9. Files

| | |
| --- | --- |
| `(include <string>)` | read the named file as a signature. The path is relative to the including file |
| `(reference <string> <term>?)` | read the named file as the **reference input**, optionally naming a normalization program |

Both have command-line equivalents. There may be at most one `reference` per
run.

### 9.1 Reference inputs

A proof is only worth as much as its assumptions. `reference` names the SMT-LIB
file the proof is about, and turns on a check that every `assume` corresponds to
something actually asserted there.

Reading a reference file:

- declarations populate the symbol table as usual;
- `(assert F)` adds `F` to the **reference assertions**;
- `(check-sat-assuming (F1 … Fn))` adds those too, since they were part of the
  query;
- `define-fun` becomes an assertion equating the symbol with its body, unless
  an option says to read it as a Eunoia definition instead;
- `(reset-assertions)` and `(reset)` discard what has accumulated;
- commands beginning `get-` are parsed and ignored;
- everything else is ignored or, if not in the grammar, a parse error.

Then every `(assume <symbol> G)` must have `G` among the reference assertions.

Not supported, and a parse error: `define-fun-rec`, `define-funs-rec`, `push`,
`pop`, and solver-specific commands. Recursive definitions should be written as
a declaration plus a quantified assertion.

### 9.2 Validation up to normalization

The check above is syntactic, so it only works if the signature's terms are
built exactly as the `.smt2` file writes them. `(reference "f.smt2" normalize)`
runs a program over both the assertions and the assumptions first:

```smt
(program normalize ((T Type) (S Type) (f (-> S T)) (x S) (a Int) (b Int) (y T))
   :signature (T) T
   (
     ((normalize (/ a b)) (eo::qdiv a b))
     ((normalize (f x))   (_ (normalize f) (normalize x)))
     ((normalize y)       y)
   )
)
```

— here, folding constant division into rational literals, for a solver that
reads it that way. The generic-traversal shape is the one from
[§6.2](#62-patterns).

> This is the seam where Eunoia meets the world it is describing, and it is
> worth being explicit that the seam is *textual*. Nothing checks that a
> signature's `+` means SMT-LIB's `+`; the reference check establishes that the
> proof assumes what the query asserted, in whatever reading of the symbols the
> signature supplies.

---

## 10. Grammar

Reproduced from the manual's appendix. Signature and proof files are
`<eo-command>*`; reference files are `<smtlib2-command>*`.

```
<eo-command> ::=
    (assume <symbol> <term>)
  | (assume-push <symbol> <term>)
  | (declare-consts <lit-category> <type>)
  | (declare-parameterized-const <symbol> (<typed-param>*) <type> <attr>*)
  | (declare-rule <symbol> (<typed-param>*) <assumption>? <premises>? <arguments>? <reqs>? <conclusion> <attr>*)
  | (define <symbol> (<typed-param>*) <term> <attr>*)
  | (include <string>)
  | (program <symbol> (<typed-param>*) :signature (<type>+) <type> ((<term> <term>)*)?)
  | (reference <string> <term>?)
  | (step <symbol> <term>? :rule <symbol> <simple-premises>? <arguments>?)
  | (step-pop <symbol> <term>? :rule <symbol> <simple-premises>? <arguments>?)
  | <common-command>

<common-command> ::=
    (declare-const <symbol> <type> <attr>*)
  | (declare-datatype <symbol> <datatype-dec>)
  | (declare-datatypes (<sort-dec>^n) (<datatype-dec>^n))
  | (declare-sort <symbol> <numeral>)
  | (echo <string>?) | (exit) | (reset) | (set-option <attr>)

<smtlib2-command> ::=
    (assert <term>) | (check-sat) | (check-sat-assuming (<term>*))
  | (declare-fun <symbol> (<type>*) <type>)
  | (define-const <symbol> <type> <term>)
  | (define-fun <symbol> (<typed-param>*) <type> <term>)
  | (define-sort <symbol> (<symbol>*) <type>)
  | (reset-assertions) | (set-info <attr>) | (set-logic <symbol>)
  | (get-<symbol> <sexpr>*) | <common-command>

<keyword>       ::= :<symbol>
<attr>          ::= <keyword> <term>?
<sexpr>         ::= <symbol> | <keyword> | <literal> | (<sexpr>*)
<term>          ::= <symbol> | (<symbol> <term>+) | (! <term> <attr>+)
<type>          ::= <term>
<typed-param>   ::= (<symbol> <type> <attr>*)
<sort-dec>      ::= (<symbol> <numeral>)
<sel-dec>       ::= (<symbol> <type>)
<cons-dec>      ::= (<symbol> <sel-dec>*)
<datatype-dec>  ::= (<cons-dec>+)
<lit-category>  ::= '<numeral>' | '<decimal>' | '<rational>' | '<binary>' | '<hexadecimal>' | '<string>'

<assumption>      ::= :assumption <term>
<premises>        ::= <simple-premises> | :premise-list <term> <term>
<simple-premises> ::= :premises (<term>*)
<arguments>       ::= :args (<term>*)
<reqs>            ::= :requires ((<term> <term>)*)
<conclusion>      ::= :conclusion <term> | :conclusion-explicit <term>
```

> **Unsettled.** This grammar does not derive several things the language
> plainly accepts, so it should be read as an outline rather than as a
> definition. In particular `<term>` has no `<literal>` alternative, so `5` and
> `"abc"` are not terms; `<datatype-dec>` has no `par` alternative, so the
> parametric datatypes of [§3.6](#36-datatypes) cannot be written; and the
> annotated-term form `(! <term> <attr>+)` appears here and nowhere in the prose,
> so what an annotation on a term means is undocumented. `let` and `eo::define`
> are likewise absent — `let` is described only as a parser option that can be
> switched off, and `eo::define` is named once in the manual's overview as a
> binder for sharing subterms and then never mentioned again.

---

## 11. Where the language is unsettled

Collected from the marks above. These are not documentation gaps; they are
places where there is a real question and the current answer is *whatever the
implementation does*. Several are inherited from `docs/notes.md` §4, which
reached them from the other direction — by trying to write checks for them.

**What is a well-formed signature?** Eunoia has no such notion. Typing is on
demand, so a `define` body without `:type`, a program case no proof reaches, and
a rule that could conclude a non-`Bool` term are all accepted. Either those are
defects a conforming checker may report, or a signature is well-formed exactly
when the proofs people happen to write against it check — which makes
well-formedness a property of a corpus rather than of a file. Everything below
is a special case of this question.

**Are the attribute contracts normative?** [§4.11](#411-the-declaration-contracts).
The manual says a nil terminator *must* have the operator's tail type and a
chainable combiner *should* be variadic. Nothing enforces either. If they are
requirements, violating declarations may be rejected; if they are advice, the
desugaring of a violating declaration needs a definition it does not have.

**Are overlapping program cases legal?** [§6.1](#61-how-a-program-evaluates).
First-match-wins makes shadowing well defined, so an unreachable case is a smell
rather than a violation — unless the language intends coverage or disjointness,
which nothing states.

**Is a program body part of the language's type discipline?**
[§6.3](#63-what-a-program-body-is-not). The manual says bodies are not
statically type checked, which reads as a description of an implementation
choice; whether a checker that *did* check them would be conforming, and would
reject signatures in use today, is open.

**What does a file's role mean?** [§1.1](#11-three-file-roles). Role is decided
by invocation, so literal normalization — and therefore term identity — is not
determined by the text alone.

**How much of SMT-LIB is assumed?** [§9.2](#92-validation-up-to-normalization).
A signature's `+` is whatever the signature says it is. Nothing relates it to
SMT-LIB's `+`, and calculi in the wild deliberately differ from the standard in
places (mixed arithmetic, variadic operators with nil terminators, strings as
sequences).

**What is `eo::hash` allowed to be?** [§5.3](#53-core-operators). Injective on
values, and nothing else is stated — not stability across runs, not agreement
between checkers. `eo::cmp`, and any signature that sorts terms, inherits the
question.

**Category preservation in arithmetic.** [§5.4](#54-arithmetic-boolean-string-and-conversion).
`eo::add` on decimals gives a decimal; `eo::qdiv` on decimals gives a rational.
Which operators preserve their arguments' category is observable from the
examples and stated as a rule nowhere.

**Binding.** [§4.9](#49-binder). A binder's variable list is not related to its
body by anything. Capture and freshness have no account in the language.

**Discriminators and updaters.** [§3.6](#36-datatypes). Named as products of
`declare-datatype` and then never described.

**`Quote` versus `~>`.** [§8.1](#81-the-proof-commands-as-sugar). Two notations,
one thing or two, unstated.

---

## What this account leaves out on purpose

Not gaps — deliberate exclusions, listed so a reader can tell the two apart.

| left out | where it belongs |
| --- | --- |
| building, installing and invoking a checker; command-line options; streaming | the checker's own documentation |
| trace tags, statistics, error message formatting, dagified printing | likewise |
| the `.eos` semantics-set language and the compiler that reads it | their own reference; out of charter ([`../README.md`](../README.md)) |
| the case for the ecosystem's arrangement | `tools/ynoia/docs/why-eunoia.md`; out of charter |
| proposed changes to Eunoia | the host repository's report to the language's maintainers |
| the derived-operator signature reconstructing the list operators in pure Eunoia | the manual's appendix, which is the right place for it |
