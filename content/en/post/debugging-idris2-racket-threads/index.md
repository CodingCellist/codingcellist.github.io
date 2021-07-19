---
# Documentation: https://wowchemy.com/docs/managing-content/

title: "Debugging Idris2 Racket Threads"
subtitle: ""
summary: "A dive into functional concurrency, FFIs, and thread weirdness."
authors: [thomas-e-hansen]
tags: ["concurrency", "idris2", "ffi", "debugging"]
categories: [] # [idris2, concurrency, debugging]
date: 2021-02-24
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

I was trying to write some tests for the Racket backend of
[Wen](https://wen.works)'s pull request about adding threading and concurrency
primitives to Idris2. There was a discussion as to whether or not to provide
mutexes and condition variables in Idris2, and given that I argued we should,
the responsibility to write tests for these fell on me. I naïvely thought "How
hard can it be?" and got to work.

### A bit of background

Condition variables require a mutex in order to guarantee the atomicity of
waiting on them. In C, the `pthread_cond_wait` function takes a reference to a
condition variable and a reference to a **locked** mutex. If we don't have this
locked mutex, we cannot guarantee that the thread atomically goes from having
the mutex to waiting on the CV; a race-condition could occur in terms of waiting
on the CV, which could lead to signalling being missed or worse, erroneous
wake-ups (aka. spurious wake-ups). Racket does not have native support for
mutexes, which means they have to be implemented via semaphores. So before
testing the CVs, I wanted to make sure the mutex implementation was correct as
well. This is where things got odd...

### The initial problem

A mutex is said to be "owned" by the thread which locks/acquires it. A thread
should not be allowed to unlock/release a mutex if it does not own it (this may
result in an error or undefined behaviour, depending on the type of mutex). So a
simple test was:

```idris
import System
import System.Concurrency

child : Mutex -> IO ()
child m =
  do sleep 1
     mutexRelease m
     putStrLn "Child released the mutex (NOT ALLOWED)"

main : IO ()
main =
  do m <- makeMutex
     mutexAcquire m
     putStrLn "Main acquired the mutex"
     t <- fork (child m)
     threadWait t
```

Now, it turns out that due to the Racket implementation relying on semaphores,
the fact that the child successfully unlocks the mutex is "fine" (not fine in
terms of what should be allowed with mutexes, but fine given that the mutex is
actually a semaphore under the hood). But that was not the interesting case.
What _was_ interesting, was that when flipping the thing around...

```idris
import System
import System.Concurrency

child : Mutex -> IO ()
child m =
  do mutexAcquire m
     putStrLn "Child acquired the mutex"
     sleep 4

main : IO ()
main =
  do m <- makeMutex
     t <- fork (child m)
     sleep 1   -- give the child time to acquire
     mutexRelease m
     putStrLn "Main released the mutex (NOT ALLOWED)"
     threadWait t
```

... it immediately threw an error about the thread not owning the mutex:

```bash
$ idris2 --no-banner --no-colour --cg racket Main.idr --exec main
Exception in mutexRelease: thread does not own mutex
```

This seems fine, except, the child never acquired the mutex! (The error-message
also appears on a double-release or, in this case, releasing without acquiring
first). Running it using the Chez-Scheme backend gave the expected result:

```bash
$ idris2 --no-banner --no-colour --cg chez Main.idr --exec main
Child acquired the mutex
Exception in mutex-release: thread does not own mutex 570989815728
```

It turned out, that no amount of sleeping in the `main` thread would cause the
child to acquire the mutex before `main` would attempt to release it. Somehow,
Racket seemed to be running things sequentially rather than in parallel... To
confirm that the issue was indeed not with the mutexes, I came up with a
different example:

```idris
import System
import System.Concurrency

child : IO ()
child =
  do sleep 1
     putStr "Wor"
     sleep 2

main : IO ()
main =
  do putStrLn "Hello"
     t <- fork child
     sleep 4
     putStrLn "ld"
     sleep 5
```

It should print out "Hello World", with the child printing the "Wor" part of
"World". However, running it with the Racket backend instead produced

```bash
$ idris2 --no-banner --no-colour --cg racket Test.idr --exec main
Hello
ld
Wor$ 
```

Printing "Wor" before dropping me back at the terminal prompt, having seemingly
only executed the `child` thread when it absolutely had to because the program
was wrapping up. (Obviously, replacing `sleep 4` with `threadWait t` solved the
problem, but that was cheating; the problem was the thread not executing in
parallel in the first place.) Strange, very strange... Showing this behaviour to
Wen provided some re-assurance that it wasn't just something I was doing wrong,
because she could also reproduce the behaviour on her end. You know you've found
a good problem when everyone in the group chat goes "Hmm, that shouldn't
happen." "What if we do- Nope, still doesn't work..." "What about- Nah, not that
either" "Oh interesting! That _is_ really odd!..."

Wen suggested I could try to look through the Racket that Idris2 was generating.
Now, it turns out that that is quite big: for a simple program like the test
above, it produces around 350 lines of Racket, of which the `main` and `child`
bits are a single line of around 3000-4000 characters long. After mindlessly
trying to make sense of it (I had never used or seen Racket before), Wen
suggested writing a couple of simple Racket programs just to get familiar with
the language and threading semantics first instead of trying to learn the
language whilst simultaneously trying to debug some machine-generated programs
in it.

### A brief detour to learn Racket

Racket is based on the Scheme dialect of Lisp, so when
[you want a horse, you have a ((((((((((((horse))))))))))))](https://toggl.com/blog/build-horse-programming)
. You can define things with `(define name body+)`, and similar to Idris, you
also have `let-in` notation: `(let ([var val]+) body+)` (+ here being a
multiplicity: at least one of \<_thing_\>). The function `display` displays
things to the default output stream, and procedures are sequences of operations
beginning with the keyword `begin`. Since it is a functional programming
language, you can of course also invoke the almighty $\lambda$: `(lambda args
body+)`. So a program which sleeps for a second then prints "Hello World" would
look like:

```scheme
#lang racket/base
(define (main)
  (sleep 1)
  (display "Hello World\n")
  )

(void (main))
```

The `(void (main))` bit just ignores its arguments and returns `#<void>`. It's
used here to keep Racket from complaining after executing `main`, but it does
still evaluate `main` when written like this. Note also, that we're telling
Racket to only use `racket/base`. This is because this is the same functionality
that the Idris2 output uses, and we want to keep things as consistent as
possible.

Having a single-threaded program working, we can then move on to multiple
threads. The `thread` function takes a function of no arguments and spawns it in
a new thread. So to create a multi-threaded "Hello World", we can do:

```scheme
#lang racket/base
(define (main)
  (display "Hello ")
  (thread (lambda () (display "World\n")))
  (sleep 1)
  )

(void (main))
```

Now to define the crux of our problem:

```scheme
#lang racket/base
(define (child)
  (sleep 1)
  (display "Wor")
  (sleep 2)
  )

(define (main)
  (display "Hello\n")
  (thread (lambda () (child)))
  (sleep 4)
  (display "ld\n")
  (sleep 5)
  )

(void (main))
```

Run it aaaaand... we get the correct result! So the problem is definitely with
Idris's generated Racket and not with Racket itself! That's a relief (and also,
makes a lot of sense, Racket is a pretty mature language after all). Armed with
an improved knowledge of Racket, let's try to have a look at the Idris2 codegen
again, after a couple of minor modifications:

1. Using only `putStrLn`, since without the newline Racket sometimes buffers the
   output.
2. Getting rid of as much syntactic sugar as possible in order to minimise the
   number of things that really shouldn't, but possibly, maybe, could be
   affecting things. If you're familiar with `do` notation, you know that it is
   really just a nice way to write series of nested `>>=` (read 'bind')
   applications. These in turn, when doing IO in Idris2, are sugar for the
   `io_bind` function.

### Back to the problem

Desugared, our program looks like this:

```idris
import System
import System.Concurrency

child : IO ()
child =
  sleep 1
  `io_bind` (\_ =>
  putStrLn "Wor"
  `io_bind` (\_ =>
  sleep 2
  ))

main : IO ()
main =
  putStrLn "Hello"
  `io_bind` (\_ =>
  fork child
  `io_bind` (\t =>
  sleep 4
  `io_bind` (\_ =>
  putStrLn "ld"
  `io_bind` (\_ =>
  sleep 5
  ))))
```

(Ooh, look at the end of `main`; we've made ourselves a little Lisp-like
thing!)  
Now for the codegen:

```scheme
(define Main-main (lambda (ext-0) (let ((act-285 ((PreludeC-45IO-putStrLn 'erased (vector 0 (vector 0 (vector 0 (lambda (b) (lambda (a) (lambda (func) (lambda (arg-149) (lambda (eta-0) (PreludeC-45IO-map_Functor_IO 'erased 'erased func arg-149 eta-0)))))) (lambda (a) (lambda (arg-482) (lambda (eta-0) arg-482))) (lambda (b) (lambda (a) (lambda (arg-483) (lambda (arg-485) (lambda (eta-0) (let ((act-17 (arg-483 eta-0))) (let ((act-16 (arg-485 eta-0))) (act-17 act-16))))))))) (lambda (b) (lambda (a) (lambda (arg-644) (lambda (arg-645) (lambda (eta-0) (let ((act-24 (arg-644 eta-0))) ((arg-645 act-24) eta-0))))))) (lambda (a) (lambda (arg-647) (lambda (eta-0) (let ((act-51 (arg-647 eta-0))) (act-51 eta-0)))))) (lambda (a) (lambda (arg-7243) arg-7243))) "Hello") ext-0))) (let ((act-201 (PreludeC-45IO-fork (lambda (eta-0) (Main-child eta-0)) ext-0))) (let ((act-145 ((System-sleep 'erased (vector 0 (vector 0 (vector 0 (lambda (b) (lambda (a) (lambda (func) (lambda (arg-149) (lambda (eta-0) (PreludeC-45IO-map_Functor_IO 'erased 'erased func arg-149 eta-0)))))) (lambda (a) (lambda (arg-482) (lambda (eta-0) arg-482))) (lambda (b) (lambda (a) (lambda (arg-483) (lambda (arg-485) (lambda (eta-0) (let ((act-17 (arg-483 eta-0))) (let ((act-16 (arg-485 eta-0))) (act-17 act-16))))))))) (lambda (b) (lambda (a) (lambda (arg-644) (lambda (arg-645) (lambda (eta-0) (let ((act-24 (arg-644 eta-0))) ((arg-645 act-24) eta-0))))))) (lambda (a) (lambda (arg-647) (lambda (eta-0) (let ((act-51 (arg-647 eta-0))) (act-51 eta-0)))))) (lambda (a) (lambda (arg-7243) arg-7243))) 4) ext-0))) (let ((act-117 ((PreludeC-45IO-putStrLn 'erased (vector 0 (vector 0 (vector 0 (lambda (b) (lambda (a) (lambda (func) (lambda (arg-149) (lambda (eta-0) (PreludeC-45IO-map_Functor_IO 'erased 'erased func arg-149 eta-0)))))) (lambda (a) (lambda (arg-482) (lambda (eta-0) arg-482))) (lambda (b) (lambda (a) (lambda (arg-483) (lambda (arg-485) (lambda (eta-0) (let ((act-17 (arg-483 eta-0))) (let ((act-16 (arg-485 eta-0))) (act-17 act-16))))))))) (lambda (b) (lambda (a) (lambda (arg-644) (lambda (arg-645) (lambda (eta-0) (let ((act-24 (arg-644 eta-0))) ((arg-645 act-24) eta-0))))))) (lambda (a) (lambda (arg-647) (lambda (eta-0) (let ((act-51 (arg-647 eta-0))) (act-51 eta-0)))))) (lambda (a) (lambda (arg-7243) arg-7243))) "ld") ext-0))) ((System-sleep 'erased (vector 0 (vector 0 (vector 0 (lambda (b) (lambda (a) (lambda (func) (lambda (arg-149) (lambda (eta-0) (PreludeC-45IO-map_Functor_IO 'erased 'erased func arg-149 eta-0)))))) (lambda (a) (lambda (arg-482) (lambda (eta-0) arg-482))) (lambda (b) (lambda (a) (lambda (arg-483) (lambda (arg-485) (lambda (eta-0) (let ((act-17 (arg-483 eta-0))) (let ((act-16 (arg-485 eta-0))) (act-17 act-16))))))))) (lambda (b) (lambda (a) (lambda (arg-644) (lambda (arg-645) (lambda (eta-0) (let ((act-24 (arg-644 eta-0))) ((arg-645 act-24) eta-0))))))) (lambda (a) (lambda (arg-647) (lambda (eta-0) (let ((act-51 (arg-647 eta-0))) (act-51 eta-0)))))) (lambda (a) (lambda (arg-7243) arg-7243))) 5) ext-0)))))))
(define Main-child (lambda (ext-0) (let ((act-113 ((System-sleep 'erased (vector 0 (vector 0 (vector 0 (lambda (b) (lambda (a) (lambda (func) (lambda (arg-149) (lambda (eta-0) (PreludeC-45IO-map_Functor_IO 'erased 'erased func arg-149 eta-0)))))) (lambda (a) (lambda (arg-482) (lambda (eta-0) arg-482))) (lambda (b) (lambda (a) (lambda (arg-483) (lambda (arg-485) (lambda (eta-0) (let ((act-17 (arg-483 eta-0))) (let ((act-16 (arg-485 eta-0))) (act-17 act-16))))))))) (lambda (b) (lambda (a) (lambda (arg-644) (lambda (arg-645) (lambda (eta-0) (let ((act-24 (arg-644 eta-0))) ((arg-645 act-24) eta-0))))))) (lambda (a) (lambda (arg-647) (lambda (eta-0) (let ((act-51 (arg-647 eta-0))) (act-51 eta-0)))))) (lambda (a) (lambda (arg-7243) arg-7243))) 1) ext-0))) (let ((act-85 ((PreludeC-45IO-putStrLn 'erased (vector 0 (vector 0 (vector 0 (lambda (b) (lambda (a) (lambda (func) (lambda (arg-149) (lambda (eta-0) (PreludeC-45IO-map_Functor_IO 'erased 'erased func arg-149 eta-0)))))) (lambda (a) (lambda (arg-482) (lambda (eta-0) arg-482))) (lambda (b) (lambda (a) (lambda (arg-483) (lambda (arg-485) (lambda (eta-0) (let ((act-17 (arg-483 eta-0))) (let ((act-16 (arg-485 eta-0))) (act-17 act-16))))))))) (lambda (b) (lambda (a) (lambda (arg-644) (lambda (arg-645) (lambda (eta-0) (let ((act-24 (arg-644 eta-0))) ((arg-645 act-24) eta-0))))))) (lambda (a) (lambda (arg-647) (lambda (eta-0) (let ((act-51 (arg-647 eta-0))) (act-51 eta-0)))))) (lambda (a) (lambda (arg-7243) arg-7243))) "Wor") ext-0))) ((System-sleep 'erased (vector 0 (vector 0 (vector 0 (lambda (b) (lambda (a) (lambda (func) (lambda (arg-149) (lambda (eta-0) (PreludeC-45IO-map_Functor_IO 'erased 'erased func arg-149 eta-0)))))) (lambda (a) (lambda (arg-482) (lambda (eta-0) arg-482))) (lambda (b) (lambda (a) (lambda (arg-483) (lambda (arg-485) (lambda (eta-0) (let ((act-17 (arg-483 eta-0))) (let ((act-16 (arg-485 eta-0))) (act-17 act-16))))))))) (lambda (b) (lambda (a) (lambda (arg-644) (lambda (arg-645) (lambda (eta-0) (let ((act-24 (arg-644 eta-0))) ((arg-645 act-24) eta-0))))))) (lambda (a) (lambda (arg-647) (lambda (eta-0) (let ((act-51 (arg-647 eta-0))) (act-51 eta-0)))))) (lambda (a) (lambda (arg-7243) arg-7243))) 2) ext-0)))))
```

Told you it wasn't pretty... An attempt at prettifying it by formatting it to a
max line length of 80 characters (without "proper" indentation since you'd
otherwise end up with 100s of lines of 1 statement) leaves us with:

```scheme
(define Main-dmain (lambda (ext-0) (let ((act-286 ((PreludeC-45IO-putStrLn
'erased (vector 0 (vector 0 (vector 0 (lambda (b) (lambda (a) (lambda (func)
(lambda (arg-149) (lambda (eta-0) (PreludeC-45IO-map_Functor_IO 'erased 'erased
func arg-149 eta-0)))))) (lambda (a) (lambda (arg-482) (lambda (eta-0)
arg-482))) (lambda (b) (lambda (a) (lambda (arg-483) (lambda (arg-485) (lambda
(eta-0) (let ((act-17 (arg-483 eta-0))) (let ((act-16 (arg-485 eta-0))) (act-17
act-16))))))))) (lambda (b) (lambda (a) (lambda (arg-644) (lambda (arg-645)
(lambda (eta-0) (let ((act-24 (arg-644 eta-0))) ((arg-645 act-24) eta-0)))))))
(lambda (a) (lambda (arg-647) (lambda (eta-0) (let ((act-51 (arg-647 eta-0)))
(act-51 eta-0)))))) (lambda (a) (lambda (arg-7243) arg-7243))) "Hello") ext-0)))
(let ((act-202 (PreludeC-45IO-fork (lambda (eta-0) (Main-child eta-0)) ext-0)))
(let ((act-146 ((System-sleep 'erased (vector 0 (vector 0 (vector 0 (lambda (b)
(lambda (a) (lambda (func) (lambda (arg-149) (lambda (eta-0)
(PreludeC-45IO-map_Functor_IO 'erased 'erased func arg-149 eta-0)))))) (lambda
(a) (lambda (arg-482) (lambda (eta-0) arg-482))) (lambda (b) (lambda (a) (lambda
(arg-483) (lambda (arg-485) (lambda (eta-0) (let ((act-17 (arg-483 eta-0))) (let
((act-16 (arg-485 eta-0))) (act-17 act-16))))))))) (lambda (b) (lambda (a)
(lambda (arg-644) (lambda (arg-645) (lambda (eta-0) (let ((act-24 (arg-644
eta-0))) ((arg-645 act-24) eta-0))))))) (lambda (a) (lambda (arg-647) (lambda
(eta-0) (let ((act-51 (arg-647 eta-0))) (act-51 eta-0)))))) (lambda (a) (lambda
(arg-7243) arg-7243))) 4) ext-0))) (let ((act-118 ((PreludeC-45IO-putStrLn
'erased (vector 0 (vector 0 (vector 0 (lambda (b) (lambda (a) (lambda (func)
(lambda (arg-149) (lambda (eta-0) (PreludeC-45IO-map_Functor_IO 'erased 'erased
func arg-149 eta-0)))))) (lambda (a) (lambda (arg-482) (lambda (eta-0)
arg-482))) (lambda (b) (lambda (a) (lambda (arg-483) (lambda (arg-485) (lambda
(eta-0) (let ((act-17 (arg-483 eta-0))) (let ((act-16 (arg-485 eta-0))) (act-17
act-16))))))))) (lambda (b) (lambda (a) (lambda (arg-644) (lambda (arg-645)
(lambda (eta-0) (let ((act-24 (arg-644 eta-0))) ((arg-645 act-24) eta-0)))))))
(lambda (a) (lambda (arg-647) (lambda (eta-0) (let ((act-51 (arg-647 eta-0)))
(act-51 eta-0)))))) (lambda (a) (lambda (arg-7243) arg-7243))) "ld") ext-0)))
((System-sleep 'erased (vector 0 (vector 0 (vector 0 (lambda (b) (lambda (a)
(lambda (func) (lambda (arg-149) (lambda (eta-0) (PreludeC-45IO-map_Functor_IO
'erased 'erased func arg-149 eta-0)))))) (lambda (a) (lambda (arg-482) (lambda
(eta-0) arg-482))) (lambda (b) (lambda (a) (lambda (arg-483) (lambda (arg-485)
(lambda (eta-0) (let ((act-17 (arg-483 eta-0))) (let ((act-16 (arg-485 eta-0)))
(act-17 act-16))))))))) (lambda (b) (lambda (a) (lambda (arg-644) (lambda
(arg-645) (lambda (eta-0) (let ((act-24 (arg-644 eta-0))) ((arg-645 act-24)
eta-0))))))) (lambda (a) (lambda (arg-647) (lambda (eta-0) (let ((act-51
(arg-647 eta-0))) (act-51 eta-0)))))) (lambda (a) (lambda (arg-7243) arg-7243)))
5) ext-0)))))))

(define Main-child (lambda (ext-0) (let ((act-24 ((System-sleep 'erased (vector
0 (vector 0 (vector 0 (lambda (b) (lambda (a) (lambda (func) (lambda (arg-149)
(lambda (eta-0) (PreludeC-45IO-map_Functor_IO 'erased 'erased func arg-149
eta-0)))))) (lambda (a) (lambda (arg-482) (lambda (eta-0) arg-482))) (lambda (b)
(lambda (a) (lambda (arg-483) (lambda (arg-485) (lambda (eta-0) (let ((act-17
(arg-483 eta-0))) (let ((act-16 (arg-485 eta-0))) (act-17 act-16)))))))))
(lambda (b) (lambda (a) (lambda (arg-644) (lambda (arg-645) (lambda (eta-0) (let
((act-24 (arg-644 eta-0))) ((arg-645 act-24) eta-0))))))) (lambda (a) (lambda
(arg-647) (lambda (eta-0) (let ((act-51 (arg-647 eta-0))) (act-51 eta-0))))))
(lambda (a) (lambda (arg-7243) arg-7243))) 1) ext-0))) (let ((act-25
((PreludeC-45IO-putStrLn 'erased (vector 0 (vector 0 (vector 0 (lambda (b)
(lambda (a) (lambda (func) (lambda (arg-149) (lambda (eta-0)
(PreludeC-45IO-map_Functor_IO 'erased 'erased func arg-149 eta-0)))))) (lambda
(a) (lambda (arg-482) (lambda (eta-0) arg-482))) (lambda (b) (lambda (a) (lambda
(arg-483) (lambda (arg-485) (lambda (eta-0) (let ((act-17 (arg-483 eta-0))) (let
((act-16 (arg-485 eta-0))) (act-17 act-16))))))))) (lambda (b) (lambda (a)
(lambda (arg-644) (lambda (arg-645) (lambda (eta-0) (let ((act-25 (arg-644
eta-0))) ((arg-645 act-25) eta-0))))))) (lambda (a) (lambda (arg-647) (lambda
(eta-0) (let ((act-51 (arg-647 eta-0))) (act-51 eta-0)))))) (lambda (a) (lambda
(arg-7243) arg-7243))) "Wor") ext-0))) ((System-sleep 'erased (vector 0 (vector
0 (vector 0 (lambda (b) (lambda (a) (lambda (func) (lambda (arg-149) (lambda
(eta-0) (PreludeC-45IO-map_Functor_IO 'erased 'erased func arg-149 eta-0))))))
(lambda (a) (lambda (arg-482) (lambda (eta-0) arg-482))) (lambda (b) (lambda (a)
(lambda (arg-483) (lambda (arg-485) (lambda (eta-0) (let ((act-17 (arg-483
eta-0))) (let ((act-16 (arg-485 eta-0))) (act-17 act-16))))))))) (lambda (b)
(lambda (a) (lambda (arg-644) (lambda (arg-645) (lambda (eta-0) (let ((act-26
(arg-644 eta-0))) ((arg-645 act-26) eta-0))))))) (lambda (a) (lambda (arg-647)
(lambda (eta-0) (let ((act-51 (arg-647 eta-0))) (act-51 eta-0)))))) (lambda (a)
(lambda (arg-7243) arg-7243))) 2) ext-0)))))
```

Not the best. But hey, at least vim can now highlight matching brackets (it
deals very poorly with very long lines), so that's something... (Also note that
for brevity's sake I've left out the numerous generated definitions of all the
functions Idris2 uses). Looking over the program itself, there doesn't really
seem to be anything wrong. Ignoring the various etas, args, Functors, etc., the
`let`-bindings seem sensible enough, and the bracket-matching helps us spot that
things happen where they should, e.g. `sleep 4` happens after `fork child`.

### First suspect: `fork`

Looking at the Racket output, we get the following chain of calls:
1. `Main-main` calls `PreludeC-45IO-fork`
2. which is defined as
   ```scheme
   (lambda (arg-0 ext-0) (PreludeC-45IO-prim__fork arg-0 ext-0))
   ```
   i.e. it internally calls `PreludeC-45IO-prim__fork`
3. which is defined as
   ```scheme
   (lambda (farg-0 farg-1) (blodwen-thread farg-0))
   ```
   calling `blodwen-thread`
4. which, finally, is defined as
   ```scheme
   (define (blodwen-thread proc)
           (thread (lambda () (proc (vector 0)))))
   ```
   and simply uses the Racket built-in `thread` function.

Nothing immediately suspicious here, and a quick Racket program confirms it is
fine:
```scheme
#lang racket/base
(define (blodwen-thread proc)                                                    
  (thread (lambda () (proc (vector 0)))))

(define (main)
  (display "Hello\n")
  (let ([t (blodwen-thread (lambda (v)
                               (sleep 1)
                               (display "Wor\n")
                               (sleep 5)
                               ))])
       (sleep 2) (display "ld\n") (sleep 6))
  )

(void (main))
```
```bash
$ racket test-fork.rkt
Hello
Wor
ld 
```

So no problems there. That's both reassuring and annoying since it means we have
to poke at the internals; the obvious suspect is fine.

### Second suspect: `putStrLn`

It could be that `putStrLn` is affecting the threads in some weird way. To test
this, we can replace all the generated `PreludeC-45IO-putStrLn` with `display`.
A handy shortcut for this in Vim is the command `c%`: `c` deletes based on the
given "motion" and enters 'Insert' mode, `%` is a motion from the next or
currently highlighted item to its match. So when highlighting a bracket, `c%`
deletes everything inside that pair of matching brackets. I could put the code
here, but honestly it takes up a lot of space and it doesn't get more
interesting, so I'm not going to bother. Even more so because it turns out that
with native `display` instead of the Idris functions, it still doesn't work...
Moving on.

### Third suspect: `sleep`

The only remaining suspect in the code is `sleep`. After a discussion with
Edwin, it also turns out that it is doing external function calls and Racket
might be cautious about that, so it seems increasingly likely that it is the
problem. Same strategy as above: use `c%` to replace everything within the
brackets containing `System-sleep` with an equivalent `sleep` statement and then
see if anything changes.

```scheme
(define Main-dmain (lambda (ext-0) (let ((act-286 ((PreludeC-45IO-putStrLn
'erased (vector 0 (vector 0 (vector 0 (lambda (b) (lambda (a) (lambda (func)
(lambda (arg-149) (lambda (eta-0) (PreludeC-45IO-map_Functor_IO 'erased 'erased
func arg-149 eta-0)))))) (lambda (a) (lambda (arg-482) (lambda (eta-0)
arg-482))) (lambda (b) (lambda (a) (lambda (arg-483) (lambda (arg-485) (lambda
(eta-0) (let ((act-17 (arg-483 eta-0))) (let ((act-16 (arg-485 eta-0))) (act-17
act-16))))))))) (lambda (b) (lambda (a) (lambda (arg-644) (lambda (arg-645)
(lambda (eta-0) (let ((act-24 (arg-644 eta-0))) ((arg-645 act-24) eta-0)))))))
(lambda (a) (lambda (arg-647) (lambda (eta-0) (let ((act-51 (arg-647 eta-0)))
(act-51 eta-0)))))) (lambda (a) (lambda (arg-7243) arg-7243))) "Hello") ext-0)))
(let ((act-202 (PreludeC-45IO-fork (lambda (eta-0) (Main-child eta-0)) ext-0)))
(let ((act-146 (sleep 4))) (let ((act-118 ((PreludeC-45IO-putStrLn
'erased (vector 0 (vector 0 (vector 0 (lambda (b) (lambda (a) (lambda (func)
(lambda (arg-149) (lambda (eta-0) (PreludeC-45IO-map_Functor_IO 'erased 'erased
func arg-149 eta-0)))))) (lambda (a) (lambda (arg-482) (lambda (eta-0)
arg-482))) (lambda (b) (lambda (a) (lambda (arg-483) (lambda (arg-485) (lambda
(eta-0) (let ((act-17 (arg-483 eta-0))) (let ((act-16 (arg-485 eta-0))) (act-17
act-16))))))))) (lambda (b) (lambda (a) (lambda (arg-644) (lambda (arg-645)
(lambda (eta-0) (let ((act-24 (arg-644 eta-0))) ((arg-645 act-24) eta-0)))))))
(lambda (a) (lambda (arg-647) (lambda (eta-0) (let ((act-51 (arg-647 eta-0)))
(act-51 eta-0)))))) (lambda (a) (lambda (arg-7243) arg-7243))) "ld") ext-0)))
(sleep 5)))))))

(define Main-child (lambda (ext-0) (let ((act-24 (sleep 1))) (let ((act-25
((PreludeC-45IO-putStrLn 'erased (vector 0 (vector 0 (vector 0 (lambda (b)
(lambda (a) (lambda (func) (lambda (arg-149) (lambda (eta-0)
(PreludeC-45IO-map_Functor_IO 'erased 'erased func arg-149 eta-0)))))) (lambda
(a) (lambda (arg-482) (lambda (eta-0) arg-482))) (lambda (b) (lambda (a) (lambda
(arg-483) (lambda (arg-485) (lambda (eta-0) (let ((act-17 (arg-483 eta-0))) (let
((act-16 (arg-485 eta-0))) (act-17 act-16))))))))) (lambda (b) (lambda (a)
(lambda (arg-644) (lambda (arg-645) (lambda (eta-0) (let ((act-25 (arg-644
eta-0))) ((arg-645 act-25) eta-0))))))) (lambda (a) (lambda (arg-647) (lambda
(eta-0) (let ((act-51 (arg-647 eta-0))) (act-51 eta-0)))))) (lambda (a) (lambda
(arg-7243) arg-7243))) "Wor") ext-0))) (sleep 2)))))
```

Testing, and...

```bash
$ racket test-native-sleep.rkt
Hello
Wor
ld
```

Ah shoot. That did work correctly. So something is wrong with Idris2's
`sleep` and we need to look at the internals.

### Finding the source of the problem

Fun though poking around at a system you don't fully understand is, sometimes it
is also best to just ask the people who really know it. Talking things over with
Edwin and Wen, Edwin suggested that it may be to do with the fact that `sleep`
is implemented as a foreign function; `sleep` uses the system sleep by default
(as an FFI-binding in `libidris2_support.so`). I asked on the Racket Slack
whether Racket was doing something weird with foreign function calls. It turned
out that Racket threads are green/virtual threads.

For the uninitiated (which included myself until I was doing this) the
difference is to do with system/OS threads, which are managed by the Operating
System and hence can execute in parallel regardless of which program created
them, and green threads which are managed by a virtual machine or, in Racket's
case, a runtime. This means that if the runtime blocks, every green thread
managed by the runtime also blocks. Guess what happens on foreign function
calls? The Racket runtime waits for the foreign call to return! This makes sense
and works fine for a lot of functions, but it definitely also causes problems
with `sleep`, whose entire purpose is to take a while to return. So this needs
to be fixed and use `blodwen-sleep`, which is `sleep` defined using Racket's
`sleep` function, instead of the external `idris2_sleep` C-binding.

### Fixing the problem

As mentioned, `blodwen-sleep` is already a function in the `support.rkt` file,
so if it can be used instead of `idris2_sleep` by the code-gen, then everything
should be fine. Which function gets generated by the various codegen backends is
specified through
[FFI directives](https://idris2.readthedocs.io/en/latest/ffi/ffi.html). Looking
through `libs/base/System.idr`, we can see that `sleep` and `usleep` both bind
to C using:
```idris
%foreign support "idris2_sleep"
```

The `support` function is just shorthand for a C binding of the given function
name to `libidris2_support`. Since Racket is a flavour of Scheme, we specify the
new code-gen as follows:
```idris
%foreign "scheme,racket:blodwen-sleep"
         support "idris2_sleep"
```
and similar for `usleep` (being _very_ careful to write _`u`_`sleep` and not
`sleep`; that one took me a bit to figure out why some tests suddenly seemed to
hang -- they were just sleeping for 10000 seconds instead of 10000
microseconds). With this change, the Racket backend uses `blodwen-sleep` for
sleeping, and everything else still uses `idris2_sleep`.

Recompile Idris2, run the tests, and... Success! The program now behaves as
expected, due to `sleep` never calling anything outside of Racket meaning the
green threads behave as expected. And even better: The mutex tests now behave as
expected and pass, meaning the Racket mutex implementation is fine!

### Wrapping up

To make it clear for future users what was happening, I added a couple of
comments to `support/racket/support.rkt` mentioning that threads are actually
green threads and to be careful with `sleep` and threading. Since the changes
modified the Idris2 compiler, I also added a description of what and why to the
`CHANGELOG`. Then all that remained to be done was to `git push` and submit a
pull request to the main repository. With `sleep` fixed and some certainty that
mutexes worked as expected, I could now actually write the tests for the
condition variables' implementation in Racket. As with all good tests however,
these resulted in finding more problems. This blog post is already long, so if
you're somehow still interested in my ramblings,
[here is that bit](/en/post/implementing-condition-variables).


### Acknowledgements

Thanks to [Wen](https://wen.works) for doing the massive and impressive work of
originally implementing the various concurrency primitives, and for
helping and encouraging me to explore and understand Racket. Also thanks to
[Edwin](https://www.type-driven.org.uk/edwinb/)
for helping narrow down the problem and explaining various Idris2 internals, and
to the Racket community for being nice and helpful in terms of explaining how
Rackets thread internals work.

