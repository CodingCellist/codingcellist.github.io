---
# Documentation: https://wowchemy.com/docs/managing-content/

title: "Hunting an Idris2 Codegen Bug"
subtitle: ""
summary: "I accidentally discovered a bug in the Idris2 codegen. Let's explore
          how to narrow it down, and hopefully fix it."
authors: [thomas-e-hansen]
tags: [fp, idris2, debug]
categories: []
date: 2023-04-21
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

## Background

I had working on an annoyingly difficult Ph.D.-related project recently, and
when it finally _did_ work, Idris itself crashed. And spectacularly so! I got an
error message which I'd never seen before:

```
Exception in string-append: erased is not a string
```

This isn't an `INTERNAL ERROR`, which typically happen when there is an
`idris_crash` call somewhere, so it had to be something to do with the compiled
Idris code. And it had to be something serious, because `erased` values are (as
the name suggests) not meant to be there; they're never meant to be used at
runtime! So something was up with the Idris compiler. That's scary, because
there is _a lot_ that makes Idris2 tick, and like all compiled code, it's really
mostly meant to be machine-generated and executed, not read by humans...

After asking for help on the Idris discord, both
[stefan-hoeck](https://github.com/stefan-hoeck)
and
[dunham](https://github.com/dunhamsteve)
suggested ways to get more readable compiled code out (by compiling to NodeJS)
and to potentially get a stack trace (by using Racket Scheme instead of Chez).
With that, I was able to narrow down the problem to the built-in `mod` function.
The `mod` function is part of the Idris2 prelude's `Integral` interface, and for
all the definitions in the prelude is implemented along the following lines:

```idris
Integral Int where
  div x y =
    case y == 0 of
         False => prim__div_int x y

  mod x y =
    case y == 0 of
         False => prim__mod_int x y
```

This is, as you may have noticed, neither `total` nor `covering`. So what
happens with that? My first thought was to "fix" this by filling in the missing
`True` case and adding a descriptive crash message in those cases. However,
dunham figured out that the issue was actually more serious than that. He
defined `mod` exactly the same, just outside the `Integral` interface, and got
the expected crash message!

```idris
partial
mod : Int -> Int -> Int
mod a b = case b == 0 of False => prim__mod_Int a b

partial
main : IO ()
main = printLn (mod 10 0)
```

```
ERROR: Unhandled input for Main.case block in mod at src.Error:9:1--10:31
```

The error I was seeing was only reproducible when using the built-in
`Prelude.Num.mod`, suggesting that there was something wrong with the code
generation/compilation itself!


## The problem

As part of his investigation, dunham had discovered that the generated scheme
code _did_ contain the correct error message, but somehow the generated function
call was wrong:

```scheme
(define PreludeC-45Num-u--mod_Integral_Int 
  (lambda (arg-0 arg-1) 
          (let ((sc0 (PreludeC-45EqOrd-u--C-61C-61_Eq_Int arg-1 (blodwen-toSignedInt 0 63)))) 
            (cond ((equal? sc0 0) (blodwen-euclidMod arg-0 arg-1)) 
                  (else ((Builtin-idris_crash 'erased) "Unhandled input for Prelude.Num.case block in mod at Prelude.Num:131:3--133:40"))))))
```

That final line evaluating `Builtin-idris_crash 'erased`, followed by an error
string, should just be the evaluation of `Builtin-idris_crash` _applied to_ that
same error string. An extra `'erased` was getting in there somehow.

The first thing I did was to check whether this applied to just the Scheme
backends, or every backend. Unfortunately, I could reproduce the erroneous code
generation on both the NodeJS and the Reference-counting C (RefC) backends,
meaning the problem was universal.

{{< spoiler text="Show NodeJS code" >}}

```js
/* Prelude.Num.mod */
function Prelude_Num_mod_Integral_Int($0, $1) {
 switch(Prelude_EqOrd_x3dx3d_Eq_Int($1, Number(_truncBigInt32(0n)))) {
  case 0: return _mod($0, $1);
  default: return Builtin_idris_crash(undefined)('Unhandled input for Prelude.Num.case block in mod at Prelude.Num:131:3--133:40');
 }
}
```

{{</spoiler>}}

{{< spoiler text="Show RefC code" >}}

```c
switch(extractInt(var_6)){
      case 0 :
      {
        tmp_15 = mod_Int64(var_0, var_1);
        break;
      }
      default :
      {
        // start Builtin_idris_crash(NULL)                   // Prelude.Num:131:3--133:40
        Value_Arglist *arglist_16 = newArglist(0,1);
        arglist_16->args[0] =  newReference(NULL);
        Value *(*fPtr_17)(Value_Arglist*) = Builtin_idris_crash_arglist;
                                                             // Prelude.Num:131:3--133:40
        Value *closure_17 = (Value*)makeClosureFromArglist(fPtr_17, arglist_16);
                                                             // Prelude.Num:131:3--133:40
        // end   Builtin_idris_crash(NULL)                   // Prelude.Num:131:3--133:40
        Value * var_4 = trampoline(closure_17);              // Prelude.Num:131:3--133:40
        Value * var_5 = (Value*)makeString("Unhandled input for Prelude.Num.case block in mod at Prelude.Num:131:3--133:40");
                                                             // Prelude.Num:131:3--133:40
        tmp_15 = tailcall_apply_closure(var_4, var_5);
        removeReference(var_5);
        removeReference(var_4);
      }
    }
```

{{</spoiler>}}


## Hunting down the bug

Idris comes with logging functionality for exactly this kind of scenario. So the
first thing I tried to help me narrow down what was wrong was to add some
`%logging` around the affected code. Unfortunately, neither `compile.casetree`
or just `compile` yielded anything. But I had the expected error string: it
started with "Unhandled input". So armed with ripgrep and the Idris2 source, I
tried searching for that string.

This led me to `TTImp.ProcessDef.mkRunTime`, specifically lines 804-806:

```idris
           let clauses = case cov of
                              MissingCases _ => addErrorCase clauses_init
                              _ => clauses_init
```

Going down a `TTImp` hole is rarely fun. `TTImp` is an abbreviation for "Type
Theory with Implicits" and is the underlying representation of Idris2 code. As
far as I understand, this is roughly the "assembly" of Idris -- all Idris code gets turned into
`TTImp`, which is relatively simple while being powerful enough to express
everything you need to reason about a complete Idris program. So yeah, digging
through that stuff is seldom fun, but sometimes you just gotta.

Coming back to the code I had found, it turned out the `addErrorCase` function
was defined locally (in a `where`-block) to `mkRunTime`. Its function was to
traverse the list of existing `case` clauses until it reached the final one,
and then append a `MkCrash` clause. However, as you can see from the code
above, there were no log messages being emitted when this was happening. Adding
log messages involved dealing with `Core` (what the Idris compiler uses for
state), which is always a bit delicate: there is _a lot_ going on, lots of
datatypes in scope, lots of compiler and/or functional programming specific
language in use, and lots of functions which manipulate these things in various
ways, but I managed to add a new log topic: `compile.casetree.missing`.

This initially seemed to do nothing, until I realised that I needed to put the
`%logging` pragmas around the interface implementation itself and then recompile
Idris2 to see the effects. Otherwise, the compiler happily skipped over the
already-compiled prelude and just compiled the file that was using it. Getting
output only led to more confusion though. The log outputs of the file with a
custom `mod` function and the prelude were the same!

```idris
LOG compile.casetree.missing:5: Adding uncovered error for [[a, b]: ($resolved2578 [__]@b[1] [__]@a[0] $resolved2456) = ($resolved55 a[0] b[1])]
LOG compile.casetree:5: Clauses are [[a, b]: ($resolved2578 [__]@b[1] [__]@a[0] $resolved2456) = ($resolved55 a[0] b[1]), [a, b]: ($resolved2578 [__] [__] [__]) = (Builtin.idris_crash [__] "Unhandled input for Issue2950.case block in mod at Issue2950:9:1--9:52")]
LOG compile.casetree:5: simpleCase: Clauses:
  (Issue2950.case block in mod [__]@{pat0::1} [__]@{pat0::0} Prelude.Basics.False) = (prim__mod_Int {pat0::0} {pat0::1})
  (Issue2950.case block in mod [__] [__] [__]) = (Builtin.idris_crash [__] "Unhandled input for Issue2950.case block in mod at Issue2950:9:1--9:52")
```

```idris
LOG compile.casetree.missing:5: Adding uncovered error for [[x, y]: ($resolved1587 [__]@y[1] [__]@x[0] $resolved386) = ($resolved55 x[0] y[1])]
LOG compile.casetree:5: Clauses are [[x, y]: ($resolved1587 [__]@y[1] [__]@x[0] $resolved386) = ($resolved55 x[0] y[1]), [x, y]: ($resolved1587 [__] [__] [__]) = (Builtin.idris_crash [__] "Unhandled input for Prelude.Num.case block in mod at Prelude.Num:132:3--134:40")]
LOG compile.casetree:5: simpleCase: Clauses:
  (Prelude.Num.case block in mod [__]@{pat0::1} [__]@{pat0::0} Prelude.Basics.False) = (prim__mod_Int {pat0::0} {pat0::1})
  (Prelude.Num.case block in mod [__] [__] [__]) = (Builtin.idris_crash [__] "Unhandled input for Prelude.Num.case block in mod at Prelude.Num:132:3--134:40")
```

Sure, one used `a,b` and the other `x,y`, and there was some different numbering
of the machine-generated names, but other than that the clauses were exactly the
same. I tried following what happened to the `clauses` returned by the
`addErrorCase`, but this only confirmed that the runtime trees were the same:

```idris
Runtime tree for Issue2950.case block in mod:
  case {arg:2} : Prelude.Basics.Bool of
    Prelude.Basics.False => (prim__mod_Int {arg:1}[1] {arg:0}[0])
    _ =>
      (Builtin.idris_crash [__] "Unhandled input for Issue2950.case block in mod at Issue2950:9:1--9:52")
```

```idris
Runtime tree for Prelude.Num.case block in mod:
  case {arg:2} : Prelude.Basics.Bool of
    Prelude.Basics.False => (prim__mod_Int {arg:1}[1] {arg:0}[0])
    _ =>
      (Builtin.idris_crash [__] "Unhandled input for Prelude.Num.case block in mod at Prelude.Num:132:3--134:40")
```

On one hand, this was good, because it meant `TTImp` was fine (I knew that
the custom `mod` version gave the expected error message). On the other, this
was annoying because it meant the next step was to try to debug the compiler to
figure out how the completely fine `TTImp` got turned into not-completely-fine
Scheme (or JavaScript or C).

### Digging through the compiler

