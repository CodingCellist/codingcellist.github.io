---
# Documentation: https://wowchemy.com/docs/managing-content/

title: "Functional Programming Nomenclature Intro"
subtitle: ""
summary: "A brief (ish) overview of common terminology and syntax used in FP,
          with the aim of getting you to think in words rather than weird
          symbols."
authors: [thomas-e-hansen]
tags: [functional programming, guide, intro, lookup]
categories: []
date: 2023-04-24
lastmod: 2023-04-24
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

{{< toc >}}


## Preface

When starting out in functional programming (FP), you'll likely see a lot of
syntax in the languages that you have never come across before and therefore
don't know how to pronounce. Or vice-versa: someone might keep referring to "the
'bind' operator" without you having a clue what that looks like in the language
you're working in. The aim of this post is to try to cover most of those things.

The motivation for creating this post was/is deeply personal. When I first
started my Ph.D., I encountered a multitude of terms and concepts that everyone
around me seemed to Just Know (TM), while I was left feeling perplexed and out
of the loop. Eventually, through numerous awkward questions and conversations
where I felt quite foolish, I managed to unravel the meanings of these arcane
terms and symbols.  Since, as far as I could tell, there wasn't a simple
nomenclature out there ("simple" meaning "answering 'what is this called?'
without raising exponentially more questions") I decided to put together this
reference to hopefully help others avoid the same confusion and headaches I
faced.

You can read it in one go and try to remember the terms, but I believe it might
work better as a lookup reference that you have open adjacent to whatever you're
currently working on. But that's up to you  : )

In any case, the idea is that reading this should at least let you think about
FP in words rather than mystical runes you don't understand (which I've
personally found can be difficult). It should also, hopefully, make it easier
to talk about FP things or understand the feedback you get given from other FP
people.

(Note: Since I mainly do functional programming in
[Idris](https://www.idris-lang.org),
some of these examples will be Idris-specific. However, the syntax should
hopefully not differ too much compared to other FP languages (e.g. Haskell).)


## Disclaimer

**This document is, by nature, a never-ending Work In Progress, and the
explanations are only as good as my own understanding.** Should you encounter
any errors (or terms you would like added), please reach out on this website's
[GitHub repository](https://github.com/CodingCellist/personal-website).


## Syntax


* `>>=` --- "bind"
  {{< spoiler text="More details" >}}

  Bind takes a result and a function which uses the result,
  and combines the two, e.g. a variable `greeting` containing the string
  `"Hello World"` and the function `putStrLn` could be combined as

  ```
  greeting >>= putStrLn
  ```

  which would print the greeting to the terminal when run.

  {{</ spoiler >}}

* `>>` --- "seq", short for "sequence"
  {{< spoiler text="More details" >}}

  In Idris land, this behaves similar to "bind", except it only works with
  things that produce a side-effect (e.g. printing to the terminal) without also
  returning a new value to handle.

  {{</ spoiler >}}

* `:` --- "has/of type" in Idris, and "cons" in Haskell (yes this is
    confusing)

* `::` --- "cons" in Idris, and "has/of type" in Haskell (yes this is
    confusing)

* `[]` --- also referred to as "Nil"

* `()` --- "unit", sometimes also written as: `Unit`


## Terms

* "first-class" --- being able to use the concept everywhere in the language,
    e.g. functions are _first-class_ if you can manipulate them just like you
    would any other term in the language (assign them to variables, pass them to
    other functions, put them in data structures, etc).

* "a record" --- a data structure containing named fields of data where those
    names are automagically also turned into functions (getters).  
    Typically, records also come with special syntax to update their fields.

* "a projection" --- a getter for a record (functional programmers like to use
    maths terminology).

* "data" --- things that you create by describing how to _construct_ them, e.g.
   `MkPair a b` is a _data_ constructor used to create a pair `(a, b)`
  {{< spoiler text="More on pairs" >}}
  Pairs typically also have the projections (getter functions) `fst` and `snd`
  to retrieve `a` and `b` respectively.
  {{</ spoiler >}}

* "codata" --- things that you create by defining their getters rather than
    their constructors; effectively describing how to _deconstruct_ the thing.
    For example, we could define a 'CoPair' as "a thing that has the projections
    `fst` and `snd` such that I can call `fst` on it to get the thing's first
    element and `snd` to get the thing's second element".
  - Why? Mainly because it allows us to define infinite things: a `Stream` is a
      thing you deconstruct by taking the first element, followed by a _stream_
      of potentially infinitely more things. As long as we can take at least one
      element, which is the projection (getter function), everything is fine and
      we can reason about it.

* "mapping" --- synonymous with "function"
  - Usually found in combination with "from a to b", e.g. "a mapping from `Int`
      to `Nat`" means "a function that takes an `Int` and returns a `Nat`".

* "pure" --- something which does not produce any side effects (like printing to
    the terminal) and returns the same output given the same input

* "covering" --- a function where you have defined what to return for all its
    possible inputs.

* "total" --- in Idris: a function which is either covering or productive (what
    is considered total varies from language to language).

* "partial" --- a function where you have _not_ defined what to do for every
    possible input, or a function which may never terminate. In opposition to
    "total".

* "bottom" (also written `_|_` or $\bot$) --- something which is provably false
    or absurd. If you can "construct bottom", you should have a contradiction
    somewhere.

* "top" (also written $\top$) --- something which is trivially true; a
    tautology.

* "eta-expansion" ($\eta$-expansion) --- TODO

* "binders" --- TODO
  - "lambda binders" ($\lambda$-binders) --- TODO
  - "Pi binders" ($\Pi$-binders) --- TODO

* "rig" --- in Idris: the accessibility, i.e. `0` for erased, `1` for linear,
    and `w` (the default, usually not written) for unrestricted.
  {{< spoiler text="Show technical definition" >}}
  A _rig_ is a mathematical concept. It is a set of elements with two binary
  operations "add" and "multiply" such that both operations have an identity
  (e.g. 0 and 1 respectively for natural numbers), multiplication distributes
  over addition, both operations are commutative (a + b = b + a), and
  multiplying by the additive identity (0 for natural numbers) always returns
  that identity (so for natural numbers: a * 0 = 0 * a = 0).  
  The name "rig" comes from "_ring_ without negation" (Get it? We remove the 'n'
  from "ring" to get "rig" because it doesn't have Negation. Mathematicians
  truly are funny people...)  
  The accessibilities in Idris form a rig, hence we refer to them as such.
  {{</ spoiler >}}

* "rig 0" --- in Idris: erased / runtime inaccessible.

* "rig 1" --- in Idris: linear / must be used exactly once.

* "rig w" --- rig omega; in Idris: unlimited use.

* $\cong$ --- TODO

* $\preceq$ --- TODO

* $\vdash$ --- TODO


## Category Theory terms

Category Theory (CT) is a whole area of maths, explaining it is beyond the scope
of this blog entry. Unfortunately for us, a lot of FP is built on ideas and
concepts from CT so we have to at least be aware of it and know _some_ of the
terminology...

{{< spoiler text="Category Theory for Programmers" >}}
Bartosz Milewski has a blog series called
"[Category Theory for Programmers](https://bartoszmilewski.com/2014/10/28/category-theory-for-programmers-the-preface/)"
(also available as a
[book](https://github.com/hmemcpy/milewski-ctfp-pdf)),
which covers the "basics" of CT. I have put 'basics' in quotes here, because I
own the book and read the first section, about 120 _dense_ pages, after which
Bartosz concludes "We've learned the basic vocabulary of category theory." At
this point, I gave up.

**To be clear,** it is _many_ times better than any of the more formal
literature at explaining these things! It just also, in my opinion, goes way
above and beyond what the everyday functional programmer will ever need, and the
explanations have on multiple occasions hurt my brain (I'm still not sure if I
actually understand contravariant functors or if my brain has tricked itself
into thinking it understands it to avoid further headaches...).  The first
couple of entries/chapters might be worth a read, but beyond that you're doing
it out of ~~masochistic tendencies~~ personal interest.
{{</ spoiler >}}

* "category"
  - don't think "a category of what?"
  - it's a mathematical way of describing things which have a common structure
  - examples: TODO
  - "My understanding is that a category describes a whole category of systems
      or the theories that share the same structure." --
      [Bartosz Milewski](https://bartoszmilewski.com/2014/11/04/category-the-essence-of-composition/#comment-45643)

* "functor" --- a mapping from one category to another
  - TODO: examples

* "endofunctor" --- a mapping from a category to itself
  - since Idris (and Haskell) may be considered a category, all functors in them
      are technically _endofunctors_ (and mathematicians like to be precise).

* TODO: eventually get to the infamous "A monad is just a monoid in the category
    of endofunctors, what's the problem?"
  - actual quote:  
    "All told, a monad in X is just a monoid in the category of endofunctors of
    X, with product × replaced by composition of endofunctors and unit set by
    the identity endofunctor." -- Saunders Mac Lane, Categories for the Working
    Mathematician.


{{< spoiler text="Would You Like To Know More?" >}}

* Blog series: [Category Theory for Programmers](https://bartoszmilewski.com/2014/10/28/category-theory-for-programmers-the-preface/)

* Book: [The Little Typer](https://thelittletyper.com/)

{{</ spoiler >}}


And as always, thanks for reading  : )

