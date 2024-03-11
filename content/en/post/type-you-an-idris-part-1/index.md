---
# Documentation: https://wowchemy.com/docs/managing-content/

title: "Type You an Idris – Part 1: Warmup"
subtitle: ""
summary: "The best way to learn & understand a thing is to implement it. So
          let's implement (a subset) of Idris2! This part is an introduction and
          covers some function exercises that will help later."
authors: [thomas-e-hansen]
tags: [type-you-an-idris, splv2020, idris2, type-theory, functional-programming]
categories: []
date: 2022-09-02
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

I've personally struggled with properly understanding the internals of Idris2.
By "properly", I mean: knowing where to look when I encounter errors,
understanding what people in the Idris community refer to when discussing
certain concepts and parts of Idris, knowing what the intermediary
representations are for implementing custom backends, that kind of stuff. Every
time I've encountered these in the past, I've gone "I really ought to learn this
at some point!", and then promptly gotten distracted by a project or some
reading I was doing.

So now, just short of 2 years into my PhD, armed with at least _some_
understanding of the underlying concepts and terms, I've decided to try and jump
back in to Edwin's course from the Scottish Programming Language and
Verification Summer School (SPLV) in 2020, which has you implement `TinyIdris`
--- a scaled down version of full Idris. When I attended this live, I hadn't
even technically started yet, so the whole thing was a bit overwhelming and
above my level; hopefully this time it's manageable.

If you're also confused, or just want to know more, come along for the ride!

(oh, and in case you just want to watch the course, it is on
[this YouTube playlist](https://www.youtube.com/playlist?list=PLmYPUe8PWHKqBRJfwBr4qga7WIs7r60Ql))

{{< toc >}}

## Setting up

First, we'll need a copy of the starting source code for TinyIdris. Use `git` to
clone it to a directory of your choice (I've gone with `splv20-tinyidris`):

```sh
$ git clone git@github.com:edwinb/splv20 splv20-tinyidris
```

Next, if you're running a reasonably recent version of Idris2
(⩾ v0.5.0), you'll need to apply [this patch](/uploads/splv20-v0.5.1.patch)
using `git apply` from the root of the directory where you checked out the
repository. The reason for is that there were a number of changes in v0.5.0
which meant the following needed fixed in TinyIdris before it would even build:

* `Data.Strings` has been renamed to `Data.String`.
* The type `k` of `kind` is used in numerous places without being runtime
    accessible.
* A lot of functions discarded their result implicitly in `do` notation, which
    is no longer allowed (and we can't just stick an `ignore` in front because,
    for performance reasons, `Core` is not an implementation of `Monad`).
* `Data.List1.toList` has been generalised to `Prelude.Foldable.toList` (so
    just `toList`).
* `Data.List1` now uses `:::` as a constructor, not `::`, meaning that we can't
    pattern-match on `[p']` or similar since it desugars to `p' :: []`. Instead,
    we need to match on `(p' ::: [])`. There were also some similar problems in
    terms of constructing and returning new `List1`s.
* `Show` is now `total`, but this introduces some... _difficulties_ when
    implementing it for certain datatypes. A solution is to just stick a
    `covering` at the top of the function declaration.
* A couple of functions in `Core.Env` use `tm` from `Weaken tm` without
    declaring that `tm` is implicit and with ω-multiplicity
    (runtime accessible).
* Updating `record`s via the
    ```idris
    record { field = val } r
    ```
    syntax is deprecated in favour of
    ```idris
    { field := val } r
    ```
    and similar for
    ```idris
    record { field $= fun } r
    ```

With the patch applied, we're ready to build TinyIdris, when we eventually get
to that. For now, let's start with the Warmup Exercises.

(note: in this post, I'll assume you're familiar with interactive editing since
it makes life so much easier. If you're not, check out the Type-Development with
Idris book, or the
[Idris editor wiki](https://github.com/idris-lang/Idris2/wiki/1-%5BLanguage%5D-Editor-support).)


## Exercise 1 - Equalities

This exercise is just to get into Idris again: A bit of equality and proofs.

### Part 1: Name equality

First, we need to write an `Eq Name` implementation. Here, the interactive
editing can help us a lot: Let's start by giving a base definition of `==` (I
prefer to implement these like any other function, i.e. putting `==` in
parentheses. If you prefer infix notation, then by all means use that):

```idris
Eq Name where
  (==) n1 n2 = ?eq_rhs
```

Case-splitting on `n1` and then on `n2` gives us:

```idris
Eq Name where
  (==) (UN x)   (UN y)   = ?eq_rhs_2
  (==) (UN x)   (MN y z) = ?eq_rhs_3
  (==) (MN x y) (UN z)   = ?eq_rhs_4
  (==) (MN x y) (MN z w) = ?eq_rhs_5
```

I hope you'll agree that a sensible definition of `Eq Name` is that it only
makes sense to compare user-written names and machine-generated names
respectively; no cross-comparing. So let's delete lines 3 and 4, and introduce a
catch-all pattern for those cases (and rename the constructor arguments
slightly, to make it easier to see what's going on):

```idris
Eq Name where
  (==) (UN x)   (UN y)   = ?eq_rhs_2
  (==) (MN x i) (MN y j) = ?eq_rhs_5
  (==) _        _        = False
```

Now all that remains is to fill in the definitions. `UN`s (`U`ser written
`N`ames) are equal iff their names match, and `MN`s (`M`achine written `N`ames)
are equal iff their names and number match:

```idris
Eq Name where
  (==) (UN x)   (UN y)   = x == y
  (==) (MN x i) (MN y j) = x == y && i == j
  (==) _        _        = False
```

### Part 2: Provably equal names

Proving that two `Name`s are equal is a bit more complicated. Although,
thankfully, this is not a `DecEq` (_decidable_ equality) implementation, which
means we don't need to prove how it is impossible for the `Name`s to be equal.

{{< spoiler text="If you are uncertain about proofs, `DecEq`, etc..." >}}
If you are uncertain about `DecEq`, proofs, and contras, I've written an intro
(well, more of a complete explanation) to proof-by-datatype and decidable
equality which you can find in
[this blog post](/en/post/intro-to-decidable-equality).
{{< /spoiler >}}

Again, start by interactively generating a definition, then case-splitting on
the arguments, and introducing a generic pattern match for different types of
`Name`s:

```idris
nameEq : (x : Name) -> (y : Name) -> Maybe (x = y)
nameEq (UN x)   (UN y)   = ?nameEq_rhs_2
nameEq (MN x i) (MN y j) = ?nameEq_rhs_5
nameEq _        _        = Nothing
```

Let's start with `UN`s. Idris comes with built-in decidable equality for
`String`s, so let's use that! If two names' strings are decidedly equal, then
the `Name`s must be too. Recall that `Refl` is a proof of equality, and that
`rewrite` lets us use proofs to transform the type of the right hand side:

```idris
nameEq : (x : Name) -> (y : Name) -> Maybe (x = y)
nameEq (UN x)   (UN y)   =
  case decEq x y of
       (Yes prf)   => rewrite prf in Just Refl
       (No contra) => Nothing

nameEq (MN x i) (MN y j) = ?nameEq_rhs_5
nameEq _        _        = Nothing
```

We can use a similar approach with `MN`s. It'll be a bit longer, since it'll
require 2 `case`-blocks and `rewrite`s, but you should hopefully already have
guessed its layout. Here it is:

```idris
nameEq : (x : Name) -> (y : Name) -> Maybe (x = y)
nameEq (UN x)   (UN y)   =
  case decEq x y of
       (Yes prf)   => rewrite prf in Just Refl
       (No contra) => Nothing

nameEq (MN x i) (MN y j) =
  case decEq x y of
       (Yes prfXY) => case decEq i j of
                           (Yes prfIJ) =>
                                rewrite prfXY in rewrite prfIJ in Just Refl
                           (No contra) => Nothing
       (No contra) => Nothing

nameEq _        _        = Nothing
```

### Part 3: _Decidably_ equal names

Remember how I just said we thankfully didn't have to implement `DecEq Name`?
Psych! That's part 3 ^^

Let's start as usual (case-splitting, etc.):

```idris
DecEq Name where
  decEq (UN x)   (UN y)   = ?decEq_rhs_2
  decEq (UN x)   (MN y j) = ?decEq_rhs_3
  decEq (MN x i) (UN y)   = ?decEq_rhs_4
  decEq (MN x i) (MN y j) = ?decEq_rhs_5
```

If we take the same approach as for `nameEq`, we see the problem:

```idris
DecEq Name where
  decEq (UN x)   (UN y)   =
    case decEq x y of
         (Yes prf)   => rewrite prf in Yes Refl
         (No contra) => No ?decEq_rhs_7

  decEq (UN x)   (MN y j) = ?decEq_rhs_3
  decEq (MN x i) (UN y)   = ?decEq_rhs_4
  decEq (MN x i) (MN y j) = ?decEq_rhs_5
```

The problem is that the type of `?decEq_rhs_7` is `UN x = UN y -> Void`, i.e. a
proof that if the two names are equal, then we have a contradiction; in other
words, a proof that the two names _cannot_ be equal. However, we only have a
proof that their internal strings differ. Sounds like we need a helper function!
Rename the `?decEq_rhs_7` hole to `?unStringsDiffer` and interactively lift it
to a new function:

```idris
unStringsDiffer : (contra : x = y -> Void) -> (prf : UN x = UN y) -> Void
```

This lemma is trivial enough that Idris can actually figure it out from the type
declaration. With your text cursor on `unStringsDiffer`, ask Idris to
interactively generate a definition:

```idris
unStringsDiffer : (contra : x = y -> Void) -> (prf : UN x = UN y) -> Void
unStringsDiffer contra Refl = contra Refl
```

It might look a bit odd at first because the arguments to `Refl` are implicit,
but trust the type-checker that it _is_ a valid counter-proof. Now we just slot
it into the definition from earlier:

```idris
DecEq Name where
  decEq (UN x)   (UN y)   =
    case decEq x y of
         (Yes prf)   => rewrite prf in Yes Refl
         (No contra) => No (unStringsDiffer contra)

  decEq (UN x)   (MN y j) = ?decEq_rhs_3
  decEq (MN x i) (UN y)   = ?decEq_rhs_4
  decEq (MN x i) (MN y j) = ?decEq_rhs_5

```

Reloading the file confirms that things type-check and Idris is happy.

We'll come back to the cross-comparing cases in a bit. First, let's handle
`MN`s (I'll be omitting the preceding definitions from hereon, for brevity):

```idris
  decEq (MN x i) (MN y j) =
    case decEq x y of
         (Yes prfXY) => rewrite prfXY in
              case decEq i j of
                   (Yes prfIJ) => rewrite prfIJ in Yes Refl
                   (No contra) => No ?mnNumbersDiffer
         (No contra) => No ?mnStringsDiffer
```

You might have noticed that I decided to `rewrite` before the second
`case`-block here. This is to save a bit of space, _and_ because if we now look
at the type of `?mnNumbersDiffer` we get:

```idris
mnNumbersDiffer : MN y i = MN y j -> Void
```

By using the `rewrite` outside the `case`-block, Idris knows that the names are
the same, but that the numbers might not be; i.e. that the numbers are the only
possible difference. This makes for slightly nicer logic/reasoning in my opinion
(although, as we'll see shortly, it doesn't technically matter). If we'd used
the `rewrite` _inside_ the `case`-block, we'd get:

```idris
mnNumbersDiffer : MN x i = MN y j -> Void
```

Here, although _we_, the human, know that we're under a `(Yes prfXY)`-case, we
have never actually applied that to the terms we're working with, so Idris
doesn't know that the strings `x` and `y` are the same and that only `i` and `j`
might differ.

If we now lift both the holes, making sure to lift these all the way above the
`DecEq Name` declaration, we'll get some useful lemma types from which we can
generate definitions:

```idris
mnNumbersDiffer : x = y -> (i = j -> Void) -> MN y i = MN y j -> Void

mnStringsDiffer : (x = y -> Void) -> MN x i = MN y j -> Void
```

For `mnNumbersDiffer`, you'll notice that Idris has included more information
than we need: the proof that `x = y`. This is because the hole-lifting
functionality uses a "better safe than sorry" approach, including as much
information from the context where the hole was as it can. Refine the types a
bit (and name the arguments, just for neatness) to get:

```idris
mnNumbersDiffer : (contra : i = j -> Void) -> (prf : MN _ i = MN _ j) -> Void

mnStringsDiffer : (contra : x = y -> Void) -> (prf : MN x _ = MN y _) -> Void
```

Like with `unStringsDiffer`, these are trivial enough that Idris can generate
their definitions:

```idris
mnNumbersDiffer : (contra : i = j -> Void) -> (prf : MN _ i = MN _ j) -> Void
mnNumbersDiffer contra Refl = contra Refl

mnStringsDiffer : (contra : x = y -> Void) -> (prf : MN x _ = MN y _) -> Void
mnStringsDiffer contra Refl = contra Refl
```

The underscores in the types here are why I said that the first `rewrite`
doesn't technically matter for the `No` case: The `mnNumbersDiffer` lemma holds
without needing any info about the strings.

Coming back to the cross-comparing cases. To us, clearly we cannot construct an
instance of `Refl` for these, since `MN` takes more arguments than `UN`.
However, Idris doesn't know this (yet)! Start by adding `No` to both instances:

```idris
  decEq (UN x)   (MN y j) = No ?decEq_rhs_3
  decEq (MN x i) (UN y)   = No ?decEq_rhs_4
```

If we now look at the type of `?decEq_rhs_3` we see that need some way of saying
that `UN x = MN y j -> Void`. Having something which cannot be constructed is
known as that thing being `Uninhabited`, with its construction resulting in
something `absurd` (i.e. if we constructed it, we clearly broke the rules
somehow). We can sketch the two `Uninhabited` implementations:

```idris
Uninhabited ((UN _) = (MN _ _)) where
  uninhabited prf = ?un_mn_uninhabited

Uninhabited ((MN _ _) = (UN _)) where
  uninhabited prf = ?mn_un_uninhabited
```

Now, if we simply case-split on `prf` in each definition, Idris generates an
`impossible` pattern for both:

```idris
Uninhabited ((UN _) = (MN _ _)) where
  uninhabited Refl impossible

Uninhabited ((MN _ _) = (UN _)) where
  uninhabited Refl impossible
```

The `impossible` keyword means that there is no way to make the expression
type-check. Which is correct: there is no way we pass arguments to `Refl` which
make `UN` be identical to `MN`.

Having `Uninhabited` implementations allows us to use `absurd` to finish off the
`DecEq Name` implementation:

```idris
  decEq (UN x)   (MN y j) = No absurd

  decEq (MN x i) (UN y)   = No absurd
```

Together with all the previous definitions, we can reload and confirm that
`DecEq Name` type-checks and that there are no holes left.

Now, let's move on to slightly more relevant exercises.


## Exercise 2 - Scope manipulation

### Part 1: Variable removal

The first part of the scope manipulation exercises is to implement `dropFirst`,
which will remove all references to the most recently bound variable. The type
of `dropFirst` is given as:

```idris
dropFirst : List (Var (v :: vs)) -> List (Var vs)
```

As with Exercise 1, let's start by defining and case-splitting on the argument:

```idris
dropFirst : List (Var (v :: vs)) -> List (Var vs)
dropFirst [] = ?dropFirst_rhs_0
dropFirst (x :: xs) = ?dropFirst_rhs_1
```

The first case is trivial: If we have no bound variables, then there is nothing
to remove.

```idris
dropFirst [] = []
```

The second case is a bit more complicated. If we inspect the type of
`?dropFirst_rhs_1` we get:

```idris
 0 v : Name
 0 vs : List Name
   x : Var (v :: vs)
   xs : List (Var (v :: vs))
------------------------------
dropFirst_rhs_1 : List (Var vs)
```

Seems like we somehow need to deconstruct and reconstruct a `Var` term, in order
to remove `v` from `x` (and there'll probably be some recursion to deal with
`vs`). The question is how to deconstruct `x`? I guess we could always try
case-splitting again:

```idris
dropFirst ((MkVar p) :: xs) = ?dropFirst_rhs_2

 0 v : Name
 0 vs : List Name
 0 p : IsVar n i (v :: vs)
   xs : List (Var (v :: vs))
------------------------------
dropFirst_rhs_2 : List (Var vs)
```

Hmm, now we have the proof that the index `i` is a valid index for `n` in `(v ::
vs)`. It doesn't really seem closer, but this is actually partway there: We now
have a mention of the variable we're trying to remove! Let's case-split one more
time, this time on `p`:

```idris
dropFirst ((MkVar First) :: xs) = ?dropFirst_rhs_3
dropFirst ((MkVar (Later x)) :: xs) = ?dropFirst_rhs_4
```

Ah ha! Now we're finally getting somewhere! `First` is a proof that the variable
`v` was the first thing in the list. How do we drop that? Well, we just do! We
just don't mention it on the RHS and continue removing the other references:

```idris
dropFirst ((MkVar First) :: xs) = dropFirst xs
```

For the second part, it helps a bit to look at the type of `Later`:

```idris
  Later : IsVar n i ns -> IsVar n (S i) (m :: ns)
```

This means: "If I have a proof that `i` is a valid index for `n` in `ns`, then I
can extend `ns` with `m`, as long as I increment the index." How does this help
us, you might ask? Let's have a look at the type for our final pattern-match in
`dropFirst` again:

```idris
dropFirst ((MkVar (Later x)) :: xs) = ?dropFirst_rhs_4
```

What does our insight of what `Later` means determine for `x`? Don't worry if
you don't get it; I didn't until I inspected the type again:

```idris
 0 v : Name
 0 vs : List Name
 0 x : IsVar n i vs
   xs : List (Var (v :: vs))
------------------------------
dropFirst_rhs_4 : List (Var vs)
```

Notice the type of `x`. Since `Later` determines that we could extend something
as long as we incremented the index, this entails that `v` never was present in
`x` in the first place; it occurs _later_! If you're still not convinced,
construct and inspect the type of the following `let`-expression:

```idris
dropFirst ((MkVar (Later x)) :: xs) = let var' = MkVar x in ?dropFirst_rhs_4

 0 v : Name
 0 vs : List Name
 0 x : IsVar n i vs
   xs : List (Var (v :: vs))
   var' : Var vs
------------------------------
dropFirst_rhs_4 : List (Var vs)

```

Putting `x` back in a `Var` shows that the only names present in it are the list
`vs`; there is no `v`. What this means is that we can keep `(MkVar x)` and
recursively remove references to `v` from the rest. Like so:

```idris
dropFirst ((MkVar (Later x)) :: xs) = (MkVar x) :: dropFirst xs
```

The astute reader (i.e. not me when I was writing this), might have noticed a
similarity between `First` and `Later`, and `Z` and `S`. This is because they're
essentially the same! You can think of `First` as a proof that the index `Z` is a
valid index to retrieve the requested variable, and similarly for `Later x` and
`S n`. This way of thinking about `Var` and indexes into lists of variables is
very useful in the next exercise, so keep that in mind  : )

Phew! For a warmup, it's certainly picked up a bit. On to part 2...

### Part 2: Variable insertion

Having removed variable references from a scope, we now have to do the opposite:
add them to a scope. But with the twist of having to insert the reference in the
middle of the scope. Looking at the type, this is illustrated by the `Var (outer
++ inner)` part. The `outer` list is the outer scope and the `inner` list is the
inner scope.

```idris
insertName : Var (outer ++ inner) -> Var (outer ++ n :: inner)
```

There is also note from Edwin:

> The type here isn't quite right, you'll need to modify it slightly.

Now I'm going to slightly deviate here to explain in more detail what `Var`
represents, since I got this _completely_ wrong in the first draft of this post.

The `Var` type describes a "de Bruijn index". These are notoriously difficult to
get right and reason about, which is why Idris puts it in a type: Then the
type-checker forces us to get it right. Having the function called `insertName`
is actually slightly misleading: we're technically not inserting anything, we're
"just" updating a de Bruijn index.

Looking at the type of `insertName` again, the argument has type
```idris
Var (outer ++ inner)
```

This could be read as "I have a de Bruijn index into the list `outer ++
inner`". With that in mind, our return type reads as:

<p align="center">
"I want a de Bruijn index into the list <code>outer ++ n :: inner</code>"
</p>

Now, _what exactly_ does actually that mean? (The numbers Mason! What do they
mean?!)

Lets consider, for example, `outer` and `inner` each having three elements. In
this case, our indices would be from 0 to 5, like so:

```
    outer            inner
[   |   |   ] ++ [   |   |   ]
  0   1   2        3   4   5
```

And what we want, is an index into something which looks like:

```
    outer                 inner
[   |   |   ] ++ n :: [   |   |   ]
```

Some guiding questions to help understand what needs doing:

{{< spoiler text="How does this affect the indices of `outer`?" >}}

It doesn't. They remain the same, i.e. `0 ↦ 0`, `1 ↦ 1`, and `2 ↦ 2`.

{{< /spoiler >}}

{{< spoiler text="How does this affect the indices of `inner`?" >}}

They all get incremented by 1 since `n` now precedes them, i.e. `3 ↦ 4`, `4 ↦
5`, and `5 ↦ 6`.

{{< /spoiler >}}

{{< spoiler text="What is the range of the new index?" >}}

The new indices range from 0 to 6, since there's an extra thing in the lists
we're indexing.

{{< /spoiler >}}

So far so good? Now what is the argument to the `insertName` function? It is an
existing index over `outer ++ innner`! This is important because we need to know
which part of the combined list it is an index into:

{{< spoiler text="If it is an index into `outer`, what should be done?" >}}

Nothing! It should stay the same since it would still index the same place if
there was something added to the list after it.

{{< /spoiler >}}

{{< spoiler text="If it is an index into `inner`, what should be done?" >}}

It should get incremented, since our new index describes something where `n`
occurs before `inner`.

{{< /spoiler >}}

Does your brain hurt yet? Mine is starting to...

In order to be able to reason about where the index falls, we need to know the
shape of at least one of the lists. This is why there is that comment from
Edwin: we need one of the implicit arguments in the definition, but they're
currently erased!

The issue is subtle, but becomes slightly clearer if we define, case-split, and
inspect the type of the resulting hole without modifying the function type:

```idris
insertName : Var (outer ++ inner) -> Var (outer ++ n :: inner)
insertName (MkVar p) = ?insertName_rhs_0

 0 n : Name
 0 inner : List Name
 0 outer : List Name
 0 p : IsVar n i (outer ++ inner)
------------------------------
insertName_rhs_0 : Var (outer ++ (n :: inner))
```

Here we can see that `p` indexes the combined list, but we don't know which part
of it. And we _can't_ know because both `inner` and `outer` are erased by
default.

Restore the editor to only contain the original function declaration. We need to
be able to reason about at least one of the lists/scopes, and we saw that
nothing needs to be done if we're indexing `outer`. So lets start by making the
`outer` scope runtime-accessible:

```idris
insertName : {outer : _} -> Var (outer ++ inner) -> Var (outer ++ n :: inner)
```

With the type now in the correct shape, generate a definition again, and bring
the `outer` list into context in the definition:

```idris
insertName : {outer : _} -> Var (outer ++ inner) -> Var (outer ++ n :: inner)
insertName {outer} x = ?insertName_rhs
```

Having `outer` be runtime-accessible means we can pattern-match on it, which
means we can know where we're currently indexing. There are three distinct cases
to consider:

{{< spoiler text="1. Outer is empty. Where does the given index point and what should be done as a result?" >}}

If `outer` is empty, the only possibility is that the index was pointing into
`inner`, and any index into `inner` needs incrementing (we're adding stuff to
the front of it), so it should always be incremented.

{{< /spoiler >}}

The next two cases depend on whether the index was 0 or not:

{{< spoiler text="2. Outer is non-empty, but the given index is 0. Where does the given index point and what should be done as a result?" >}}

If the given index is 0, then it points to the start of the current `outer`
(remember, we're given an index over `outer ++ inner`), and so it should be left
as it is (no need to update an index which occurs prior to where the scope
extension happened).

{{< /spoiler >}}

{{< spoiler text="3. Outer is non-empty, but the given index is also non-zero. What options are there in terms of where the index points?" >}}

If both `outer` is non-empty and the given index is non-zero, then there are two
options: either the index points to somewhere in `outer` and we just haven
discovered that yet; or it points to somewhere in `inner` and should always be
updated.

{{< spoiler text="How do we know which it is?" >}}

We check on a sub-term, i.e. a smaller `outer` and a smaller index, and see
which of the two previously covered cases we hit first.

{{< /spoiler >}}

{{< /spoiler >}}

Please take your time to read over this several times and try and think it
through in your head (or on paper!). It is a really complicated, but
unfortunately also crucial part of handling variables, so having an idea of how
it's supposed to work is essential. I'll go over two examples after the code has
been written, so if you're mostly convinced you get it, feel free to read ahead
to double-check.

Right then! Let's put this into code, shall we? We pulled `outer` into scope, so
we'll start by generating some insightful pattern-matches by case-splitting on
it:

```idris
insertName {outer = []} x = ?insertName_rhs_0
insertName {outer = (y :: xs)} x = ?insertName_rhs_1
```

This tells us whether `outer` was empty (in which case we should always update
the index) or whether it was non-empty.

We still don't know what the index was, however, so case-split on both `x`s:

```idris
insertName {outer = []} (MkVar p) = ?insertName_rhs_2
insertName {outer = (y :: xs)} (MkVar p) = ?insertName_rhs_3
```

Now that we have the index, let's code in the first scenario: `outer` is empty
and we've been given an index to update. Since we know `outer` is empty, the
index must point into `inner`, which we're adding stuff in front of, so it needs
to be updated. Checking the type of the `?insertName_rhs_2` hole confirms this:

```idris
 0 n : Name
 0 inner : List Name
 0 p : IsVar n i inner
------------------------------
insertName_rhs_2 : Var (n :: inner)
```

Note that `p` now only refers to `inner` (since `[] ++ inner === inner`), and
the type of the hole says that the index must be into a list one bigger than
`inner`. How do we update the index in this case? We increment it using `Later`!
We can double-check that this has the desired effect by adding the following
`let`-expression and examining the type of the hole again:

```idris
insertName {outer = []} (MkVar p) = let 0 p' = Later p in ?insertName_rhs_2


 0 n : Name
 0 inner : List Name
 0 p : IsVar n i inner
 0 p' : IsVar n (S i) (?m :: inner)
------------------------------
insertName_rhs_2 : Var (n :: inner)
```

Here we can see that the type of our new index, `p'`, contains an incremented
number and indexes a list where something occurs in front of `inner`. The types
are keeping us sane while we do the de Bruijn index updates! (We have to write
`0 p'` in the `let`-expression because `p` is erased and so we're only allowed
to create new expressions from it if those are also erased.)

Put the updated index in a `Var` to complete the definition of the first case:

```idris
insertName {outer = []} (MkVar p) = MkVar (Later p)
```

For the remaining cases, we need to know what the index was.

```idris
insertName {outer = (y :: xs)} (MkVar p) = ?insertName_rhs_3
```

Case-splitting on `p` gives us:

```idris
insertName {outer = (y :: xs)} (MkVar First) = ?insertName_rhs_4
insertName {outer = (y :: xs)} (MkVar (Later x)) = ?insertName_rhs_5
```

In the first case, `First` is the same as saying that the given index was zero
(i.e.  it indexes the front of `outer`). In this case we should **not** update
the index! It stays the same since the update concerns a position further down
in the combined list, so just reconstruct the index as it was:

```idris
insertName {outer = (y :: xs)} (MkVar First) = (MkVar First)
```

Now we get to the truly challenging bit! The index is non-zero, but the `outer`
list is also non-empty, and as a result we don't know what to do with the index.
To update or not to update, that is the question.

```idris
insertName {outer = (y :: xs)} (MkVar (Later x)) = ?insertName_rhs_5
```

Are we stuck? No! If we decrement the index, it must now point into the list `xs
++ inner` (by the pattern-match, it originally pointed into the list `(y :: xs)
++ inner`). This brings us one step closer to knowing where the index points:
Either `xs` will turn out to be empty, in which case the index points to
somewhere in `inner` and we should update it; or the reduced index will turn out
to be zero, in which case it points to the start of `xs` and should be left
alone.

We do this by recursion. Since `outer` is an implicit argument, Idris
automatically figures out that `xs` is the new outer:

```idris
insertName {outer = (y :: xs)} (MkVar (Later x)) =
  let rec = insertName (MkVar x) in ?insertName_rhs_5   -- rec has {outer=xs}
```

This line may look like it's not doing anything, but note that we have put `x`
back in a `Var` _without_ the `Later` that previously surrounded it. This is the
same as when we recurse on `n` from an `(S n)`-expression, so the given index
_has_ been decremented.

If we inspect the type of the hole now, we get:

```idris
 0 n : Name
 0 inner : List Name
   y : Name
   xs : List Name
 0 x : IsVar n i (xs ++ inner)
   rec : Var (xs ++ (?n :: inner))
------------------------------
insertName_rhs_5 : Var (y :: (xs ++ (n :: inner)))
```

Since `insertName` returns something of type `Var`, we need to remember to
extract the new index:

```idris
insertName {outer = (y :: xs)} (MkVar (Later x)) =
  let (MkVar x') = insertName (MkVar x) in ?insertName_rhs_5


 0 n : Name
 0 inner : List Name
   y : Name
   xs : List Name
 0 x : IsVar n i (xs ++ inner)
 0 x' : IsVar n i (xs ++ (?n :: inner))
------------------------------
insertName_rhs_5 : Var (y :: (xs ++ (n :: inner)))
```

Hey look at that! We've done it!! Our new index, `x'`, is an index into `xs`
followed by something in front of `inner`. That's exactly what we were trying to
do!  However, if we try to wrap things up by returning it, Idris complains:

```idris
insertName {outer = (y :: xs)} (MkVar (Later x)) =
    let (MkVar x') = insertName (MkVar x) in MkVar x'


-- Error: While processing right hand side of insertName. Can't solve constraint
-- between: xs ++ (?n :: inner)
-- and y :: (xs ++ (n :: inner)).
```

This is where the types keep us in check! In order to recurse on a smaller term,
we decremented the index. Which means the recursively updated index is
off-by-one! We've recursed correctly, but forgotten to restore the larger scope
which also includes `y`. It is very good that the type makes Idris catch this,
otherwise de Bruijn manipulation ~~would be~~ is extremely easy to get wrong!
Fix things by remembering that the index actually needs to be one greater since
we decremented it in the recursive call:

```idris
insertName {outer = (y :: xs)} (MkVar (Later x)) =
    let (MkVar x') = insertName (MkVar x) in MkVar (Later x')
```

Now. If you're not convinced that this actually does what I've said it does, I
don't blame you. I wasn't convinced either. So let's go through a couple of
examples:

{{< spoiler text="Example 1" >}}

Consider once more the case where both `outer` and `inner` contain three
elements, indexed 0 through 5:

```
    outer            inner
[   |   |   ] ++ [   |   |   ]
  0   1   2        3   4   5
```

If we're given, for example, the index `1` as the argument to the `insertName`
function, what happens?

```
index         outer            inner
  1       [   |   |   ] ++ [   |   |   ]
            0   1   2        3   4   5
```

Neither of the first two patterns match: `outer` is non-empty, and the index is
non-zero. So we recurse, reducing both the index and the `outer` list in size:

```
index         outer            inner
  1       [   |   |   ] ++ [   |   |   ]
            0   1   2        3   4   5

index         outer            inner
  0           [   |   ] ++ [   |   |   ]
                0   1        2   3   4
```

(Note here that since our combined scope shrunk, so did the indices! This
(hopefully) makes sense: we're considering a smaller problem, with a slightly
different, smaller scope, but indices start at 0.)

Here we've hit our second case! The given index is zero, but there is still
stuff in `outer`, so the index must point to the start of `outer`. What do we do
with those indices? We leave them alone since adding things to the front of
`inner` wouldn't change where the index points. So our returned index stays the
same as the given one, i.e. `0`.

```
index         outer            inner
  1       [   |   |   ] ++ [   |   |   ]
            0   1   2        3   4   5

index         outer            inner
  0           [   |   ] ++ [   |   |   ]
                0   1        2   3   4

ANSWER: Don't change anything, leave index as given: 0
```

HOWEVER, once this comes back up the recursive call, we can see the index is
clearly wrong: it was correct in a smaller scope, but not the larger scope;
specifically, it's off by one! So we restore the index to its correct state by
incrementing it. Incrementing `0` gives `1`, which is the index we were given.
We, the human, know it pointed into `outer` (check the diagrams), so we've left
it alone, which was the point! Hurray!

```
index         outer                 inner
  1       [   |   |   ]   ++    [   |   |   ]
            0   1   2             3   4   5

  |
  v

index         outer                 inner
0+1= 1    [   |   |   ] ++ n :: [   |   |   ]
            0   1   2      3      4   5   6
```

{{< /spoiler >}}

{{< spoiler text="Example 2" >}}

Consider yet again the case where both `outer` and `inner` contain three
elements, indexed 0 through 5:

```
    outer            inner
[   |   |   ] ++ [   |   |   ]
  0   1   2        3   4   5
```

Now if we're given, for example, the index `4` as the argument to the
`insertName` function, what happens?

```
index         outer            inner
  4       [   |   |   ] ++ [   |   |   ]
            0   1   2        3   4   5
```

Neither of the first two patterns match: `outer` is non-empty, and the index is
non-zero. So we recurse, reducing both the index and the `outer` list in size.
And we keep doing this while neither of the first two patterns of `insertName`,
neither of our base-cases, match:

```
index         outer            inner
  4       [   |   |   ] ++ [   |   |   ]
            0   1   2        3   4   5

index         outer            inner
  3           [   |   ] ++ [   |   |   ]
                0   1        2   3   4

index         outer            inner
  2               [   ] ++ [   |   |   ]
                    0        1   2   3

index         outer            inner
  1                   Ø ++ [   |   |   ]
                             0   1   2
```

This is our first pattern! The `outer` part is empty, so the given index must
point somewhere in the `inner` list (and indeed we, the human, can see this).
Any index into `inner` must be incremented, since we're adding stuff to the
front of `inner`, so we increment the index by 1, giving 2. We can confirm this
would match the same place by drawing the result of prepending `n`:

```
index         outer                 inner
1+1= 2                Ø ++ n :: [   |   |   ]
                           0      1   2   3
```

Now. As with the previous example, we did some subtraction and reducing to reach
this point. For every recursive call, we removed an element from `outer` and
subtracted one from the given index. In order to get the correct result, we
therefore need to undo this. Travelling back up the recursive calls, we undo
this step three times, resulting in a final index of `2 + 3 = 5`. Is this
correct?

```
index         outer                 inner
  4       [   |   |   ]   ++    [   |   |   ]
            0   1   2             3   4   5

  |
  v

index         outer                 inner
2+3= 5    [   |   |   ] ++ n :: [   |   |   ]
            0   1   2      3      4   5   6
```

Yes it is! Everything lines up, and our updated index points to the same
location as before the combined list was extended! Fantastic!!


{{< /spoiler >}}

So yeah... That's de Bruijn indices... A good warmup exercise, huh?... Please go
for a walk or a cup of coffee or something at this point. It took so long to get
here, with so many tiny details to get exactly right, so I don't blame you if
you feel mentally fatigued by this point.

Well done for making it to the end of this part! I hope it made somewhat sense.

And now for something completely different. (Which is fortunately a bit simpler,
in my opinion.)


## Exercise 3 - Lists and Trees

Exercise 3 has us do some more exercises with proofs and lemmas. We start with
lists.

### Part 1: Appending Nil does nothing

The first part is to prove that appending `Nil` (typically written `[]`) to a
list doesn't change the list. This one is not trivial enough for Idris to just
find: If we ask Idris to generate the definition, it comes back with a `No
search results` message. So we have to do a bit of work (although not too much).

As always, creating a definition and case-splitting on the argument is a good
initial approach:

```idris
appendNilNeutral : (xs : List a) -> xs ++ [] = xs
appendNilNeutral [] = ?appendNilNeutral_rhs_0
appendNilNeutral (x :: xs) = ?appendNilNeutral_rhs_1
```

In the first case, we are appending `Nil` to itself. That sounds trivial. And
indeed, a proof-search on `?appendNilNeutral_rhs_0` finds that it is `Refl`:

```idris
appendNilNeutral : (xs : List a) -> xs ++ [] = xs
appendNilNeutral [] = Refl
appendNilNeutral (x :: xs) = ?appendNilNeutral_rhs_1
```

The second case, the recursive/inductive step, is a bit more tricky. We can get
some help by asking about the type of the hole:

```idris
 0 a : Type
   x : a
   xs : List a
------------------------------
appendNilNeutral_rhs_1 : x :: (xs ++ []) = x :: xs
```

So, we need to prove that appending `Nil` to the tail of the list doesn't change
it. As I hinted to earlier, we can use recursion here (since we'll either need
to prove this for the next `head'`/`tail'` pair, or the tail will be empty, in
which case we've won). We also need to use this proof in our general proof. That
sounds like a job for `rewrite`! (I've shortened the hole name a bit, in order
to make it fit nicely in the code block).

```idris
appendNilNeutral (x :: xs) = rewrite appendNilNeutral xs in ?aNN_rhs_1
```

This type-checks and Idris is happy so far. If we now inspect the hole to see
what's changed, we find:

```idris
 0 a : Type
   x : a
   xs : List a
------------------------------
aNN_rhs_1 : x :: xs = x :: xs
```

Well that certainly improved things! We've won!! The logic here, is that since
Idris now knows that appending `Nil` to the tail of the list doesn't change the
tail, all that remains is to prove that reconstructing the list (from our
destructive pattern-match on `x :: xs`) doesn't change the list. That
_definitely_ sounds trivial! And indeed, a proof-search on `?aNN_rhs_1` finds it
is `Refl`, completing the definition:

```idris
appendNilNeutral : (xs : List a) -> xs ++ [] = xs
appendNilNeutral [] = Refl
appendNilNeutral (x :: xs) = rewrite appendNilNeutral xs in Refl
```

### Part 2: List appending is associative

Next up is to prove that appending lists is associative, i.e. it doesn't matter
if we append list `b` to list `a` and then append list `c` to the result, or if
we first append list `c` to list `b` and then append that result to list `a`. In
mathsy notation (also seen in the type):

```idris
xs ++ (ys ++ zs) = (xs ++ ys) ++ zs
```

This one appears difficult, but actually isn't. Start by defining and
case-splitting, _but only on the first argument (`xs`)_.

```idris
appendAssoc :  (xs : List a) -> (ys : List a) -> (zs : List a)
            -> xs ++ (ys ++ zs) = (xs ++ ys) ++ zs
appendAssoc [] ys zs = ?appendAssoc_rhs_0
appendAssoc (x :: xs) ys zs = ?appendAssoc_rhs_1
```

As I said, this one is a bit deceptive: Before we case-split any further, let's
start by inspecting what we currently have:

```idris
 0 a : Type
   zs : List a
   ys : List a
------------------------------
appendAssoc_rhs_0 : ys ++ zs = ys ++ zs
```

Hmm, that doesn't seem complicated... Is it just `Refl`?... A proof-search on
`?appendAssoc_rhs_0` says "Yes"! This is a great example of remembering to check
whether we actually _need_ to split further, or if the current information is
enough to solve the problem. Note that we've not imported `Data.List` or
anything here, so this is purely Idris being clever and figuring out that append
is associative for two lists, based on the function definition.

Now we need to prove the general case. Again, let's inspect the information we
currently have:

```idris
 0 a : Type
   x : a
   xs : List a
   zs : List a
   ys : List a
------------------------------
appendAssoc_rhs_1 : x :: (xs ++ (ys ++ zs)) = x :: ((xs ++ ys) ++ zs)
```

The head (`x`) has been pulled out of the `append` call. We now need to prove
that extending the list with `x` doesn't change it as long as `++` is
associative. Does this seem familiar? It is the same idea as with
`appendNilNeutral`! Recurse on `xs`:

```idris
appendAssoc (x :: xs) ys zs = rewrite appendAssoc xs ys zs in ?appendAssoc_rhs_1
```

If we now inspect the hole, we get:

```idris
 0 a : Type
   x : a
   xs : List a
   zs : List a
   ys : List a
------------------------------
appendAssoc_rhs_1 : x :: ((xs ++ ys) ++ zs) = x :: ((xs ++ ys) ++ zs)
```

Remember that the logic is that we'll either keep recursing on the tail, or
reach the base-case `[] ys zs`, in which case we've won. We know we'll
eventually reach the base-case since lists in Idris cannot be infinite and we're
removing an element each time, so we know that eventually everything will be
fine. All that remains to prove is that restoring `x` to the front of the list
doesn't change the recursive append result. This is trivial and completes the
proof/definition:

```idris
appendAssoc :  (xs : List a) -> (ys : List a) -> (zs : List a)
            -> xs ++ (ys ++ zs) = (xs ++ ys) ++ zs
appendAssoc [] ys zs = Refl
appendAssoc (x :: xs) ys zs = rewrite appendAssoc xs ys zs in Refl
```

This also concludes the parts on lists. Now we move on to trees.

### Part 3: Rotating trees left

The first part of the exercise on trees is to implement a lemma. We can look at
the type to get some information as to what this lemma is meant to show:

```idris
   n : a
   n' : a
   rightr : Tree ys
   rightl : Tree xs
   left : Tree xs
 0 xs : List a
------------------------------
rotateLemma :  Tree ((xs ++ (n :: xs)) ++ (n' :: ys))
            -> Tree (xs ++ (n :: (xs ++ (n' :: ys))))
```

This lemma, you may not be surprised to hear, uses parts of the previous
exercise. We need to show that we can reorder appending in the context of trees,
which will inevitably involve manipulating the lists in the nodes. Specifically,
we need to show that it is okay to sequence the operations, instead of doing
them out-of-order and then combining those results.

Now, this lemma is a good bit more difficult than the previous stuff. You
will probably not get it right by just trying to brute-force coding a solution
(I tried, it didn't go well). When the problem just wouldn't budge, I asked
Edwin for a hint. He suggested trying to write the proof on paper first, and
then transfer it into Idris, which is what I'm going to suggest you stop and do
at this point as well.

There are hints below, but I'll save you from the first pitfall I immediately
fell into: We need to prove that the _right_ side can be written as the _left_
side, and not the other way around. Why, you might ask? Because what we're
trying to prove is that we can slot the expression from the first argument of
`rotateLemma` into the lemma's rhs without any problems; that expression is the
only thing we have access to after all.

So your mission, should you choose to accept it, is to prove on paper that

```idris
Tree (xs ++ (n :: (xs ++ (n' :: ys))))
```

can be written as

```idris
Tree ((xs ++ (n :: xs)) ++ (n' :: ys))
```

Good luck!


{{< spoiler text="Hint 1" >}}
Remember that we've proved that append (`++`) is associative. How might this
help in terms of cons (`::`)?
{{< /spoiler >}}


{{< spoiler text="Hint 2" >}}
Recall, from the defininion of `++`, that `a :: as` could technically be written
`[a] ++ as`.
{{< /spoiler >}}


{{< spoiler text="Solution" >}}

{{< math >}}
$
xs ++ (n :: (xs' ++ (n' :: ys)))
$
{{< /math >}}

<p align=right>
by definition of <code>++</code>: (1)
</p>
{{< math >}}
$
\Leftrightarrow xs ++ ([n] ++ (xs' ++ ([n'] ++ ys)))
$
{{< /math >}}

<p align=right>
by associativity on <code>xs</code>, <code>[n]</code>, and
<code>xs' ++ ([n'] ++ ys)</code>: (2)
</p>
{{< math >}}
$
\Leftrightarrow (xs ++ [n]) ++ (xs' ++ ([n'] ++ ys))
$
{{< /math >}}

<p align=right>
by associativity on <code>xs ++ [n]</code>, <code>xs'</code>, and
<code>[n'] ++ ys</code>: (3)
</p>
{{< math >}}
$
\Leftrightarrow ((xs ++ [n]) ++ xs') ++ ([n'] ++ ys)
$
{{< /math >}}

<p align=right>
by associativity on <code>xs</code>, <code>[n]</code>, and <code>xs'</code>: (4)
</p>
{{< math >}}
$
\Leftrightarrow (xs ++ ([n] ++ xs')) ++ ([n'] ++ ys)
$
{{< /math >}}

<p align=right>
by definition of <code>++</code>: (5)
</p>
{{< math >}}
$
\Leftrightarrow (xs ++ (n :: xs')) ++ (n' :: ys)
$
{{< /math >}}

{{< math >}}
$
\Box
$
{{< /math >}}

{{< /spoiler >}}

Nicely done! With that, we can now transfer the proof into Idris. If you kept
track of what rules you applied where (which is generally a good idea when
writing formal proofs), this should be almost trivial.

{{< spoiler text="If you have a shorter solution... (don't worry if not)" >}}

If you read the above solution and thought "What on Earth?? My solution is just
one line", then you're likely correct (put it into Idris to check). There _is_ a
much shorter solution, and I'll come back to it, but for now we're going to take
the long route.

{{< /spoiler >}}

Let's start by lifting the `rotateLemma` to a new function:

```idris
rotateLemma :  (n : a) -> (n' : a) -> Tree ys -> Tree xs_0 -> Tree xs
            -> Tree ((xs ++ (n :: xs_0)) ++ (n' :: ys))
            -> Tree (xs ++ (n :: (xs_0 ++ (n' :: ys))))

[...]

rotateL (Node left n (Node rightl n' rightr))
    = rotateLemma n n' rightr rightl left $ Node (Node left n rightl) n' rightr
```

As with the lemmas in Exercise 1, Idris has included absolutely everything we
could need, since it doesn't know exactly what we need. It has also revealed
that the two `xs` in the original hole are actually different: there is an `xs`
and an `xs_0`/`xs'`. This changes the paper proof a tiny bit, so make sure to
change that now (essentially just make sure to keep track of the name, the rest
is the same).

With that done, let's tidy things up a bit. As indicated by the initial layout
of the exercise, we don't actually need any of the extra information Idris has
included:

```idris
rotateLemma :  Tree ((xs ++ (n :: xs')) ++ (n' :: ys))
            -> Tree (xs ++ (n :: (xs' ++ (n' :: ys))))

[...]

rotateL (Node left n (Node rightl n' rightr))
    = rotateLemma $ Node (Node left n rightl) n' rightr
```

Much better! Now start by interactively sketching the definition of
`rotateLemma`:

```idris
rotateLemma :  Tree ((xs ++ (n :: xs')) ++ (n' :: ys))
            -> Tree (xs ++ (n :: (xs' ++ (n' :: ys))))
rotateLemma x =
    ?rotateLemma_rhs
```

Inspecting `?rotateLemma_rhs` we get the following type information:

```idris
 0 xs_0 : List a
 0 xs : List a
 0 ys : List a
 0 n' : a
 0 n : a
   x : Tree ((xs ++ (n :: xs_0)) ++ (n' :: ys))
------------------------------
rotateLemma_rhs : Tree (xs ++ (n :: (xs_0 ++ (n' :: ys))))
```

This is where our paper proof comes in! Idris can figure out that `a :: as`
corresponds to `[a] ++ as`, so we don't need to `rewrite` that. Instead, go
straight to the first associativity step:

```idris
rotateLemma x =
    rewrite appendAssoc xs [n] (xs' ++ ([n'] ++ ys)) in
    ?rotateLemma_rhs
```

This improves things a bit:

```idris
 0 xs' : List a
 0 xs : List a
 0 ys : List a
 0 n' : a
 0 n : a
   x : Tree ((xs ++ (n :: xs')) ++ (n' :: ys))
------------------------------
rotateLemma_rhs : Tree ((xs ++ [n]) ++ (xs' ++ (n' :: ys)))
```

We're successfully rearranging the terms and parentheses!! This is great news
for formalising the proof in Idris!

Adding in the second associative step improves things further:

```idris
rotateLemma x =
    rewrite appendAssoc xs [n] (xs' ++ ([n'] ++ ys)) in
        rewrite appendAssoc (xs ++ [n]) xs' ([n'] ++ ys) in
        ?rotateLemma_rhs

 0 xs' : List a
 0 xs : List a
 0 ys : List a
 0 n' : a
 0 n : a
   x : Tree ((xs ++ (n :: xs')) ++ (n' :: ys))
------------------------------
rotateLemma_rhs : Tree (((xs ++ [n]) ++ xs') ++ (n' :: ys))
```

Almost there! However, if we try to add our third step, Idris complains:

```idris
rotateLemma x =
    rewrite appendAssoc xs [n] (xs' ++ ([n'] ++ ys)) in
        rewrite appendAssoc (xs ++ [n]) xs' ([n'] ++ ys) in
            rewrite appendAssoc xs [n] xs' in
            ?rotateLemma_rhs

-- Error: While processing right hand side of rotateLemma. Rewriting by
-- xs ++ (?u ++ xs') = (xs ++ ?u) ++ xs'
-- did not change type
-- Tree (((xs ++ [n]) ++ xs') ++ ([n'] ++ ys)).
```

What's gone wrong? Well, the problem is that we have the left hand side of an
equality, namely:

```idris
xs ++ ([n] ++ xs') = (xs ++ [n]) ++ xs'
```

Whereas what we actually need is the right hand side:

```idris
(xs ++ [n]) ++ xs' = xs ++ ([n] ++ xs') 
```

In short, we need to move the parentheses the other way.

One way of doing this could be to define some `appendAssoc'` which proves the
other direction. But fortunately, this problem of lhs vs rhs is a fairly common
problem and Idris provides a built-in function for it: `sym`

```idris
> :doc sym
Builtin.sym : (0 _ : x = y) -> y = x
  Symmetry of propositional equality.
```

Using `sym`, we can include the final step:

```idris
rotateLemma x =
    rewrite appendAssoc xs [n] (xs' ++ ([n'] ++ ys)) in
        rewrite appendAssoc (xs ++ [n]) xs' ([n'] ++ ys) in
            rewrite sym $ appendAssoc xs [n] xs' in
                    ?rotateLemma_rhs

 0 xs' : List a
 0 xs : List a
 0 ys : List a
 0 n' : a
 0 n : a
   x : Tree ((xs ++ (n :: xs')) ++ (n' :: ys))
------------------------------
rotateLemma_rhs : Tree ((xs ++ (n :: xs')) ++ (n' :: ys))
```

Aha! Now the type of the hole matches the type of `x`; we've won!!

Complete the definition by slotting `x` into the `x`-shaped hole:

```idris
rotateLemma x =
    rewrite appendAssoc xs [n] (xs' ++ ([n'] ++ ys)) in
        rewrite appendAssoc (xs ++ [n]) xs' ([n'] ++ ys) in
            rewrite sym $ appendAssoc xs [n] xs' in
                    x
```

Almost there! For the final part of this exercise, we "just" need to rotate
trees right as well.

### Part 4: Rotating trees right

Unsurprisingly, this is going to be very similar to the `rotateL` exercise.

This should hopefully be almost second-nature by now: Start by generating a
definition and case-splitting on the argument:

```idris
rotateR : Tree xs -> Tree xs
rotateR Leaf = ?rotateR_rhs_0
rotateR (Node left n right) = ?rotateR_rhs_1
```

In the first case, we're rotating a tree consisting only of a single leaf. There
isn't anything to do in this case, so we just return the leaf:

```idris
rotateR Leaf = Leaf
```

In the second case, however, we need to do something similar to `rotateL`. But
here we're trying to rotate the tree right (or clockwise), not left, so we care
about the mirror-case compared to `rotateL`: the right half of the tree is
general, the left half of the tree is interesting. Let's start by defining that:

```idris
rotateR (Node Leaf n right) = ?rotateR_rhs_1
rotateR ((Node leftl n' leftr) n right) = ?rotateR_rhs_2
```

In the case where the left side of the tree is a leaf, we cannot rotate the tree
right, so we just return the existing tree:

```idris
rotateR (Node Leaf n right) = Node Leaf n right
```

When we _do_ have a left side of the tree, we need to:

1. Move the left node to be the current/top node,
2. move the former top node to be the right child of the old left node,
3. and move the former left node's right subtree (the "left-right" tree, if you
   will) to be the left branch of the old top node.

(This is hard to explain in text, so I'd strongly recommend drawing a diagram to
better illustrate things.)

As with `rotateL`, Idris won't just accept that the two trees are the same. We
need to help it by defining a lemma. Put a hole in its place for now:

```idris
rotateR (Node (Node leftl n' leftr) n right) =
    ?rotateRLemma $ Node leftl n' (Node leftr n right)
```

Inspecting the type of this hole gives us some insight into what needs to be
done:

```idris
   n' : a
   leftr : Tree ys
   leftl : Tree xs
   n : a
   right : Tree ys
 0 xs : List a
------------------------------
rotateRLemma :  Tree (xs ++ (n' :: (ys ++ (n :: ys))))
             -> Tree ((xs ++ (n' :: ys)) ++ (n :: ys))
```

This looks oddly familiar... It's the inverse of `rotateLemma`!

Now, I'd love to say that there is some `sym`-like function we could just stick
in front of `rotateLemma`, but unfortunately not. Since not all functions are
invertible, we have to write this one by hand. Start by lifting the hole to a
new function and cleaning up all the extra stuff Idris adds:

```idris
rotateRLemma :  Tree (xs ++ (n' :: (ys' ++ (n :: ys))))
             -> Tree ((xs ++ (n' :: ys')) ++ (n :: ys))

[...]

rotateR (Node (Node leftl n' leftr) n right) =
    rotateRLemma $ Node leftl n' (Node leftr n right)
```

And then generate the start of a definition:

```idris
rotateRLemma :  Tree (xs ++ (n' :: (ys' ++ (n :: ys))))
             -> Tree ((xs ++ (n' :: ys')) ++ (n :: ys))
rotateRLemma x = ?rotateRLemma_rhs
```

Once again, remember that we are working right-to-left here and _not_
left-to-right; we're trying to slot `x` into the `?rotateRLemma_rhs` hole. Now
you _could_ go about this the long way as with the original `rotateLemma`, but
there is a shorter way. It just requires a bit more thinking.

Start by looking at the appends (the `++` operations). Those are the things we
want to reorder using `appendAssoc`. There are 3 terms:

* `xs`
* `n' :: ys'`
* `n :: ys`

{{< spoiler text="If you came up with a one-line solution to 3.3..." >}}

If you came up with a one-line solution to 3.3, then there _is_ an inverse for
the definition of this proof. It's simply `sym`. Stick that in front of the same
thing you wrote as the definition for 3.3 and you're done!

{{< /spoiler >}}

These can be reordered using a single call to `appendAssoc`: the inner grouping
is between the first two terms (`xs` and `(n' :: ys)`), and the outer grouping
is with the third term (`n :: ys`). As I mentioned earlier though, we're going
the other way from `rotateL`, and so we need a `sym` for the single
`appendAssoc` call to work. Putting it all together gives:

```idris
rotateRLemma x =
    rewrite sym $ appendAssoc xs (n' :: ys') (n :: ys) in ?rotateRLemma_rhs
```

I don't blame you if you didn't spot this in 3.3. I didn't until I wrote this
and went "Hang on a minute! That should just work for 3.3!!". It requires being
able to squint at the type right, which is a skill/art that unfortunately just
takes some practice. Hopefully taking both the long and the short way has
helped a bit with this  : )

If we inspect the hole in our one-line definition we get:

```idris
 0 ys : List a
 0 ys' : List a
 0 xs : List a
 0 n : a
 0 n' : a
   x : Tree (xs ++ (n' :: (ys' ++ (n :: ys))))
------------------------------
rotateRLemma_rhs : Tree (xs ++ (n' :: (ys' ++ (n :: ys))))
```

Which is the type of `x`! As with `rotateLemma`, slot `x` into the `x`-shaped
hole to complete the definition:

```idris
rotateRLemma x =
    rewrite sym $ appendAssoc xs (n' :: ys') (n :: ys) in x
```

And just to neatly finish with having the symmetry in the source code: if you
haven't already, tidy up the definition of the first `rotateLemma`:

```idris
rotateLemma x =
    rewrite appendAssoc xs (n :: xs') (n' :: ys) in x
```

(N.B.: Due to the way Idris names things when lifting the holes and the fact
that we're dealing with the left tree vs the right tree, you'll need to swap `n`
and `n'`, as well as rename `ys'` to `xs'`)


## End of warmup

Well that certainly took a while! I was originally going to write this as a
walkthrough of the entire SPLV'20 TinyIdris course, but then the warmup alone
got to over 7000 words and I thought "Hmm, maybe this should be multiple
parts..." ^^;;

Thanks for reading this far, I hope it was helpful!  : )

<!--
With our warm-up done, let's move on to the real stuff!


```sh
$ idris2 --build tinyidris.ipkg
```
and see what we need to do. It'll spit out some warnings about shadowing names
(which makes sense, since TinyIdris was made by ripping out parts of regular
Idris), but crucially it should also spit out these four lines:

```
Warning: compiling hole TTImp.Elab.Term.todo_infer_lam
Warning: compiling hole TTImp.Elab.Term.todo_in_part_2
Warning: compiling hole Core.CaseBuilder.weakenNs
Warning: compiling hole Core.CaseBuilder.weaken
```

These are the missing functions which we need to implement/fix. So then, let's
get cracking!


### Weakening

Weakening, as mentioned in the course, is the introduction of a new name to an
existing scope.
-->

