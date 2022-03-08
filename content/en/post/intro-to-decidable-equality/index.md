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
date: 2022-03-08
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


## Decidable Equality

We've finally arrived! Decidable equality! Let's go!!!

### What is decidable?

So, what does it mean for something to be decidable? It means we can _decide_
whether that thing is true or not. Let's try to express that in a datatype!

```idris
data Decide : Type -> Type where
  ItHolds : (prf : p) -> Decide p
  Unsound : (contra : Void) -> Decide Void
```

And let's break it down to make sure we understand it:
- `data Decide : Type -> Type where` --- The `Decide` datatype depends on some
    `Type` (remember, we're using datatypes as proofs).
- `ItHolds : (prf : p) -> Decide p` --- The `ItHolds` constructor takes a proof
    of type `p`, and constructs a `Decide p` (effectively proving `p` held since
    we could pass an instance of it to `ItHolds`).
- `Unsound : (contra : Void) -> Decide Void` --- Expresses something which
    cannot be (we would be passing some `Void` to it, but `Void` cannot exist so
    this statement is unable to be proven, i.e. 'false').

So far so good: We have a datatype for reasoning about decidable properties. Now
let's try to use it!

### Trying to use `Decide`

Our `Decide` datatypes technically models _any_ decidable property, so in order
to arrive at decidable _equality_, we need to combine it with `Equals`. As we
saw while covering the fundamentals, `Equals` describes a relationship between
two things, so we'll also need two things which can be equal. An easy example is
`Nat`s:

```idris
decideEquals : (n : Nat) -> (m : Nat) -> Decide (n === m)
decideEquals 0     0     = IsSound Refl
decideEquals 0     (S j) = ?decide_rhs_2
decideEquals (S k) 0     = ?decide_rhs_3
decideEquals (S k) (S j) = ?decide_rhs_4
```

So far so good. We've case-split the function into the various options, and
successfully proved the first case: if both arguments are 0, then we know that
there is a sound proof of equality, which in this case is `Refl`.

However, if we try to implement any of the other holes, we run into some
trouble. Consider the types of `?decide_rhs_2` and `?decide_rhs_3`:

```idris
-- ?decide_rhs_2 : Decide (Equal 0     (S j))
-- ?decide_rhs_3 : Decide (Equal (S k) 0    )
```

We know these proofs cannot exist, and we have a concept for that: the `Unsound`
constructor, right? Well yes but actually no. If we try to introduce `Unsound`
on the right hand side of `decide 0 (S j)` Idris (rightfully) complains:

```idris
-- decideEquals 0     (S j) = Unsound ?decide_rhs_2

--- Error: While processing right hand side of decide. When unifying:
---     Decide Void
--- and:
---     Decide (0 === S j)
--- Mismatch between: Void and Equal 0 (S j).
```

When we defined `Decide`, we defined that `Unsound` takes an argument of type
`Void` but we're trying to construct an `Equal 0 (S j)`. These are clearly not
the same types (although they are both impossible). Thing is, as we went over
when defining `Void`, there is _no way_ we can pass `Unsound` something of type
`Void`! `Void` cannot be constructed; that was kinda the whole idea... A similar
issue pops up if we try using `Unsound` in the `decide (S k) 0` case.

This is a problem... We've defined something which models the impossible
(`Void`), but in order to use it we currently need to prove the impossible. This
is contradictory. Are we stuck?

### The solution: expressing contradictions

We are not stuck (at least, not completely). We just need to rethink a couple of
things. Remember I talked about proof by contradiction? (It was a while back, I
don't blame you if you don't). Those are our way out!

In case you need a refresher, the tl;dr for proofs by contradiction is:

1. Make an assumption,
2. show that from there you arrive at some contradiction,
3. this means your assumption must be false,
4. you're done. Hurray!

What we've expressed with `Void` is something impossible. But we haven't
actually expressed _how_ something might be impossible. There needs to be a link
between impossible things and the `Void` datatype.

#### The missing link

Sticking to our example of deciding if two `Nat`s are provably equal, let's
define a case where `Nat`s are provably _not_ equal. But this time, via proof by
contradiction.

We'll start with `(S k) ≠ 0`, i.e. it is impossible for the successor of a
number to be zero. We need to express this as a proof by contradiction... How
about "If I can prove that `(S k)` is `0`, then I have done the impossible"?
That sounds pretty accurate, don't you think? Let's write that in Idris!

```idris
public export
succNotZero : (prf : (S k) === 0) -> Void
```

Now the question becomes "How do we implement this?". We, the programmers, know
that it is not possible. When we were coming up with `Void`, we saw that
definitions based on unsound proofs of equality cannot be defined since we
cannot match on the proof (it doesn't exist). But how do we communicate this to
Idris?

#### Impossible definitions

For things where there is no way to define them, Idris provides the `impossible`
keyword. This tells the type-checker "Hey! Here, in this expression, there
should be no way whatsoever to make this type-check". So if we want to provide a
definition for `succNotZero`, we can write:

```idris
succNotZero Refl impossible
```

And Idris is happy with this: There is no way to pass the implicit argument to
`Refl`, which means we cannot pattern-match on the argument, which means we
cannot construct `Void`. Well, that's what we've been trying to say all along!
Fantastic!

#### The trick to counter-proofs

The trick to counter-proofs is functions which return `Void`. We saw this when
proving the successor of a `Nat` cannot be zero, and we can also use it to prove
that zero cannot be the successor of a `Nat`:

```idris
public export
zeroNotSucc : (prf : 0 === (S j)) -> Void
zeroNotSucc Refl impossible
```

Since `Void` cannot be constructed, neither can the argument(s) to a function
which returns `Void` (or we'd be able to return something from it). Hopefully
you agree that this is a proof by contradiction:

1. We started out with an assumption (e.g. `0 === (S j)`),
2. expressed that this was contradictory (given the proof, we could construct
   `Void` --- "construct `Void`" is a contradiction in terms),
3. so our assumption must be false (`Refl impossible`).
4. Idris agrees, since it cannot find a solution to the implicit argument for
   `Refl`. Hurray!

### Decidable with proof-by-contradiction

With that cleared up, let's make a better definition of something decidable. We
previously had that `Decide` was either a proof or something impossible. Let's
refine that definition to:

Something decidable is either a proof, or something which _should be_
impossible (i.e. a contradiction).

Let's put this in a datatype, shall we?

```idris
public export
data Dec : Type -> Type where
  Yes : (prf : prop)            -> Dec prop
  No  : (contra : prop -> Void) -> Dec prop
```

The change here is that for the case where the property provably doesn't hold,
we provide a `contra` which explains _how_ the property cannot hold. Oh and
we've renamed the constructors to `Yes` and `No`. It's a lot easier to read (and
shorter to write).

### Decidable equality (for real this time)

### Proving things impossible is _hard_

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


## Beyond Equality: Custom Predicates


## Conclusion


## Acknowledgements

- the hacker known as "Alex" (aka. mangopdf), for making me realise I was
    [writing a textbook when I didn't need to](https://mango.pdf.zone/i-give-you-feedback-on-your-blog-post-draft-but-you-dont-send-it-to-me)

