---
# Documentation: https://wowchemy.com/docs/managing-content/

title: "Writing Up a PhD"
subtitle: "A log of the train wreck to come"
summary: ""
authors: [thomas-e-hansen]
tags: [misc, phd, academia]
categories: [seed]
date: 2024-01-16
lastmod: 2024-03-08
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

I am coming up on the end of my allotted time for my PhD and need to write up.
There is little content of this follow-along-journal-kind out there (as far as I
know), so I thought it might be interesting to document, if nothing else for
myself to look back over someday. I'll update this from time to time, either
when something big happens or changes, or when I feel I should add a bit
(probably around once per week). Fair warning: this will likely become rambling
and incohesive as the stress increases, and for this I ask you to please be
understanding.

Welcome to the slow-motion train wreck! Enjoy!


## 2024-01-15

* Supervisor meeting with details for what next
* Not to worry about not having published. That will come with the write-up
    (hopefully).
* Need to get my example working with sequences of operations, but then I'm
    good!
* And then I can start writing.
* Speaking of: we put together a rough plan for what chapters there will be
  - "Hey, I think we're actually gonna make it!"

![Photo of a notebook page reading "Thesis layout", with a list of chapters](/phd-writeup/00-thesis-layout.jpg)


## 2024-02-21

Wow! A lot of time has passed since the last update. I keep meaning to write,
but was either too exhausted or had other evening commitments; such is life
sometimes. Anyway!

The weeks immediately after the previous update (2024-01-05) were an emotional
roller-coaster: I spent 2 weeks trying to solve a problem with my core idea. I
needed to make it recursive, but the type checker seemed to stall on the final
bit where the recursion actually happened.

The solution suddenly came to me and I face-palmed: I was using auto-implicit
syntax (`@{...}`) for an implicit argument (which uses `{...}`). ONE SYMBOL!
Having celebrated that it all now reloaded fine, I went off to teach, came back,
only to discover that Vim had not highlighted my code correctly due to the
code-block being bigger than the screen... I never fixed anything; the block was
not commented in. That's why it was all fine. And surprise surprise, commenting
things in didn't magically fix things. My commit from then reads:

> Author: Thomas E. Hansen <email>
> Date:   Tue Jan 30 17:59:53 2024 +0000
>
>     [ ATMSt ] I tried so hard, and got so far
>
>     But in the end, it doesn't even matter
>     (Or at least, not if you forget to comment the block you're modifying
>     back in -_-). I really thought I'd done it...

Back to the drawing board... At least I had my supervisor meeting the next day
and could ask then.

At the meeting we sat down to discuss this, my supervisor had a go and realised
"huh, I see... this is trickier than I thought" (you don't say ^^). 40 minutes
of joint poking and debugging later though, we'd done it!

> Author: Thomas E. Hansen <email>
> Date:   Wed Jan 31 18:39:34 2024 +0000
>
>     [ ATMSt ] IT FINALLY WORKS!!!

The day before my birthday as well! The amount of relief I felt now that this
was finally working can only be described as immense; I now, after all these
years, had a _working_ proof of concept which showed that my idea was sound and
that a solution could be implemented.

* Rewrote code from meeting to be nicer
* And also played with it to check that implementation wasn't doing anything
    silly and still obeyed the same rules as the original theory.
* Tidied the trace to not include the initial state. Led to some fun oddities
    due to when PRNG was happening.
* Made a note on my whiteboard saying to write ~100 words per day initially
    (Edwin's suggestion --- "can't edit what isn't written")
* Eventually managed to actually write ~100 words  ^^;;
* Ported one of my blog-post-style documents on generating arbitrary `Vect`
    instances into LaTeX as part of my thesis. It's free ~~real estate~~ word
    count increase.
* Writing is slow to get started, but then it gets going. So far, still not at
    ~100 words / day, things keep coming up (and writing emails takes an
    unreasonable amount of time.)
* Need to write a talk for SPLS in March. February is surprisingly short
    suddenly.


## 2024-02-26

* Not much thesis writing going on bc. I foolishly agreed to give a talk at a
    seminar on the 6th of March
  - Which is coming along much faster than I expected!
* Otoh, I have discovered some really neat ways Idris2 can help with what I'm
    doing, which is cool
  - `failing` can take a (sub)string of an error message to match, catching when
      you fail bc. of a typo or mismatched arg.s rather than the error you were
      trying to demo.
* Also discovered a misconfiguration in a test I'd written, showing that my
    PhD's approach helps me write my PhD showcase itself  ^^


## 2024-03-08

Managed to give my talk at the seminar earlier this week, which was really good.
I ended up working on the slides until 8 minutes before the seminar was
starting, because I suddenly also had to update the website and schedule, but it
all worked out.

It is always interesting to see what people are working on, and there were a
great many number of interesting talks. Simon Gay gave a talk on train tracks
and dependent types which, as anything involving trains does now, made me go
"Oooh! Can we do fun Factorio-like things with this?". It was also really nice
and validating to have people come up to me during the coffee break and mention
that they were doing similar things in industry, but worse, due to the lack of
dependent types. Or that they had some ideas for how I could generalise it. One
person came up to me in the pub after the seminar and said that it was the best
introduction to dependent types they'd seen and that they were really interested
now, so that was really awesome to hear. All the more reason to give these talks
I guess  : )

Now it is time to get back to writing. On the bright side, the talk from the
seminar should definitely be portable into a part of my thesis. On the less
bright side, I need to actually write out the content from it, I can't just
speak it.

Oh and I want to get some info-vis-like progress meter going for my word count.
So that's what I'm procrastinating with right now  ^^

