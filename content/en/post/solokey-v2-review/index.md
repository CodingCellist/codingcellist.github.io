---
# Documentation: https://wowchemy.com/docs/managing-content/

title: "SoloKey v2 Review"
subtitle: ""
summary: "After numerous delays, production problems (thanks pandemic), and
          little communication on the Kickstarter page, my Solo v2 keys finally
          arrived. Overall, they were mostly worth the wait."     # TODO after article written
authors: [thomas-e-hansen]
tags: [review,hardware,oshw,u2f,solo2]        # TODO: think a bit about these
categories: []
date: 2022-11-21
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


{{< toc >}}


## Intro

SoloKey makes open-source and open-hardware security keys à la YubiKey, with the
latest iteration being the v2. I always think it is cool when people manage to
make open-source profitable, and had been looking to get security keys for a
while, so when the SoloKey v2 (aka. Solo v2) launched on Kickstarter, I was
eager to support it. It took a while to arrive but it seems to work well,
although the software is in its early stages and the documentation needs
improving.


## Kickstarter and shipping issues

The Kickstarter campaign was successfully funded in late February 2021, with an
estimated delivery window of April-June 2021. Now, delays are almost inevitable
with crowd-funded projects, especially ones launched during the pandemic (with
the shipping crisis, semiconductor shortage, etc.). Even so, I had almost given
up on ever receiving the keys.

There had been numerous set-backs and problems discovered, the most egregious
necessitating a redesign of the hardware and acquiring a new production machine
(which then later needed an add-on to solve a process bottleneck). It quickly
became clear that the original delivery window was unfeasible. And, to be fair,
SoloKey admitted this. Still, the delivery experience wasn't good.

I received an email with a shipping number from Leetronics (SoloKey's European
contractor) on the 19th of April 2022. I occasionally checked this, but there
were never any updates besides "we will receive a shipment and deliver it to
you". After a couple of months, I had completely forgotten about it, until I
suddenly got a package notification, around the _14th of October_ 2022. This was
5 months after the shipping number was created, 4 months after the
["we'll get to it by the end of June"-promise](https://www.kickstarter.com/projects/conorpatrick/solo-v2-safety-net-against-phishing/posts/3484043),
and just under 3 months after the
["it will be a few more weeks"-update](https://www.kickstarter.com/projects/conorpatrick/solo-v2-safety-net-against-phishing/posts/3561679).
I'm happy I got the keys and that they work, but the delivery experience was not
good, even for a Kickstarter project.

(There was never an update to the original shipping number by the way. It still
just says "The sender has announced that this item will be delivered to Deutsche
Post on April 19, 2022.", despite it being several months after delivery...)


## Packaging and Initial Impressions

Opening the parcel, the packing is very minimal. Each key is packed in a small
cardboard "envelope" that feels nice and seems sturdy enough to protect the
contents. Unfortunately, it is not the easiest to open: the perforation could be
better and I often ended up undoing the glue rather than the perforation, unless
I took care to snap every perforated tab one at a time. (It also doesn't help
that the stickers are big and often cover the perforated lines.)

<TODO: Image of perforation>

Besides the keys, there is also a really neat business-card with the schematics
for the reversible USB-A connector. This looks great, and is also ties in well
with their Open-Source Hardware (OSHW) aim/philosophy.

<TODO: Image of card>

Moving on to the keys themselves, the Limited Edition (LE) was the first one I
opened and it looks cool! The purple is a nice colour, and the traces are nicely
visible as well. However, the resin/epoxy that they used to seal the PCB looks
bubbly, as if the air didn't escape when drying (or perhaps its just the
glitter; it is hard to tell (and even harder to photograph)...) 

<TODO: Image of LE with bubbly resin>

Compare this with the resin on the normal Solo v2:

<TODO: Image of non-LE>

Turning over the key, we get my favourite detail: a little bee on the back of
every key!!

<TODO: Image of BEE!>

Comparing the USB-C with USB-A, it is clear that the USB-C sticks out/tilts a
bit. This is possibly just how the USB-C connector is attached to the PCB, it is
taller than the USB-A connector after all, but it looks a bit odd.

<TODO: Image of USB-C tilt>

I'm always fan of customisation, so I ordered a bunch of cases to try out. They
are relatively easy to put on; it doesn't feel like the cases or the key will
break when putting them on. SoloKey do include some cases with the keys, so the
extra colours are optional. The included cases are slightly different: they have
a small round dip in the case for easier grip.

<TODO: Image of the cases?>

With the cases applied, another thing I had noticed becomes even more obvious:
there is a _healthy_ dollop of resin on the LEs. I am not sure if this was
because of the glittery resin being less viscous than the transparent one or if
this is only my two LEs (I doubt it), and it doesn't really affect anything, but
it seems a bit weird that these got so much resin compared to the other keys.

<TODO: Image of the chonky LEs>

With the keys looking nice, it was time to try them out. But first I decided to
update the firmware, to make sure everything was as recent (and hence hopefully
error-free) as possible.


## Updating the firmware on Windows

