---
# Documentation: https://wowchemy.com/docs/managing-content/

title: "Intro to Decidable Equality"
subtitle: ""
summary: "One of the more difficult concepts in Idris, I've found, is proving
          things by dependent types. The 'simplest' introduction to this is
          probably the `DecEq` interface, which this post aims to introduce,
          explain, and implement."
authors: [thomas-e-hansen]
tags: [idris2, intro, formal-methods]
categories: []
date: 2022-02-23
lastmod:
featured: false
draft: false

# Featured image
# To use, add an image named `featured.jpg/png` to your page's folder.
# Focal points: Smart, Center, TopLeft, Top, TopRight, Left, Right, BottomLeft, Bottom, BottomRight.
image:
  caption: ""
  focal_point: ""
  preview_only: false

# Projects (optional).
#   Associate this post with one or more of your projects.
#   Simply enter your project's folder or file name without extension.
#   E.g. `projects = ["internal-project"]` references `content/project/deep-learning/index.md`.
#   Otherwise, set `projects = []`.
projects: []
---

### Introduction

If you're just getting started with Idris, you might have heard that it is
possible to prove things in Idris. But what does that mean? How do you "prove"
anything programmatically? Isn't testing the best we can do? These were
certainly some of my thoughts when I first got into Idris and dependent types. 4
years later, I'm still not at the point where I would say I _get it_, but I do
know a lot more than I started out with. And having tried to explain this to
various people, both friends and family, hopefully those experiences mean I can
write something at least semi-coherent which provides a nice introduction to
these things.

This post is also a Literate Idris file, which means you can load it at the REPL
and test the functions it defines! Since we're covering some fundamentals, let's
start by hiding their default definitions, so that we can define our own, and
since we're doing proofs, let's also enable totality checking by default:

```idris
module DecEqIntro

%hide (==)
%hide (===)
%hide Void
%hide Prelude.Not
%hide Builtin.Equal
%hide Builtin.Refl
%hide Builtin.sym

%default total
```

### Fundamentals

Rather than jumping in at the deep end and starting off with `DecEq`, let's
start with a couple of fundamental concepts. These can be difficult to wrap your
head around in their own right, so since everything follows from them, let's try
to walk through them. We'll start with what is (hopefully) familiar ground:
non-dependent types.

#### Non-dependent types promise nothing

To explain how regular, i.e. non-dependent, types come with no guarantees, we're
going to take a page out of the "Type-Driven Development with Idris" (TDD) book
and start by considering the type of the `(==)` operator:

```idris
(==) : Eq ty => ty -> ty -> Bool
```

This reads as: "Given that the type `ty` implements the `Eq` interface, we can
take 2 things of type `ty` and return a `Bool`". However, there is nothing in
this type that promises anything about the output! What do I mean by this? Well,
the following is a valid, albeit confusing, implementation of `(==)` for natural
numbers:

```idris
namespace Nat
  export
  (==) : Nat -> Nat -> Bool
  (==) Z     Z     = False
  (==) Z     (S j) = True
  (==) (S k) Z     = True
  (==) (S k) (S j) = False
```

This clearly makes no sense in terms of what we, the programmers, normally
understand by `(==)`, but as far as the type-checker is concerned, it is a valid
implementation; we've taken 2 `Nat`s and returned a `Bool`, just like we said we
would in the type declaration.

Now, you could definitely argue that nobody in their right mind would implement
`(==)` like this, and you'd almost definitely be right. And anyone who
subsequently tried to use this `(==)` function would be thoroughly confused. But
the point is that there is nothing in the _type_ of the function which prevents
us from doing silly things. And in that sense, it promises nothing.

However, with _dependent_ types (types which can depend on values) we can define
some stronger, type-level guarantees.

#### Proof by datatype

Before we define a proof, I'll try to explain the intuition for "proof by
datatype". What, in my experience, tends to confuse people is how a datatype can
constitute a proof. The best real-world parallel I've come up with so far is
bronze: If you find some old artefacts which are made of bronze, then since you
know bronze is an alloy of tin and copper, you know whomever made the artefacts
must have had access to tin and copper. The existence of bronze "proves" the
existence of some tin and copper. And if you could disassemble the bronze into
its components, you could show this since you'd extract some tin and copper from
that deconstruction. To illustrate this, we could define the following datatypes
in Idris:

```idris
public export
data Tin = Sn

public export
data Copper = Cu

public export
data Bronze : Type where
  MkBronze : Tin -> Copper -> Bronze
```

The `MkBronze` constructor takes two arguments: one of type `Tin` and one of
type `Copper` and returns something of type `Bronze`. We can think of
constructors as functions, which means we know that the only way we could call
this `MkBronze` function was if we provided it with its required arguments.
There's nothing magical going on here, that's just how functions work! You can't
fully evaluate a function call if you haven't given the function all its
arguments.

The real twist here, the bit where the notion of proofs comes in, is that since
`MkBronze` is the only thing which can create something of type `Bronze`, and
since we defined that `MkBronze` takes 2 very specific arguments, then we know
that if we have something of type `Bronze`, then we must have called `MkBronze`
at some point (or we wouldn't have been able to create the thing of type
`Bronze`), so we _must_ have had something of type `Tin` and something of type
`Copper` previously, otherwise we wouldn't have been able to call `MkBronze` to
get our `Bronze`! (Feel free to read over that previous bit a couple of times.
It took me a while to convince myself of/understand that the first time I came
across it). In other words: The existence of something of type `Bronze` _proves_
the existence of some things of type `Tin` and `Copper`.

To summarise, the reason we call this is a proof is because, according to all
the rules of our functional programming "game", it _is_ a proof: Having `Bronze`
means we could call `MkBronze`, which means we have _proved_ that we had some
`Tin` and `Copper` at some point; otherwise we'd never have been able to call
`MkBronze`.

With that in mind, let's see how this idea can be used to define something
slightly more useful: A proof of equality.

#### Proofs of equality

To define equality as a datatype, we'll start by explicitly stating what
equality is:

- It is a relationship between 2 things,
- which expresses that those things are, for all intents and purposes,
    equivalent; that they're the same thing.

We can express this as an Idris datatype like so:

```idris
public export
data Equal : a -> b -> Type where
  Refl : {0 x : _} -> Equal x x
```

This is somewhat more complicated than the `Bronze` data declaration, so let's
break things down:

- `data Equal : a -> b -> Type where` --- Defines a _dependent_ type carrying
    two things of type `a` and `b` in the `Type`.
- `Refl :` --- Declares a constructor for `Equal`. In this case we're calling it
    `Refl`, short for "reflexive": a mathematical concept meaning (roughly) the
    same as "is equal".
- `Refl : {0 x : _} ->` --- Defines that the argument to `Refl` is implicit (i.e.
    we don't need to explicitly pass it when calling `Refl`), that the argument
    is called `x`, and that it is of a type that Idris can figure out by itself
    (`_`). We have also expressed that `x` is not needed at runtime (that's what
    the `0` does), since we only actually care about the _property_ that `a` and
    `b` are equal, and not the values themselves.
- `Refl : {0 x : _} -> Equal x x` --- Defines that if we (implicitly) give
    `Refl` some value `x`, then it returns an `Equal x x`, i.e. something of
    type `Equal`, where the `a` and `b` stored in `Equal` is _the same thing_
    (we pass `x` in both places, and there is only one `x` given, so it must be
    the same thing).

This `Equal` datatype with the `Refl` constructor can, based on the intuition I
explained earlier, be considered a proof that 2 things are equal. If we have an
`Equal a b`, then `a` must be the same as `b` or we wouldn't have been able to
construct the `Equal` via a `Refl` call.

A couple of examples to illustrate this:

1. The unit type `()` is equal to itself:
   ```idris
   public export
   ex1 : Equal () ()
   ex1 = Refl
   ```
2. The unit type `()` is equal to itself (explicitly passing `x` to `Refl`):
   ```idris
   public export
   ex2 : Equal () ()
   ex2 = Refl {x=()}
   ```
3. 2 is equal to 2:
   ```idris
   public export
   ex3 : Equal 2 2
   ex3 = Refl
   ```

The above examples show both why implicit arguments are useful, but also how
they can lead to confusion in proof types: the `Refl` used in `ex3` _looks_ the
same as the `Refl` used in `ex1`, but since the implicit arguments are
different, they are actually different `Refl` calls (we see this in the type
declaration).

Writing `Equal` all the time reads awkwardly (we don't write verbatim "x equals
y" all the time when writing equations), and it also quickly becomes tiring, so
let's finish the section on equality proofs by defining some infix syntax for
`Equal`:

```idris
infixl 6 ===

public export
(===) : a -> b -> Type
(===) = Equal
```

This lets us use `(===)` in the middle of expressions where we would have used
`Equal` instead, e.g.:

```idris
public export
ex4 : 3 === 3
ex4 = Refl
```

And just to show how equality proofs (and Idris) are actually quite powerful,
here's an example with computation:

```idris
public export
ex5 : (1 + 2 * 3) === 7
ex5 = Refl
```

Alright, that's all well and good, but how would we prove the opposite: That
something is not equal; that the equality is `False`?

#### Proofs of False

To prove that something is false, one might be tempted to write:

```idris
falseAttempt : (2 === 3) === False
```

But we cannot implement this, since there is no way to call `Refl` to obtain the
expression `(2 === 3)`. (This is actually somewhat reassuring, since it suggests
our approach to proofs is sound.)

Another attempt might look like:

```idris
falseAttempt2 : (2 == 3) === False
```

But while we might be able to implement this, it would actually not guarantee
anything about 2 and 3! All it would prove, was that the _function call_ `(==) 2
3` returned `False`. Which, as we saw at the beginning, guarantees nothing.

To get around this, we need some datatype which captures the concept of "false"
or "untrue". In logic and type-theory, we often call this "bottom" or "void" and
write it "⊥". But there is still the question of how to express this as a
datatype, especially in terms of constructors: What arguments would those even
take??

Let's put that aside for now and instead think of what "false" means in the
context of proofs. If we've proven something to be false, then we've shown that
it cannot be the case. A common tactic in maths is "proof by contradiction": You
assume a statement to be true, and then show that if that statement _was_ true,
then you would arrive at a contradiction. And from said contradiction, you could
likely prove anything since you've broken the rules to begin with. We can use a
similar idea to define a datatype which captures the concept of "false". Here is
the _entire_ definition of that datatype:

```idris
public export
data Void : Type where
```

Initially you might object, because clearly there is no way we can use this:
there are no constructors which can be used to get something of type `Void`. But
that's entirely intentional! What we are expressing here is "If I have something
of type `Void`, then I have broken the rules". Similar to contradictions in
maths and logic, where the contradiction breaks some foundational rule and so
continuing defies the point of those reasoning systems, Idris has a foundational
rule of "datatypes are created by data-constructors" which, if broken, means we
might as well assume anything; in those cases, all bets are off!

The `Void` datatype in and of itself is not super useful, but it is useful for
expressing impossibilities.

#### Expressing contradictions

Now that we have some way of indicating that we've broken the rules, we can
start writing down contradictions. A contradiction is some statement which, if
true, breaks the rules. Using `Void`, we can express this as a function:

```idris
public export
falsum1 : 2 === 3 -> Void
```

The function `falsum1` returns something of type `Void`. But since we have
defined `Void` such that it can never be constructed, we know this can never be!
The function can never return a value! What `falsum1` effectively says is "If I
can prove 2 equals 3, then I have broken the rules and can also construct
`Void`".  Which is true: As we saw earlier, there is no way to call `Refl` to
get an `Equal 2 3`. Unless we cheat. In which case anything goes, and we might
as well also say that we can construct datatypes which have no constructors.

To finish the "implementation" of `falsum1`, we write the following:

```idris
falsum1 Refl impossible
```

The `impossible` keyword tells Idris that the correct behaviour here is that
there is no way to make the expression type-check. Which, again, is true: The
only constructor for `2 === 3` is `Refl`, and the only way we could match on
that in `falsum1` would be if the implicit argument was 2 _and_ 3 at the same
time.  For this reason, it is also not possible to write out the implicit
argument as we did with the proofs of equality: If we could write that out, then
it wouldn't be `impossible`.

Again, let's look at some examples. This time, of things which _cannot_ be true:

1. 0 is not the successor of a natural number
   ```idris
   public export
   falsum2 : 0 === (S _) -> Void
   falsum2 Refl impossible
   ```
2. `Nat`s are not `String`s:
   ```idris
   public export
   falsum3 : Nat === String -> Void
   falsum3 Refl impossible
   ```
3. Plus doesn't get evaluated before times:
   ```idris
   public export
   falsum4 : (1 + 2 * 3) === 9 -> Void
   falsum4 Refl impossible
   ```

And similar to what we did for `Equal`, let's define some shorthand for writing
down contradictions. Since they're used for proofs of things which _aren't_
true, we'll call it `Not` (and write `p` for "property"):

```idris
public export
Not : Type -> Type
Not p = p -> Void
```

### Interlude

Whew!... That took a lot longer than I initially expected, but that's the
fundamentals done. If you're still with me, let's finally move on to what I
actually promised this would be about: decidable equality!

### Decidable Equality


### Absurdities


### Lemmas


### Beyond Equality: Custom Predicates


### Conclusion


### Acknowledgements

