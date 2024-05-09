---
# Documentation: https://docs.hugoblox.com/managing-content/

title: "Why I'm Transferring off EteSync"
subtitle: ""
summary: ""
authors: [thomas-e-hansen]
tags: [calendars, encryption, privacy, foss]
categories: [evergreen]
date: 2024-04-20
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

About a year or so ago,
[I made a post](/en/post/renewing-gpg-keys)
mentioning that past me was very into cryptography and encrypting just about
anything which could be, and how this was a bit of a headache for current me to
deal with (and it has
[nearly cost me a lot of data](/en/post/recovering-from-a-broken-smartcard)
at least once). At the time, it was in the name of "everyone is watching, no
company is trustworthy, no data of mine shall be useful off-device!". Which I
still believe to some extent, although I'm now slightly more in the
["you're still gonna be Mossad'ed upon"](https://www.usenix.org/system/files/1401_08-12_mickens.pdf)
camp. 

In that rush to secure everything, I also set up an account with EteSync, an
end-to-end-ecrypted (e2ee) calendar and contact synchronisation tool. And it is
sadly becoming more of a hindrance, rather than just an esoteric setup. Privacy
continues to be very important to me, but I'm also increasingly needing my
devices to Just Work. And while EteSync is a really cool proof-of-concept, it is
simply not there yet...


## The situation

To give you the full context: I use a Linux laptop for work, with Thunderbird as
my mail and calendar manager, I have an iPhone as my personal smartphone, and if
I ever need to access things from a family member's laptop or desktop, a private
browsing window is good enough: just give me some sort of web-based portal/UI
where I can log in and access my calendar.

In a perfect world, these would all seamlessly sync and happily talk to each
other. Unfortunately, the world is not perfect: finding an e2ee app which _also_
lets you hook Thunderbird up to it is bordering on Unobtanium, and Apple is very
reluctant (to say the least) to let anyone interoperate with their precious
special technology (although the EU is slowly working on forcing their hand).
For now though, this means
[background sync is not possible](https://github.com/etesync/ios/issues/23#issuecomment-633837720),
which in turn means that the EteSync app's "synchronise" functionality -- a
somewhat core part of a calendar and contact _synchronisation_ product -- has to
be run manually. This assumes the user remembers to do so regularly,
[has iCloud sync turned off for the items they want to sync](https://www.etesync.com/user-guide/ios/),
and that the user doesn't forget to open the app for long enough that their
session expires, meaning they have to log back in and set everything up again
(this has happened to me on several occasions and, if I recall correctly,
reconfiguring the app for some reason does a fresh copy: duplicating all my
contacts every time I got logged out).

There _is_ a recent-ish feature request to
[add reminders to do a sync](https://github.com/etesync/ios/issues/101)
but given how... dead
([the creator disagrees with that word](https://discuss.privacyguides.net/t/etesync-is-dead-long-live/13203),
but I can't think of a better one)
[the EteSync repos](https://github.com/orgs/etesync/repositories)
seem, and that the feature request has not received any interaction for a year
at the time of writing, I doubt this will be addressed any time soon.

The creator of EteSync (and as far as I can tell: BDFL), Tom Hacohen, also has
an entirely different project to look after:
[Svix](https://svix.com/).
This project
[sounds like it is a much better business](https://console.dev/interviews/svix-tom-hacohen)
than an e2ee API for the few nerds out there who care about that (I'm sorry, but
there genuinely aren't as many of us as we'd like to think). And that's great! I
exchanged a number of emails with Tom when trying to help figure out why
[iOS syncing was failing](https://github.com/etesync/ios/issues/16),
and he seems like a really nice and friendly person, who cares about open source
and privacy, and has the skills, time, and money to put something out there
which reflects that. So I'm genuinely glad that this most recent project of his
is successful! However, matter of fact then is, that this also means that there
are virtually no resources (human or otherwise) available to work on EteSync,
beyond keeping the website and servers alive (which is important and
time-consuming work! Maintenance takes a surprising amount of resources, I know
that all too well). Bug fixes, feature requests, and product improvements are
unlikely to come.


## When this became an issue

Initially, when I first started using EteSync, sync not working entirely
smoothly on iOS was not a problem. I had found an app which had everything I
wanted: sync, e2ee, a web portal, and cross-platform support including Linux!
I was willing to pay for its service and development, and help out with what
debugging I could. I didn't mind the rough edges. It was the middle of COVID, it
wasn't exactly like I was scheduling events away from my computer.

But now I _do_ increasingly find myself scheduling events out in the real world.
And I also increasingly find myself needing to coordinate things with other
people. I have thankfully not missed any events (yet), but it is getting to a
point where I several times per week go "Oh shoot, I need to check the calendar
but it is not synced to my phone and I can't be bothered starting up my Linux
machine". ("Why is it no longer synced?" you might ask. Because I got tired of
cleaning up the duplicate contacts, calendars, and events every time I got
locked out.) Some of the things I need to look up are small. But a not
insignificant amount of them are also bigger things like "When am I going to my
friend's wedding?", "Do I already have something scheduled at the same time as
that seminar series I promised to attend?", or "When was it my parents were
making an effort to come see me amidst all this PhD madness?" And
[I'm not the only one for whom this is a problem](https://discuss.privacyguides.net/t/restore-etesync-calendar-contacts-sync/11764/11).

If everything synced to my phone as intended, there would be no issues and this
blog post would not exist. If you've been following the blog or know me
personally, you'll hopefully agree that I'm not afraid of "getting my hands
dirty" and wrangling various configs, systems, and tools to get some tool
working on my slightly arcane setup. The difference is that with most of these
things, once they are set up, they mostly chug along without issue. EteSync, in
its current state, sadly does not: the rough edges have remained rough, and the
tiny cuts are approaching 1000.


## The sad conclusion

Unfortunately, all of this means that I will not be renewing my annual
subscription to EteSync. I had previously been supporting them at the
"Supporter" tier, paying 2x the asking price, because I was delighted to see
someone working on a product like this and I wanted to keep its existence and
development going. But given that it (still) doesn't do the one thing I need it
for, I feel it is time to say "Farewell for now".

I would love for someone to take up the mantle and revive the project. Or build
something on top of their protocols and servers. Heck, I have personally flirted
with the idea several times! But I'm not exactly swimming in free time or energy
(writing a PhD is hard, who knew??), so for now it seems that that's not an
option and EteSync will remain on life-support.

The final nail in the coffin was when I found out that one can configure CalDAV
for the default iCloud calendar. Is Apple good? By no means! But I personally
don't think they're as bad as Google when it comes to privacy, and their stuff
_does_ largely Just Work. And that is increasingly what matters to me.


