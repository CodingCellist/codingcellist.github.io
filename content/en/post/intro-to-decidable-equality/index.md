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

By the way, this post is also a Literate Idris file, which means you can load
[the markdown it's based on](/files/DecEqIntro.md)
at the REPL and try using the functions it defines!


## What we're aiming for

The goal at the end of this journey, is to be able to write the `Dec` interface
(which models properties that either provably hold or provably _cannot_ hold)
and some instances of it. However, in order to do this we need to understand and
implement certain other things like `Equal` and `Void`.

Worry not! This will all become clear in due course!


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

%hide Builtin.Equal
%hide Builtin.Refl

%hide Builtin.sym
%hide Prelude.prim__void
%hide Prelude.void
%hide Prelude.absurd

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
decideEquals 0     0     = ItHolds Refl
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
--- ?decide_rhs_2 : Decide (Equal 0     (S j))
--- ?decide_rhs_3 : Decide (Equal (S k) 0    )
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

We'll start with `(S k) ≠ Z`, i.e. it is impossible for the successor of a
number to be zero. We need to express this as a proof by contradiction... How
about "If I can prove that `(S k)` is `0`, then I have done the impossible"?
That sounds pretty accurate, don't you think? Let's write that in Idris!

```idris
public export
succNotZero : (prf : (S k) === Z) -> Void
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
zeroNotSucc : (prf : Z === (S j)) -> Void
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

With a refined, and crucially more usable, datatype, let's have a go at using it
to define decidable equality again. As before, we'll use `Nat`s and start by
case-splitting on the arguments:

```idris
decNat : (m : Nat) -> (n : Nat) -> Dec (m === n)
-- decNat 0     0     = ?decNat_rhs_1
-- decNat 0     (S j) = ?decNat_rhs_2
-- decNat (S k) 0     = ?decNat_rhs_3
-- decNat (S k) (S j) = ?decNat_rhs_4
```

The first case is trivial, 0 is equal to itself:

```idris
decNat 0     0     = Yes Refl
```

The second and third cases are false, so we start by prefixing them with `No`:

```idris
-- decNat 0     (S j) = No ?decNat_rhs_2
-- decNat (S k) 0     = No ?decNat_rhs_3
```

Now you'll notice that rather than complaining, Idris provides the following
types for the holes:

```idris
--- decNat_rhs_2 : Equal 0     (S j) -> Void
--- decNat_rhs_3 : Equal (S k) 0     -> Void
```

Now that's something we can work with! With our refined `Dec` datatype, we don't
have to provide the impossible, we just have to provide a proof that the
property arrives at a contradiction! Even better, we've already defined the two
counter-proofs!

```idris
decNat 0     (S j) = No zeroNotSucc
decNat (S k) 0     = No succNotZero
```

#### The non-trivial case

For the final case, we run into a small problem: How do we deal with two
non-zero numbers which _might_ be equal?

```idris
decNat (S k) (S j) = ?decNat_rhs_4
```

We can't just stick a `Yes` in there, since we don't know if `k` equals `j`...
In order to figure this out, we first need some more information about `k` and
`j`, so let's recurse:

```idris
-- decNat (S k) (S j) = case decNat k j of
--                           (Yes prf) -> ?decNat_rhs_5
--                           (No contra) -> ?decNat_rhs_6
```

This helps us a bit: If we know `k === j` (the `Yes prf` case), then `(S k) ===
(S j)`; we've just proved that `k` and `j` are the same number, after all.
Similarly, if we can prove that `k` and `j` being the same would lead to a
contradiction, then using `S` shouldn't change that.

Let's put that in the case expression, and then inspect the holes:

```idris
-- decNat (S k) (S j) = case decNat k j of
--                           (Yes prf) -> Yes ?decNat_rhs_5
--                           (No contra) -> No ?decNat_rhs_6
```

#### More missing links

For the first hole, we get:

```idris
---   k : Nat
---   j : Nat
---   prf : Equal k j
---  ------------------------------
---  decNat_rhs_5 : Equal (S k) (S j)
```

So we have a proof that `k === j`, but we want a proof that `(S k) === (S j)`.
Seems like we need some way to link `prf` and `S`, which we don't at the moment.
Let's come back to that after looking at the `No` case:

```idris
---  k : Nat
---  j : Nat
---  contra : Equal k j -> Void
--- ------------------------------
--- decNat_rhs_6 : Equal (S k) (S j) -> Void
```

Hmm... Here we have a proof that if `k === j`, we'd have a contradiction. But we
want a proof that if `(S k) === (S j)` we'd have a contradiction. This also
seems like we need a link to `S`, which we don't have at the moment...

### We were on the verge of greatness

Unfortunately, missing the two links to `S` means we can't quite complete the
definition for `decNat`. Without them, there is no way to convince Idris that
one proof (or counter-proof) leads to the next. This is a problem, but
thankfully one which is not too difficult to solve.

{{< spoiler text="Side note on `rewrite`..." >}}
The builtin equality in Idris supports this thing called `rewrite`. It lets us
use a proof to update the rhs, like so:

```idris
-- decNat (S k) (S j) = case decNat k j of
--                           (Yes prf) -> rewrite prf in Yes Refl
--                           (No contra) -> No ?decNat_rhs_6
```

Here, `rewrite` has used the proof `prf` (which shows that `k` and `j` are
equal) to show that it is fine to construct the `Refl` for `(S j)`.
Unfortunately, `rewrite` is slightly magic and _requires_ the builtin equality.
So we can't use it with our own equality (although the two are identical) and we
have to do things by hand.
{{< /spoiler >}}

Well then. Let's make the final push!

#### Linking `k === j` and `S`

First things first: The missing link between equality and the successor
function. If `k` and `j` are the same, then applying `S` doesn't change that.
For the mathematically inclined, this is also known as the "injective" property:

```idris
public export
succInjective : (prf : k === j) -> (S k) === (S j)
```

This definition gets interesting! If we start by defining:

```idris
-- succInjective prf = ?succInjective_rhs
```

Then the type of the hole becomes:

```idris
---  0 k : Nat
---  0 j : Nat
---  prf : Equal k j
--- ------------------------------
--- succInjective_rhs : Equal (S k) (S j)
```

Which isn't very helpful; it's just re-told us what we're trying to prove.
**However,** if we now case-split on `prf`, the picture suddenly changes:

```idris
-- succInjective Refl = ?succInjective_rhs_0

---  0 k : Nat
---  0 j : Nat
--- ------------------------------
--- succInjective_rhs_0 : Equal (S j) (S j)
```

What's happened?? Suddenly we only care about `j`! This is because matching on
`Refl` tells us something _about_ `k` and `j`: `Refl` only takes a single
argument, so by pattern-matching on `Refl`, Idris can deduce that `k` and `j`
must have been the same (or we wouldn't have been able to call `Refl`; just like
with `MkBronze`!!). This is supremely useful, since `Equal (S j) (S j)` is
trivial to prove:

```idris
succInjective Refl = Refl
```

Once again, the implicit arguments confuse us here: The left hand side (lhs) and
the right hand side (rhs) look identical, but the `Refl` on the lhs is actually
`Refl {x=j}` and the `Refl` on the rhs is actually `Refl {x=(S j)}`. Idris can
figure this out automatically which saves us some typing but admittedly looks a
bit confusing. Trust me when I say it's worth it. Especially for bigger proofs.

#### Linking `k === j -> Void` and `S`

With `k === j -> (S k) === (S j)` defined, can we take a similar approach to the
counter-proof? I don't see why not! If we have one contradiction, then mixing
`S` doesn't magically fix things, it just leads to another contradiction:

```idris
public export
succDiffers : (contra : k === j -> Void) -> (sPrf : (S k) === (S j)) -> Void
```

Another way to read this type is "If I know that `k === j` is nonsense, but at
the same time someone has given me a proof that `(S k) === (S j)`, then that
proof must also be nonsense!".

Like with `succInjective`, our initial definition doesn't match on anything but
let's us inspect the type of the rhs.

```idris
-- succDiffers contra sPrf = ?succDiffers_rhs

---  0 k : Nat
---  0 j : Nat
---    sPrf : Equal (S k) (S j)
---    contra : Equal k j -> Void
--- ------------------------------
--- succDiffers_rhs : Void
```

_Ah, mince!_ We need to return `Void` here, but we know that that's impossible!
Is all lost? Not quite. If we try matching on `sPrf` (the proof that `S`
magically fixed things) we get:

```idris
-- succDiffers contra Refl = ?succDiffers_rhs_0

---  0 k : Nat
---  0 j : Nat
---    contra : Equal j j -> Void
--- ------------------------------
--- succDiffers_rhs_0 : Void
```

Exactly _how_ does this help us? Well, we now know that `(S k)` and `(S j)` were
the same (that's what `sPrf` was telling us) so `k` and `j` must have been the
same. But we also have a counter-proof, a function, showing us that _if_ that's
the case, then we have a contradiction. We can apply this to dismiss the proof
as nonsense (or rather, show that the other proof _also_ arrives at a
contradiction):

```idris
succDiffers contra Refl = contra Refl
```

#### Why don't we break the rules already?

Have we beaten the system? Have we returned `Void`? No! `contra` is impossible;
there is no way to give its body a definition. What we have done is explained to
Idris that "if I somehow give you a `contra : j === j -> Void` and a
`Refl {x=(S j)}`, then I have broken the rules and we can use that `contra` to
return `Void`".

This is a very important thing to be able to show. It shows that breaking the
rules in one place results in them being broken everywhere. If we take a false
statement as true (i.e. have it exist as a function), then our entire system of
reasoning becomes unsound and we can do silly things like construct `Void` from
this statement.

Continuing to prove things _after_ we have shown there is a contradiction is
nonsensical.

### Decidable equality (for real real this time)

With all the missing links now in place, we can finally, actually define
decidable equality for natural numbers. No more tricks or princesses in other
castles, I promise.

```idris
public export
decEqNat : (m : Nat) -> (n : Nat) -> Dec (m === n)
decEqNat 0     0     = Yes Refl
decEqNat 0     (S j) = No zeroNotSucc
decEqNat (S k) 0     = No succNotZero
{-
decEqNat (S k) (S j) = case decEqNat k j of
                            (Yes prf) = Yes ?decEqNat_rhs_5
                            (No contra) = No ?decEqNat_rhs_6
-}
```

That was where we left off last time. Except now that we have shown that there
are links between proofs and counter-proofs and `S`, we can complete the
definition by applying these as relevant:

```idris
decEqNat (S k) (S j) = case decEqNat k j of
                            (Yes prf) => Yes (succInjective prf)
                            (No contra) => No (succDiffers contra)
```

This final case shows that if we have _proved_ `k` and `j` to be equal, then a
proof for "Are `(S k)` and `(S j)` equal?" is decidably `Yes`, and we obtain the
relevant proof via `succInjective`.

And vice-versa, if we have proved that `k` and `j` _cannot_ be equal, then we
can use that counter-proof to construct another one using `succDiffers`, which
shows that `(S k)` and `(S j)` cannot be equal. And with that, the answer is
decidably `No`.


## We did it!

That's decidable equality. Having `Refl` and `Void` allows us to write functions
which can tell if two things are equal along with explaining _how_ they are
equal (or how they _cannot possibly_ be equal). This is only possible thanks to
dependent types, which lets us describe relationships between data in the type
of things. Without it, we do not get any guarantees from the return types of
functions.

Coming back to the very start where we were looking at `==`. If we now compare
the types of two functions for comparing `Nat`s:

```idris
boolEqNat : (m : Nat) -> (n : Nat) -> Bool

decEqNat' : (m : Nat) -> (n : Nat) -> Dec (m === n)
```

(I've had to call the function `decEqNat'` since we already have `decEqNat`).

We can see that the _type_ of the function now provides a relationship between
the inputs.  Where `Bool` doesn't have any mention of whether it's actually
looking at `m` and `n`, `Dec` explicitly mentions `m` and `n` _and_ states that
the function will return a proof datatype relating them, if it returns a `Yes`.
That's pretty cool, no?

### It _is_... but that sure took a while!...

Yeah, sorry about that. This took 4-5 times as long as I thought it would. For
those bits where I went "ah but first, we actually also need [...]", that was
genuinely me getting caught off-guard having forgotten a thing.

I hope that you still think it was worth it, and that you now understand both
the concept and inner workings of decidable equality. Thanks for reading along!
 : )


## Acknowledgements

- Zoe Stafford (z-snails/z_snail) and Guillaume Allais (gallais) for help with
    understanding `rewrite` and `void`.
- the hacker known as "Alex" (mangopdf), for making me realise I was
    [writing a textbook when I didn't need to](https://mango.pdf.zone/i-give-you-feedback-on-your-blog-post-draft-but-you-dont-send-it-to-me)


## Would you like to know more?

Really? You've not had enough?... Alrighty then!

(note: be aware that this will be a lot more crash-coursey than the previous
stuff, since this blog entry is already extremely long)

### Generalising stuff

You may not be surprised to hear that there are general ways of defining
pretty much all of the above. Generalising is what logicians do best, after all.
Without further ado, let's get to it!

#### Generalising decidable equality

Decidable equality is a thing we can define for lots of types. So it would be
nice to be able to just use a general function, e.g. `decEq`, for all these
types. I got ya fam!

```idris
public export
interface DecEq ty where
  decEq : (a : ty) -> (b : ty) -> Dec (a === b)
```

Now anything that implements the `DecEq` interface has to specify an
implementation of the `decEq` function, which will describe how to prove (and
how to disprove) equality between two members of the type. And then you can just
use `decEq` whenever you need a proof of equality for some type which implements
it. Neat!

#### Generalising contradictions

We saw how to state that an expression cannot be made to type-check using the
`impossible` keyword. When this applies to a datatype in general, we say that
the type is "_uninhabited_". Constructing an uninhabited type is a
contradiction, so we define the following interface:

```idris
public export
interface Uninhabited ty where
  uninhabited : ty -> Void
```

This enforces that uninhabited types must be able to show that a contradiction
occurs, e.g. using `impossible`:

```idris
public export
Uninhabited (True === False) where
  uninhabited Refl impossible

public export
Uninhabited (False === True) where
  uninhabited Refl impossible
```

#### Generalising counter-proofs

If we can generalise contradictions, can we also generalise counter-proofs? Why
yes, we can!

We've discussed that once we have `Void`, anything goes (aka. it is pointless to
continue after a contradiction has been found). The generalisation of this
requires a tiny amount of trickery:

```idris
public export
void : (0 v : Void) -> a
void v = assert_total $ idris_crash "ERROR: Called 'void'"
```

The type of the function captures that from `Void` we can construct anything.
However, the function definition crashes Idris with the given error message,
whilst also asserting to the totality-checker that doing so is total. **We are
subverting the totality-checker here**, but it is okay (necessary, even) because
we should never be able to call `void` (we can only call it if we have a
`Void`) and if we somehow _do_ call `void`, the user should definitely know
something has gone horribly wrong!

In the Idris source code, `void` is defined in terms of `prim__void` which is an
external function. However, all external implementations of `prim__void` crash
the runtime they target, so the definitions are effectively equivalent.

#### That's absurd!

To finish generalising counter-proofs, we need one more thing: A link to
generalised contradictions. Since a `Void` lets us construct anything and
constructing `Void` is impossible, we call any type that lets us do this
`absurd`:

```idris
public export
absurd : Uninhabited ty => ty -> a
absurd u = void (uninhabited u)
```

This `absurd` function expresses that if we have some instance of something
`Uninhabited`, then that's the same as having constructed `Void` (since
uninhabited means the type cannot exist).

#### This is generally nice

The `DecEq` and `Uninhabited` interfaces, combined with the `absurd` function,
allow us to write `Dec` things more nicely (if we can define the interfaces for
the type):

```idris
public export
DecEq Bool where
  decEq False False = Yes Refl
  decEq False True  = No absurd
  decEq True  False = No absurd
  decEq True  True  = Yes Refl
```

Look at how nice and simple that implementation is! It's so much easier to read
than writing out custom proofs.

### And this, is to go even further beyond!

Simple equality is not always the most interesting. Quite often, it is more fun
to reason about more complicated properties of more complex structures. And that
is totally possible! As long as you're willing to do the work...

```idris
public export
data Repetition : a -> List a -> Type where
  Just : Repetition x [x]
  More : (x : a) -> Repetition x xs -> Repetition x (x :: xs)
```

Here we have a proof showing that a list `xs` consists purely of repetitions of
`x`. It's slightly a toy example, but it illustrates the point of being "willing
to do the work" quite well.

We'd like to just write:

```idris
-- isRepetition : DecEq a => (x : a) -> (xs : List a) -> Dec (Repetition x xs)
```

But, as with natural numbers, we need some intermediary proofs before we can do
that. Except, this time we've thrown a `List` into the mix! How is that a
problem? Well, proofs over lists can fail in multiple places: either the head
(the first element), or somewhere in the tail (the following elements). This
means there's a lot more to prove before we can write the final decidable thing.

```idris
public export
Uninhabited (Repetition x []) where
  uninhabited Just impossible
  uninhabited (More x ys) impossible
```

The easiest is to prove that we cannot have a repetition if the list is empty.
There is no way to call either of the constructors, so we simply use
`Uninhabited` and `impossible`. So far, so good.

Next, let's try the positive cases. If we have a proof that `x` is the same as
`y`, then we can put that in a singleton list for `Repetition` purposes:

```idris
public export
singletonRep : (prf : x === y) -> Repetition x [y]
singletonRep Refl = Just
```

Matching on `Refl` makes Idris recognise that the two are the same thing, so we
can call `Just` without any problem; we only have one thing, which we can put in
a list.

With that taken care of, let's show that if `x` is the same as `y`, and we have
an existing repetition of `x`, then we can extend the repetition to one more
element:

```idris
public export
allGood :  {x : _}
        -> (another : x === y)
        -> (rep : Repetition x (z :: xs))
        -> Repetition x (y :: (z :: xs))
allGood Refl rep = More x rep
```

Again, matching on `Refl` makes Idris realise that `x` and `y` are the same
thing, and we already know that `(z :: xs)` is just a repetition of `x`, so we
can extend it with the extra `x` using `More`.

{{< spoiler text="Another side note on `rewrite`..." >}}
If we weren't defining everything from scratch, we could use `rewrite` to prove
the positive cases. We wouldn't define intermediary proofs for each and every
one of the positive cases. But unfortunately for us, we _are_ defining
everything from scratch, and so we need these extra positive proofs.

Ah well. It's probably good for the soul or something.
{{< /spoiler >}}

### Proving things impossible is _hard_

We've shown that we can prove things to be okay for a this more complicated
property, but what about the cases where things are not okay? Well, those are
pretty difficult: We don't need to show that it is unlikely to succeed, we need
to show that it is _guaranteed_ to fail!

We'll start with showing that if `x` _cannot_ be the same as `y`, then a proof
of repetition involving both (where `y` was the first element in the list) is a
contradiction:

```idris
public export
headDiffers :  (contra : (x === y) -> Void)
            -> (prf : Repetition x (y :: _))
            -> Void
headDiffers contra Just = contra Refl
headDiffers contra (More x _) = contra Refl
```

This is already more confusing than the positive proofs. In the first line of
the definition, we have a singleton list containing `y` as a repetition of `x`
(meaning they are equal), but we also proved that `x` doesn't equal `y`, so we
can show that the `Refl` used for the repetition must be contradictory.

In the second line of the definition, we have the same thing, except there's
more than one element in the list involving `y`. However, the other elements are
irrelevant since we know the first one forms a contradiction. So we use the
first element to show that the `Refl` used for the repetition must be
contradictory.

Now let's do the tail case: If we have a proof that some repetition of `x` is
actually a contradiction, then it doesn't matter if we extend the repetition,
it'll still contain a contradiction!

```idris
public export
tailDiffers :  (contra : Repetition x (z :: xs) -> Void)
            -> (prf : Repetition x (y :: (z :: xs)))
            -> Void
tailDiffers contra (More x absurdTail) = contra absurdTail
```

We can only match on `More` since `(y :: (z :: xs))` is not a singleton list (it
has at least 2 elements). And when matching on `More`, we also gain access to
the sublist that we know contains a contradiction! So we just refer to that
contradiction.

### Plus ça change...

Finally, let's put together the `isRepetition` function. Note that we could not
have written this definition if we'd missed _any_ of the steps above...

```idris
public export
covering
isRepetition : DecEq a => (x : a) -> (xs : List a) -> Dec (Repetition x xs)

isRepetition x [] = No absurd

isRepetition x (y :: []) =
  case decEq x y of
       (Yes prf) => Yes (singletonRep prf)    -- rewrite prf in Yes Just
       (No contra) => No (headDiffers contra)

isRepetition x (y :: (z :: xs)) =
  case decEq x y of
       (Yes headOK) =>                        -- rewrite headOK in case...
          case isRepetition x (z :: xs) of
               (Yes tailOK) => Yes (allGood headOK tailOK)  -- rewrite tailOK...
               (No contra) => No (tailDiffers contra)

       (No contra) => No (headDiffers contra)
```

This may look familiar to the other `Dec` function we wrote, and that's because
it is! The general strategy for writing these is the same, but the intermediary
steps and proofs/lemmas/functions are really where things get hairy. A good rule
of thumb is "If it seems trivial, prove it!!" -- chances are you'll need that
trivial (counter-)proof at some point in your more involved proofs.


## That's all folks!

Genuinely this time. If there's more you want to learn, I strongly encourage you
to experiment with datatypes for custom properties and proving these! You'll
likely get it wrong, both your datatypes and the properties involving them, but
that's just part of the _"Type, define, refine"_ mantra of Idris.

gl hf!

