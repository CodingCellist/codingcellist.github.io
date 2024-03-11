---
# Documentation: https://wowchemy.com/docs/managing-content/

title: "Dai Station: an Idris Constraint Solver"
subtitle: ""
summary: "As part of my Ph.D. exploration on how we know the types we're using
          model what we think they do, I decided to try to implement a
          constraint solver in Idris (technically Idris2, but Idris1 is
          deprecated at this point, so I use 'Idris' and 'Idris2'
          interchangeably)."
authors: [thomas-e-hansen]
tags: [idris2, functional programming, constraint programming]
categories: []
date: 2023-02-16
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
"inspiration" (or just a student in general, actually) _remember to cite it!_**


{{< toc >}}


## Intro

As part of my Ph.D. exploration on how we know the types we're using model what
we think they do, I decided to try to implement a constraint solver in Idris
(technically Idris2, but Idris1 is deprecated at this point, so I use 'Idris'
and 'Idris2' interchangeably).

In case you are not familiar with the term, a "constraint solver" is a tool
which solves Constraint Satisfaction Problems (CSPs). CSPs appear in a
surprising number of both real-life and game scenarios:
  * Optimised packing aka. The Knapsack Problem (given a number of items with a
      value and weight, pack the highest total value in a limited space, e.g. a
      knapsack, while keeping the total weight as low as possible),
  * Sudoku,
  * timetabling / scheduling,
  * N-Queens (arranging N queens on an N-by-N chess board such that none of them
      threaten each other),
  * solitaire,
  * ware distribution / routing.

These are called "constraint problems" (or CSPs) because they all involve
variables which are _constrained_ in certain ways (for example, in Sudoku, one
constraint is that no line may contain duplicate digits).

The motivation was (partially) that I just wanted to try it to see if it could
be done, but also (more seriously) because verifying correctness via something
like model-checking is very expensive, whereas constraint solving is less
expensive and so might be "good enough" for certain scenarios (side-note: I
haven't come up with such a scenario yet...). Of course, there is no such thing
as a free lunch: constraint modelling is a whole science on its own, and we
don't get counterexamples when no solutions can be found.

So yeah, it seemed like a worthwhile thing to implement. If nothing else, just
for the fun of it (for a suitable definition of "fun").


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

![A still of Dai Station: a moustachioed man wearing a conductors uniform and hat, holding a regulations book](ivortheengine-fandom-wiki-dai-station.jpg "Dai Station (Image from [Fandom wiki](https://static.wikia.nocookie.net/ivortheengine/images/a/a7/D1-1-.gif/revision/latest?cb=20081114013036), CC-BY-SA)")

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
idea is: given a number of variables which have some domains of possible values,
along with some constraints between these variables:

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
with respect to the constraints and the hypothetical change (assignment or
removal), pruning any value which no longer works from their domains. This
saves us from trying sub-trees that involve values which we _know_ are invalid
in the current attempt.

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

Based on the general idea, we can come up with some pseudocode:

### Main recursive function / starting-point

```
// main function
forwardCheck(varList):
  if allAssigned(varList):
    stop and return the solution

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
        // invalid assignment detected
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
        // invalid deletion detected
        // our value deletion resulted in no candidates for
        // forwardVar; undo ALL our changes and break out
        // of the loop
        undoRevise
        undoDelete
        break
```

### Arc revision

(updating a domain based on the directional constraint)

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

{{< spoiler text="Show Idris representation" >}}

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

Before even making a start on writing the main functions, we need to implement
some tooling.  Mostly this is for arc revision, but there are a couple of
annoying consequences implied when doing arc revision, which will also require
some custom functions.

### Some notes on state

Annoyingly, most pseudocode (including mine) assume that domains, variables, and
arcs exist globally and uniquely. That is, updating a variable in one function
updates it everywhere in the general context. This is very convenient for
thinking about how the algorithm works, but less so for implementing it
(especially in a functional language).

I initially tried having everything return a pair with a boolean and the new
state. The idea being that the boolean would indicate whether or not the
revision was successful (and potentially help integrate this into Liam
O'Connor's [Half-Deciders](http://liamoc.net/images/applications.pdf), to have
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

Let's think a bit more thoroughly about what needs doing for arc revision (I
often find putting these things into words helps a lot more than just staring at
pseudocode): Arc revision involves accessing the arcs and variables in the
problem, checking their domains and values against the accepted pairs in the
relevant arc, and then removing any value from its parent domain if it isn't
consistent with the arc. And all of this is done as part of either an
assignment- or a deletion-attempt, meaning there is a current, special variable
which is the one we're attempting to manipulate. Okay, that (hopefully) makes
things clearer!

Since we're not as lucky as to have globally accessible state, in order to
revise arcs, we'll need the list of variables, _the list of arcs_, and the
current variable. We don't get `ConcurrentModificationException`s in Idris, but
it's still good to avoid modifying the list we're iterating over, especially
when we ideally want a nice termination condition (like the list being empty).
So to help with that, we'll store the list of revised variables as a separate
_`Snoc`_`List` (to preserve the ordering).

Let's put all of that into a function declaration!

```idris
fcReviseFutureArcs :  (vars  : List Variable)
                   -> (rArcs :  List Arc)
                   -> (currVar : Variable)
                   -> (newVars : SnocList Variable)
                   -> Maybe (List Variable, List Arc)
```

"Iterate, but make it functional" -- The easiest way to do this is often to use
recursion, so we'll need a base-case: If we have exhausted the list of variables
without creating any problems, we're done:

```idris
fcReviseFutureArcs [] rArcs currVar newVars =
  Just (asList newVars, rArcs)
```

Otherwise, we "iterate": we look at the first variable in the list and revise
the arc between it and the current variable, _unless_ we've reached the current
variable (which it would be nonsensical to revise with itself), in which case we
keep it as-is and keep going on the rest of the variables.

```idris
fcReviseFutureArcs (fv :: fvs) rArcs currVar newVars =
  if fv == currVar
     then fcReviseFutureArcs fvs rArcs currVar (newVars :< fv)
     else ?reviseTheArc
```

But in order to revise the arc, we need to actually have it; we need some way to
retrieve a specific arc. That sounds slightly complicated, so let's make a
helper function!

#### Finding a specific arc

```idris
findArc :  (v1 : Variable)
        -> (v2 : Variable)
        -> (arcs : List Arc)
        -> Maybe Arc
```

An arc _connects_ `v1` to `v2` iff it goes _from_ `v1` _to_ `v2`. It is possible
that there is no arc between the two variables, which means they don't constrain
each other in any way, which is completely fine; less revision work for us! On
the other hand, if we somehow ended up with more than one arc between the
variables, something's gone horribly wrong...

```idris
findArc v1 v2 arcs =
  case filter (connects v1 v2) arcs of
       [] => Nothing
       (arc :: []) => Just arc
       (arc :: (_ :: _) => assert_total $ idris_crash "findArc_multiarc_ERROR"
```

#### Back to arc revision

Now that we can retrieve a specific arc, we can revise it! (Unless there is
nothing to revise against, in which case we just keep going.)

```idris
fcReviseFutureArcs (fv :: fvs) rArcs currVar newVars =
  if fv == currVar
     then fcReviseFutureArcs fvs rArcs currVar (newVars :< fv)
     else case findArc fv currVar of
          Nothing => fcReviseFutureArcs fvs rArcs currVar (newVars :< fv)
          Just arc => ?reviseTheArc arc
```

Now. How do we actually revise a specific arc? Like, how do we do it in a
functional style?

First things first. Revising an arc is the act of taking an arc and pruning the
domain of one of its variables. This changes the arc (since one of its variables
change), so we get a new, revised arc back. However, pruning the domain may
result in it being wiped out, which is indicative of a dead end in our current
attempt, in which case we should discard the defective attempt.

This gives us a starting point:

```idris
fcRevise : (arc : Arc) -> Maybe Arc
fcRevise arc@(MkArc from to validTups) = ?fcRevise_rhs
```

Now we "just" need to prune a domain. The arc is between a forward-checked
variable and the current variable, so we only want to update the `from`
variable's domain. A domain is a list of values, so revising it should yield a
new list of values (which may be empty, in which case something's wrong!):

```idris
fcRevise : (arc : Arc) -> Maybe Arc
fcRevise arc@(MkArc from to validTups) =
  case ?reviseDom (getDom from) to validTups [<] of
       [] => Nothing
       revisedDom@(_ :: _) => ?fcRevise_success_rhs
```

#### A subtlety with domains

You may have noticed we use `getDom` rather than `from.dom` in the code above.
This is because there is an incredibly subtle, but critical problem with just
using the projection: what happens if we are partially through trying a solution
and the forward-checked variable is assigned? Its domain may still have
candidate values which could be tried in a different attempt, _but_ it doesn't
make sense to check against those here! What matters is the value the variable
_currently_ holds.

When we're forward-checking, we want to know if our current attempt on a
variable is consistent with respect to some other variable and the arc between
them. Now, if the other variable, the one we are forward-checking, is already
assigned, then we don't care about confirming our attempt with values it _may_
take in the future, we only care about if our attempt is consistent with our
overall attempt so far! In other words, we only want to check against the
assigned value!

So the `.dom` projection is not good enough: it doesn't consider whether the
variable is assigned (why would it?). We need a function which returns the
domain iff the variable is _unassigned_ and, if the variable _is_ assigned,
returns a singleton list containing the assigned value as the "domain". This is
what the `getDom` function does.

This subtlety took me a lot of `Debug.Trace`-ing to narrow down, since without
it, the code looks perfectly correct, except the resulting arc revisor ends up
trying nonsense despite it having established earlier on that there exists a
value assignment which works for the subtree we're currently exploring.

#### Revising a domain

Out of the frying pan, into the fire. Domain revision (the `?reviseDom` hole)
also requires a bit of thinking about. Mostly because of imperative pseudocode:
it has us iterate through the list of value pairings, testing each one until a
support is found or we've exhausted the possible pairings, in which case the
value needs to be pruned from the domain.

As with the main arc revision function, the obvious alternative to iterating is
to recurse on something. In this case, we are iterating over a domain, which is
a list of values. That sounds like it should work recursively. However, we also
need to remember that we're doing this with respect to a current variable and
some valid tuples from an arc. _And_, we're constructing a new domain, so best
keep track of that as well!

All in all, this becomes:

```idris
reviseDom :  (fvDom : List Nat)
          -> (currVar : Variable)
          -> (validTups : List (Nat, Nat))
          -> (newDom : SnocList Nat)
          -> List Nat
```

If we have exhausted our list of values, we are done and can present our new
domain (it may be empty, but we've dealt with that in `fcRevise`):

```idris
reviseDom [] currVar validTups newDom = toList newDom
```

Otherwise, we need to try the potential value from the domain with all possible
pairings from the current variable's domain (still remembering that domains are
fickle, tricksy things). And we're in functional-land, so rather than trying a
pairing one at a time, we just construct all of them!

```idris
reviseDom (fVal :: fVals) currVar validTups newDom =
  let pairings := map (MkPair fVal) (getDom currVar)
```

Now that we have the pairings, we need to check if there is at least one pair
which is supported/valid, i.e. if _any_ of the pairings are an _element_ of the
`validTups`.

```idris
      supported := any (\pairing => elem pairing validTups) pairings
```

As a bonus, `any` is lazy and short-circuits from the left, meaning we'll stop
as soon as a supporting pair is found.

The whole point of this was to revise the domain, so if we found a support, we
keep the value, and if we didn't, we don't.

```idris
  in if supported
        then reviseDom fvs currVar validTups (newDom :< fv)
        else reviseDom fvs currVar validTups newDom
```

#### Updating a domain

Now that we can revise a domain, being careful to respect previous assignments,
the only piece left in this part of the puzzle is how to propagate the domain
update.

```idris
fcRevise : (arc : Arc) -> Maybe Arc
fcRevise arc@(MkArc from to validTups) =
  case reviseDom (getDom from) to validTups [<] of
       [] => Nothing    -- domain got wiped out, no new state
       revisedDom@(_ :: _) => ?fcRevise_success_rhs
```

Since domains belong to variables, but variables exist both on their own _and_
as part of arcs (and we don't have shared state/pass-by-reference), we need to
perform two updates: first, update the variable to have a new domain, and then
update the arc's `from` variable to the one with the new domain.

```idris
       revisedDom@(_ :: _) =>
         let revisedVar : Variable := { dom := revisedDom } from
             revisedArc : Arc := { from := revisedVar } arc
         in Just revisedArc     -- successfully updated the state
```

(Idris was having trouble inferring the type of the record updates, hence the
explicit typing in the `let`-bindings.)

#### Completely revising an arc

Remember,
[a long time ago](#back-to-arc-revision),
we were "just" trying revise an arc?... It's almost time to fit the pieces
together; home stretch!

We've now got a function for revising a single arc, which updates its internal
state, and returns `Nothing` if a domain-wipeout occurred as part of the arc
revision. In the latter case, we need to throw away any intermediary computation
that may have occurred and propagate the `Nothing`/failure indication.

```idris
     else case findArc fv currVar of
          Nothing => fcReviseFutureArcs fvs rArcs currVar (newVars :< fv)
          Just arc =>   -- we can now do something here!
            case fcRevise arc of
                 Nothing => Nothing     -- wipeout, discard the state
                 Just rArc => ?arcRevisionSuccess
```

In the case where arc revision succeeded, we need to propagate the new state to
the rest of the problem we're solving. We are already keeping a (snoc)list of
new variables, so that part is fine. But we also need to be careful to replace
all outdated copies of the variable in the list of arcs, since any of them may
use the variable as part of a different constraint!

```idris
            case fcRevise arc of
                 Nothing => Nothing     -- wipeout, discard the state
                 Just rArc =>   -- arc revision succeeded, propagate!
                   let fv' = rArc.from
                       rArcs' = map (setArcVar fv') rArcs
                   in ?arcRevisionSuccess
```

Here, `setArcVar` takes the new variable and updates the corresponding `from` or
`to` field of each arc (depending on which contains the old copy), leaving the
arc unaffected if it doesn't involve `fv'` at all.

#### Recurse!

Finally, we remember that all of this was part of a massive detour to do one
"small" recursive step: we still need to repeat this entire process for any
variables we haven't forward-checked yet:

```idris
                 Just rArc =>   -- arc revision succeeded, propagate!
                   let fv' = rArc.from
                       rArcs' = map (setArcVar fv') rArcs
                       newVars' = newVars :< fv'
                   in fcReviseFutureArcs fvs rArcs' currVar newVars'
```

### Propagating changes in general

As if nested record updates weren't enough of a pain to update, there are also
these pesky lists of records we're passing around. And, annoyingly, we also
sometimes need to propagate changes to those. However, they are slightly
trickier since, for example, in the case of the list of variables, ordering
matters: there are various heuristics one can apply to variable selection, but
the default is to try them _in the order given_. This is one of the reasons why
we've been using `SnocList`s everywhere.

To replace variables, and possibly other things, in the general problem, while
preserving the order they were given in, we need a couple of helper functions.
The logic is straightforward: recurse through the list; if we've found the
item to replace, do it; otherwise, keep going down the rest of the list until
it's empty or we find the thing to replace.

```idris
orderedReplace : Eq a => List a -> a -> List a
orderedReplace [] _ = []
orderedReplace (x :: xs) new =
  if x == new
     then new :: xs
     else x :: orderedReplace xs new
```

For a list of new elements, we can traverse that list, using the function above
to perform a single update with each element.

```idris
orderedUpdates : Eq a => List a -> (upds : List a) -> List a
orderedUpdates done [] = done
orderedUpdates todo (upd :: upds) =
  let anUpdate = orderedReplace todo upd
  in orderedUpdates anUpdate upds
```

(It's entirely possible there are functions which can do this in the standard
library, but I found it easier to just define them.)


## Forward-Checking!

Finally we've arrived at the thing we were talking about using! The tooling took
_a while_ to get through, although I guess that makes sense given that it's
doing the brunt of the work...

Anyway, onwards!

### Actual function declarations

Now that we know the shape of the things we're passing around (lists of
variables and arcs), we can give the original function declarations some actual
types:

```idris
forwardCheck :  (vars : List Variable)
             -> (arcs : List Arc)
             -> Maybe (List Variable, List Arc)
```

The left- and right-branching parts operate on a specific variable and value, so
we need to remember to include that:

```idris
branchFCLeft :  (vars : List Variable)
             -> (arcs : List Arc)
             -> (currVar : Variable)
             -> (currVal : Nat)
             -> Maybe (List Variable, List Arc)

branchFCRight :  (vars : List Variable)
              -> (arcs : List Arc)
              -> (currVar : Variable)
              -> (currVal : Nat)
              -> Maybe (List Variable, List Arc)
```

We always return a `Maybe`, since we want to discard the state using `Nothing`,
if it turned out to be inconsistent.

### The starting point

The starting point, `forwardCheck`, stops if we've assigned all the variables (a
solution has been found), and otherwise selects a variable and value to continue
with:

```idris
forwardCheck vars arcs =
  if all isJust $ map (.assigned) vars
     then Just (vars, arcs)
     else let var = selectVar vars
              val = selectVal var
          in -- first, branch left
             case branchFCLeft vars arcs var val of
                  -- inconsistency found, branch right with
                  -- the original state
                  Nothing => branchFCRight vars arcs var val

                  -- if all is well, but no solution was found,
                  -- try branching right with the new state
                  Just (vars', arcs') =>
                    branchFCRight vars' arcs' var val
```

The `selectVar` and `selectVal` functions just pick the first unassigned
variable, and the first value, in the given list. There is no cleverness going
on.

### Branching left

Branching left is the part where we try to assign the value to the variable, and
only keep going if the forward-checking/arc revision went well. This is where
the helper functions from earlier come into play: we need to update the variable
to its assigned version in both the list of variables and list of arcs.

```idris
branchFCLeft vars arcs currVar currVal =
  let assignedVar = assign currVar currVal
      vars' = orderedReplace vars assignedVar
      arcs' = map (setArcVar assignedVar) arcs
  in -- now check that the assignment works with the arcs
     case fcReviseFutureArcs vars' arcs' assignedVar [<] of
          Nothing => Nothing    -- nope, didn't work
          Just (rVars, rArcs) =>    -- hurray! revision success
            let vars'' = orderedUpdates vars' rVars
                arcs'' = orderedUpdates arcs' rArcs
            in -- continue with the new state
               forwardCheck vars'' arcs''
```

As you may have noticed, `let`-bindings are absolutely fantastic for this
implementation: they give us just enough imperativeness to do the small state
updates we need as part of each step.

### Branching right

Branching right is trying to remove the value from the variable's domain
(usually because an inconsistency was found), and then checking that everything
is still okay; that we can continue without that value. Idris provides a very
useful function which can help us here: `delete` (from `Data.List`), which
removes an element from a list. That's exactly what we need!

```idris
branchFCRight vars arcs currVar currVal =
  -- remove the value from the domain
  let smallerVar : Variable := { dom $= delete currVal } currVar
  in case getDom smallerVar of
          [] => -- oops, domain wipeout!
              Nothing

          (_ :: _) =>
              let vars' = orderedReplace vars smallerVar
                  arcs' = map (setArcVar smallerVar) arcs
              in case fcReviseFutureArcs vars' arcs' smallerVar [<] of
                      Nothing =>  -- inconsistent!
                                 Nothing

                      Just (rVars, rArcs) =>  -- still good
                        let vars'' = orderedUpdates vars' rVars
                            arcs'' = orderedUpdates arcs' rArcs
                        in forwardCheck vars'' arcs''
```

### Termination problems

So now that we've implemented the functions, do we have a constraint solver?
Let's try to run it!

```
Dai> :exec solve "4Queens.csp"
No solutions found :'(
Dai> :exec solve "8Queens.csp"
No solutions found :'(
Dai> :exec solve "langfords2_3.csp"
No solutions found :'(
```

That's odd... If we try to run this on a CSP, the solver is slow (which is
fine), but none of the problems seem to have a solution (which is not fine).
What is happening??

It turns out, this implementation has one fatal flaw: termination. When
`forwardCheck` has found a solution, it doesn't call the left- or
right-branching functions, it just returns the state. Which sounds good; that's
what we want it to do. Until you realise that this happens _during_ a recursive
descent on the list of variables, meaning: `forwardCheck` returns, having
happily concluded that everything is assigned, this jumps out of the assignment
step (branch-left), _and then continues with the deletion step (branch-right)_!!

So we conclude there is a solution, and then promptly delete the final assigned
value and keep trying other things. No wonder nothing has a solution!

This is no fault of the algorithm itself. It just assumes that there is a way to
stop, completely breaking out of the solving, as soon as the solution is found.
So what can we do about that?...

#### The hacky solution

Well, we _can_ technically display the solution and quit. Simply:

```idris
forwardCheck vars arcs =
  if all isJust $ map (.assigned) vars
     then assert_total $ idris_crash $ "DONE! " ++ show vars
```

It's not the cleanest, but it technically works ^^;;

#### The proper solution

Okay, but having crashing be the correct/expected behaviour when all is well
isn't really good practice. Instead, we could thread a `done` boolean or
similar, to indicate whether we should keep going? No no, we've been down that
road before: threading booleans and state makes it much easier to operate on the
wrong state, it is better to use a `Maybe` if possible. But what is redundant
when we've found a solution?

It turns out, there _is_ something we can discard once a solution has been
found: the arcs! When all the variables have been successfully assigned, i.e. a
solution has been found, there is no need to keep the arcs around any longer
since we're done checking against them!

So:
  * Wherever there is a `List Arc` in the main 3 functions, we need to use a
      `Maybe (List Arc)`. This allows us to "lose" the arcs once a solution has
      been found.
  * When `forwardCheck` concludes we're done, it needs to drop the arcs from its
      return value, both to indicate we're done and to prevent the recursive
      calls and calls to the branches from trying more arc revisions.
  * In the left- and right-branching functions, we need to add a case where the
      arcs have disappeared, in which case we just return the variables and
      `Nothing` for the arcs, since there is nothing we can revise against.

### A minor refactor later...

{{< spoiler text="Show the refactored code" >}}

```idris
forwardCheck :  (vars : List Variable)
             -> (arcs : Maybe (List Arc))
             -> Maybe (List Variable, Maybe (List Arc))

branchFCLeft :  (vars : List Variable)
             -> (arcs : Maybe (List Arc))
             -> (currVar : Variable)
             -> (currVal : Nat)
             -> Maybe (List Variable, Maybe (List Arc))

branchFCRight :  (vars : List Variable)
              -> (arcs : Maybe (List Arc))
              -> (currVar : Variable)
              -> (currVal : Nat)
              -> Maybe (List Variable, Maybe (List Arc))
```

```idris
-- if we've lost the arcs, we must be done
forwardCheck vars Nothing = Just (vars, Nothing)

forwardCheck vars (Just arcs) =
  if all isJust $ map (.assigned) vars
     then Just (vars, Nothing)  -- remove the arcs when done

     [...]

             -- branch left, remembering to put the arcs in a `Maybe`
             case branchFCLeft vars (Just arcs) var val of
                  Nothing =>
                    -- branch right as usual (no new state)
                    branchFCRight vars (Just arcs) var val

                  Just (vars', Nothing) =>  -- no arcs to continue with
                    branchFCRight vars' Nothing var val

                  Just (vars', Just arcs') =>
                    -- branch right as usual (with new state)
                    branchFCRight vars' (Just arcs') var val
```

```idris
-- if we've lost the arcs, we must be done
branchFCLeft vars Nothing currVar currVal = Just (vars, Nothing)

-- otherwise, proceed as usual
branchFCLeft vars (Just arcs) currVar currVal =
            [...]
            in -- continue with the new state
               forwardCheck vars'' (Just arcs'')
```

```idris
-- if we've lost the arcs, we must be done
branchFCRight vars Nothing currVar currVal = Just (vars, Nothing)

-- otherwise, proceed as usual
branchFCRight vars (Just arcs) currVar currVal =
                        [...]
                        in forwardCheck vars'' (Just arcs'')
```

{{</ spoiler >}}

Trying the solver on a 4-queens problem now gives us:

```
Dai> :exec solve "4Queens.csp"
Found a solution!
[ v0: 1
, v1: 3
, v2: 0
, v3: 2
]
```

If we plot that on a 4-by-4 chessboard, we get:

```
   | 0 | 1 | 2 | 3 |
---+---+---+---+---+
 0 |   | q |   |   |
---+---+---+---+---+
 1 |   |   |   | q |
---+---+---+---+---+
 2 | q |   |   |   |
---+---+---+---+---+
 3 |   |   | q |   |
---+---+---+---+---+
```

None of the queens threaten each other, so that's correct!!

Let's try with a slightly harder problem: Langford's Problem for pairs, with 3
pairs:

```
Dai> :exec solve "langfords2_3.csp"
Found a solution!
[ v0: 2
, v1: 4
, v2: 3
, v3: 6
, v4: 1
, v5: 5
]
```

If we put duplicate pairs of numbers on the given (1-based!) indices, we get:

```
3  1  2  1  3  2
```

Which we can verify to be correct: there is one digit between the 1s, two
between the 2s, and three between the 3s!

Unsurprisingly, the solver is also significantly faster now that it stops when
it finds a solution, instead of always emptying the entire search space...


## Doing Computer **Science**

Something which many people, myself included, often forget is to put the
"science" in "Computer Science": we need actual, concrete data! We need
evaluation(s)!

To collect the data, I used a simple script which called `/usr/bin/time`. (The
full details, and data, can be found in the
[the GitHub repo](https://github.com/CodingCellist/dai-station),
in `evaln` directory.)

### Initial performance

One observation I made when playing around with the solver, was that there was
no discernible difference in solver time between the n-queens problems. So I
decided to only test the Langford's instances.

Even then, the performance seems unaffected until we reach `langfords3_9`
(arrange a Langford sequence of 9 triples of numbers). At which point the time
to solve increases by two orders of magnitude! Ô.o

| CSP instance |  Time  |
| ------------ | -----: |
| langfords2_3 |  0.90s |
|              |  0.92s |
|              |  0.89s |
| langfords2_4 |  0.91s |
|              |  0.90s |
|              |  0.87s |
| langfords3_9 | 53.30s |
|              | 53.32s |
|              | 54.70s |

As a result, I initially stopped `langfords3_10` because it had been running for
over 2 minutes.

### Remember arc consistency?

There's a small, but important step I had completely forgotten: to avoid
exploring pointless initial guesses, we should enforce arc consistency before
even trying to solve!

This makes no difference for n-queens (each queen could, hypothetically, stand
on any square), but for Langford's it does make a difference. For example, there
are many fewer candidate positions for the 3s than there are for the 1s.

But again, we're doing computer _science_ here, so let's implement it and see
what happens!


| CSP instance | Time w/o initial arc-consist. | Time w. initial arc-consist. |
| ------------ | ----------------------------: | ---------------------------: |
| langfords2_3 |                         0.90s |                        0.87s |
|              |                         0.92s |                        0.88s |
|              |                         0.89s |                        0.93s |
| langfords2_4 |                         0.91s |                        0.95s |
|              |                         0.90s |                        0.91s |
|              |                         0.87s |                        0.87s |
| langfords3_9 |                        53.30s |                       46.29s |
|              |                        53.32s |                       46.43s |
|              |                        54.70s |                       46.46s |

The smaller instances are basically unaffected. There seems to be some
improvements on the `2_3`-instance, but that could also be a fluke of the runs,
given that the `2_4`-instance now seems ever so slightly slower...

### Retrying `langfords3_10`

At this point I got curious and decided to run the `langfords3_10` instance,
just to see if it would finish in "reasonable" time. After some time, having
changed away from the window to do some other work, I discovered that it _had_
finished successfully!

However, it took around 5 minutes, meaning any evaluation involving it would be
slow...


## Conclusion

I'm pretty happy with how that turned out. It was a fun exercise in converting
imperative to functional code, and figuring out how best to represent (and pass
around and modify) the problem representation. There are numerous places, as you
may have noticed, where dependent types possibly could have saved me some pain.
But to do that you need to figure out the correct types, as well as work out the
proofs and how to best/ergonomically pass these around, which can be a huge
challenge in and of itself. And I just wanted a working, proof-of-concept
constraint solver, so here we are ^^

The code is [on GitHub](https://github.com/CodingCellist/dai-station) for any
and all to browse. If you do something cool with it, please let me know! It's
always cool when others find use-cases for a silly code-adventure you did ^^

As always, thanks for reading. I hope it was interesting  : )


## Acknowledgements

* Ian Miguel for his lectures on implementing constraint solvers, which taught
    me everything I know about the topic.
* Guillaume Allais (gallais) for the idea of using `Maybe` for the state
    updates, thereby eliminating the possibility of accidentally using a bad
    state when a guess failed.


## Extra: A small heuristic

Constraint solvers can use various heuristics to try to be clever about variable
and/or value selection. These are, as mentioned, _heuristics_; they're rules of
thumb which tend to work well.

There are two types of heuristics: static and dynamic. Static heuristics are
ones which are set before starting the solver, and which remain constant
throughout the solving; e.g. trying each value in ascending order. _Dynamic_
heuristics, on the other hand, are heuristics which are computed and change as
the solver makes progress.

A simple heuristic to implement, in the case of Dai Station, is the "Smallest
Domain First" (SDF) heuristic: when selecting the next variable, select the one
with the smallest domain, since we're likely to find a dead-end faster this way.
And in Idris, it's just a simple `sortBy` call:

```idris
sdfSort : List Variable -> List Variable
sdfSort vars =
  sortBy (\ v1, v2 => compare (length $ getDom v1) (length $ getDom v2)) vars
```

(I also created a `Heuristic` datatype, so that I could toggle the heuristic by
passing around a `Maybe Heuristic` to the three main functions.)

### Does it work?

Remembering that we're computer _scientists_, we of course evaluate our new
heuristic-based search vs our old non-heuristic-based search (this time only
with `langfords3_9` and `langfords3_10`, since they're the most likely to see a
noticeably difference in performance):

| CSP instance  |  Time w/o SDF |  Time w. SDF |
| ------------- | ------------: | -----------: |
| langfords3_9  |        47.36s |       44.03s |
|               |        47.61s |       44.07s |
|               |        47.35s |       44.21s |
| langfords3_10 |       305.71s |      238.61s |
|               |       303.91s |      241.25s |
|               |       304.04s |      243.24s |

Hurray, it's faster! On the smaller problem, it only saves us around 3 seconds,
but on the bigger one, it saves us a whole minute! That's neat!!

