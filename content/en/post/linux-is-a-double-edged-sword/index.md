---
# Documentation: https://wowchemy.com/docs/managing-content/

title: "Linux is a Double Edged Sword"
subtitle: ""
summary: ""
authors: [thomas-e-hansen]
tags: [misc, rant, linux, os]
categories: [seed]
date: 2024-01-16
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

* Talking with someone about Apple ecosystem, linux, and cross-device
     integrations in general
* Made me realise how much of this is actually a pain
* I usually joke "It's hell, but one of my own creation so I at least know which
    torture devices there are."
* Tbf, Arch quite probably has more pains than other distros
  - Although mine has been surprisingly stable for the past 5 years...

* Configs are cool
* But configs are also a pain to set up, keep in sync, backup, etc.

* There are wikis for everything
  - Side-note: if not, SOL
* But everything I've written have been through a frustration+caffeine fuelled
    "flow", which produces really good configs and scripts which Just Work.
  - And should they ever break, going back through all those wiki pages and
      details will likely be a similar exercise in frustration
  - If the project even still exists (this has happened! termite, ferdi,
      woff2ttf, etc)

* Sure, writing these mini-tools, scripts, configs, etc. have taught me an
    incredible amount about both those concepts and configuring systems in
    general
* But increasingly, I also just want a system that works and doesn't require
    arcane wpa_supplicant runes, which I had to get from a lecturer who also ran
    Arch, to connect to my university's network. Plug-n-play is really nice,
    y'know?...

* Can make things very secure: LUKS, PAM, firewalls
* But I 100% am not an expert on those, even though I dual-boot with Windows
    with FDE on.
  - If _that_ breaks, then **by design**, all my data is actually just _gone_.

* "But Tom, make backups!" "Just backup using <insert-favourite-tool-here>"
* See previous points: the choice and modularity is the beauty of linux, but
    also, I'd need to sort this out myself, it'd likely be a CLI which I then
    need to comb through man-pages to find the right incantations for (because
    everyone seemingly agrees there are no sane defaults), and if I miss any
    data because I happened to not know that _obviously_ the Linux FSH stores X
    important thing in Y totally-definitely-obvious path, then I'm once again
    SOL

* I do genuinely like this OS, and I do genuinely like my machine.
  - Don't think I couldn't use a tiling VM for work at this point (although,
      _maybe_ MacOS virtual desktops would be an alright substitute)
* But I am also increasingly aware that, by intention/design/philosophy, it is
    all up to me should anything go wrong. And sometimes, you just don't want
    that.

