---
# Documentation: https://wowchemy.com/docs/managing-content/

title: "Writing a PRNG using ChatGPT"
subtitle: ""
summary: "What do you do if you need a pseudorandom number generator but don't
          know anything about how to implement that and, crucially, don't care
          how good it is? You _could_ read some papers, but ChatGPT had been
          making waves for a while, so why not try that?"
authors: [thomas-e-hansen]
tags: [chapgpt, idris2, randomness]
categories: []
date: 2023-03-15
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

I needed a pseudorandom number generator (PRNG) for a project I was working on.
And Idris _does_ come with that built-in: `System.Random`. Except, its
functionality lives in the `IO` world and my project involved stuff working at
the type-level, which doesn't do `IO` (because having the compiler be able to
arbitrary I/O is probably a bad idea). So I needed to write my own.

It didn't need to be good, this was for a proof-of-concept, and I'd heard that
ChatGPT was decent for simple single-use code, so I thought I might as well try
it. It turned out _pretty good:_

> [TH] Hello. I'm trying to write some Idris code for generating pseudorandom
> numbers. Could you help me with this?

> [ChatGPT] Sure, I can help you with that! There are several ways to generate
> pseudorandom numbers in Idris, but one of the simplest is to use the standard
> library's `Random` module.
>
> Here's a basic example of how you could use the `Random` module to generate a
> random integer between 0 and 99:
> ```idris
> import Random
>
> randInt : IO Int
> randInt = do
>   gen <- mkStdGen 42 -- Seed the random number generator [...]
>   rand <- randomR (0, 99) gen -- Generate a random integer between 0 and 99
>   pure rand
> ```

