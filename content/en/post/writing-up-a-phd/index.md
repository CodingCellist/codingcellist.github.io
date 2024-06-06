---
# Documentation: https://wowchemy.com/docs/managing-content/

title: "Writing Up a PhD"
subtitle: "A log of the train wreck to come"
summary: ""
authors: [thomas-e-hansen]
tags: [misc, phd, academia]
categories: [sapling]
date: 2024-01-16
lastmod: 2024-03-18
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

{{< chart data="wcount-plot" >}}

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


## 2024-03-18

I've spent the past however many days (10 according to this changelog, aaaah!)
working on a little automatic word-count plot for the top of this page. That way
I can point people at that whenever they ask me how things are going  : P

Not the best in terms of actually making progress, but very good in terms of fun
(and learning new tools? no no: growing my skillset; yes, that sounds much
better)

It took a bit of work to get going, and because I'd rather do pretty much
_anything_ other than writing my thesis, the details of that are up (in rough
form) in this other blog post:
[auto-plotting-thesis-word-count](/en/post/auto-plotting-thesis-word-count/)

I even managed to get some writing done! From the talk I gave about 2 weeks ago,
but now in more written form. I am still just jotting things down informally and
in bullet-points; "easier to edit and expand something actually written" and all
that. As part of that, I vaguely remembered hearing LaTeX had neat glossary
support, and looked into that. It _is_ pretty nice, not gonna lie, and not even
that troublesome to set up (as LaTeX things go). But my enjoyment from it --
being able to use a little macro whenever I wanted to refer to a glossary term
and/or its definition -- did again remind me that LaTeX was written by
programmers for programmers to some extent; good luck convincing a regular user
this is better than chords in MS Word or however that program does it.

Oh and according to the script, there are about 400-500 words more in my thesis
now (no clue if that includes glossary items), so that's pretty neat! And I'll
be even happier to see the line go up tonight  ^^


## 2024-04-03

I got an email last week saying that my "continuation period" was now starting
and that, as such, I would no longer be receiving any funding. My first reaction
was "What??" -- I thought I had another month before that happened -- but
unfortunately the admin office was able to confirm that we were indeed 6 months
off September (which is when the University actually, properly come breathing
down my neck) and my funding was 3.5 years, so it all added up. My supervisor is
currently writing a grant application but doesn't have an active grant, and it
is the end of teaching. So now I'm burning savings, yaaay...

Oh well, as my supervisor so nicely put it: "Well, better get writing then" (to
be clear: this was done in good humour, and I did/do find the comment funny).

Even with that said, finding motivation to write can be hard. Or rather, it is
very easy to spend the morning writing emails and helping people out on the
various discords I'm in, going for lunch, and then spending the afternoon going
"I really should be writing" whilst simultaneously not getting any actual
writing done. The graph is doing its job though: looming over me and publicly
shaming the (lack of) work I've been doing.

Anyhow, I did manage to eventually get some writing done today -- doubly
frustrating is that once I get going, it just all comes flowing -- thanks to a
notebook from 2 years ago which not only has implementation details and
explanations (thank you, past me) but _also_ has a summary/birds-eye-view at the
end of the section detailing how it all ties together (THANK YOU, past me!).

This, in combination with finding some early-2000s pop and pop-punk music to put
on in the background, resulted in me sort of just happily vibing along and
writing. Which surprised me somewhat, as I can normally not write anything while
listening to stuff with lyrics: either the lyrics end up sneaking into the
current sentence, or I end up just listening to the music. However, for mostly
just transferring stuff I've already written from one medium to another, it
seems to work (or at least it did today).

Also apparently I'm giving a talk tomorrow. But it is meant to be a technical
one, going over implementation details, so I might just walk through the code
live as the talk; won't be the first time somebody does that at a PL
(Programming Languages) Group session ^^;;


## 2024-06-06

Where have I been the past 2 months? I've been
[writing a TyDe'24 paper](/en/post/tyde-24-paper)! Which was very exciting but
also extremely tiring. But I am quite happy with it, and according to a quick
`texcount`, it should net me ~16k extra words on the graph (when I eventually
add it in), which is _definitely_ worth it  : )

Today I restart trying to write up parts of my thesis which I did roughly 2
years ago. Once again: thank goodness for notebooks. Even with them though,
it'll still be work to retrace my steps. Oh well, I'm sure it'll come faster and
faster the more I work through it.

I also had a look over the _tiny_ thesis outline and drafting I'd done so far in
my main thesis repo. I guess the good news are that I am beginning to see how
the chapters need merging, changing, what needs to go where, etc. But the bad
news are that my first thought to all the old stuff that was there was "Christ!
It all needs rewriting!" To be fair, it is bullet-point stuff I wrote for a
PhD-review over a year ago, so I would be somewhat surprised if I didn't have a
better grasp on things now. Well, time to get to it I guess...

Oh and I'm trying out a new pomodoro-style thing called "Plantie" -- you grow
virtual trees or fruit or something during the time slots. Very cute. I've
always been highly sceptical of the pomodoro technique -- something about
maintaining "flow" and all that -- but a friend said it really helped for
larger, marathon-like tasks. Which writing up a huge chunk of work from two
years ago happens to be. So I'm giving it a shot. I can see the wisdom in taking
frequent breaks for those kinds of tasks, and hey, worst case I just uninstall
the app and still have some amount of work done. Seems worth a try.

