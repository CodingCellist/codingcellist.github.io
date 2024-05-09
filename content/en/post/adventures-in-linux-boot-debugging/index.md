---
# Documentation: https://docs.hugoblox.com/managing-content/

title: "Adventures in Linux Boot Debugging"
subtitle: ""
summary: "It all started yesterday morning, where I booted up my laptop and
          found that the greeter (the visual login prompt) was not displaying
          anything: I had a cursor and a black screen."
authors: [thomas-e-hansen]
tags: [linux,drivers,debugging,gpu]
categories: [sprout]
date: 2024-05-09
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

## Arch, my beloved

It all started yesterday morning, where I booted up my laptop and found that the
greeter (the visual login prompt) was not displaying anything: I had a cursor
and a black screen. "Not to worry," I thought to myself "typically this is just a
case of rebooting." It was not. However, when a Linux system breaks, it is
rarely completely broken. By pressing `Alt` and one of the function keys (for
example `F3`), one can switch `tty`s (_teletypes_, a now emulated remnant from
the dawn of computers), and log in via a classic login shell. From here, it was
time to see if the system journal contained anything useful:

```
$ journalctl -b 0 -p warning
May 07 14:18:36 skidbladnir kernel: nouveau 0000:01:00.0: gr: intr 00000040
<...>
May 07 14:18:39 skidbladnir kernel: nouveau 0000:01:00.0: gr: DATA_ERROR 0000009c [] ch 5 [00ff976000 WebKitWebProces[1002]] subc 0 class c197 mthd 0d78 data 00000004
May 07 14:18:39 skidbladnir kernel: nouveau 0000:01:00.0: gr: DATA_ERROR 0000009c [] ch 5 [00ff976000 WebKitWebProces[1002]] subc 0 class c197 mthd 0d78 data 00000004
May 07 14:18:39 skidbladnir kernel: nouveau 0000:01:00.0: gr: DATA_ERROR 0000009c [] ch 5 [00ff976000 WebKitWebProces[1002]] subc 0 class c197 mthd 0d78 data 00000004
May 07 14:18:39 skidbladnir kernel: nouveau 0000:01:00.0: gr: DATA_ERROR 0000009c [] ch 5 [00ff976000 WebKitWebProces[1002]] subc 0 class c197 mthd 0d78 data 00000004
<etc>
```

Well that's not good... Nouveau is an open-source GPU driver, and whatever was
going on, it was clearly _very_ unhappy. I have had this happen once after a
kernel upgrade, so I looked through the journal, this time without filtering by
`warning` or higher, to find when I last updated my kernel: the previous boot.
Oh well, that is to be expected from a rolling release like Arch from time to
time I guess. So I downgraded, rebooted, everything was fine, and I submitted a
bug to the Arch GitLab with details and logs, and went about my work day as
usual, happy to have discovered an issue and informed people who know a lot more
about it, so that they could hopefully fix it (or at least pass it on to the
kernel devs themselves, if it were a bug in the Linux kernel and not just in
Arch's release of it).


## That would've been nice and easy

5 hours and one reboot later, the problem was back.

On the older kernel version.

And again, it was not going away despite several reboots, with the system
journal showing exactly the same stream of error messages...  
_\*visible concern\*_

So: close the GitLab ticket with apologies (although thankfully it didn't seem
like anyone else had started investing time in it), upgrade back to the newer
kernel, and reinstall the graphics drivers just for good measure. Aand the
system rebooted and greeted me without issue! Good enough for getting on with my
evening of video games, but I was still highly suspicious.

Which brings us to today, the day of writing this, where indeed I tried starting
my laptop and was greeted by a black screen with only a cursor. But could it
just be that the display wasn't rendering properly? Yes it could! Logging in as
I normally would, despite no visual feedback whatsoever, resulted in a working X
session. Nice. But, my terminal emulator is GPU-accelerated, so trying to open
that resulted in completely nonsense windows.

![Picture of a computer window, the top half is random noise and the bottom half is black with random grey stripes](mkinitcpio-39-bug/terminalnt-1.png "Ah yes, a perfectly rendered terminal window")

As with my greeter though, the terminal emulator itself was working just fine,
so thanks to touch-typing, I managed to install `urxvt` which is _not_
GPU-accelerated. Now I had a terminal emulator where I could actually see what
was happening! Truly a luxury.


## Logs, logs, and more logs

With a workable terminal emulator, I set about trying to dig deeper, to get more
log output to see if any of them were useful. Using `dmesg -W` -- watching for
new kernel messages -- I got the following errors whenever I tried mousing over
the GPU-accelerated terminal window:

```
[ 1034.885491] nouveau 0000:01:00.0: Xorg[936]: validating bo list
[ 1034.885493] nouveau 0000:01:00.0: Xorg[936]: validate: -22
[ 1034.885554] nouveau 0000:01:00.0: Xorg[936]: fail ttm_validate
[ 1034.885556] nouveau 0000:01:00.0: Xorg[936]: validating bo list
[ 1034.885557] nouveau 0000:01:00.0: Xorg[936]: validate: -22
[ 1034.885742] nouveau 0000:01:00.0: Xorg[936]: fail ttm_validate
<etc>
```

And trying to run `glxgears`, I got this cryptic output:

```
nouveau: kernel rejected pushbuf: Invalid argument
nouveau: ch5: krec 0 pushes 1 bufs 11 relocs 0
nouveau: ch5: buf 00000000 0000000b 00000004 00000004 00000000 0x6b142743f000 0x570000 0x80000
nouveau: ch5: buf 00000001 00000007 00000002 00000000 00000002 (nil) 0x400000 0x80000
nouveau: ch5: buf 00000002 00000006 00000004 00000000 00000004 0x6b1434729000 0x14000 0x1000
nouveau: ch5: buf 00000003 0000000a 00000002 00000002 00000002 (nil) 0x550000 0x20000
nouveau: ch5: buf 00000004 00000013 00000004 00000004 00000000 0x6b1434724000 0x1a000 0x4000
nouveau: ch5: buf 00000005 00000012 00000002 00000000 00000002 (nil) 0x2400000 0x400000
nouveau: ch5: buf 00000006 00000014 00000004 00000004 00000000 0x6b1429888000 0x2280000 0x20000
nouveau: ch5: buf 00000007 00000008 00000002 00000002 00000000 (nil) 0x480000 0xd0000
nouveau: ch5: buf 00000008 00000010 00000002 00000000 00000002 (nil) 0x2180000 0x80000
nouveau: ch5: buf 00000009 00000011 00000002 00000000 00000002 (nil) 0x2200000 0x80000
nouveau: ch5: buf 0000000a 0000000f 00000004 00000004 00000004 (nil) 0x19000 0x1000
nouveau: ch5: psh 00000000 0000000000 0000002f14
nouveau: 	0x20024062
nouveau: 	0x00000000
nouveau: 	0x0047f800
<cut>
nouveau: 	0x00000000
nouveau: 	0x00000000
nouveau: 	0x00000000
nouveau: 	0x00000000
nouveau: 	0x20010364
nouveau: 	0x3f800000
nouveau: 	0x20010674
nouveau: 	0x0000003d
nouveau: 	0x200406c0
nouveau: 	0x00000000
nouveau: 	0x00014000
nouveau: 	0x00000001
nouveau: 	0x1000f010
nouveau: kernel rejected pushbuf: Invalid argument
nouveau: ch5: krec 0 pushes 1 bufs 8 relocs 0
nouveau: ch5: buf 00000000 0000000b 00000004 00000004 00000000 0x6b142743f000 0x570000 0x80000
nouveau: ch5: buf 00000001 00000008 00000002 00000002 00000002 (nil) 0x480000 0xd0000
nouveau: ch5: buf 00000002 0000000a 00000002 00000002 00000000 (nil) 0x550000 0x20000
nouveau: ch5: buf 00000003 00000006 00000004 00000000 00000004 0x6b1434729000 0x14000 0x1000
nouveau: ch5: buf 00000004 00000010 00000002 00000000 00000002 (nil) 0x2180000 0x80000
nouveau: ch5: buf 00000005 00000011 00000002 00000000 00000002 (nil) 0x2200000 0x80000
nouveau: ch5: buf 00000006 00000007 00000002 00000002 00000002 (nil) 0x400000 0x80000
nouveau: ch5: buf 00000007 00000012 00000002 00000002 00000000 (nil) 0x2400000 0x400000
nouveau: ch5: psh 00000000 0000002f14 00000037b4
nouveau: 	0x200505f2
nouveau: 	0x00000000
nouveau: 	0x02400000
<cut>
```

```
$ wc -l glxgears.out
120863 glxgears.out
```

Which uhh, that's _a lot_ of hex values to dump to the output. That doesn't
normally happen... And "kernel rejected pushbuf" is almost definitely not good.


## To the archives!

One of the beauties of Arch Linux is the
[package archive](https://archive.archlinux.org).
It contains both date- and name-indexed archives of every package in the
official repositories. Needless to say, this is a godsend when trying to narrow
down exactly _when_ a system broke.

Looking on the archive under `xf86-video-nouveau` however, the plot only
thickened: my current nouveau install was created on 2024-03-23, which was way
earlier than when my system started breaking, and version before then was from
November 2021! No harm in trying to downgrade to the much older version I guess,
but as expected, this did not magically fix things.

Which brings us to my next trick: you can set `pacman`'s `mirrorlist` file to
point to only one server, and have that be one of the dated archive URLs.
Combined with the flags that tell `pacman` "I don't care about the state of the
database, do a fresh fetch from the mirrors and up- or downgrade regardless"
(which, in case you were wondering, are `-Syyuu`), this means you can very
easily restore the system to a known good date and then work your way forwards
from there. Bonus points if you pay attention to which packages are changing
between the operations. Helps reduce your list of suspects.

Last Friday, 2024-05-03, was definitely working (I think): set the url,

```
## Arch Linux repository mirrorlist
Server=https://archive.archlinux.org/repos/2024/05/03/$repo/os/$arch
```

force `pacman` to pull the info and downgrade things

```
sudo pacman -Syyuu
```

trace a protective ward, sprinkle some salt, and

```
reboot
```

... ... ... And we're back to normal!! For now at least.

Unsurprisingly, rebooting again reproduced the error.

That previous sentence makes this particularly annoying because it means the
problem is likely nondeterministic. Which is annoying in and of itself, but is
_particularly_ annoying because the only way to try to test that is to reboot a
bunch of times and record the results. Which is too slow to be fun, while also
being a process which cannot easily be automated (automating power cycling with
custom logs is cumbersome). So I did it by hand, because at this point it was
annoying me enough that I wanted to get to the end of it best as I could. The
results were:

* Using the package archive from 2024-05-03: 8 good reboots, 2 bad.
* Using the package archive from 2024-05-04: 3 good reboots, 7 bad!

Okay so the 3rd of May was not perfect, but something clearly gets much worse
after the 4th of May. What on Earth??


## Rounding up the suspects

In order to get a list of suspects, I reset the mirror so it pointed to the
2024-05-03 archive, and noted which packages were changed. One by one, the
suspects emerged:

* abseil-cpp
* dart
* glibc
* glslang
* harfbuzz
* harfbuzz-icu
* hwdata
* libpsl
* minicom
* mkinitcpio
* pcsclite
* python-jaraco.functools
* qt6-base
* shaderc
* spirv-tools
* tzdata

Examining each and every one of these would have taken way too long, due to the
nonderministic nature meaning 10 reboots to check the problem, across 16
packages, that would be roughly 160 minutes total!

Besides, not all suspects were looking equally guilty. Especially the following
packages were unlikely to be affecting things:

* dart -- a cross-platform programming language; unlikely to be involved with
    GPU-drivers
* harfbuzz and harfbuzz-icu -- open source text shaping libraries; phenomenally
    cool software, but again, unlikely to be affecting the GPU-drivers
* hwdata -- hardware identification databases
* libpsl -- lists to do with web suffixes
* minicom -- serial communication program
* pcsclite -- smartcard middleware
* python-jaraco.functools -- more different python functools
* tzdata -- time zone and summer time information 

This left me with -- *sigh* -- 7 suspects:

* abseil-cpp
* glibc
* glslang
* mkinitcpio
* qt6-base
* shaderc
* spirv-tools

Down to about 70 minutes of rebooting. Yaaay... Anyway, it was an improvement on
160 minutes, and there was only one way to get through it.


## So. Many. Reboots...

Armed with podcasts, I started out by yet again pointing the mirror to the
2024-05-04 archive, and editing `pacman.conf` to ignore the seven suspects. That
way, the next update would only upgrade the packages I felt mostly safe weren't
breaking things. Nine out of ten reboots were normal; so far so good.

First up, the biggest suspect: `glibc`. I have previously had really odd bugs
happen with one minor version of glibc that weren't present in the next one, and
it was also the package with the broadest set of dependents. Remove it from the
`IgnorePkg`-list, upgrade, and onwards. Nine out of ten successful reboots!
Fantastic!

I then moved on to `abseil-cpp`. Mainly because I doubted it was the cause, so I
might as well get it out of the way. 8 out of 10 reboots went fine , abseil-cpp
was indeed not it.

Going in alphabetical order brought me to `glslang`. 10/10!! That's a first!
Maybe I should just keep my system on this seemingly magic combination of
updates forever?

Next up was `mkinitcpio`. There had been some bug reports about version 39 on
the Arch Linux GitLab, but they didn't seem to show the same symptoms, or be
related, to the issue I was having. When it rains it pours though! Only four out
of 10 normal reboots this time -- I'd found the problem child. To be completely
certain however, I "promoted" `mkinitcpio` to Prime Suspect, _downgraded_ it (to
excuse it from any potential subsequent failures), and proceeded with the
remaining three suspects: `qt6-base`, `shaderc`, and `spirv-tools`. They came in
at 9/10, 10/10, and 10/10 successful reboots respectively. I think we've got
'im!


## The final test

With the rest of the suspects cleared beyond reasonable doubt, one final test
remained: keeping `mkinitcpio` on the naughty list, I restored the mirror list
to its usual state, and updated the entire system. _In theory_ this should
change nothing, but by now I was expecting almost anything. Needless to say, I
was heavily hoping this would not change anything.

(Drum roll please...)

9/10 normal reboots! :tada: That settles things! Although I have no idea why
mkinitcpio is suddenly messing up the GPU, keeping it at 38.1 is the only thing
that has allowed me to reliably boot up my system. (I did also triple-check by
re-updating to 39 with all the latest packages installed. That resulted in only
a single successful boot out of 10; something was clearly amiss). Now, finally,
I could
[file a bug report](https://gitlab.archlinux.org/archlinux/mkinitcpio/mkinitcpio/-/issues/267),
in the right place this time, and with
[a _ton_ of logs](https://github.com/CodingCellist/arch-linux-mkinitcpio-2024-05-09-findings)
which hopefully will be helpful.

Oh and as a bonus: until whatever the issue is gets resolved, I get to keep my
working system by simply keeping `mkinitcpio` on the "Yeah don't update that one
though" list.

-----

Hope you enjoyed coming along on this little ramble about I approached a fairly
broken linux system. I have more stories like this one in my projects notebook,
which I'll get round to writing up aaany time now... This time I decided to
write as I was debugging, both to keep things fresh in mind, and to actually get
something written, and I think it worked pretty well. I'll definitely keep that
in mind for future interesting tangents I end up on.

Thank you so much for reading!  : )

P.S. I know, theoretically, that the hardcore next step would be to bisect to
try to find the exact moment things went wrong. However, this took a lot of time
to narrow down _without_ having to recompile a large project like `mkinitcpio`.
And having already spent a total of a work day on this, I am simply out of time
to investigate further.

