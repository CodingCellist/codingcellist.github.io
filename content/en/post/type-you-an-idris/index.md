---
# Documentation: https://wowchemy.com/docs/managing-content/

title: "Type You an Idris for Great Good"
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
which meant the following needed fixed in TinyIdris before it would build:

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

