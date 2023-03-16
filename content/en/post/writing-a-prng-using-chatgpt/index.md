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
date: 2023-03-16
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
>   gen <- mkStdGen 42 -- Seed the random number generator with a value of 42
>   rand <- randomR (0, 99) gen -- Generate a random integer between 0 and 99
>   pure rand
> 
> ```
> 
> In this example, we're using the `mkStdGen` function to create a new random
> number generator with a seed value of 42. We then use the `randomR` function
> to generate a random integer between 0 and 99. Finally, we return the
> generated random number using `pure`.
>
> Note that the `randInt` function has an `IO` type, which means that it has
> side effects and cannot be pure. This is because generating random numbers is
> impure, since it relies on an external source of randomness.
>
> If you want to generate a sequence of random numbers, you can use the
> `RandomGen` typeclass to create a random number generator and the `random`
> function to generate a random value from that generator:

Sensible first response, but it has the problem with using `IO`. Let's try being
more specific:

> [TH] Ah but this requires using IO. I am trying to write a pure library, where
> all the functions will be implemented from scratch. Is this something you can
> help with?

> [ChatGPT] Certainly! To generate pseudorandom numbers in a pure context,
> you'll need to use a pure random number generator. One popular choice for this
> is the Mersenne Twister algorithm, which is known for its good statistical
> properties and long period.
>
> Idris has a package for Mersenne Twister called `mt` that you can use to
> implement a pure random number generator.
>
> Here's an example of how you could use the `mt` package to generate a list of
> random integers:
>
> ```idris
> module Random
>
> import mt
>
> generateRandomSequence : Int -> List Int
> generateRandomSequence n = evalState (replicateM n random) (initGen 12345)
>
> random : State MT Int
> random = do
> gen <- get
> let (x, gen') = twist gen
> put gen'
> pure x
> ```
>
> In this example, we define a function `generateRandomSequence` that takes an
> integer `n` and returns a list of `n` random integers. The function uses the
> `evalState` function from the standard library's `Control.Monad.State` module
> to run a sequence of stateful actions in the `MT` monad.
>
> The stateful action that generates a single random integer is defined by the
> `random` function, which uses the `get` function to get the current state of
> the random number generator, the `twist` function from the `mt` package to
> generate a new random value and a new state, and the `put` function to update
> the state of the random number generator.
>
> The random number generator is initialized with a seed value of 12345 using
> the `initGen` function from the `mt` package.
>
> Note that since the `generateRandomSequence` function is pure, it does not
> have any side effects and can be used in any context without causing impurity.

Ah... This is a common problem with ChatGPT: it will happily make up modules and
APIs as need be. There is no `mt` module. But that's okay, we can just ask it to
help write something like that. At this point I _had_ skimmed a paper on PRNGs,
meaning I knew the words "Merkle-Damgård construction", but not what they meant.

> [TH] Okay, but we are trying to write the randomness function itself. Given
> that Idris represents 32-bits as `Bits32` and 64-bits as `Bits64`, could you
> help me write a Merkel-Damgård construction in Idris?

> [ChatGPT] Certainly! The Merkle-Damgard construction is a way to build a hash
> function from a compression function. To implement a pseudorandom number
> generator based on this construction, we can use the compression function to
> update the state of the generator and produce a new random value.
>
> Here's an example implementation of a 32-bit pseudorandom number generator
> based on the Merkle-Damgard construction:
>
> ```idris
> module Random
>
> import Data.Bits
> import Data.Word
>
> -- Define the state of the generator
> data PRNGState = PRNGState Word32
>
> -- Define the compression function
> compress : Word32 -> Word32 -> Word32
> compress state input = (state `shiftL` 1) `xor` input
>
> -- Define the random function
> random : PRNGState -> (Word32, PRNGState)
> random (PRNGState state) =
>   let newState = compress state 0x6C078965
>       output = compress newState 0x7F4A7C13
>   in (output, PRNGState newState)
> ```
>
> In this example, we define a data type `PRNGState` to represent the state of
> the pseudorandom number generator. The state is initialized with a 32-bit seed
> value.
>
> We define the `compress` function to be the compression function used in the
> Merkle-Damgard construction. The `compress` function takes the current state
> of the generator and an input word, and produces a new state by left-shifting
> the current state by one bit and XORing it with the input word.
>
> The `random` function takes a `PRNGState` value and produces a pair consisting
> of a random 32-bit word and a new `PRNGState` value. The function first uses
> the `compress` function to update the state of the generator with the constant
> value 0x6C078965. It then uses the `compress` function again to produce a
> random output word using the updated state and the constant value 0x7F4A7C13.
>
> To generate a sequence of random numbers, you can use the `randoms` function
> from the standard library's `Data.List` module, which takes a generator
> function and a count and returns a list of random values:
>
> ```idris
> import Data.List
>
> generateRandomSequence : Int -> List Word32
> generateRandomSequence n = randoms (fst . random) (PRNGState 12345) n
> ```
>
> In this example, we define a function `generateRandomSequence` that takes an
> integer `n` and returns a list of `n` random 32-bit words. The function uses
> the `randoms` function to generate the random sequence by applying the
> `random` function to a `PRNGState` value initialized with a seed value of
> 12345.

Now we're getting somewhere! But where did those magic numbers come from?...

> [TH] I'm not sure I understand how the constant values were picked. Could you
> please explain this?

> [ChatGPT] Certainly! The constant values used in the compression function are
> crucial to the security of the pseudorandom number generator.
>
> In the case of the Merkle-Damgard construction, the compression function takes
> two inputs: the current state of the hash function, and a new message block
> that needs to be hashed. The job of the compression function is to mix these
> inputs together in a way that makes it hard for an attacker to predict the
> output of the hash function.
>
> To achieve this, the compression function should be designed to have good
> diffusion and confusion properties. Diffusion means that a small change in the
> input should result in a significant change in the output, while confusion
> means that the output should not reveal any information about the input.
>
> The constant values used in the compression function are carefully chosen to
> achieve these properties. In the case of the 32-bit pseudorandom number
> generator example I provided, the constant values are:
>
>   - 0x6C078965
>   - 0x7F4A7C13
>
> These values were chosen based on the "Mersenne Twister" pseudorandom number
> generator, which is a widely-used and well-studied algorithm based on the same
> Merkle-Damgard construction. The specific values were chosen based on a
> combination of empirical testing and mathematical analysis, to ensure that the
> resulting pseudorandom number generator has good statistical properties and is
> resistant to attacks.
>
> In practice, the choice of constants can be an area of ongoing research and
> analysis for cryptographic algorithms. It's important to choose constants that
> are well-vetted and have been shown to provide good security properties, and
> to update the constants periodically as new research and attacks are
> discovered.

Neat! Now to correct the syntax errors:

> [TH] Okay, I see now, thanks for the explanation! In Idris, we use Bits32 not
> Word32. Could you please update the code to reflect this?

> [ChatGPT] Certainly! Here is the updated code that uses `Bits32` instead of
> `Word32`:
>
> ```idris
> module Random
>
> import Data.Bits
> import Data.Word
>
> -- Define the state of the generator
> data PRNGState = PRNGState Bits32
>
> -- Define the compression function
> compress : Bits32 -> Bits32 -> Bits32
> compress state input = (state `shl` 1) `xor` input
>
> -- Define the random function
> random : PRNGState -> (Bits32, PRNGState)
> random (PRNGState state) =
>   let newState = compress state 0x6C078965
>       output = compress newState 0x7F4A7C13
>   in (output, PRNGState newState)
> ```
>
> In this updated version, we define the `PRNGState` data type to hold a 32-bit
> value as a `Bits32.` The `compress` function takes two `Bits32` values as
> input and produces a new `Bits32` value as output. The `compress` function is
> defined to left-shift the state value by one bit and XOR it with the input
> value.
>
> The `random` function takes a `PRNGState` value and produces a pair consisting
> of a random 32-bit word as a `Bits32` value and a new `PRNGState` value. The
> function first uses the `compress` function to update the state of the
> generator with the constant value 0x6C078965. It then uses the `compress`
> function again to produce a random output word using the updated state and the
> constant value 0x7F4A7C13.
>
> Note that the `shl` function is used instead of `shiftL` to left-shift the
> state value by one bit, since `shl` operates on `Bits32` values.

It's not right about the `shl` function, it _is_ actually just `shiftL`, but
that's a simple fix. Now, I would like to stick this in a repository, so I'll
need a README. I _could_ write this myself, but hey we're having fun with this
anyway, so how far can we get?

> [TH] Wonderful! And could you help me write a README file for the github
> repository? It should have a brief note on what this code is, mention that it
> is licensed under the BSD-3-Clause license, and a disclaimer explaining that
> ChatGPT helped write the code.

> [ChatGPT] Of course! Here's an example README file that you can use:
>
> ```
> # Idris Pseudorandom Number Generator
>
> This is a simple pseudorandom number generator written in the Idris programming language. The generator uses a Merkle-Damgard construction with a 32-bit compression function to
>```

Fine, but I'd like to be more copy-pasteable:

> [TH] Thanks. Could you write that same README in markdown format, using
> 80-character line limits?

> [ChatGPT] Certainly! Here's an updated version of the README in Markdown
> format with 80-character line limits:
>
> ```markdown
> # Idris Pseudorandom Number Generator
>
> This is a simple pseudorandom number generator written in the Idris programming
> language. The generator uses a Merkle-Damgard construction with a 32-bit
> compression function to produce pseudorandom 32-bit values.
>
> ## License
>
> This code is licensed under the BSD-3-Clause license. See the `LICENSE` file for
> details.
>
> ## Disclaimer
>
> This code was written with the assistance of ChatGPT, a language model created by
> OpenAI. The author of this repository takes full responsibility for the
> implementation and any errors or omissions that may be present.
> ```

Now that's nice! I'm not super comfortable with the phrase about taking full
responsibility for the implementation and any errors though. This code should
_definitely_ not be used for anything serious!...

> [TH] Could you please add a sentence to the disclaimer explaining that this
> library may not be robust and so shouldn't be used for serious cryptographic
> work or anything where the randomness is critical?

> [ChatGPT] Certainly! Here's the updated disclaimer with the additional sentence:
>
> ```markdown
> ## Disclaimer
>
> This code was written with the assistance of ChatGPT, a language model created by
> OpenAI. The author of this repository takes full responsibility for the
> implementation and any errors or omissions that may be present. However, please
> note that this library may not be robust and therefore should not be used for
> serious cryptographic work or any applications where the quality of the
> randomness is critical. Use at your own risk.```
> ```

Much better! At this point, I had also tried pasting the code into an Idris file
and as a result, had gotten a complaint from the compiler: `PRNGState` has the
constructor `PRNGState`. ChatGPT is using Haskell syntax (which makes sense,
given that there is more Haskell than Idris out there so Haskell's syntax is the
statistically more likely when generating the next word).

> [TH] Thanks! I've spotted another mistake in the code: In Idris, we cannot use
> the name of the datatype as the name of the constructor. Instead, it is common
> to use 'Mk' as a prefix in the constructor. Could you please update the code?

> [ChatGPT] Sure! Here is the updated code that uses the `MkPRNGState`
> constructor:
>
> ```idris
> module Random
>
> import Data.Bits
> import Data.Word
>
> -- Define the state of the generator
> data PRNGState = MkPRNGState Bits32
>
> -- Define the compression function
> compress : Bits32 -> Bits32 -> Bits32
> compress state input = (state `shl` 1) `xor` input
>
> -- Define the random function
> random : PRNGState -> (Bits32, PRNGState)
> random (MkPRNGState state) =
>   let newState = compress state 0x6C078965
>       output = compress newState 0x7F4A7C13
>   in (output, MkPRNGState newState)
> ```
>
> In this updated version, we use the `MkPRNGState` constructor to create values
> of the `PRNGState` type. The `random` function is updated to pattern-match
> against the `MkPRNGState` constructor.

Now that's pretty cool, it also updated the calls and pattern-matches! But the
`compress` function still looks magic to me:

> [TH] How have you chosen the compress function in the code?

> [ChatGPT] The `compress` function used in the code is a simple bitwise
> operation that takes two `Bits32` values as inputs and returns a `Bits32`
> value. The implementation is taken from the TinyMT pseudorandom number
> generator, which is a small, fast, and high-quality pseudorandom number
> generator designed for use in simulations and gaming applications.
>
> The specific values used in the `compress` function were chosen based on the
> characteristics of the TinyMT generator. The `0x6C078965` constant is the
> default multiplier used in the TinyMT algorithm, and the `0x7F4A7C13` constant
> is used as a default XOR value. These values have been shown to produce good
> quality pseudorandom numbers with good statistical properties.

Right. ChatGPT is trained on existing text, including code, so in cases where
there is a common way to implement a thing, it makes sense that it copied one of
those. That should probably be cited:

> [TH] I see. Could you please add comments to the code explaining where each
> implementation is taken from?

> [ChatGPT] Sure, here's the updated code with comments added to explain where
> each implementation is taken from:
>
> ```idris
> module Random
>
> import Data.Bits
> import Data.Word
>
> -- Define the state of the generator
> data PRNGState = MkPRNGState Bits32
>
> -- Define the compression function
> -- The implementation is taken from the TinyMT pseudorandom number generator
> -- https://github.com/MersenneTwister-Lab/TinyMT/blob/master/TINYMT32.h
> compress : Bits32 -> Bits32 -> Bits32
> compress state input = (state `shl` 1) `xor` input
>
> -- Define the random function
> -- The implementation is a simple Merkle-Damgard construction that uses the
> -- compress function to produce pseudorandom 32-bit values
> random : PRNGState -> (Bits32, PRNGState)
> random (MkPRNGState state) =
>   let newState = compress state 0x6C078965
>       output = compress newState 0x7F4A7C13
>   in (output, MkPRNGState newState)
> ```
>
> In this updated version of the code, each implementation is now accompanied by
> a comment that explains where it was taken from.

Now here's where I got over-excited and forgot what I was dealing with: that
link is plausible and so I happily put it in the code. I have since reverted
that commit because the link doesn't actually point anywhere. The user and repo
are real, but the path to the file is wrong. The correct link is:

[https://github.com/MersenneTwister-Lab/TinyMT/blob/master/tinymt/tinymt32.h](https://github.com/MersenneTwister-Lab/TinyMT/blob/master/tinymt/tinymt32.h)

However, this is still wrong, because it turns out the file _doesn't contain the
constants_. So the reference is made up, insofar as it doesn't contain what
ChatGPT claims it does, and where the magic constants actually are taken from is
anyone's guess...

Anyway, remember how I said `shl` doesn't exist? Why refactor manually when you
can ask ChatGPT to do so?

> [TH] And another minor fix: In Idris the function is actually shiftL not shl.
> Could you please fix this?

> [ChatGPT] You're correct, my apologies for the confusion. The correct function
> in Idris for performing a left shift is `shiftL`. Here is the updated code:
>
> ```idris
> module Random
>
> import Data.Bits
> import Data.Word
>
> -- Define the state of the generator
> data PRNGState = MkPRNGState Bits32
>
> -- Define the compression function
> -- The implementation is taken from the TinyMT pseudorandom number generator
> -- https://github.com/MersenneTwister-Lab/TinyMT/blob/master/TINYMT32.h
> compress : Bits32 -> Bits32 -> Bits32
> compress state input = (state `shiftL` 1) `xor` input
>
> -- Define the random function
> -- The implementation is a simple Merkle-Damgard construction that uses the
> -- compress function to produce pseudorandom 32-bit values
> random : PRNGState -> (Bits32, PRNGState)
> random (MkPRNGState state) =
>   let newState = compress state 0x6C078965
>       output = compress newState 0x7F4A7C13
>   in (output, MkPRNGState newState)
> ```
>
> Thanks for bringing that to my attention!

Here it hasn't actually "learnt" anything, it has just taken my correction as
the ground truth. Which is fine for corrections in programs, but it does assume
the correction you've given ChatGPT is actually correct.

At this stage, I was enthusing with a friend about the generated results. I was
thoroughly impressed that it could write Idris (subject to some corrections, but
still), and even more so that the code actually seemed to work! My friend asked
a great question: "If it can do this, what about Agda, which has mixfix
operators?".

I know very little Agda, and have never used it, so I didn't know. But wait!
Given that ChatGPT wrote the code, would it know? It definitely would have at
least as good an understanding of Agda's syntax as I did; probably better
actually!

> [TH] Would this code work in Agda with mixfix operators?

> [ChatGPT] The Idris code we wrote should be translatable to Agda without much
> difficulty. However, Agda does not support mixfix operators in the same way
> that Idris does. Instead, you can define custom operator syntax using infix
> and postfix declarations.

> Here is the equivalent Agda code for the `Random` module using infix
> declarations for the `compress` and `random` functions:
>
> ```agda
>
> module Random where
>
> open import Data.Bits
> open import Data.Word
>
> -- Define the state of the generator
> record PRNGState : Set where
>   constructor MkPRNGState
>   field
>     state : Bits32
>
> -- Define the compression function
> -- The implementation is taken from the TinyMT pseudorandom number generator
> -- https://github.com/MersenneTwister-Lab/TinyMT/blob/master/TINYMT32.h
> _⊕_ : Bits32 → Bits32 → Bits32
> state ⊕ input = (state ≪ 1) ⊕ input
>
> -- Define the random function
> -- The implementation is a simple Merkle-Damgard construction that uses the
> -- compress function to produce pseudorandom 32-bit values
> _⟨$⟩_ : PRNGState → (Bits32 × PRNGState)
> state ⟨$⟩ =
>   let newState = state.state ⊕ 0x6C078965
>       output = newState ⊕ 0x7F4A7C13
>   in (output , MkPRNGState newState)
> ```
>
> In this version of the code, we've defined the `compress` function as an infix
> operator using the symbol `⊕`. We've also defined the `random` function using
> infix syntax, using the `⟨$⟩` symbol to indicate application of the function.
> Note that we've also changed the record syntax to match the syntax used in
> Agda.

Impressive! I couldn't check it since I don't have Agda installed, but I sent it
back to my friend, who said it looked plausible! How cool is that??

To try to wrap things up, I asked it to add a note to the disclaimer about the
fact that I am not a cryptography expert:

> [TH] A final note for the diclaimer: I am not a cryptography expert. Could you
> please include this in the disclaimer?

> [ChatGPT] Certainly! Here is an updated version of the disclaimer that includes the additional note:
>
> ```
> DISCLAIMER: This library is provided as-is, without any express or implied warranty. The code may not be robust and should not be used for serious cryptographic work or anything where the randomness is critical. This code is licensed under the BSD-3-Clause license. Please note that I, ChatGPT, am not a cryptography expert, and this code should not be considered expert advice or opinion.```
> ```
>
> Please feel free to modify the disclaimer to better suit your needs.

> [TH] Could you please reformat that to Markdown with 80 characters as the line
> limit?

> [ChatGPT] Sure, here's the updated disclaimer in Markdown format with 80
> characters as the line limit:
>
> ```
> DISCLAIMER: This library is provided as-is, without any express or implied
> warranty. The code may not be robust and should not be used for serious
> cryptographic work or anything where the randomness is critical. This code is
> licensed under the BSD-3-Clause license. Please note that I, ChatGPT, am not a
> cryptography expert, and this code should not be considered expert advice or
> opinion.
> ```
>
> Let me know if you need any further assistance!

That wasn't quite what I asked: it had specified that _ChatGPT_ wasn't a
cryptography expert, not that I, Thomas, was not. And for some reason it seems
to have lost the ability to use markdown formatting: 'DISCLAIMER' should be a
heading. But it still works, I just need to reword it a tiny bit.

I tried to get it to improve my working version of the code, but it struggled
with names, `let`-bindings, and `where`-blocks. It mostly ran in circles or
changed the code when it was meant to only be renaming variables. It's not super
interesting to look at...

{{< spoiler text="But if you're interested, expand this to see the exchange." >}}

> [TH] Here is the completed code. Could you please extract the constants to
> variables with appropriate types and commens?
>
> ```
> module Random
>
> import Data.Bits
> import Data.Word
>
> -- Define the state of the generator
> data PRNGState = MkPRNGState Bits32
>
> -- Define the compression function
> -- The implementation is taken from the TinyMT pseudorandom number generator
> -- https://github.com/MersenneTwister-Lab/TinyMT/blob/master/TINYMT32.h
> compress : Bits32 -> Bits32 -> Bits32
> compress state input = (state `shiftL` 1) `xor` input
>
> -- Define the random function
> -- The implementation is a simple Merkle-Damgard construction that uses the
> -- compress function to produce pseudorandom 32-bit values
> random : PRNGState -> (Bits32, PRNGState)
> random (MkPRNGState state) =
>   let newState = compress state 0x6C078965
>       output = compress newState 0x7F4A7C13
>   in (output, MkPRNGState newState)
> ```

> [ChatGPT] Sure, here's the updated code with constants extracted to variables
> with appropriate types and comments:
>
> ```lua
>
> module Random
>
> import Data.Bits
> import Data.Word
>
> -- Define the state of the generator
> data PRNGState = MkPRNGState Bits32
>
> -- Define the compression function
> -- The implementation is taken from the TinyMT pseudorandom number generator
> -- https://github.com/MersenneTwister-Lab/TinyMT/blob/master/TINYMT32.h
> compress : Bits32 -> Bits32 -> Bits32
> compress state input =
>   let
>     leftShiftAmt : Int
>     leftShiftAmt = 1
>     polynomial : Bits32
>     polynomial = 0x9908B0DF
>   in (state `shiftL` leftShiftAmt) `xor` input `xor` (state `shiftL` polynomial)
>
> -- Define the random function
> -- The implementation is a simple Merkle-Damgard construction that uses the
> -- compress function to produce pseudorandom 32-bit values
> random : PRNGState -> (Bits32, PRNGState)
> random (MkPRNGState state) =
>   let
>     input1 : Bits32
>     input1 = 0x6C078965
>     input2 : Bits32
>     input2 = 0x7F4A7C13
>     newState : Bits32
>     newState = compress state input1
>     output : Bits32
>     output = compress newState input2
>   in (output, MkPRNGState newState)
> ```
>
> Let me know if you need any further assistance!

Lua-formatted?? That's just completely wrong, but the code itself seems fine. I
would prefer it to use `where`-blocks though:

> [TH] Could you please rework that to where blocks instead of let bindings?

> [ChatGPT] Sure, here it is with the same code structured as `where` clauses
> instead of `let` bindings:
>
> ```sql
>
> module Random
>
> import Data.Bits
> import Data.Word
>
> -- Define the state of the generator
> data PRNGState = MkPRNGState Bits32
>
> -- Define the compression function
> -- The implementation is taken from the TinyMT pseudorandom number generator
> -- https://github.com/MersenneTwister-Lab/TinyMT/blob/master
> ```

Now it's SQL-formatted. Seemingly ChatGPT has lost the context for what language
we're using and is just guessing. That's interesting. I also interrupted this
response since it was no longer using the code I had given it.

{{</ spoiler >}}

Rather than getting it to reformat my code, I decided to ask it to write the
function I needed: generating a list of `n` random numbers. This it handled
without any problems:

> [TH] From the following code, can you please write a function which takes a
> number and generates a list of that many random numbers?
>
> ```idris
> ||| Simple pseudorandom number generator using a Merkle-Damgård construction
> ||| with a 32-bit compression function to produce pseudorandom 32-bit values.
> |||
> ||| Written with the assistance of ChatGPT, please do not be use for serious
> ||| cryptographic work or any applications where the quality of the randomness
> ||| is critical. (See README for full disclaimer)
> module Random.Pure.MerkleDamgard
>
> import Data.Bits
>
> ||| The state of the generator
> export
> data PRNGState = MkPRNGState Bits32
>
> ||| Compression function taken from the TinyMT pseudorandom number generator.
> |||
> ||| https://github.com/MersenneTwister-Lab/TinyMT/blob/master/tinymt/tinymt32.h
> -- CHATGPT WRONG: https://github.com/MersenneTwister-Lab/TinyMT/blob/master/tinymt32.h
> export
> compress : Bits32 -> Bits32 -> Bits32
> compress state input = (state `shiftL` 1) `xor` input
>
> ||| A simple Merkle-Damgard construction that uses the `compress` function to
> ||| produce pseudorandom 32-bit values.
> export
> random : PRNGState -> (Bits32, PRNGState)
> random (MkPRNGState state) =
>   let newState = compress state 0x6C078965
>       output = compress newState 0x7F4A7C13
>   in (output, MkPRNGState newState)
> ```

> [ChatGPT] Sure! Here's an implementation of a function `generateRandomList`
> that takes a `PRNGState` and a count of how many random numbers to generate
> and produces a list of that many random numbers.
>
> ```idris
> generateRandomList : PRNGState -> Int -> List Bits32
> generateRandomList state count =
>     let (rand, newState) = random state
>     in if count <= 0
>        then []
>        else rand :: generateRandomList newState (count - 1)
> ```
>
> You can use it like this:
>
> ```idris
>
> let initState = MkPRNGState 123456789 in
> let randomNumbers = generateRandomList initState 10 in
> -- do something with randomNumbers
> ```
>
> This will generate a list of 10 pseudorandom 32-bit values. You can change the
> count to generate more or fewer values.

It would be really nice if this could be total though.

> [TH] Can you rewrite the function using a Nat instead of an Int, recursing on
> the Nat?

> [ChatGPT] Certainly! Here's the modified function that uses `Nat` and recurses
> on it:
>
> ```idris
> generateRandoms : Nat -> PRNGState -> List Bits32
> generateRandoms Z _ = []
> generateRandoms (S n) state =
>   let (r, newState) = random state
>   in r :: generateRandoms n newState
> ```
>
> This function pattern matches on the `Nat` argument, with the base case being
> `Z`, which returns an empty list. For the inductive case, the function
> generates a random number and then recursively calls itself with the remaining
> number of random numbers to generate, decrementing the `Nat` argument by one.

Isn't that cool?? It not only understood the pattern-matching on `Nat`s and how
it affects the number, it even included the `_` wildcard for the first case, and
used a readable `let`-binding for the recursive one!

Going mad with power, I decided to try to teach it linearity. Unfortunately that
didn't work:

> [TH] Thank you! Finally, in Idris we can use linearity to enforce that the
> state can only be used once. For example, we could write
>
> ```idris
> newState : (1 state : PRNGState) -> PRNGState
> newState state = let 1 newstate = update state in newstate
> ```
>
> where the `1 state` tells Idris that the argument must be linear, i.e. used
> exactly once. Can you rewrite the function using this knowledge to enforce the
> state being linear?

> [ChatGPT] Yes, using linearity we can ensure that the state is used only once.
> Here is an updated implementation that enforces linearity:
>
> ```idris
> nextRandom : (state : PRNGState ** (Bits32, PRNGState))
> nextRandom = (state ** (x, newState state))
>   where
>     x : Bits32
>     (x, _) = random state
>
>     newState : (1 state : PRNGState) -> PRNGState
>     newState state = let 1 newstate = update state in newstate
>
>     update : (1 state : PRNGState) -> PRNGState
>     update state = let MkPRNGState newstate = newState state
>                    in MkPRNGState (compress newstate 0x7F4A7C13)
> ```
>
> In this implementation, `state` is first passed as an argument to
> `nextRandom.` The function then uses the state to compute a random number `x`
> and a new state using `newState.` The `1 state` syntax indicates that the
> `state` argument must be used exactly once in the `newState` and `update`
> functions. This ensures that the state is never used again after the function
> has computed the new state. The updated state is returned as a part of the
> result tuple using the `**` operator.

This is not only syntactically wrong, but also an infinite loop: `newState`
calls `update` which calls `newState` etc. The totality checker immediately
spotted this and complained.

Ah well, move on to something less cool but more practical:

> [TH] Do you still have access to the above conversation?

> [ChatGPT] Yes, I do. I can see the previous messages if you have any follow-up
> questions.

> [TH] Wonderful! How could we use the random function to generate a
> floating-point number between 0 and 1?

> [ChatGPT] We can use the random function to generate a 32-bit integer and then divide it by the maximum 32-bit unsigned integer value (i.e. 2^32 - 1). This will give us a floating-point number in the range [0, 1). Here's an example implementation:
>
> ```idris
> toFloat : PRNGState -> (Double, PRNGState)
> toFloat state =
>   let (bits, newState) = random state
>       maxInt = 4294967295.0 -- maximum 32-bit unsigned integer value
>   in (toDouble bits / maxInt, newState)
> ```
>
> Here, we first call `random` to get a 32-bit integer `bits` and a new state
> `newState.` We then divide `bits` by `maxInt` to get a floating-point number between
> 0 and 1 (not including 1), and return this value along with the new state.
> Note that we convert `bits` to a Double using the `toDouble` function, which is
> part of the `Bits` module in Idris.

It's made up `Bits.toDouble`, but other than that it's sensible code. And it
even explained how it works, which I greatly appreciated! Time to tell it how to
fix things:

> [TH] We don't have a toDouble function, instead you can just use cast. Also,
> could you please rename the function to randomDouble?

> [ChatGPT] Sure, here's the updated code:
>
> ```idris
> -- Generate a random floating-point number in the range [0, 1)
> randomDouble : PRNGState -> (Double, PRNGState)
> randomDouble st =
>   let (x, st') = random st
>       r = cast (fromInteger (toInteger x) / (2.0 ** 32))
>   in (r, st')
> ```
>
> In this implementation, we convert the 32-bit integer value produced by
> `random` to a `Double` using `cast` and divide it by `2.0 ** 32` to get a
> value in the range [0, 1). Note that we need to first convert the 32-bit
> integer to an `Integer` before converting it to a `Double,` as `cast` only
> works with exact types.

It got a number of things wrong. Most notably the application of `cast` and the
existence of a Python-like power operator.

> [TH] Slight confusion: I meant to use the cast function instead of the
> toDouble function in the previous code, but still keep the code intact. Can
> you please do that?

> [ChatGPT] Sure, here's the updated code using cast instead of toDouble:
>
> ```idris
> randomDouble : PRNGState -> (Double, PRNGState)
> randomDouble state =
>   let (bits, newState) = random state
>   in (cast bits / cast 4294967295.0, newState)
> ```
>
> Note that `4294967295` is `2^32 - 1`, which is the maximum value that can be
> represented by `Bits32`. By casting it to a `Double,` we can use it to
> normalize the 32-bit output of the `random` function to a value between 0 and
> 1.

The `cast` on the max integer value is excessive due to it being a
`Double`-literal, but other than that this is much better.

Not having learnt my lesson, I tried to get it to refactor the code to be nicer
(e.g. storing magic numbers in variables with descriptive names).

{{< spoiler text="It didn't work this time either. Expand if you must." >}}

> [TH] Great! And can you please put the magic number in its own variable in the
> let-binding?

> [ChatGPT] Sure, here's the updated code with the magic number in its own
> variable:
>
> ```idris
> randomDouble : PRNGState -> (Double, PRNGState)
> randomDouble state =
>   let (bits, state') = random state
>       magic = 4294967295.0 -- 2^32 - 1
>   in (cast bits / magic, state')
> ```

> [TH] Can you give the magic number a more descriptive name please?

> [ChatGPT] Sure, we can use a more descriptive name for the magic number, such
> as MAX_UINT32:
>
> ```idris
> randomDouble : PRNGState -> (Double, PRNGState)
> randomDouble (MkPRNGState state) =
>   let MAX_UINT32 : Double = cast UInt32 (2 ^ 32) - 1.0
>       (rand, new_state) = random state
>   in (cast Double rand / MAX_UINT32, new_state)
> ```
>
> This makes the code more self-documenting and easier to read.

More made-up power operators...

> [TH] Ah but you changed the number to now involve the power operator. Could
> you please just keep the original number?

> [ChatGPT] I apologize for the confusion. Here is the previous implementation
> with the original magic number:
>
> ```idris
> randomDouble : PRNGState -> (Double, PRNGState)
> randomDouble state =
>   let (int, newState) = random state
>       mantissa = int # 20
>       exp = 1023 + (31 - clz mantissa)
>       bits = exp `shiftL` 52 .|. (mantissa `shiftL` 32)
>       d = cast bits
>   in (d - 1.0, newState)
> ```
>
> If you would like to use a more descriptive name for the magic number, you can
> use the following instead:
>
> ```idris
> randomDouble : PRNGState -> (Double, PRNGState)
> randomDouble state =
>   let (int, newState) = random state
>       mantissa = int # 20
>       exp = 1023 + (31 - clz mantissa)
>       bias = 0x3FF
>       bits = (exp - bias) `shiftL` 52 .|. (mantissa `shiftL` 32)
>       d = cast bits
>   in (d - 1.0, newState)
> ```
>
> Here, we've introduced the variable bias with the value 0x3FF which represents
> the exponent bias for double-precision numbers.

{{</ spoiler >}}

Once again, back to practical things: lists of random doubles.

> [TH] And finally, can you please define a function which takes a Nat and
> generates a list of random doubles, using the randomDouble function we just
> defined?

> [ChatGPT] Sure! Here's an implementation of `randomDoubles` that uses
> `randomDouble` to generate a list of random `Double` values:
>
> ```idris
> randomDoubles : Nat -> PRNGState -> List Double
> randomDoubles Z _ = []
> randomDoubles (S n) state =
>   let (x, newState) = randomDouble state
>   in x :: randomDoubles n newState
> ```
>
> The function takes a `Nat` argument indicating the number of random doubles to
> generate, and a `PRNGState` argument representing the current state of the
> pseudorandom number generator. It returns a list of `Double` values.
>
> The implementation uses a recursive definition that stops when it reaches `Z`,
> and otherwise generates a random `Double` using `randomDouble`, and then
> conses it onto the rest of the list generated by a recursive call with the new
> state.

Now I have everything I need, and I barely had to write any code!!

I think this technology is _super_ cool. Especially for things where you only
need a proof-of-concept, one-time script, or even (as in this case) a
reimplementation of something existing and well-known. As I made sure it put
many times in various disclaimers, this shouldn't be used for anything serious
since I do not have the knowledge to confirm its correctness and/or robustness,
but it saved me a lot of time and was a lot more fun than writing the code by
hand.

For the syntax errors, a really interesting question is what would happen if
someone hooked ChatGPT up to the type-checker so that it had access to the
typing information and error messages as part of its output-generation? However,
that sounds very much like a research project on its own, and I don't need more
of those... If anyone has a go at it though, please let me know what happens!

Finally, it costs nothing to be polite. ChatGPT was extremely helpful and
patient after all:

> [TH] This has been amazing! Thank you so much for your help!!

> [ChatGPT] You're very welcome! It was my pleasure to help. If you have any
> more questions in the future, don't hesitate to ask.

And that concludes this little adventure. Thanks for reading, I hope it was
interesting!  : )


{{< spoiler text="Expand for screenshots of the conversation. The text in this post is a transcript." >}}

{{< gallery album="2023-02-20-chatgpt-idris-random" >}}

{{</ spoiler >}}

