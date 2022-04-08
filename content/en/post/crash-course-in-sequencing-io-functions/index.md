---
# Documentation: https://wowchemy.com/docs/managing-content/

title: "A Crash Course in Sequencing IO Functions"
subtitle: ""
summary: ""
authors: [thomas-e-hansen]
tags: []
categories: []
date: 2022-03-25
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

## Intro

This is yoinked from an answer I gave on
[the Idris2 discord](https://discord.gg/YXmWC5yKYM)
where someone was confused about using `IO` when there was multiple functions
involved. I've slightly restructured it, but it's still basically the Discord
answer verbatim.

There's only 2000 characters to use in Discord, so this is a very rough and
quick introduction to IO, the 'bind' operator, and `do` notation. If I ever
understand monads, I'll try to write a more "proper" introduction.


## IO, continuations, and values

`IO ()` represents an I/O action which returns no value (e.g. `putStrLn
"Welcome!"` only outputs the string `Welcome!`; it doesn't also return some
value for further computation):

```idris
printWelcome : IO ()
printWelcome = putStrLn "Welcome!"
```

This is not very exciting... So how can we sequence functions which do I/O? And
how do we deal with functions that compute a value from that I/O?

### IO and continuations

To combine two `IO ()` actions, we use `>>=` (read "bind"). The type of `>>=`
for `IO` is:

```idris
(>>=) : IO a -> (a -> IO b) -> IO b
```

This reads as: "If I have a value of
type `a` from some I/O, and I know what to do with it (function from `a` to `IO
b`), then I can just do that and get the result (`IO b`)").

So to output two strings, we could write:

```idris
main : IO ()
main = putStrLn "Hello" >>= (\ _ => putStrLn "World!")
```

The anonymous function

```idris
\  _ => putStrLn "World!"
```

is the _continuation_ of doing

```idris
putStrLn "Hello"
```

(And we discard its result using `_`).

### IO, continuations, and values

If we instead have a value we care about, e.g. an `IO String`, we can describe
what to do with that value in the continuation like we would with any anonymous
function:

```idris
main : IO ()
main = getLine >>= (\ str => putStrLn ("Hello " ++ str))
```

And we can chain this as much as we want (indented for _some_ readability):

```idris
main : IO ()
main = getLine >>=
         (\ str => putStrLn ("Hello " ++ str) >>=
           (\ _ => putStrLn "Welcome to Idris!" >>=
             (\ _ => putStrLn "Enjoy yourself!"
             )))
```

### IO, continuations, values, and do-notation

Sequences of bind are almost entirely unreadable (and tedious to write). So we
instead use do-notation:

```idris
main : IO ()
main = do s <- getLine
          _ <- putStrLn "Hello " ++ str
          _ <- putStrLn "Welcome to Idris!"
          putStrLn "Enjoy yourself!"
```

Which is equivalent to the verbose `>>=` notation, but looks much nicer and is
easier to write!  : )

### All the other functions

Functions which don't return IO can be used in combination with `pure` or `let`:

```idris
main : IO ()
main = do someVal <- pure someFunc
          let otherVal = otherFunc
          putStrLn ("Look ma: " ++ someVal ++ " and " ++ otherVal ++ "!")
```

(assuming the functions `someFunc` and `otherFunc` returned strings)


## And there you have it!

That's a crash-course in how you combine `IO` with functions, include non-`IO`
computations, and sequence multiple things you want to do. Thanks for reading!  : )

