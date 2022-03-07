---
# Documentation: https://wowchemy.com/docs/managing-content/

title: "An attempt at explaining Decidable Equality"
subtitle: ""
summary: "One of the more difficult concepts in Idris, I've found, is proving
          things through dependent types. The 'simplest' introduction to this is
          probably the `DecEq` interface, which this post aims to introduce,
          explain, and implement."
authors: [thomas-e-hansen]
tags: [idris2, intro, formal-methods]
categories: []
date: 2022-03-03
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

## Introduction

If you're just getting started with Idris, you might have heard that it is
possible to prove things in Idris. But how does that make any sense? We can
certainly write _tests_ in programs, but how on earth do you "prove" something??
4 years after I encountered Idris, I'm not sure I'd necessarily say I _get it_.
But I do know a lot more than I started out with! And having tried to explain
this to various people, both friends and family, hopefully I can write something
at least semi-coherent which provides a nice explanation.

By the way, this post is also a Literate Idris file, which means you can load it
at the REPL and test the functions it defines!

## Hiding the built-in stuff

Since proofs and decidable equality are somewhat fundamental to Idris, there are
a lot of definitions provided by default. But we want to understand these, not
just use them, so let's start by hiding these defaults in order to implement our
own:

```idris
module DecEqIntro

%hide (==)
%hide (===)
%hide Void

%hide Prelude.Not
%hide Prelude.Dec
%hide Prelude.Uninhabited
%hide Prelude.absurd

%hide Builtin.Equal
%hide Builtin.Refl
%hide Builtin.sym

%default total
```

## Fundamentals

Rather than jumping in at the deep end and trying to implement `DecEq`
immediately (alongside everything that we'll need for it), let's start with a
couple of fundamental concepts. These can be difficult to wrap your head around
in their own right, so it's worth taking a moment to go through them. We'll
start with what is (hopefully) familiar ground: non-dependent types.

### Non-dependent types promise nothing

If you've done some functional programming before, you might have seen something
along these lines as the type of boolean equality:

```idris
(==) : Eq ty => ty -> ty -> Bool
```

This defines the `==` operator, which allows us to compare two instances of a
type `ty` for boolean equality (i.e. `True` or `False`), provided that the type
actually has a notion of "equals" (this what the interface constraint `Eq ty =>`
does).

There's only one small problem with this: It doesn't keep us from doing silly
things:

```idris
namespace Nat
  export
  (==) : Nat -> Nat -> Bool
  (==) Z     Z     = False
  (==) Z     (S j) = True
  (==) (S k) Z     = True
  (==) (S k) (S j) = False
```

This clearly makes no sense in terms of what anyone would normally understand by
`(==)`, but as far as the type-checker is concerned, it is a valid
implementation: We've taken 2 `Nat`s and returned a `Bool`, just like we said we
would in the type declaration.

Now, you could definitely argue that nobody in their right mind would implement
`(==)` like this, and you'd definitely be right (or I really hope you would).
And anyone who tried to use this `(==)` function would be thoroughly confused.
But the point is that there is nothing in the _type_ of the function which
prevents us from doing silly things. In that sense, the type promises nothing
about the return value of the function. This isn't great...

Fortunately, with _dependent_ types (types which can depend on values) we can
define some stronger type-level guarantees.

### The idea of proofs in Idris

Let's start by trying to explain _how_ we can have "proofs" in code. I'm going
to try to explain this using a real-world parallel: bronze.

Bronze is an alloy made up of tin and copper, which revolutionised humanity's
tools around 3500 BCE (at the cost of stone chippers going the way of the
saber-tooth tiger). Since we know that bronze requires access to tin and copper,
if you find some old artefacts made of bronze, you know that whomever made the
artefacts must have had access to tin and copper.

In that sense, the existence of bronze "proves" the existence of some tin and
copper. Let's relate that back to Idris by defining some datatypes:

```idris
public export
data Tin = Sn

public export
data Copper = Cu

public export
data Bronze : Type where
  MkBronze : Tin -> Copper -> Bronze
```

We can create something of type `Tin` with the `Sn` constructor, and something
of type `Copper` with the `Cu` constructor. So far so good. The `MkBronze`
constructor is where things get interesting!

The `MkBronze` constructor takes two arguments: one of type `Tin` and one of
type `Copper` and returns something of type `Bronze`. If we think of
constructors as special functions, we know that in order to call this `MkBronze`
function we need to provide it with its required arguments (that's just how
functions work). So to create something of type `Bronze`, we'd first need to
have some things of type `Tin` and type `Copper` which we could pass to the
`MkBronze` function. Are you starting to see where I'm getting with this?  : )

#### Proof by existence

Let's take the leap to proofs! If we have something of type `Bronze`, we have a
_proof_ that we had something of type `Tin` and something of type `Copper` at
some point. How is this a proof? Well, `MkBronze` is the only thing which can
create something of type `Bronze` and `MkBronze` takes 2 very specific
arguments: something of type `Tin` and something of type `Copper`. We have a
thing of type `Bronze`, so clearly we were able to call `MkBronze` at some
point. This in turn means we must have had something of type `Tin` and something
of type `Copper` at that point, otherwise we wouldn't have been able to pass
them as arguments to `MkBronze`. So the existence of `Bronze` _proves_ the
existence of `Tin` and `Copper`!

Feel free to read over that previous bit a couple of times. The first time I
realised this was how proofs in Idris worked, it took me a while to convince
myself that I'd actually understood it correctly ^^


#### I get it now!

The reason we call this is a proof is because, according to all the rules of our
functional programming "game", it _is_ a proof: Having `Bronze` means we could
call `MkBronze`, which means we have _proved_ that we had some `Tin` and
`Copper` at some point; otherwise we'd never have been able to call `MkBronze`!

Awesome! With that in mind, let's see how this idea can be used to define
something slightly more useful: A proof of equality.

### Proofs of equality

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

This is a tad more complicated than the `Bronze` data declaration, so let's
break it down:

- `data Equal : a -> b -> Type where` --- Defines a _dependent_ type carrying
    two things of type `a` and `b` in the type.
- `Refl :` --- Declares a constructor for `Equal`. In this case we're calling it
    `Refl` (short for "reflexive": a mathematical concept meaning, roughly, the
    same as "is equal").
- `Refl : {0 x : _} ->` --- Defines that the argument `x` to the `Refl`
    constructor is implicit (i.e. we don't need to explicitly pass it when
    calling `Refl`) and that it is of a type that Idris can figure out by itself
    (`_`). We have also expressed that `x` is not needed at runtime (that's what
    the `0` does), since we only actually care about the _property_ that `a` and
    `b` are equal, and not the values themselves.
- `Refl : {0 x : _} -> Equal x x` --- Defines that if we give `Refl` some value
    `x`, then it returns an `Equal x x`, i.e. something of type `Equal`, where
    the `a` and `b` stored in `Equal` is _the same thing_: We put `x` in both
    places and there is only one argument `x` given, so it must be the same
    thing.

This `Equal` datatype with the `Refl` constructor can, based on the intuition I
explained earlier, be considered a proof that 2 things are equal. If we have an
`Equal a b`, then `a` must be the same as `b` or we wouldn't have been able to
call `Refl` to obtain that `Equal`.

We can construct some examples to illustrate this:

1. If we pass `Refl` a number, e.g. 0, explicitly, it is equal to itself:
   ```idris
   public export
   ex1 : Equal 0 0
   ex1 = Refl {x=0}
   ```
2. The unit type `()` is equal to itself:
   ```idris
   public export
   ex2 : Equal () ()
   ex2 = Refl {x=()}
   ```
3. 0 is equal to 0 (this time, letting implicit arguments figure out that
   `x=0`):
   ```idris
   public export
   ex3 : Equal 0 0
   ex3 = Refl
   ```
4. Unit is equal to unit (again, letting the implicit argument do its job):
   ```idris
   public export
   ex4 : Equal () ()
   ex4 = Refl
   ```

#### The double-edged sword of implicit arguments

The last 2 examples show why implicit arguments are useful, but also how they
can lead to confusion in proof types: the `Refl` used in `ex3` _looks_ the same
as the `Refl` used in `ex4`, but since the implicit arguments are different,
they are actually different `Refl` calls (we see this in the type declaration).

On the flip side, when we know two things are equal, it is enough to express
that in the type, and then as long as they actually are equal, the implicit
argument takes care of the rest. That's pretty handy!

#### Shorthand for `Equal`

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

This lets us use `===` in the middle of expressions where we would have used
`Equal` instead, e.g.:

```idris
public export
ex5 : 3 === 3
ex5 = Refl
```

And just to show how equality proofs (and Idris) are actually quite powerful,
here's an example with computation:

```idris
public export
ex6 : (1 + 2 * 3) === 7
ex6 = Refl
```

### Whooa, we're halfway there!

We've had one proof, yes. But what about second proof?

I'm glad you asked! We're trying to get to decidable equality. Which means we'll need a proof of
things being equal (we've just seen that) **and** a proof of things _not_ being
equal. Let's try to do that second part next.

### Proofs of False

To prove that something is false, we might try to write:

```idris
falseAttempt1 : (2 === 3) === False
```

But we cannot implement this! There is no way to call `Refl` to obtain the
expression `(2 === 3)`, which we need to show is `False`. (This is actually
somewhat reassuring, since it suggests our approach to proofs is sound.)

Now we might be tempted to write:

```idris
falseAttempt2 : (2 == 3) === False
```

And while we might be able to implement this, it would actually not guarantee
anything about our values! All it would prove, was that the _function call_
`2 == 3` returned `False`. Which, as we saw at the beginning, guarantees
nothing... Are we stuck? Only somewhat. We just need a different approach.

#### False cannot be

What we need is some datatype which captures the concept of "false" or "untrue".
In logic and type-theory, we often call this "bottom" or "void" and write it
"⊥".  Now the question is "How on Earth do we express this as a datatype?"
Especially in terms of constructors: What arguments would those even take??

Well, if we think slightly more maths-y (this may be a blessing or a curse,
depending on how much you enjoy logic and proof-theory), a common approach is
"proof by contradiction": If we assume p to be true and we then arrive at a
contradiction, it would be silly to keep going; our assumption was false.

A different way to say "our assumption was false" is: "we could never write (or,
_construct_) that assumption according to our logic". Now that's beginning to
sound more like something we can define in Idris!

#### The representation of false

We need a datatype which captures something we cannot construct; an untrue
statement... Well, the easiest way to do that would just be to not provide any
constructors, no? Then there's nothing to call, so we can't construct the
datatype! Let's try that!

```idris
public export
data Void : Type where
```

This is a perfectly valid datatype declaration, we can "forward-declare" data
definitions just like we can for functions. Except if we never define any
constructors (neither here nor later) then we can never create something of type
`Void` but we can still talk about it.

Since we prove things by having instances of datatypes whose constructors can
only be called if certain conditions are met (like `Refl` for `Equal`), we can
never prove `Void`. This is great! How so? Well, in terms of logical reasoning
and proofs, you can never prove something false to be true either! (This might
sound obvious when put into English, but it's important to realise nonetheless).
There is nothing we can do to prove the statement "1 times 1 is 2" or that "the
square root of 2 is 1". <!-- Get out of here with your Terryology! -->

Since there are no constructors for `Void`, and we use constructors to prove
things, `Void` represents an untrue statement for which no proof can exist.
Pretty clever, no?


## Interlude

Whew!... That took a lot longer than I initially expected! I know I said the
fundamentals were challenging in their own right, but still...

If you're still with me, let's finally move on to what I actually promised this
would be about: decidable equality!


### Decidable Equality

<!--
Decidable equality, as the name implies, is a procedure for determining whether
two things are equal. In Idris, we use it when we want to prove that things are
equal or, in case they aren't, provide a counter-proof showing why they cannot
be equal. As with the proofs above, we capture this concept in a datatype:

```idris
public export
data Dec : Type -> Type where
  Yes : prop -> Dec prop
  No  : Not prop -> Dec prop
```

This expresses decidability over some property which is carried in the type. The
`Yes` constructor takes a proof of the property as an argument, and the `No`
constructor takes a proof that the property cannot hold (remember, `Not p` is
shorthand for `p -> Void`).

Now we can define decidable equality by simply declaring a function which
returns some `Dec` carrying a proof which uses `Equal`:
-->


### Beyond Equality: Custom Predicates


### Conclusion


### Acknowledgements

