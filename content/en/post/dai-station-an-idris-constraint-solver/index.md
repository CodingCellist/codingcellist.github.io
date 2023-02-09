---
# Documentation: https://wowchemy.com/docs/managing-content/

title: "Dai Station: an Idris Constraint Solver"
subtitle: ""
summary: ""
authors: [thomas-e-hansen]
tags: [idris2, functional programming, constraints]
categories: []
date: 2023-02-08T16:23:56+01:00
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


**If you are a CS4402 student at the University of St Andrews reading this for
"inspiration", remember to cite it!**


# Intro

As part of my Ph.D. exploration on how we know the types we're using model what
we think they do, I decided to try to implement a constraint solver in Idris
(technically Idris2, but Idris1 is deprecated at this point, so I use 'Idris'
and 'Idris2' interchangeably).

If you are not familiar with the term, a "constraint solver" is a tool which
solves Constraint Satisfaction Problems (CSPs). CSPs appear a surprising number
of both real- and game-scenarios:
  * optimised packing aka. The Knapsack Problem (given a number of items with a
      value and weight, pack the highest total value in a limited space, e.g. a
      knapsack, while keeping the total weight as low as possible),
  * Sudoku,
  * timetabling / scheduling,
  * N-Queens (arranging N queens on an N-by-N chess board such that none of them
      threaten each other),
  * solitaire,
  * ware distribution / routing,
  * just to name a few...

These are called "constraint problems" (or CSPs) because they all have some
variables which are _constrained_ in certain ways (for example, in Sudoku, one
constraint is that no line may contain duplicate digits).

The idea was that verifying correctness via something like model-checking is
very expensive, whereas constraint solving is less expensive and so might be
"good enough" for certain scenarios (side-note: I haven't come up with one of
those yet...). Of course, there is no such thing as a free lunch: constraint
modelling is a whole science on its own, and we don't get counterexamples when
no solutions can be found. Nevertheless, it seemed like a worthwhile thing to
implement; if nothing else for the fun of it (for a suitable definition of
'fun'.)


# The most important step: naming

As with any project, the most important (and often most difficult) challenge is
finding a good name for it. Fortunately, the
[Ivor the Engine Wiki](https://ivortheengine.fandom.com/wiki/Ivor_the_Engine_Wiki)
has a list of characters and places we can pick from to expand the "Idris
Cinematic Universe". (Which is well established by the way. We have:
  * The Idris language itself, named after the
      [singing red dragon](https://ivortheengine.fandom.com/wiki/Idris);
  * Blodwen, the early prototype of Idris2, named after one of Idris the Dragon's
      kids (see further down the dragon's wiki page);
  * the proof-engine
      [Ivor](https://www.type-driven.org.uk/edwinb/papers/ivor.pdf),
      named after
      [Ivor the Engine](https://ivortheengine.fandom.com/wiki/Ivor_the_Engine_(Character));

And to top it all off, the character who pilots Ivor and discovers Idris is
called "Jones the Steam", but his first name is
[_Edwin_](https://ivortheengine.fandom.com/wiki/Edwin_Jones)!)

After much consideration, I decided to go for "Dai Station", the station manager
in Ivor the Engine. He deals with scheduling and regulations as part of his
dayjob; sounds exactly like a constraint solver! ^^

![A still of Dai Station: a moustachioed man wearing a conductors uniform and hat, holding a regulations book](/media/ivortheengine-fandom-wiki-dai-station.jpg "Dai Station (Image from [Fandom wiki](https://static.wikia.nocookie.net/ivortheengine/images/a/a7/D1-1-.gif/revision/latest?cb=20081114013036), CC-BY-SA)")

With the hardest bit out of the way, let's write a constraint solver!


# Writing a constraint solver

Turns out these are somewhat difficult to write; who knew?...

I am not starting from nothing, but I'm not exactly an expert either: many years
ago, as part of my undergrad, I took a course on constraint solvers. One of the
practicals was to write one. Which is good, because it means I have some
(distant) knowledge of how this is meant to work. What is not good is that the
pseudocode is all imperative, not functional; my old implementation is in Java;
and it is only somewhat coherent because I only got it working on my 4th "go
back to the beginning, branch, and start from scratch"-attempt, with about 24
hours to go before the deadline (the branch is called `death` and the commit
messages include gems like "The definition of insanity" and "YEET!")...

So. Not the best starting point, but better than nothing.

## General idea

The algorithm we'll be using is 2-way branching forward-checking. The general
idea is: given some variables which have some value-domains, along with
constraints between these variables:

  1. Select a variable and a value from its domain to try.
  2. Try the assignment. If the constraints still hold, try a new variable+value
       which satisfy the constraints given this assignment.
  3. If we tried the assignment and discovered we violated a constraint, remove
       the value from the domain and try again (unless we're out of options, in
       which case no solution could be found).
  4. If we have successfully managed to assign all the variables without finding
       any inconsistencies, a solution has been found and we're done!

The devil in the detail, which makes this algorithm better than a simple
brute-force "try everything until something works" approach, is "try a new
variable+value _which satisfy the constraints given this assignment_". When
trying a value, we "forward check" all the other variables with respect to the
constraints and the hypothetical assignment. This saves us from trying sub-trees
that involve values which we know are invalid in the current attempt.

Steps 2 and 3 above are called the left and right branches respectively, hence
"2-way branching".

## Arcs

"Arcs" are just constraints terminology for "directional constraints". When
talking about constraints between two variables, it can be useful to specify "v1
must be less than v2" _and_ "v2 must be greater than v1". The reason for this is
that some algorithms use this to spot that they don't need to revise all the
arcs; one direction is enough.

(As we'll see next, forward-checking isn't one of these algorithms by the way.
But it still uses arcs rather than generic constraints.)

## Pseudocode

Based on the general idea, we can come up with some pseudocode.

### Main recursive function / starting-point

```
// main function
forwardCheck(varList):
  if allAssigned(varList):
    return the solution and stop

  else:
    var := selectVar(varList)
    val := selectVal(var.domain)
    branchLeft(varList, var, val)
    branchRight(varList, var, val)
```

### Left-branching

(attempted assignment and forward-checking)

```
// try the given assignment
branchLeft(varList, var, val):
  assign(var, val)

  // don't revise the variable against itself
  forall forwardVar in (varList excluding var):
    if there is an arc between forwardVar and var:

      revise(forwardVar.domain, arc<forwardVar, var>)

      if nonEmpty(forwardVar.revisedDomain):
        // continue with the new state
        forwardCheck(varList)

      else:
        // incorrect attempt detected
        // our attempt resulted in no candidates for forwardVar
        // undo ALL our changes and break out of the loop
        undoRevise
        undoAssign
        break
```

### Right-branching

(value deletion and forward-checking)

```
// try deleting the value
branchRight(varList, var, val):
  delete(val, var.domain)

  // don't revise the variable against itself
  forall forwardVar in (varList excluding var):
    if there is an arc between forwardVar and var:

      revise(forwardVar.domain, arc<forwardVar, var>)

      if nonEmpty(forwardVar.revisedDomain):
        // continue with the new state
        forwardCheck(varList)

      else:
        // incorrect deletion detected
        // our value deletion resulted in no candidates for
        // forwardVar; undo ALL our changes and break out
        // of the loop
        undoRevise
        undoDelete
        break
```

### Arc revision

(update a domain based on the directional constraint)

```
// arc revision (domain updating)
revise(arc):
  candidates := arc.from.domain   // possible values
  pairings := arc.to.domain       // possible supporting values

  forall candidate in candidates:
    forall pairing in pairings:
      if arc.supports(candidate, pairing):
        // the candidate has at least one possible
        // pairing where the constraint still holds
        arc.from.keep(candidate)

    // all pairings were tried without success
    arc.from.discard(candidate)
```


## Function declarations

TODO

From the general idea, the first thing to do is forward-declare the main
functions:

```idris
forwardCheck : ?forwardCheckTy

branchFCLeft : ?branchFCLeftTy

branchFCRight : ?branchFCRightTy
```

Here, Idris's support for type-level holes really help, given that we don't know
how to best pass around the problem yet.

