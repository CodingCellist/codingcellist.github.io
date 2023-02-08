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

With the hardest bit out of the way, it was time to write a constraint solver!


# Writing a constraint solver

