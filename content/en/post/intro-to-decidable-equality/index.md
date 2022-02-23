---
# Documentation: https://wowchemy.com/docs/managing-content/

title: "Intro to Decidable Equality"
subtitle: ""
summary: "One of the more difficult concepts in Idris, I've found, is proving
          things by dependent types. The 'simplest' introduction to this is
          probably the `DecEq` interface, which this post aims to introduce,
          explain, and implement."
authors: [thomas-e-hansen]
tags: [idris2, intro, formal-methods]
categories: []
date: 2022-02-23
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


### Fundamentals

Before we get into `DecEq`, there are a couple of fundamental concepts we need
to discuss. These will help us understand the underlying mechanics of `DecEq`
and "proof by data-type" in general.

#### Non-dependent types promise nothing

In my experience, a lot of people struggle with this idea when getting into
functional programming and dependent types; the "How can data prove anything?"
sort of questions pop up. Taking a page out of the "Type-Driven Development with
Idris" (TDD) book here, let's start by considering the regular, i.e.
non-dependent, type of the `(==)` operator:

```idris
```

#### Proofs of equality

#### Proofs of False

#### Expressing contradictions


### Proving two things equal

### Decidable Equality

### Absurdities

### Beyond Equality: Custom Predicates

### Conclusion

### Acknowledgements

