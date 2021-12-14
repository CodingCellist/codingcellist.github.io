---
# Documentation: https://wowchemy.com/docs/managing-content/

title: "Functional Programming Nomenclature Intro"
subtitle: ""
summary: "A brief (ish) overview of common terminology and syntax used in FP,
          with the aim of getting you to think in words rather than weird
          symbols."
authors: [thomas-e-hansen]
tags: ["Functional Programming"]
categories: []
date: 2021-11-05T10:52:33+01:00
lastmod:
featured: false
draft: true

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

### Preface

This is a bunch of stuff I found highly confusing when I first started, so to
prevent others having to go through the same pain, I created this brief (ish)
introduction to the terms and readings of things commonly used Functional
Programming (FP). The idea is that reading this should at least let you think
about FP in words rather than mystical runes you don't understand (which I've
personally found can be difficult).
It should also (hopefully) make it easier to talk about things or understand the
feedback you get given from other FP'ers.

Note: Since I mainly do functional programming in
[Idris](https://www.idris-lang.org), some of these examples will be
Idris-specific. However, the syntax should hopefully not differ too much
compared to other FP languages (e.g. Haskell).


### Syntax

You might see a lot of syntax in functional programming languages that you have
not come across before and therefore don't know how to read. Or vice-versa:
Someone might keep referring to "the 'bind' operator" without you having a clue
what that looks like in the language you're programming in. This should
hopefully cover most of those things.

- `>>=` reads "bind"
- `>>` also reads "bind"?
- `::` reads "cons"
- `[]` is also referred to as "Nil"
- `()` reads "unit" and is sometimes also written as such: `Unit`


### Terms

- "first-class" -- premium and likely overpriced. Okay no. "First-class" refers
    to being able to use the concept everywhere in the language, e.g. functions
    are "first-class" if you can manipulate them just like you would any other
    term in the language (assign them to variables, pass them to other
    functions, put them in data structures, etc)
- a "record" is a data structure containing named fields of data, e.g.
  ```idris
  record Person where
    constructor MkPerson
    name : String
    age : Nat
  ```
  is a _record_ describing a person, storing their `name` and `age` as named
  fields
- a "projection" onto a record is really just a getter (functional programmers
    like the maths terminology)
- "data" -- things that you create by describing how to _construct_ them, e.g.
   `MkPair a b` is the constructor used to create a _pair_/2-tuple `(a, b)`
  - pairs typically then have the _projections_ `fst` and `snd` to retrieve `a`
      and `b` respectively from a given pair
- "codata" -- things that you create by describing how to _deconstruct_ them,
    e.g. "a thing that has the projections `fst` and `snd` s.t. I can call `fst`
    on it to get the thing's first element and `snd` to get the thing's second
    element, is called a _pair_"
  - Why? Because it's nicer to do it that way sometimes
  - Also allows for infinite things: A `Stream` is a thing you deconstruct by
      taking the first element, followed by a cons of potentially infinitely
      more `Stream`

- "mapping" -- synonymous with "function"
- "pure" -- something which does not produce any side effects and returnns the
    same output given the same input
- "covering" -- a function where you have defined what to return for all its
    possible inputs
- "total" -- it depends, but in Idris: a function which is either covering or
    productive
- "partial" -- a function which may never terminate

- "bottom" (also written `_|_` or $\bot$) -- something which is provably false or
    absurd; if you can arrive at this, you (hopefully) have a contradiction
    somewhere
- "top" (also written $\top$) -- something which is trivially true; a
    tautology

- "eta-expand"
- "binders"
  - "$\Pi$-binders"
- "Rig 0"
- $\cong$
- $\preceq$
- $\vdash$


### Category Theory (CT) terms

CT is a whole area of maths, explaining it is beyond the scope of this blog
entry.  Unfortunately for you, a lot of FP is built on ideas and concepts from
CT so you have to at least be aware of it... and know _some_ of the terminology.
- a "category"
  - don't think "a category of what?"
  - it's a mathematical way of describing things which have a common structure
  - examples: TODO
  - "My understanding is that a category describes a whole category of systems
      or the theories that share the same structure." --
      [Bartosz Milewski](https://bartoszmilewski.com/2014/11/04/category-the-essence-of-composition/#comment-45643)
- a "functor" is a mapping from one category to another
  - TODO: examples
- an "*endo*functor" is a mapping from a category to itself

Would you like to know more (TODO: image?)
- [Bartosz Milewski's book on CT for Programmers](https://bartoszmilewski.com/2014/10/28/category-theory-for-programmers-the-preface/)
    (which I have already referenced in this post) is very good!

- eventually get to the infamous "A monad is just a monoid in the category of
    endofunctors, what's the problem?"
  - actual quote:  
    "All told, a monad in X is just a monoid in the category of endofunctors of
    X, with product × replaced by composition of endofunctors and unit set by
    the identity endofunctor." -- Saunders Mac Lane, Categories for the Working
    Mathematician

