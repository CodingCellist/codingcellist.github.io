---
# Documentation: https://wowchemy.com/docs/managing-content/

title: "Type You an Idris for Great Good!"
subtitle: ""
summary: "The best way to learn & understand a thing is to implement it. So
          let's implement (a subset) of Idris2!"
authors: [thomas-e-hansen]
tags: [idris2, type-theory, functional-programming, splv2020]
categories: []
date: 2022-02-17T11:38:10+01:00
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

I've personally struggled with properly understanding the internals of Idris2.
By "properly", I mean: knowing where to look when I encounter errors,
understanding what people in the Idris community refer to when discussing
certain concepts and parts of Idris, knowing what the intermediary
representations are for implementing custom backends, that kind of stuff. Every
time I've encountered these in the past, I've gone "I really ought to learn this
at some point!", and then promptly gotten distracted by a project or some
reading I was doing.

So now, 1½ years into my PhD, armed with at least _some_ understanding of the
underlying concepts and terms, I've decided to try and jump back in to Edwin's
course from the Scottish Programming Language and Verification Summer School
(SPLV) in 2020, which has you implement `TinyIdris` --- a scaled down version of
full Idris. When I attended this live, I hadn't even technically started yet, so
the whole thing was a bit overwhelming and above my level; hopefully this time
it's manageable.

If you're also confused, or just want to know more, come along for the ride!

(oh, and in case you just want to watch the course, it is on
[this YouTube playlist](https://www.youtube.com/playlist?list=PLmYPUe8PWHKqBRJfwBr4qga7WIs7r60Ql))


### Setting up

First, we'll need a copy of the starting source code for TinyIdris. Use `git` to
clone it to a directory of your choice (I've gone with `splv20-tinyidris`):

```sh
$ git clone git@github.com:edwinb/splv20 splv20-tinyidris
```

Next, if you're running a reasonably recent version of Idris2
(⩾ v0.5.0), you'll need to apply [this patch](/files/tinyidris-0.5.0.patch)
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
    just, `toList`).
* `Data.List1` now uses `:::` as a constructor, not `::`, meaning that we can't
    pattern-match on `[p']` or similar since it desugars to `p' :: []`. Instead,
    we need to match on `(p' ::: [])`. There were also some similar problems in
    terms of constructing and returning new `List1`s.
* `Show` is now `total`, but this introduces some... _difficulties_ when
    implementing it for certain datatypes. A solution is to just stick a
    `covering` at the top.
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


### Warmup

#### Exercise 1

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

#### Exercise 2

Proving that two `Name`s are equal is a bit more complicated. Although,
thankfully, this is not a `DecEq` (_decidable_ equality) implementation, which
means we don't need to prove how it is impossible for the `Name`s to be equal.  
Again, start by interactively generating a definition using `<localleader> d`,
then case-splitting on the arguments, and introducing a generic pattern match
for different types of `Name`s:

```idris
nameEq : (x : Name) -> (y : Name) -> Maybe (x = y)
nameEq (UN x)   (UN y)   = ?nameEq_rhs_2
nameEq (MN x i) (MN y j) = ?nameEq_rhs_5
nameEq _        _        = Nothing
```

Let's start with `UN`s. Idris comes with built-in decidable equality for
`String`s, so let's use that! If two names' strings are decidedly equal, then
the `Name`s must be too. Recall that `Refl` is a proof of equality, and that
`rewrite` let's us use proofs to transform the type of the right hand side:

```idris
nameEq : (x : Name) -> (y : Name) -> Maybe (x = y)
nameEq (UN x)   (UN y)   = case decEq x y of
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
nameEq (UN x)   (UN y)   = case decEq x y of
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

#### Exercise 3

Remember how I just said we thankfully didn't have to implement `DecEq Name`?
Psych! That's exercise 3 ^^

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

  decEq (UN x)   (MN y j) =
    ?decEq_rhs_3

  decEq (MN x i) (UN y)   =
    ?decEq_rhs_4

  decEq (MN x i) (MN y j) =
    ?decEq_rhs_5

```

The problem is that the type of `?decEq_rhs_7` is `UN x = UN y -> Void`, i.e. a
proof that if the two names are equal, then we have a contradiction; in other
words, a proof that the two names _cannot_ be equal. However, we only have a
proof that their internal strings differ. Sounds like we need a helper function
(or a lemma, if you will):

```idris
unStringsDiffer : (contra : x = y -> Void) -> (prf : UN x = UN y) -> Void
```

(If you are uncertain about `DecEq`, proofs and contras, there are more details
in [this blog post](/en/post/intro-to-decidable-equality))

This lemma is trivial enough that Idris can actually figure it out from the type
declaration. Ask Idris to _generate_ a definition by putting the cursor on
`unStringsDiffer` and pressing `<localleader> g`:

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

  decEq (UN x)   (MN y j) = No ?decEq_rhs_3

  decEq (MN x i) (UN y)   = No ?decEq_rhs_4

  decEq (MN x i) (MN y j) =
    ?decEq_rhs_5

```

Reloading the file (`<localleader> r`) confirms that things type-check and Idris
is happy.

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
plausible difference. This makes for slightly nicer logic/reasoning in my
opinion (although, as we'll see shortly, it doesn't technically matter). If we'd
used the `rewrite` _inside_ the `case`-block, we'd get:

```idris
mnNumbersDiffer : MN x i = MN y j -> Void
```

Here, although _we_, the human, know that we're under a `(Yes prfXY)`-case, we
have never actually told Idris that/what that means, so it doesn't know that the
strings `x` and `y` are the same and that only `i` and `j` might differ.

If we now lift (using `<localleader> l`) both the holes, making sure to lift
these all the way above the `DecEq Name` declaration,  we'll get some useful
lemma types which we can generate definitions from:

```idris
mnNumbersDiffer : x = y -> (i = j -> Void) -> MN y i = MN y j -> Void

mnStringsDiffer : (x = y -> Void) -> MN x i = MN y j -> Void
```

For `mnNumbersDiffer`, you'll notice that Idris has actually included more
information than we need: the proof that `x = y`. This is because the
hole-lifting functionality uses a "better safe than sorry" approach, including
as much information from the context where the hole was as it can. Refine the
types a bit (and name the arguments, just for neatness) to get:

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

By the way, this is why I said that the first `rewrite` doesn't technically
matter for the `No` case: The `mnNumbersDiffer` lemma holds without needing any
info about the strings.

Coming back to the cross-comparing cases. To us, clearly we cannot construct an
instance of `Refl` for these, since `MN` takes more arguments than `UN`.
However, Idris doesn't know this (yet)! If we look at the type of `?decEq_rhs_3`
we see that need some way of saying that `UN x = MN y j -> Void`. Having
something which cannot be constructed is known as that thing being
`Uninhabited`, with its construction resulting in something `absurd` (i.e. if we
constructed it, we clearly broke the rules somehow). We can sketch the two
`Uninhabited` implementations:

```idris
Uninhabited ((UN _) = (MN _ _)) where
  uninhabited prf = ?un_mn_uninhabited

Uninhabited ((MN _ _) = (UN _)) where
  uninhabited prf = ?mn_un_uninhabited
```

Now, if we simply case-split on `prf` in each definition, Idris generates the
following for both:

```idris
  uninhabited Refl impossible
```

The `impossible` keyword means that there is no way to make the expression
type-check. Which is correct, since there is no way we can have `Refl` take its
expected implicit arguments in these two cases.

Having `Uninhabited` implementations allows us to use `absurd` to finish off the
`DecEq Name` implementation:

```idris
  decEq (UN x)   (MN y j) = No absurd

  decEq (MN x i) (UN y)   = No absurd
```

Together with all the previous definitions, we can reload and confirm that
`DecEq Name` type-checks and that there are no holes left.

With our warm-up done, let's move on to the real stuff!


<!--
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

