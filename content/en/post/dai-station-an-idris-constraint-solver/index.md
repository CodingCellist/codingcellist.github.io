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


{{< toc >}}


## Intro

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

The motivation was that verifying correctness via something like model-checking
is very expensive, whereas constraint solving is less expensive and so might be
"good enough" for certain scenarios (side-note: I haven't come up with such a
scenario yet...). Of course, there is no such thing as a free lunch: constraint
modelling is a whole science on its own, and we don't get counterexamples when
no solutions can be found. Nevertheless, it seemed like a worthwhile thing to
implement; if nothing else, just for the fun of it (for a suitable definition of
"fun".)


## The most important step: naming

As with any project, the most important (and often most difficult) challenge is:
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

With the hardest bit out of the way, time to write a constraint solver!


## Starting point

Turns out writing constraint solvers is somewhat difficult; who knew?...

I am not starting from nothing, but I'm not exactly an expert either: many years
ago, as part of my undergrad, I took a course on constraint solvers. One of the
practicals was to write one. Which is good, because it means I have some
(distant) knowledge of how this is meant to work. What is not good is that my
old implementation is in Java, and it is only somewhat coherent because I got it
working on my 4th "go back to the beginning, branch, and start from
scratch"-attempt, with about 24 hours to go before the deadline (the branch is
called `death` and the commit messages include gems like "The definition of
insanity" and "YEET!")...

So. Not the best starting point, but better than nothing.


## General idea

### Forward-Checking

The algorithm we'll be using is 2-way branching forward-checking. The general
idea is: given some variables which have some value-domains, along with
constraints between these variables:

  1. Select a variable and a value from its domain to try.
  2. Try assigning the variable to the value. If the constraints still hold, try
       a new variable+value which satisfy the constraints given this assignment.
  3. If we tried the assignment and discovered we violated a constraint, remove
       the value from the domain and try again (unless we're out of options, in
       which case no solution could be found).
  4. If we have successfully managed to assign all the variables without finding
       any inconsistencies, a solution has been found and we're done!

The devil in the detail, which makes this algorithm better than a simple
brute-force "try everything until something works" approach, is the second half
of step 2: "try a new variable+value _which satisfy the constraints given this
assignment_". When trying a value, we "forward check" all the other variables
with respect to the constraints and the hypothetical assignment, removing any
value which no longer works from their domains. This saves us from trying
sub-trees that involve values which we _know_ are invalid in the current
attempt.

Steps 2 and 3 above are called the left and right branches respectively, hence
"2-way branching".

### Arcs

"Arcs" are constraints terminology for "directional constraints". When talking
about constraints between two variables, it can be useful to specify "v1 must be
less than v2" _and_ "v2 must be greater than v1". The reason for this is that
some algorithms use this to spot that they don't need to revise all the arcs;
sometimes revising in one direction is enough.

(Forward-Checking isn't one of these algorithms by the way.
But it still uses arcs rather than generic constraints; it's simply a useful way
to think about them.)


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

### Wait a minute!...

This is imperative pseudocode, not functional!

I know, I know. But I felt it was the clearest+easiest way to write things. It
will come back to bite me in the implementation though...


## Function declarations

From the general idea, the first thing to do is forward-declare the main
functions:

```idris
forwardCheck : ?forwardCheckTy

branchFCLeft : ?branchFCLeftTy

branchFCRight : ?branchFCRightTy
```

Here, Idris's support for type-level holes really help, given that we don't know
how to best pass around the problem yet.


## Input format

Constraint problems can be modelled and input in many formats. However, I still
have the CSP instance inputs from my old coursework, so I am just going to use
that.

Each problem is stored in a plain-text `.csp`-file, which is structured as
follows:
  * Lines starting with `//` are considered comments and ignored
  * The first entry is the number of variables.
  * Then follows a number of domains, each on a new line, written  
      `lower, upper`  
      respectively indicating the lower and upper-inclusive
      bounds of the n-th variable. There must be as many of these lines as the
      declared number of variables.
  * Finally, any number of binary constraints follows. (These are _undirected_
      constraints and _not arcs_.)
    - The start of a constraint declaration is `c(v0,v1)`, where `v0` and `v1`
        are the zero-based indices of the variables the constraint concerns. 
    - After the declaration, some number of value-pairs `val0, val1` are listed
        (each on a new line). These indicate the valid value pairings of the two
        variables referenced in the constraint declaration. For example, an
        entry `2, 3` would mean that `v0` can be assigned to `2` if `v1` is
        assigned to `3`, and vice versa.
  * Input files are newline terminated.

### Idris representation

Thinking about how to represent this in Idris, I decided on 3 components:
`Variable`, `Arc`, and `CSP`. And making them records seemed like a sensible
idea, since we'll be doing a lot of updates on the variables as part of
arc revision.

{{< spoiler text="View Idris code" >}}

```idris
record Variable where
  constructor MkVar

  idx : Nat

  assigned : Maybe Nat

  dom : List Nat
```

```idris
record Arc where
  constructor MkArc

  from : Variable
  to : Variable

  validTuples : List (Nat, Nat)
```

```idris
record CSP where
  constructor MkCSP

  vars : List Variable
  arcs : List Arc
```

{{</ spoiler >}}

## The tooling needed

Before even making a start on writing the main functions, we need some tooling.
Mostly this is for arc revision, but there are a couple of annoying consequences
implied when doing arc revision, which will also require some custom functions.

### Some notes on state

Annoyingly, most pseudocode (including mine) assume that domains, variables, and
arcs exist globally and uniquely. That is, updating a variable in one function
updates it everywhere in the general context. This is very convenient for
thinking about how the algorithm works, but less so for implementing it
(especially in a functional language).

I initially tried having everything return a pair with a boolean and the new
state. The idea being that the boolean would indicate whether or not the
revision was successful (and potentially help integrate this into Liam
O'Connor's [Half Deciders](http://liamoc.net/images/applications.pdf), to have
a constraint-solver at the type-level!)

Unfortunately, this proved way too error-prone. I was passing failed states
around accidentally, forgetting to properly undo an update, etc. At one point I
had a constraint solver which did find the solution, but at the same time
somehow had ended up with 10 times as many variables as initially given, and so
kept exploring a (now much bigger) search space before eventually giving up. Not
ideal.

I discussed this with gallais, who had the brilliant suggestion that I could use
`Maybe` instead, since the work was done anyway (the boolean represented the
result of the work, not whether it needed doing) and what I really wanted to do
was to discard the bad state. By returning `Nothing` in case of failure, there
was no way to continue with the incorrect state; it simply wasn't there! This
helped with A) getting the implementation much closer to a working state, and B)
making the logic easier to follow.

### Arc Revision

Since we're not as lucky to have globally accessible state, in order to revise
arcs, we'll need the list of variables, _the list of arcs_, and the current
variable. We'll also store the list of revised variables (as a `SnocList` to
preserve the ordering) so that we can recurse on the list of variables and use
it being empty as a termination case.

```idris
fcReviseFutureArcs :  (vars  : List Variable)
                   -> (rArcs :  List Arc)
                   -> (currVar : Variable)
                   -> (newVars : SnocList Variable)
                   -> Maybe (List Variable, List Arc)
```

If we have exhausted the list of variables without encountering an
inconsistency, we're done:

```idris
fcReviseFutureArcs [] rArcs currVar newVars =
  Just (asList newVars, rArcs)
```

Otherwise, we need to revise the arc between the variable in the list and the
current variable, _unless_ it is the current variable (which would be
nonsensical to revise against), _or_ there is no arc between the variables (in
which case there is nothing constraining the pair's current configuration).

```idris
fcReviseFutureArcs (fv :: fvs) rArcs currVar newVars =
  if fv == currVar
     then fcReviseFutureArcs fvs rArcs currVar (newVars :< fv)
```

Hmm, we need some way to retrieve a specific arc. That sounds slightly
complicated, so let's make a helper function!

```idris
findArc :  (v1 : Variable)
        -> (v2 : Variable)
        -> (arcs : List Arc)
        -> Maybe Arc
findArc v1 v2 arcs =
  case filter (connects v1 v2) arcs of
       [] => Nothing
       (arc :: []) => Just arc
       (arc :: (_ :: _) => assert_total $ idris_crash "findArc_multiarc_ERROR"
```

We filter the list of arcs based on whether there is a directed connection
from `v1` to `v2`, and if there isn't one, that's fine: the variables don't
constrain each other; if there is exactly one, we return it; and if there's more
than one, something's gone wrong so we have to crash. (This was initially a
hole, but due to a funky bug with Sub-Expression Elimination, holes can get
called despite being in unreachable code, so I had to convert it to a crash.)

TODO: fcRevise, reviseDom, hasSupport; explain why not `Maybe List1`

## Acknowledgements

* Guillaume Allais (gallais) for the idea of using `Maybe` for the state
    updates, thereby eliminating the possibility of accidentally using a bad
    state when a guess failed.

