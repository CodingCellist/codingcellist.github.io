---
# Documentation: https://wowchemy.com/docs/managing-content/

title: "SoloKey v2 Review"
subtitle: ""
summary: "After numerous delays, production problems (thanks pandemic), and
          little communication on the Kickstarter page, my Solo v2 keys finally
          arrived. Overall, they were mostly worth the wait."     # TODO after article written
authors: [thomas-e-hansen]
tags: [review,solo2,hardware,oshw,u2f]        # TODO: think a bit about these
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
SoloKey admitted this. Nevertheless...

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

Comparing the USB-C with USB-A, the biggest difference is that the USB-C sticks
out/tilts a bit. This is possibly just how the USB-C connector is attached to
the PCB, it is taller than the USB-A connector after all, but it looks a bit
odd.

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


## Updating the firmware


N.B.: In this section I will be making a lot of comments on how user-friendly
this process would be for the non-developer/average user. While I know the
people buying OSHW security tokens probably aren't just your average user, it is
not impossible. There is also a difference between being computer-savvy and
knowing how to install various toolchains and how to navigate a Command Line
Interface (CLI). Finally, if the goal is wide(r)-spread adoption of these
devices (similar to YubiCo's stuff), then it is crucial that the user manuals
are comprehensible to everyone.

With that out of the way...

### Updating the firmware on Windows

The first thing I did to update the firmware was to go looking for instructions
for how to do this. The quick-start guide
([solokey.com/start](https://solokey.com/start))
has a link for how to update the firmware on Windows, perfect! However, this
guide doesn't inspire the most confidence: there are minor spelling mistakes
("than" vs "then") which makes it seem rushed, and the phrase "[it] appears
complicated to the non-developer" means it will likely be borderline impossible
and/or terrifying for the average user to follow. But the biggest hurdle is the
pre-requisite to even getting started: since the firmware is written in Rust, we
need to install Rust to update it. And installing Rust, it turns out, is not
simple at all...

#### Installing Rust on Windows

The guide points to "rustup", which presents the option of 32- or 64-bit, with
32-bit selected as the default. This is already too high a barrier in my
opinion, although the 32-bit version should work on all machines (but not
everyone knows that, or even know what architecture they're running).

A bigger problem is that the rustup installer immediately differs from the
provided guide: the guide suggests I should get a prompt for installing Rust,
but instead it complains about a lack of Microsoft compilers and points to
installing Visual Studio (VS), Microsoft's Integrated Development Environment
(IDE). Neither rustup nor the guide explains why this might be required.

<TODO: Image of differing prompts?>

I begrudgingly follow the link and download the VS installer. Here, I only
encounter more confusion (even as a developer): do I need the Windows 10/11
developer kit? Do I need to log in to VS? Because logging into VS is the next
thing I'm prompted for. It turns out the respective answers are "Yes" and "No":
you can install VS and its compilers without using VS ever. Frustrated, I spent
some time trying to find a smoother approach, e.g. using `winget`, but _the only
way_ to install Microsoft's compiler collection is via the VS installer! That's
atrocious, but I'm getting off-topic.

Finally, after not installing VS but using its installer to install a different
set of tools, I re-run the rustup installer and get the same prompt as in the
guide. Now we're at square 1 of the _precursor_ to updating the firmware; that's
not great.

The install proceeds without problems, but at the end of the process Rust
informs me that I may need to update the `PATH`. I happen to know what `PATH` is
and how to change it, but I'm a computer science professional! I seriously doubt
the average user would be able to change it (and even if they found a guide,
they might be worried about touching something so technical). Anyway, let's
continue on with the guide.

#### Finally updating the firmware

The next step is to run `cmd.exe`, use `cargo install solo2` to install
SoloKey's command line tool `solo2`, and then check that the `solo2` program
works correctly. Fortunately, this goes without any problems!

<TODO: Image of things working>

Finally, we can try to update the firmware: `solo2 update`. This warns me that
the update is major and will break previous credentials, but also includes a
note saying that if the key has not been used yet, then I can ignore the
warning. Explicitly stating this is excellent and helps resolve fears if you're
not a tech-savvy user.

<TODO: Image of warning?>

The update seems to run flawlessly, with the key being registered a couple of
time by Windows during the update (expected behaviour), and a quick check
afterwards confirms that everything went fine.

<TODO: Image of successful before/after>


### Updating the firmware on Linux

There is no guide for this on the website, which is fair enough considering the
number of possible combinations and distros. As with Windows, the first step is
to install Rust if you do not already have it installed. If you are using a
common distro, the easiest (and most likely) option is that your package manager
(`apt`, `yum`, `pacman`, `nix`, etc.) has a package which you can just install
as you would any other piece of software. Alternatively, there may be a
wiki-page, guide, or blog-post for how to install Rust for your specific setup;
web search is your friend!

After that, the next step is to update your `PATH` environment variable and then
install the `solo2` program using `cargo install solo2`.

At this point, the commands work as with Windows (`solo2 app admin version` and
`solo2 update`). You may need to use `sudo` to update firmware (or add some udev
rules if you're comfortable with that; the non-root update tool error message
contains the rules if relevant), but otherwise everything is good.

Overall, this process is a lot smoother than Windows _if_ you are familiar with
package managers.

### General impression

My general impression is that the tooling feels a bit bare-bones. The lack of a
single installer executable (or script) for Windows, and the reliance on CLIs
for everything, feels early-adopter-y. I wouldn't trust the average computer
user with it, and probably not even the more security conscious ones.


## Using the Solo v2

Having talked about the packaging and support tooling, how easy is the Solo v2
actually to use for U2F? There shouldn't be too much difference between Linux
and Windows, since the registration is done in the browser, but you never know.

The website's instructions
([solokey.com/start](https://solokey.com/start))
are generic and seem straightforward, but as we saw with the firmware update
setup, that might not be the case. Let's see, shall we?

### Registering the keys under Linux

First site I tried was GitHub: `Settings` -> `Password and Authentication` ->
`Two-factor authentication` -> `Security keys` -> `Add` -> `Register new
security key`. This seems to require that you have already set up an
authenticator app (so that you have a backup second factor should you lose your
security key), which I have, so that is fine. Then you provide a name for the
key (e.g. "Solo2-USB-A-1"), click `Add`, the light on the key pulses, and the
operation is completed when you touch the key. Rinse and repeat for the backup
key (with a different name). All in all, very straightforward and painless, with
no need for `sudo` or special udev rules or anything like that.

Similar to backups though, creating one is not enough, you need to test that it
works as well: fortunately, there are no issues using the freshly registered
keys for 2-factor login.

Moving on to Windows.

### Registering the keys under Windows

As mentioned at the start, SoloKey's instructions are the same regardless of
operating system. So hopefully the registration process should be as
straightforward as on Linux.

Unfortunately, as with the Rust setup guide, the process immediately differs
from what the guide suggests should happen: I am asked to configure a PIN.

<TODO: Image of PIN query>

I tried finding some information on their website, but nowhere on the start
guide, website FAQ, or KS FAQ is there any mention of needing to configure a
Personal Identification Number (PIN). The "developers" link at the bottom of
SoloKey's website is also not helpful, as it redirects to the code for the first
edition. I eventually managed to find
[the developer documentation](https://solo2.dev)
by going to the
[SoloKeys GitHub](https://github.com/SoloKeys)
-> `solo2` repository -> `website` field, but it only mentions _hardware_ pins
and nothing about a key-specific PIN...

#### 2-factor vs Passwordless

After a bit of searching, I found two Reddit threads
([here](TODO)
and
[here](TODOO))
which helped me understand what was happening: it is a difference between the
Universal 2-Factor (U2F) and the Fast Identity Online 2 (FIDO2)
protocol/standard.

U2F uses the key as a second factor in addition to a _regular_ password prompt,
whereas FIDO2 can provide passwordless login. However, in order to not have the
passwordless login be less secure, a PIN is required to make passwordless still
have two factors (something you know: the PIN; and something you have: the key).
If this seems unnecessarily convoluted, that's understandable. The reasoning is
that with U2F you still need to send your password over an (encrypted) internet
connection for the first factor, whereas with passwordless both factors happen
locally and the only thing that is sent is a proof of authentication.

The fact that this doesn't seem to be documented anywhere is disastrous and will
undoubtedly lead to much confusion for users: Why do I need to set a PIN? Will
the key registered on Linux work on Windows? Will adding a PIN prevent the key
from working on Linux? Are there any limitations on how long the PIN can be or
what characters it may contain? (Windows allow including alphabetic characters
and symbols in a PIN)  
**The PIN behaviour should be documented _somewhere_!**

Unfortunately, it is up to the individual website/server whether they go for U2F
or FIDO2, so there is no way to force the key to use "more traditional" U2F if
the website requests a FIDO2 authentication or registration.

#### Registering under Windows?

Given the early stage of the Solo v2, and that there have already been problems
where the fixed firmware update broke existing registrations
([details](TODOOO)),
I am hesitant to register any website on Windows (I tried a couple of other
websites, but got the same "You need to configure a PIN" prompt)...

The `solo2` Rust app has no mention of a PIN or utilities to
support checking, setting, or changing one. Not in the generic help text, nor
the help for each subcommand (I checked all of them). A search on the GitHub
repo seems to suggest
([here](TODOOOOO))
that it is `1234` when unset, although that may just be for testing purposes? If
it isn't, the default PIN should obviously be changed, and Windows seem to force
you to, but there does not seem to be a way to set it via SoloKey's official
tooling.

What's even more confusing, is that the PIN prompt doesn't appear for the same
websites on Linux (despite having the FIDO2 libraries installed). Instead I
go through a U2F registration process (password, then key prompt). If this is
less secure, then I would expect that to be fixed or highlighted, or if the PIN
is not always required, then that should be explained. It is difficult to know
because, as mentioned, there is _no documentation_ for anything regarding FIDO2
PIN configuration.


## Conclusion

In conclusion then, the Solo v2 is an impressive OSHW project which seems to
both look and work great despite all the setbacks there have been. The keys feel
durable and have been working flawlessly with the websites I have registered
them with so far. However, there appears to be a lot of work still left in the
tooling and documentation, as some of the documentation appears rushed and the
support tool seems to completely be missing a core bit of functionality (PIN
configuration). Hopefully this gets fixed sooner rather than later. I'll update
this post if/when it does.

As always, I hope this was useful. Thanks for reading  : )

