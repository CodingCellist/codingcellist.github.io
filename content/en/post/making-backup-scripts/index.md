---
# Documentation: https://wowchemy.com/docs/managing-content/

title: "Making Backup Scripts"
subtitle: "Probably good to have when the system is encrypted and you like to
           fiddle with things."
summary: ""
authors: [thomas-e-hansen]
tags: [backup, scripting, linux]
categories: [] # [linux, guide]
date: 2021-02-17T20:14:27+01:00
lastmod: 2021-02-17T20:14:27+01:00
featured: false
draft: true

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

After just over a year of running my
[dual-boot, FDEd system](/en/project/dualboot-arch-windows-encrypted/), I
decided I should probably adhere to my own disclaimer and make sure that I have
at least one backup of the system. Particularly as I have become increasingly
aware that I rely 100% on this laptop for almost all of my work, socialising,
and file storage. So let's get to work.

For the Linux system, I will be using the command-line tool `rsync`. There are
numerous other tools out there (e.g. BorgBackup, Duplicacy, rdup, just to name a
few), but `rsync` has been around for a while (since 1996) and most existing
guides+documentation use it. For the Windows system I initially looked into
various paid tools, but then my better half asked whether there wasn't some
built-in tool, which of course there was: `robocopy` or "`rob`ust file `copy`"
(no idea where the middle `o` comes from, CS is bad like that). It's different
from `rsync` in various ways and there aren't nearly as many guides out there on
it, but on the flip side, it's free (as in beer) and it seems to do the job well
enough (I mostly have games on Windows, which don't need backing up since
they're synced to a cloud account and/or mostly executables+artifacts) so I
didn't see the need to spend money when a free tool could do the job (at the
cost of a bit of documentation reading).

