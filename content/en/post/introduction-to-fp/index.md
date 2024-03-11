---
# Documentation: https://wowchemy.com/docs/managing-content/

title: "Introduction to Functional Programming"
subtitle: ""
summary: "An introduction to FP aimed at people who have mainly programmed in
          imperative and/or OO languages."
authors: [thomas-e-hansen]
tags: ["Functional Programming", "talks"]
categories: []
date: 2021-11-05T10:52:06+01:00
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

This is an introduction to the concept of "Functional Programming" (FP) aimed at
people who have not encountered FP before but might have heard of it, and/or
people who are used to programming in what's known as _imperative_ languages,
e.g. Java, C, C++, Swift, etc.

I'll be drawing comparisons to Java, since it was the primary language on the
undergraduate Computer Science (CS) degree at the University of St Andrews when
I did my undergrad degree there.
It is slightly difficult to introduce FP without having a FP language to refer
to, so I will also be introducing [Idris](https://idris-lang.org) in this
tutorial. The principles should apply to most other FP languages.


### Why should you care?

In my experience, functional programming is often seen as this niche, weird
thing in CS that few people actually use because Java and C++ are so widespread,
especially in the industry (where most people with a CS degree end up). So with
that in mind, a common question is "Why should I bother learning this?". It's a
valid question, especially since FP is a completely different way of thinking
about programming when you from a imperative programming background and/or are
most comfortable with those languages; FP can seem needlessly complicated and
complex, and it is easy to get overwhelmed by the symbols and terminology
(side-note: I have another blog post with a crash-course in FP terminology
[here](/en/post/fp-terminology-intro/). It might be useful if this post
convinces you to dive deeper into FP.)

So back to the question: Why should you care about FP? Because it's good for the
soul! Okay, on a more serious note: because a lot of programming languages are
starting to adopt FP principles. Java has `Stream`s and anonymous/unnamed
functions (or "lambdas", as they're also known), for example. JavaScript allows
passing functions around as arguments to other functions, as does Python. C++
has things like `for_each` and `copy_if`. All of these ideas relate to
functional programming!

Another reason is that I can almost guarantee it will make you a better
programmer. The more ways you have to think about a problem, the more approaches
to problems you've seen, the more tools you have in your mental toolbox, the
better you'll be at solving problems. Learning FP might make you discover
solutions to problems that you wouldn't have found (as easily) otherwise.

If none of these things have convinced you: Because, as a programmer or software
engineer, you want to be a polyglot in terms of programming languages. It is
always useful to be able to pick up a new language, e.g. when starting a new job
or project. And knowing FP will help you pick up some languages more easily.

Right, with that (hopefully) answered, let's get started!


### Functional as opposed to what?

What do we mean by "functional" programming? Unfortunately, this is a "Ask 100
functional programmers and get at least 100 answers" kind of question, but I
will try to answer with the definition I think makes most sense.

An initial answer might be "a language where functions are first-class". Here,
"first-class" means that in the programming language, functions can be passed
around, assigned to variables, etc., just like you would with numbers or data
structures. However, as mentioned above, both JavaScript and Python allow for
this (and C, if you count function pointers) but I wouldn't classify JavaScript
or Python as FP languages. So having functions be first-class is not quite
enough on its own to define "Functional Programming".

The bit that, in my opinion, makes the definition complete is "A language that
encourages the functional programming style". It's a bit more abstract, but it
helps distinguish between programming languages that borrow FP ideas and
programming languages that most people would likely agree are "Functional", e.g.
Haskell or Idris.

The "FP style", is things like defining higher-order functions; using partial
application of functions to solve multiple, slightly similar problems;
separating out computation and side effects (e.g. user interaction); using types
to assist with writing correct programs. Don't worry if you don't understand
what I mean by these things, we'll come to that in a second.


### What functional programming doesn't have to be

If you've tried looking up FP papers, it is likely you have come across terms
like "monads", "functors", "type-theory", "$\Pi$-binders", and/or "free
algebras". And many people, understandably, nope right back out at this point.

Part of the neatness of FP is that it is closely tied to the mathematical field
"Category Theory" (CT). "Why is this neat?" you might ask. Because it allows us
to build on centuries of mathematical understanding to describe and **prove**
aspects of the programming languages or the programmes themselves. This is
extremely useful, both for catching errors earlier in the development process
and for applications where you might care a lot about provable correctness (e.g.
spacecraft control systems). However, it is a also double-edged sword: CT is
incredibly powerful and useful for describing lots of information and properties
about things in very few, precise words, at the cost that anyone who isn't
familiar with CT and its terminology will be completely lost (and looking up the
Wikipedia page for Category Theory doesn't help).

But although a lot of FP is based on Category Theory, that doesn't mean all
functional programming has to be complicated pure maths! It is perfectly
possible to do FP without doing a course on CT as well, or learning various
different type-theories (another useful mathematical thing that FP is based on).

![Meme: STOP DOING TYPE THEORY! BYTES IN MEMORY WERE NOT MEANT TO BE GIVEN A MEANING](stop-doing-type-theory.png "https://nitter.net/jcreed/status/1367899760301137930")


### What is a function? A miserable little pile of instructions!

If you're coming from Java, you'll have been referring to functions as
"methods". These are callable things that take a number of arguments, or none,
and describe how to return something based on that argument. Essentially, a
function is a recipe for how to compute something. In Java, functions are
associated with classes of objects, and can be instance-independent by
specifying the `static` keyword. In functional languages, functions are their
own thing: they can be defined at the top-level of a file, without needing to be
contained in a class or struct or similar.

To define a function which computes the power of a number (ignoring negative
powers), for example, you could write the following in Java:

```java
public int power(int a, int p) {
  int pow = 1;
  for (int i = 0; i < p; i++) {
    pow *= a;
  }
  return pow;
}
```
Let's describe what is happening here: The first `int` specifies the return
type of the function, `power` is the name of the function, and `int a, int p`
specifies that the arguments to the function are `a` and `p`, and that both are
`int`s. The body of the function then defines a `pow` variable, which is also an
`int`, assigns it the initial value of 1, computes the power of `a` to the `p`
by doing `p` many multiplications (accumulating the result in `pow`), and
returns the result.

Defining the same function in Idris would look like this:
```idris
power : (a : Integer) -> (p : Integer) -> Integer
power a 0 = 1
power a p = a * power a (p - 1)
```
Again, let's describe what is happening: the first `power` declares the name of
the function, and the `:` specifies that the next bit is the function type. In
this case, `power` takes two arguments `a` and `p`, both of which are
`Integer`s, and returns an `Integer`. **In functional programming, the return
type of a function is the last type specified in the function declaration.** The
function body looks entirely different from the Java code: it is using something
called "pattern matching" (a _ridiculously_ useful feature of most FP
languages). If `p` has value `0`, then result must be `1` (since `a` to the 0
is 1), and if `p` has a different value, then the result is `a` times `a` to the
power of `p - 1`; recursion!

