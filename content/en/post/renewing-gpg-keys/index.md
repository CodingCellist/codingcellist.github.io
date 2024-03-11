---
# Documentation: https://wowchemy.com/docs/managing-content/

title: "Renewing GPG Keys"
subtitle: ""
summary: ""
authors: [thomas-e-hansen]
tags: [gpg,encryption,howto,guide,misc]
categories: []
date: 2023-07-13
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

Past me set up GPG keys at a time where I thought I'd encrypt everything. I
think I used them 3 times right after setting them up, and then never again. So
I could just let them expire, but I feel like I have to maintain them for now...

-----

If you, like past me, were more paranoid than sensible, start by retrieving your
offline master key (which you definitely know where you put and don't need to
search for at all), and mounting it. Without your master key, you will not be
able to extend the duration of your subkeys.

After you've retrieved your master key's device, import it to your GPG keyring
via

```
$ gpg --import /path/to/offline/master-key
```

This should prompt you for your password, and after entering it, GPG should
report 1 secret key imported.

<details>

<summary>You can double-check...</summary>

You can double-check by running `gpg -K` (list secret keys) and checking that
your master key does not have a `#` after its listing:

```
$ gpg -K
sec   brainpoolP384r1/0xNNNNNNNNNNNNNNNN 2020-08-08 [C]
  [...]
ssb   brainpoolP384r1/0xNNNNNNNNNNNNNNNN 2021-07-14 [S]
ssb   brainpoolP384r1/0xNNNNNNNNNNNNNNNN 2021-07-14 [E] [expires: YYYY-MM-DD]
ssb   brainpoolP384r1/0xNNNNNNNNNNNNNNNN 2021-07-14 [A] [expires: YYYY-MM-DD]
```

The first entry reading `sec ` shows that the master key is present. If it were
still offline, it would start with `sec# `, like so:

```
$ gpg -K
sec#  brainpoolP384r1/0xNNNNNNNNNNNNNNNN 2020-08-08 [C]
  [...]
ssb   brainpoolP384r1/0xNNNNNNNNNNNNNNNN 2021-07-14 [S]
ssb   brainpoolP384r1/0xNNNNNNNNNNNNNNNN 2021-07-14 [E] [expires: YYYY-MM-DD]
ssb   brainpoolP384r1/0xNNNNNNNNNNNNNNNN 2021-07-14 [A] [expires: YYYY-MM-DD]
```

</details>

With the master key now available, we can edit the keys using GPG. Enter the
edit mode by running:

```
$ gpg --edit-key '<user id/name goes here>'
  [...]
gpg>
```

Select the subkey you want to extend with the `key` command. For example, to
extend my encryption key, which is the _fifth_ among my subkeys (due to some old
revoked ones still being present for reasons), I would run:

```
gpg> key 5
  [...]
```

After which the selected key will have an asterisk `*` next to it: 

```
  [...]
ssb*  brainpoolP384r1/0xNNNNNNNNNNNNNNNN 2021-07-14 [E] [expires: YYYY-MM-DD]
ssb   brainpoolP384r1/0xNNNNNNNNNNNNNNNN 2021-07-14 [A] [expires: YYYY-MM-DD]
```

If you accidentally selected the wrong subkey, rerun the command to deselect it.

With a subkey selected, the `expire` command lets you change its expiration
date (the final line is the prompt, I haven't typed anything else yet):

```
gpg> expire
Changing expiration time for a subkey.
Please specify how long the key should be valid.
        0 = key does not expire
     <n>  = key expires in n days
     <n>w = key expires in n weeks
     <n>m = key expires in n months
     <n>y = key expires in n years
Key is valid for? (0) 
```

Type the duration to extend your subkey by and hit enter. At the time of
writing, this is cumulative to the old duration (i.e. `3y` extends it by an
additional 3 years, it _doesn't_ set the expiration to 3 years from the original
creation):

```
  [...]
Key is valid for? (0) 3y
Key expires at 2026-07-12T15:11:28 CEST
Is this correct? (y/N) 
```

If this is correct, type `y` and hit enter. If not, the default behaviour is
`n`, so hitting enter should take you back to the `Key is valid for?`-prompt.

You might be prompted to enter your GPG password again at this point. After
entering it, your key should be updated:

```
  [...]
ssb* brainpoolP384r1/0xNNNNNNNNNNNNNNNN
     created: 2021-07-14  expires: 2026-07-12  usage: E
ssb  brainpoolP384r1/0xNNNNNNNNNNNNNNNN
     created: 2021-07-14  expires: 2023-07-14  usage: A
```

If you have more subkeys, deselect the currently selected key using the `key`
command, and then select the next one with `key` command and the next index (has
the word "key" stopped making any sense yet, or is that just me?...). Then go
through the `expire` process again.

Once you're done extending the key(s), **save the changes** by running the
`save` command:

```
gpg> save
```

This will save the changes and exit GPG. You can double-check the changes were
saved correctly by running `gpg -K` to list your private keys, and checking the
output. It should say "expires" followed by the new expiration date next to the
modified keys.

If the changes didn't go through, or you forgot to extend a key, relaunch `gpg
--edit-keys` and try again.

Once you're done, remember to move your master key back offline (**I am assuming
you have a backup and/or offline copy**) by deleting it from its current
imported state:

```
$ gpg --delete-secret-key '0xNNNNNNNNNNNNNNNN'
```

Where `'0xNNNNNNNNNNNNNNNN'` is the **master key's ID, marked `sec`,** listed by
`gpg -K`. It should prompt you several times to confirm the deletion. **Be
careful not to delete the subkeys!!** I'm _assuming_ you have a backup _if_ that
does go wrong, but you should only be deleting the master key here. I got
prompted to delete a subkey and clicked "No", after which it said the operation
had failed; however, my secret key _was_ now gone (checked with `gpg -K` and by
trying to modify keys), so it seems to have worked as intended.

With the changes made, we now need to notify the world of them. If you're using
a keyserver, resubmit/resend it the public key(s). If you've got an ASCII-armor
file somewhere (e.g. your personal website), remember to also export and
reupload your public key(s) there (mine are
[here](/uploads/pubkey.asc)).
I think, if you're using keys for GitHub and similar services, you also need to
resubmit them there (it makes sense intuitively, as far as I can tell), so
remember to do that as well.

And that's it! As always, thanks for reading, I hope it was helpful  : )

