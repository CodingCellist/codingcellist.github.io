---
# Documentation: https://wowchemy.com/docs/managing-content/

title: "A month of Zen"
subtitle: ""
summary: "I finally got around to configuring my tiny Corne-ish Zen r3 keyboard.
          This is a discussion of the advantages, challenges, ease-of-use, etc.
          of using a 40-key split keyboard. It's definitely portable and very
          useable, but it's not all great."
authors: [thomas-e-hansen]
tags: [keyboards, ergonomics, zmk]
categories: []
date: 2023-02-17
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

## You cannot buy this keyboard

Let's get the important, unfortunate, and boring fact out of the way to begin
with: you cannot buy this keyboard. It was a group-buy (a sort of crowdfunding),
which finished months ago, and Darryl, the inventor/maker of the Corne-ish Zen
boards has stated that he wishes to move on to other things. So unless you find
one on the second-hand market, you can unfortunately not buy this keyboard.

And this is really a shame, because the board is pretty great; especially if
you're on the go a lot!


## General overview

The first thing I noticed was that this board is _tiny_. I knew it was a
low-profile 40-key keyboard, but I was still surprised at just how small it is!
Each side has 3 rows of 6 keys, arranged in a column-staggered layout, as well
as 3 thumb-keys, which are arranged in a small arc.

TODO: picture with dimensions

The keyboard came in a nice carrying case, which is superb for taking it with
you to work, cafés, or whatnot, and it takes up less space than the case my Bose
QC-25s came in. Each half of the keyboard also has its own little protective
fabric bag, making the product feel extremely premium and thought-through.

TODO: picture of the case and pouches

With the case, the mass to carry is 406 grams. Total! Each side weighs only
around 138 grams, which is super impressive considering that there is a PCB and
a decent amount of solder in there (every solder-point is a little sphere of
metal).

And of course, the colour is really pretty. I went for the blue anodised edition
and it looks super nice, especially when paired with black keycaps.

TODO: another picture of the board


## Configuration

As you might have guessed, configuration is a huge part of making a keyboard
this small useable at all. There are no number keys or function keys, and things
like space, shift, escape, and enter/return are somewhere on the thumb-keys.

### Layers

This means you need to use _layers_. Layers can seem like a foreign concept at
first, but they quickly become intuitive: on your current keyboard, you likely
have at least 1, maybe 2, layers! When you need to type upper-case letters, you
hold down the 'Shift' key, thereby changing _layers_ to one where the keys on
the keyboard now output their upper-case versions. And if you have a laptop,
chances are that the function keys work as either function keys or media keys
(i.e. volume, brightness, etc.) depending on whether you hold down a 'Fn' key or
not. This is also a separate layer, just one which doesn't affect most of the
other keys on the keyboard.

So you've actually been using keyboards since you started using a computer. You
just likely didn't know that was what they were called  : )

### Layout

TODO

The keyboard comes with a default layout out-of-the-box (ootb), but it is a US
layout with numbers on one layer, and Bluetooth configuration on a second one.
This is problematic for two reasons: 1) I type in languages other than English,
and so need access to things like accents, more letters (e.g. 'ø'), etc. and 2)
I have no idea where symbols are on a US/ANSI layout. For example, on a Danish
layout (which is what I'm used to), ':' is typed by pressing `Shift`+`.` and ';'
is typed by pressing `Shift`+`,`.

