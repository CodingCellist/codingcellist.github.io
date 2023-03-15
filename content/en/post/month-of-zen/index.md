---
# Documentation: https://wowchemy.com/docs/managing-content/

title: "A month of Zen"
subtitle: ""
summary: "I finally got around to configuring my tiny Corne-ish Zen r3 keyboard.
          This is a discussion of the advantages, challenges, ease-of-use, etc.
          of using a 42-key split keyboard. It's definitely portable and very
          useable, but there are some caveats."
authors: [thomas-e-hansen]
tags: [keyboards, ergonomics, zmk]
categories: []
date: 2023-02-17
lastmod:
featured: false
draft: false

# Album image descriptions
# Annoyingly, this doesn't support the `alt_text` field, so I'm using captions
# instead
gallery_item:
  - album: zen-case
    image: front.jpg
    caption: "An image of the Zen's carrying case lying flat next to a Bose
              case. The Zen's case is about 4 cm shorter."
  - album: zen-case
    image: side.jpg
    caption: "An image of the Zen's carrying case lying on its side next to a
              Bose case. The Zen's case is about 4 cm shorter."

  - album: zen-measured
    image: ruler-left.jpg
    caption: "An image of the right half of the Zen with a ruler lying to the
              left of it. There are green lines added to the image to help show
              the height being around 9.5cm."
  - album: zen-measured
    image: ruler-right.jpg
    caption: "An image of the right half of the Zen with a ruler lying to the
              right of it. There are green lines added to the image to help show
              the max height being around 9.5cm and the min height being around
              5.7cm."
  - album: zen-measured
    image: ruler-top.jpg
    caption: "An image of the right half of the Zen with a ruler lying above it.
              There are green lines added to the image to help show the length
              being around 13.7cm."
  - album: zen-measured
    image: ruler-under.jpg
    caption: "An image of the right half of the Zen with a ruler lying
              physically underneath it. Although the rounded edges and shadows
              make it difficult to see, the board seems to have a length of
              around 13.7cm."

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

{{< toc >}}

## You cannot buy this keyboard

Let's get the boring and unfortunate, but important disclaimer out of the way:
you cannot buy this keyboard. It was a group-buy (a sort of crowdfunding), which
finished almost a year ago, and Darryl, the inventor/maker of the Corne-ish Zen
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

{{< gallery album="zen-case" >}}
<br/>

Each half of the keyboard also has its own little protective fabric bag, making
the product feel extremely premium and thought-through:

![An image of two fabric pouches on a table. The pouches have a stylized "Corne-Ish Zen" printed on them.](/media/zen-pouch-horizontal.jpg)

In terms of the keyboard itself, each side has 3 rows of 6 keys, arranged in a
column-staggered layout, along with 3 thumb-keys, which are arranged in a small
arc. There is a little e-ink display for showing the battery level, Bluetooth
connection, and current layer. And the case is made of machined aluminium, which
both feels and looks amazing! I went for the blue anodised edition and it looks
very nice, especially when paired with black keycaps:

![An image of the two halves of the Zen keyboard. Each half is a mirror of the other.](/media/zen-deployed.jpg)

Roughly measured, the Zen's height, length, and width is around 9.5cm, 13.7cm,
and 1.9cm (1.4cm without keycaps) respectively.

{{< gallery album="zen-measured" >}}
<br/>

And just because I was curious, I decided to weigh the board. With the case, the
mass is 406 grams. Total! Each side weighs only around 138 grams, which is super
impressive considering that there is a PCB and a decent amount of solder in
there (every solder-point is a little sphere of metal, and metal is dense).


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

The keyboard comes with some default layouts configured out-of-the-box (ootb),
but it is a US layout with numbers on one layer, and Bluetooth configuration on
a second one. This is slightly problematic because the layout I am used to is
Danish, which means I have no idea where symbols are on a US/ANSI layout. For
example, on a Danish layout, ':' is typed by pressing `Shift`+'.' and ';' is
typed by pressing `Shift`+','. So the first thing to do was to work out some
layouts and layers which would (hopefully) make sense to me.

What I ended up with was a default layer containing the QWERTY keys, along with
some tap-dances for switching layers and some symbols I wanted more easily
accessible, and mod-taps for things like `Esc`/`Ctrl`, space/`AltGr`, etc. I
also created a layer-tap for backspace and my function+number layer, since it is
a layer I often need to access. Which side to place the functionality on was
chosen based on a combination of where I would expect to find them (muscle
memory) and my current Dygma Raise layout:

![A visualisation of the QWERTY-layer](/media/zen-qwerty-layer.png)

The "function- and number-keys" layer took a bit more work. Not making
matters easier for myself, I have become used to the i3 tiling window manager,
meaning there is some extra functionality for moving between workspaces which I
thought it would be really nice to have on dedicated keys. After some
experimentation, I settled on a layout with the numbers on the home row (with
tap-dances for the respective function-keys), the i3 keys on the top row, and
the symbols I would normally type using `AltGr`+\<number\> on the bottom row:

![A visualisation of the FNum-layer](/media/zen-fnum-layer.png)

Finally, since the Zen is a wireless Bluetooth keyboard, I needed a way to
control that. I decided to put the Bluetooth controls along the top row of my
third layer, in order to also make space for a media-and-navigation-keys hub on
the lower two rows. The "Clear Bluetooth" button was placed in the bottom left
to avoid accidental presses:

![A visualisation of the BTNav-layer](/media/zen-btnav-layer.png)

Configuring the Zen's layouts requires modifying the layout file used when
building its ZMK firmware and then flashing the new firmware to the keyboard
(Darryl has a
[video on how to](https://www.youtube.com/watch?v=ksDHHajTKoQ?t=725)).
It took me a bit of setting up and getting used to, but then it went okay. If
you are familiar with GitHub, GitHub Actions, and `git`, you'll be fine. If not,
ZMK _does_ provide an
[Initial Setup guide](https://zmk.dev/docs/user-setup),
which is pretty decent. _However,_ compared to something like Dygma or Kinesis,
where the configuration is done via a Graphical User Interface (GUI), it is a
_much_ higher barrier to entry. But hey, at least ZMK _can_ be configured and
_does_ work.

## Using the Zen

