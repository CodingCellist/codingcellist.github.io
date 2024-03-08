---
# Documentation: https://wowchemy.com/docs/managing-content/

title: "Moving to GitHub Pages"
subtitle: ""
summary: ""
authors: [thomas-e-hansen]
tags: [admin, meta, misc, hosting, rant]
categories: [succulent]
date: 2024-03-08
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

With the increased commercialisation of universities in the UK, one of the
things that the Computer Science (CS) department unfortunately lost access to,
by command from "up on high", was the providing of publicly accessible web
hosting.

It used to be that there was a `$HOME/nginx_default` directory which one could
copy files to however they wished, and that content would then be hosted. As a
CS department, this was extremely useful for numerous reasons, for example:
web-dev coursework, showcasing projects, and personal and research groups'
websites which were highly customisable (like the one you're currently reading
this on).

With the move to a more corporate IT infrastructure, central IT Services (ITS)
told our sys-admins that although the hosting service itself could stay (ITS
wanted nothing to do with it), everything would be placed behind the campus
firewall, limiting access to on-site only. Even people living locally but
outwith university properties, would be unable to view the sites. Some of us
tried protesting this, notably the Human-Computer Interaction (HCI) group, who
pointed out that their research somewhat relied on being able to host
customisable websites that they could share with a wide range of people.  I
tried defending the personal case by reaching out to our Postgraduate Research
(PGR) representative at the time, arguing that the hosting service provided
great value for PGRs and undergraduates alike, both in terms of personal and
professional growth.

Unfortunately, it seemed there was nothing to be done, and as of the start of
this year (2024), the hosting URLs were frozen in time and unable to be updated.

I had been planning to figure out an alternative hosting solution soon-ish
anyway, since I am meant to be finishing up, but this change suddenly
accelerated the need for one. My Great Big Plan<sup>TM</sup> was to play around
with self-hosting, either via a virtual private server from Hetzner or similar,
or via an Odroid N2 which I've got and is currently just sitting in a cupboard.
Except `ENOFREETIME`.

So the next-best thing, which hopefully should Just Work, is to move to GitHub
Pages. And if you're reading this from somewhere on the interwebs, then I guess
I succeeded!

