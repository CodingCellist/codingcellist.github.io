---
# Documentation: https://wowchemy.com/docs/managing-content/

title: "A month of Zen"
subtitle: ""
summary: "I finally got around to configuring my tiny Corne-ish Zen r3 keyboard.
          This is a discussion of the advantages, challenges, ease-of-use, etc.
          of using a 42-key split keyboard. It's definitely portable and very
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

The Corne-ish Zen is a small, 42-key wireless split keyboard. It uses the
[ZMK firmware](https://zmk.dev),
which means, for better and for worse, that it is extremely customisable once
you've learnt how to configure it. And you _need_ all that configuration: with
42 keys including thumbkeys, both the function and number rows are gone. So how
does that work? How do you manage without? And is it actually practical to use
such a small keyboard for everyday work? I've been using mine everyday for the
past month or so in order to find out. It's been really fun and interesting!


## You cannot buy this keyboard

Let's get the important, unfortunate, and boring fact out of the way to begin
with: you cannot buy this keyboard. It was a group-buy (a sort of crowdfunding),
which finished months ago, and Darryl, the inventor/maker of the Corne-ish Zen
boards has stated that he wishes to move on to other things. So unless you find
one on the second-hand market, you unfortunately cannot buy this keyboard.

And that is really a shame, because the board is pretty great; especially if
you're on the go a lot!


## General overview

The first thing I noticed was that this keyboard is _tiny_. I knew it was a
low-profile 42-key compact thingy, but I was still surprised at just how small
it is! It came in a nice carrying case (superb for taking it with you to work,
cafés, or whatnot) and even with the case it takes up less space than the case
for my Bose QC-25s:

TODO: picture (album?) of the cases -iCloud

Each half of the keyboard also has its own little protective fabric bag, making
the product feel extremely premium and thought-through:

TODO: picture of the pouches -iCloud

In terms of the keyboard itself, each side has 3 rows of 6 keys, arranged in a
column-staggered layout, as well as 3 thumb-keys, which are arranged in a small
arc. The case is made of machined aluminium, which both feels and looks amazing.
I went for the blue anodised edition and it looks very nice, especially when
paired with black keycaps:

TODO: picture of the board -iCloud

And just because I was curious, I decided to weigh the board. With the case, the
mass is 406 grams. Total! Each side weighs only around 138 grams, which is super
impressive considering that there is a PCB and a decent amount of solder in
there (every solder-point is a little sphere of metal, and metal is dense).

TODO: picture with scale -TODO!!


## Configuration

As I mentioned at the start, configuration is a huge part of making a keyboard
this small useable. There are no number keys or function keys, and things like
space, `Shift`, `Escape`, and enter/return are somewhere on the thumb-keys. This
means you need to use _layers_.

### Layers?

Layers can seem like a foreign concept at first, but I've found they quickly
become intuitive. On your current keyboard, you likely have at least 1, maybe 2,
layers: when you need to type upper-case letters, you hold down the `Shift` key,
thereby changing _layers_ to one where the keys on the keyboard now output their
upper-case versions. And if you have a laptop, chances are that the function
keys work as either function keys or media keys (volume, brightness, etc.)
depending on whether you hold down a `Fn` key or not. This is also a separate
layer, just one which doesn't affect most of the other keys on the keyboard.

So chances are you already use layers on a daily basis when interacting with a
computer, you just didn't know this functionality had a name  : )

### Layout

The keyboard comes with a default layout out-of-the-box (ootb), but it is a US
layout with numbers on one layer, and Bluetooth configuration on a second one.
This is slightly problematic because the layout I am used to is Danish, which
means I have no idea where symbols are on a US/ANSI layout. For example, on a
Danish layout, ':' is typed by pressing `Shift`+'.' and ';' is typed by pressing
`Shift`+','. So the first thing to do was to work out some layouts and layers
which would (hopefully) make sense to me.

<!-- TODO: move to a different blog post, if discuss at all?
I first encountered thumbkeys via the
[Dygma Raise](https://dygma.com/products/dygma-raise)
keyboard and have been a complete convict ever since. Once you get over the
initial learning bump, using your two strongest fingers for more than just the
spacebar is fantastic! As such, I wanted to move most functionality to the
thumb-keys.

It seemed sensible to have the default layer, which is the one the keyboard uses
when you turn it on, be the QWERTY-layer. To not have to re-learn too many
things, I tried keeping most functionality roughly where I would expect it to
be: `Alt` and `Ctrl` are on the left side; and `AltGr` and space are on the
right (I almost exclusively type space with my right thumb). Next, a bit of
layer trickery and thumbkey use: the leftmost thumbkey (the hardest to reach for
me) was assigned to "next layer" and "previous layer" (more on this in a second)
since that is functionality I will always deliberately be seeking out and so
I wanted it somewhere Some other parts
were transferred from my Raise layout: the large left thumb-key was assigned to
`Shift` and Windows (aka. Super or GUI), and the large right thumb-key was
assigned to return and right-`Ctrl`.
-->

What I ended up with was a default layer containing the QWERTY keys, along with
some tap-dances for switching layers and some symbols I wanted more easily
accessible, and mod-taps for things like `Esc`/`Ctrl`, space/`AltGr`, etc. I
also created a layer-tap for backspace and my function+number layer, since it is
a layer I often need to access. Which side to place the functionality on was
chosen based on a combination of where I would expect to find them (muscle
memory) and my current Dygma Raise layout:

![a visualisation of the QWERTY-layout](/media/zen-qwerty-layer.png)

The "function- and number-keys" layer took a bit more work. Not making
matters easier for myself, I have become used to the i3 tiling window manager,
meaning there is some extra functionality for moving between workspaces which I
thought it would be really nice to have on dedicated keys. After some
experimentation, I settled on a layout with the numbers on the home row (with
tap-dances for the respective function-keys), the i3 keys on the top row, and
the symbols I would normally type using `AltGr`+\<number\> on the bottom row:

![a visualisation of the FNum-layout](/media/zen-fnum-layer.png)

TODO

