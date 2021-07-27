---
# Documentation: https://wowchemy.com/docs/managing-content/

title: "Implementing Condition Variables in Racket"
subtitle: ""
summary: "Explaining and implementing Birell's 2003 paper on Condition Variables
          for Modula-2+, in Racket."
authors: [thomas-e-hansen]
tags: ["concurrency", "idris2", "racket"]
categories: [] # [idris2, concurrency]
date: 2021-07-27
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

Whoops, I got distracted with Petri Nets, Midlands Graduate School, the Idris
Developer Meeting, and a whole bunch of projects and fixes, and suddenly it's 5
months since the precursor to this. Sorry about that...

After patching the `sleep` shenanigans in the Idris Racket backend, the
Condition Variable (CV) tests needed to be written. I came up with the following
test scenarios:

- 1 Main, 1 Child thread -- Test that the child can be signalled and wakes up.
- 1 Main, N Child threads -- Test that 1 child thread gets woken on signal.
- 1 Main, 1 Child thread -- Test that the child gets woken when the CV is broadcast.
- 1 Main, N Child threads -- Test that all N children get woken when the
    CV is broadcast.
- 1 Main, 1 Child thread -- Test that the child continues after a timeout if the
    main thread never updates the CV.
- 1 Main, N Child threads -- Test that M (where M \< N) threads continue after a
    timeout if the main thread never updates the CV.

These scenarios test all supported operations on condition variables (`wait`,
`signal`, `broadcast`, and `waitTimeout`) with both 1 and multiple threads using
the CV (kind of critical to test multiple thread access in a
concurrency/synchronisation primitive). They were implemented in Idris and then
run using the `--cg racket` flag. However, since the CV implementation was
broken, it needed to be fixed.

### Brief refresher on some terminology:

**Condition Variables** are synchronisation primitives which allow threads to
wait for a condition to be true, e.g. to guarantee that worker threads don't try
to get work before the main thread has signalled that there is work. CVs
typically support 3 operations:

- `wait` -- Somewhat self-explanatory: blocks the thread, waiting until the CV
    indicates that it is okay to continue. This operation requires a _locked_
    mutex to guarantee that the thread atomically switches to waiting on the CV.
- `signal` -- Wakes 1 thread currently waiting on the CV.
- `broadcast` -- Wakes all threads currently waiting on the CV.

In addition to this, most CV implementations support something like
`waitTimeout`, which blocks the thread until either the CV is updated or the
specified timeout has elapsed.

**Semaphores** have existed for millennia, and no-one is really sure where they
come from. Well, kind of: Semaphores are technically just a form of signals,
with some of the oldest examples being smoke signals. Eventually, trains came
along, and soon after a fixed railway sign using "arms" to signal different
things to the locomotive drivers was invented, called a "Railway semaphore
signal". A while later, Dijkstra then came along and invented the
synchronisation primitive, naming it after the railway signal. Since Dijkstra
was Dutch, he used the Dutch terminology for the operations on semaphores:
_passering_ "passing", and _vrijgave_ "set free/release". These were abbreviated
P and V respectively, which turns out to be unfortunate and highly confusing
when trying to use something which uses the common, English operation names: P
and V are equivalent to "wait" and "post" respectively (yes, "respectively": the
original operation "P" is what most languages now call "wait", and the original
operation "V" is what most languages now call "post" -- V increments the
semaphore and P tries to decrement it).

### Understanding the "Implementing CVs" paper

As with most concurrency primitives, implementing them from scratch is really
hard, since there are a lot of race-conditions and edge-cases to take care of,
and often some go unnoticed until someone writes a specific multithreaded
use-case where everything breaks for seemingly no reason. Fortunately, there is
[an excellent paper by Andrew D. Birell](https://www.microsoft.com/en-us/research/wp-content/uploads/2004/12/ImplementingCVs.pdf)
detailing not only how CVs are meant to work and how to achieve this using
semaphores (which is the only simple concurrency primitive we have access to in
Racket), but even including the exact code! The paper highlights the difficulty
of doing implementing CVs correctly: The bulkiness and potential performance
impact of the semaphore-based implementation was serious enough that the team
abandoned the implementation and ended up having one of the kernel developers
implement them directly using the scheduler and the hardware's atomic
test-and-set instructions. Unfortunately, we have no such luxury in the
Racket/Idris world, so I had to understand the code in the paper.

The code uses mostly single-letter variable names which everybody knows is best
practice and makes things easy to understand. The most sensible of these is `m`,
which is the mutex used to guarantee the atomic switch to waiting on the CV. In
the paper, this mutex is part of the CV data structure, but as far as I can tell,
this is contrary to most other implementations (like C or Chez-Scheme), which
have the mutex be passed in as an argument to the `wait` function call. As such,
I chose to leave this part out and only have the CV data structure contain the
semaphores required for its correct operation and the `waiters` counter; keeping
it consistent with the other CV APIs I had seen. The `waiters` counter is the
only truly sensibly-named variable: it counts how many threads are currently
waiting on the CV. The implementation uses 3 semaphores which are "helpfully"
named `s`, `x`, and `h`. Reading through the code a couple of times with the
help of a friend, we came to the following conclusions:

- `s` -- is responsible for the actual releasing of the threads.
- `x` -- protects the `waiters` counter, guaranteeing that it is atomically
    incremented and decremented; basically a mutex.
- `h` -- ensures that there is a "handshake" when waking threads, i.e. that
    `wait`+`signal` pairs line up. This is necessary to prevent
    inter-`broadcast` mix ups: when calling `broadcast`, it has to wait for
    `wait` to have successfully woken a thread before continuing to broadcast
    to the remaining threads.

This is helpful 1) since it helps immensely with understanding the code+logic,
and 2) to have (hopefully) more helpful names in my Racket implementation.

### Implementing CVs in Racket

First step is to define a new data-type. In racket, this is done using the
`struct` keyword:

```scheme
(struct cv (countingSem waitersLock waiters handshakeSem) #:mutable)
```

This defines a new structure called `cv`, which contains the fields
`countingSem`, `waitersLock`, `waiters`, and `handshakeSem`. Specifying
`#:mutable` as a _struct-option_ (as opposed to a _field-option_) means that
every field in the struct is mutable and can be modified using the implicitly
generated `set-`_`structName-fieldName`_`!` functions.

Since the semaphores are internal to the CV, they are created as part of the
constructor:

```scheme
(define (blodwen-make-cv)
  (let ([s (make-semaphore 0)]
        [x (make-semaphore 1)]
        [h (make-semaphore 0)])
    (cv s x 0 h)))
```

I used the original variable names here for brevity, and also to maintain a
slight link between the original paper and my implementation. The field names,
which are actually used for access and modification, still have the (in my
opinion) clearer names. The `0` on the last line is the initial value of the
`waiters` counter.

Next, the simplest operation to define in Racket is `wait`:

```scheme
(define (blodwen-cv-wait my-cv m)                                                
    ; atomically increment waiters
    (semaphore-wait (cv-waitersLock my-cv))
    (set-cv-waiters! my-cv (+ (cv-waiters my-cv) 1))
    (semaphore-post (cv-waitersLock my-cv))
    ; release the provided mutex
    (blodwen-mutex-release m)
    ; wait for the counting semaphore to let us through
    (semaphore-wait (cv-countingSem my-cv))
    ; signal to broadcast that we have proceeded past the critical point/have
    ; been woken up successfully
    (semaphore-post (cv-handshakeSem my-cv))
    ; re-acquire the provided mutex
    (blodwen-mutex-acquire m)
    )
```

As with most other implementations, `wait` takes a CV `my-cv` and a locked mutex
`m`, and causes the thread to wait until the CV is updated. This is done by
waiting on the `countingSem` semaphore. Each of the fields in the `my-cv` struct
can be accessed using the implicitly generated _`structName-fieldName`_
functions. Note that `+` is just a function, so to increment `waiters` by 1, we
call it on the value retrieved from the struct: `(+ (cv-waiters my-cv) 1)`, just
like we would if we were using any other function.

With `wait` implemented, the next thing which is still mostly simple to
implement is `signal`:

```scheme
(define (blodwen-cv-signal my-cv)
    ; lock access to waiters
    (semaphore-wait (cv-waitersLock my-cv))
    (let ([waiters (cv-waiters my-cv)])
      (if (> waiters 0)

        ; if we have waiting threads, signal one of them
        (begin
          (set-cv-waiters! my-cv (- waiters 1))
          ; increment the counting semaphore to wake up a thread
          (semaphore-post (cv-countingSem my-cv))
          ; wait for the thread to tell us it's okay to proceed
          (semaphore-wait (cv-handshakeSem my-cv))
          )

        ; otherwise, do nothing
        (void)
        )
       ; unlock access to waiters
       (semaphore-post (cv-waitersLock my-cv))
       ))
```

Again, nothing crazy is going on. Rather than using `(cv-waiters my-cv)`
everywhere, we retrieve the value once using a `let` binding. And since Racket
is a functional language, we have to deal with no-ops explicitly, so the `else`
part of the `if`-statement is simply `(void)`. One new thing, compared to the
previous post on Idris/Racket concurrency, is the `begin` statement. And it's
an important one. It is a very good example of where Lisp-like languages (or
maybe just the Scheme dialects) can be somewhat tricky: Contrary to most other
programming languages, parentheses carry more meaning than ordering things.
Consider the Racket expression:

```scheme
+ 1 2
```

You might expect this to evaluate to 3, but that's not the case. This
expression, without any parentheses, is: the procedure `+`, and the numbers 1
and 2. This will likely be confusing to many people coming from outside the
Scheme/Lisp world (it certainly was for me!). The reason for this result is that
parentheses are not arbitrary, they change the fundamental meaning of things.
This is very easy to trip over, especially when trying to use parentheses to
order execution. If you want the numbers 3 and 7 (as a toy example), you might
correctly write:

```scheme
(+ 1 2) (+ 3 4)
```

and it wouldn't be unreasonable, coming from other languages, to then assume
that writing:

```scheme
((+ 1 2) (+ 3 4))
```

would result in the same numbers, just being more explicit about the ordering of
things (perhaps for extra sanity in a large sequence of operations). However,
instead of being fine, Racket complains:

```scheme
; application: not a procedure;
```

This is because, while the expression _partially_ reduces to `(3 7)`, the
parentheses change the meaning of that expression to: "Call `3` with the
argument `7`".  This doesn't make sense, `3` is a number and not something that
can be called, and so Racket complains. Adding parentheses doesn't just change
the evaluation order, it changes the meaning of the expressions themselves! To
sum up with a shorter example:  
`foo` is a variable reference; `(foo)` is the call to `foo` with no arguments;
and `((foo))` is taking the value that calling `foo` with no arguments returns,
and _calling that value_ as if it were a function/procedure, with no arguments.

However, sometimes when writing Racket, we end up in situations where it would
be really convenient to express a sequence of operations in the middle of
things, e.g. in an `if` branch. This is where `begin` is useful. Coming back to
the `signal` code:

```scheme
(if (> waiters 0)
  (begin
    (set-cv-waiters! my-cv (- waiters 1))
    (semaphore-post (cv-countingSem my-cv))
    (semaphore-wait (cv-handshakeSem my-cv))
  )
  (void)
)
```

Without `begin`, the first part of the `true` branch of the `if`-statement would
be "the call of the return value of `set-cv-waiters! [...]` with 2 arguments
(i.e. the return values of the `semaphore-*` calls)", which is not what we want
at all; we want to execute each statement as part of the `true` branch. So we
use `begin` to evaluate the expressions, ignoring every result but the last one,
which is returned.

While `begin` took a bit to explain, it is fine to use once you remember about
it. The main pitfall in implementing `signal` is that the paper puts the 3
instructions required on one line:

```c
    if (waiters > 0) { waiters--; s.V(); h.P(); }
```

In combination with the single-letter variable naming, this makes it easy to
miss one of them, which I did on my first attempt at implementing this.
Fortunately, since the implementation doesn't work without all 3, it's at least
easy to realise that a mistake has been made. Finding it however, not so much...

Moving on to the `broadcast` function, it is a bit trickier to implement: It
should wake all threads waiting on the CV at the moment of the call, which is
done by iteration in the paper. However, as you will know if you've done
functional programming before, functional programming doesn't really do
iteration. Instead, we prefer to use recursion or something from the `map`,
`traverse`, `fold`, etc family of functions. I decided that the simplest
approach would be to define a couple of helper-functions for the iterative bits
of the code. This time, the confusion of single-letter naming gets some
assistance from "single-line loops" (because why make things readable, right?):


```c
x.P(); {
    for (int i = 0; i < waiters; i++) s.V();
    while (waiters > 0) { waiters--; h.P(); }
} x.V();
```

The first helper is to implement the `for`-loop. It can be broken down into a
base-case and a recursive step:

1. If `i` is zero, then we are done.
2. Otherwise, we need to signal a waiting thread, and recurse with `i` being 1
   smaller.

There are 2 things we need to keep track of: The CV which things are waiting on,
and `i`. So the definition of our helper becomes:

```scheme
; for (int i = 0; i < waiters; i++) s.V();
(define (broadcast-for-helper my-cv i)
    (if (= i 0)
      ; if i is zero, we're done
      (void)
      ; otherwise, we signal one waiting thread, decrement i, and keep going
      (begin
        (semaphore-post (cv-countingSem my-cv))

        (broadcast-for-helper my-cv (- i 1))
        )))
```

The single-equals in Racket is numerical equality, since variable assignment is
done either as argument-passing to functions or through `let`-bindings.

The second helper is to implement the `while`-loop. Like the `for`-loop, it can
be broken into very similar steps. One difference is that we keep track of
`waiters` rather than `i`, but the main difference is that since we are waking
up all the threads, we need to wait for the handshakes to complete, indicating
that the thread has successfully been woken and that there is now one fewer
waiters. With these things in mind, the `while` helper becomes:

```scheme
; while (waiters > 0) { waiters--; h.P(); }
(define (broadcast-while-helper my-cv waiters)
    (if (= waiters 0)
      ; if waiters is 0, we're done
      (void)
      ; otherwise, wait for "waiters" many threads to tell us they're awake
      (begin
        (semaphore-wait (cv-handshakeSem my-cv))
        (broadcast-while-helper my-cv (- waiters 1))
        )))
```

With both the helpers implemented, draw the rest of the owl:

```scheme
(define (blodwen-cv-broadcast my-cv)
    ; lock access to waiters
    (semaphore-wait (cv-waitersLock my-cv))
    (let ([waiters (cv-waiters my-cv)])
      ; for (int i = 0; i < waiters; i++) s.V(); so start at "waiters - 1"
      (broadcast-for-helper my-cv (- waiters 1))
      ; wait on "waiters" many threads to have been woken
      (broadcast-while-helper my-cv waiters)
      ; unlock access to waiters
      (semaphore-post (cv-waitersLock my-cv))
      ))
```

Unfortunately, this doesn't quite work and the keen-eyed reader might have
spotted why: There is something wrong with the `for`-loop transcription. Since
it goes from `i = 0` to `i < waiters`, it is natural to transcribe the latter as
`waiters - 1`; we do something as soon as we call the function after all.
However, the condition now ends up being doubly accounted for and missing an
iteration, as the other natural thing is to have 0 as the base case in the
recursive helper:

```scheme 
; for (int i = 0; i < waiters; i++) s.V();
(define (broadcast-for-helper my-cv i)
    (if (= i 0)
      ; if i is zero, we're done
      (void)
      [...]
```

This took forever to spot and confused me for ages, since I was confident that I
had transcribed the paper correctly. It took an extra pair of eyes to finally
spot it, and fortunately it was a trivial fix. With the mistake fixed, the code
becomes:

```scheme
; BROADCAST
(define (blodwen-cv-broadcast my-cv)
    ; lock access to waiters
    (semaphore-wait (cv-waitersLock my-cv))
    (let ([waiters (cv-waiters my-cv)])
      ; signal "waiters" many threads; counting *until* 0 in the helper
      ; function, hence "waiters" and NOT "waiters - 1"
      (broadcast-for-helper my-cv waiters)
      ; wait on "waiters" many threads to have been woken
      (broadcast-while-helper my-cv waiters)
      ; unlock access to waiters
      (semaphore-post (cv-waitersLock my-cv))
      ))
```

Including a comment to remind myself, and others, that the lack of
`waiters - 1` is intentional.

With this, all the tests passed under the Racket backend, and there was much
rejoicing. Almost.

### A final note: `wait-timeout`

Unfortunately, the paper does not describe an implementation of `wait-timeout`.
My guess is that they just never needed it in their kernel. I had some attempts
at implementing it myself using Racket's `sync/timeout` functionality, but I
couldn't get it to work. Unfortunately for the implementation, I didn't really
need the functionality either, but I _did_ need to get on with more research-y
projects. As such, CVs under the Racket backend do not support this at the time
of writing, but it is possible someone else might come along and implement it if
they need that functionality and _have_ to use the Racket backend.

With that said, I am still fairly happy that I was successfully able to port the
implementation from the paper to the Idris Racket backend and that the core
functionality of CVs now works. I learned a lot about both CVs and Racket on the
way, and it was a solid exercise in implementing concurrency primitives  : )

### Acknowledgements

- Thanks to Andrew D. Birell for writing the paper which greatly facilitated
    this implementation.
- Thanks to [Tom Harley](https://www.magnostherobot.co.uk/) for helping me
    understand the paper and decipher the purposes of the internal semaphores.
- Thanks to Edwin Brady for helping with ironing out the final creases in the
    implementation, like the off-by-one error.

