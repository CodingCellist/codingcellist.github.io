---
# Documentation: https://wowchemy.com/docs/managing-content/

title: "Recovering From a Broken Smartcard"
subtitle: "'Safety regulations are written in blood' -- It turns out good
           practices are there for a reason. Who knew?"
summary: "My Nitrokey suddenly broke. This is some ramblings about working my
          way through the harebrained backup schemes I established, and setting
          up something a bit more sane+safe..."
authors: [thomas-e-hansen]
tags: [gpg, howto, linux, encryption, backup]
categories: []
date: 2021-07-28
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

About a week ago, I was wrapping up a workday and just needed to commit and
push to wrap things up for the day. No problem: `git commit -S` etc, plug in my
GPG smartcard (a [Nitrokey](https://www.nitrokey.com/) Pro 2), wait for the PIN
prompt as usual, and- Huh. No PIN prompt. Strange, but maybe my USB-C dongle
was acting up. Unplug the smartcard, plug into one of the builtin USB-A ports on
the laptop, repeat everything and... Still no prompt. I also at this point
noticed that the little red LED that normally lights up when plugged in wasn't
doing so. Oh no.

I don't use the smartcard for much, apart from commit signing, the occasional
email encryption for the couple of people that have it set up, and some very
occasional per-file encryption. Commit signing I could potentially live without,
but there is something pleasing about having the little green `verified` next to
your commits. In any case, the LED not lighting up no matter which port,
adapter, or OS I was using, across reboots, probably meant it had suffered a
hardware fault. Which meant the subkeys were inaccessible... But of course I'd
been sensible and made a backup, right? Well, yes but actually kinda. I keep my
master key offline and, in a similar fashion, I'd chosen to sacrifice a bit of
security for the ability to recover my subkeys in exactly this kind of
situation: I originally generated the keys on a secure computer (instead of
generating them directly on the smartcard) and then transferred them to both the
smartcard and a couple of backup drives. Which I of course had placed somewhere
clever and secure. I'm sure you can see what the problem was here... Something
something "a backup is only a backup if it's usable"...

But, I eventually managed to find one of the drives. Great! I should be able to
recover my keys now. Unfortunately, past Thomas was clever and kept things safe:
Having the raw subkeys on an external drive would not be the best of practices,
since if the drive was lost, anyone could get the data off it, which would be
disastrous for things like encryption keys. So past Thomas had encrypted things.
And past Thomas had done so quite well; a bit too well in fact... After about
half an hour of figuring out how exactly the encryption layers were set up,
trying to remember the passwords I'd used (always a fun game), and figuring out
which files were hidden where, I could finally say the classic 1337 h4xx0r
phrase: "I'm in." So. Having recovered the backups of my secret keys, type `gpg
--import` and it should be good, right? Unfortunately, it would seem not. I must
have misconfigured things when I initially exported them, so although I _could_
recover the master key, the subkeys were still shown with a `>` after them,
indicating that gpg was expecting to find them on the smartcard. The smartcard
that I was trying to recover from losing.

At this point, I counted my losses. There is, as far as I know, no practical way
to recreate the same subkeys from the master key. So I revoked the subkeys,
wrote a ticket to the Nitrokey support team asking about the durability of the
Pro 2 (it was < 1 year old, I felt it should have lasted a bit longer), and set
about both generating new keys, but also being more sensible about everything.
So without further ado:

### Learning my lesson -- A guide on how _not_ to end up in my situation.

If you have looked at backups previously, you may be familiar with the '3-2-1'
rule: 3 backups, on at least 2 types of media, with at least 1 backup offsite.
And if you have looked at gpg smartcards and/or FIDO/U2F tokens previously, you
might have read that it is good practice to have at least 1 backup token. I'd
only had 1 token (because hardware is expensive) and 2 backups. The 2 backups
thing turned out to be very good, since without it, I would have realised that
my master key was lost as well. So even though it was convoluted to recover, it
_was_ recovered. But in any case, my backups clearly needed to be (a) easier to
recover from, (b) actually tested/working, and (c) on at least one extra device.

Setting things up again then:

1. Use `gpg --import` in combination with your offline master key to bring your
   master key back online. Hopefully you remember the passphrase associated with
   it (in my case, I almost didn't; always fun when you get an "Bad passphrase
   (try 2 of 3)" message and realise the stakes might be another bit higher than
   you already knew they were. Thankfully I got it on a very nervous third try).
2. Start the key editing tool using `gpg --expert --edit-key <keyid>`.
3. For each of the subkeys, use `key <n>` to select the subkey; verify that you
   have the right key selected; then check it again, is it really the subkey?
   are you 110% sure?; if so, then type `revkey` to revoke the subkey.
4. With the subkeys revoked, create new ones using the `addkey` command.
   Depending on your old setup, you'll want to select the same configuration. In
   my case, I had separate subkeys for signing, encrypting, and authenticating,
   so I recreated these. For each subkey, start by typing `addkey`. Then:
   1. For the **signing** and the **encryption** subkeys, GPG will likely have
      an option available that automatically sets the right uses, e.g. (4) for
      an RSA signing subkey, and (6) for an RSA encryption subkey. Pick the
      option/algorithm that you want to use.
   2. Select a keysize, e.g. 3072.
   3. Set an expiration time if you want one.
   4. Confirm that the settings are correct and that you really want to create
      the subkey, then unlock your masterkey with its passphrase. The subkey
      should be generated and you will be put back at the key editing menu when
      the process is complete.
   5. For the **authenticating** subkey, select the option with the algorithm
      you want and the "(set your own capabilities)" text, e.g. (8) for RSA.
   6. Type `A` (followed by return/enter) to toggle the 'authenticate'
      capability, then type `S` (followed by return/enter) and then `E`
      (followed by return/enter) to toggle the 'sign' and 'encrypt' capabilities
      respectively. You should end up with a dialog displaying "Currently
      allowed actions: Authenticate". If not, you may have accidentally enabled
      some capabilities. Toggle them again to disable them.
   7. Type `Q` (followed by return/enter) to confirm the capabilities. Then
      repeat steps 2-4 for this key as well.
 5. With the subkeys created, type `save` to save and quit the edit mode.

**Confirm that your key and subkeys were saved** by typing `gpg -K`. You should
see the subkeys followed by `[S]`, `[E]`, and `[A]` for the sign, encrypt, and
authenticate subkeys respectively.

With the new keys in place, time to create an actually working backup:
1. Run
   ```sh
   gpg --expert --output gpg-masterkey.asc --export-secret-keys <keyid>
   ```
   (replacing `<keyid>` with the ID for your key, without the angle brackets)
   and enter the passphrase when prompted, to export the secret keys,
   **including** the master key to the file `gpg-masterkey.asc`. Adjust the
   filename as you want. Optionally, you can also specify `--armor` before
   `--output` to output the key in ASCII rather than as a binary file. This is
   useful if you want to print the key, but might also be a security risk since
   it is human-readable.
2. Run
   ```sh
   gpg --expert --output gpg-subkeys.asc --export-secret-subkeys <keyid>
   ```
   (again, replacing etc) to export the secret subkeys to the file
   `gpg-subkeys.asc`. As with the master key, adjust the parameters as you
   want. (Note: `--export-secret-subkeys` is a GNU-specific extension to PGP and
   so might not work, export- or import-wise, with non GPG programs. This is why
   we export both.)
3. Copy the resulting files to your secure backup drives.

**Verify that your backups actually work!** You should repeat these steps for
the files you just created, and for each one on the backup drives to check that
they were not corrupted during copying.
1. Create a temporary directory somewhere (I tend to use `$HOME/gpg_tmp` and
   will be assuming that in the rest of this) and `chmod` it to permissions
   `700`.
2. Run
   ```sh
   gpg --homedir="$HOME/gpg_tmp" -K
   ```
   twice to have GPG set up the right files and so you can confirm that the
   secret keys are not in the temporary directory.
3. Run
   ```sh
   gpg --homedir="$HOME/gpg_tmp" --import gpg-subkeys.asc
   ```
   to import the subkeys. Then verify that they're there but, crucially, that
   the master key is not by running
   ```sh
   gpg --homedir="$HOME/gpg_tmp" -K
   ```
   You should see all the keys, but the master key should have a hash symbol (#)
   after it, indicating that it is offline.
4. Run
   ```sh
   gpg --homedir="$HOME/gpg_tmp" --import gpg-masterkey.asc
   ```
   to import the masterkey. Then verify that the hash sign no longer appears
   when running
   ```sh
   gpg --homedir="$HOME/gpg_tmp" -K
   ```
   You can also verify that all the keys import when importing the
   `gpg-masterkey.asc` file by removing the directory and start again, skipping
   step 3.
5. Just to be completely safe/paranoid, `shred` all the files in the directory
   by triple-checking that the command below points to the right directory and
   then running it
   ```sh
   find "$HOME/gpg_tmp" -type f -exec shred "{}" \;
   ```
   (this requires `find` and `shred` installed. If you don't have these, either
   install them, use something similar, or don't worry about deleting the files
   that thoroughly). Then, being very careful, run
   ```sh
   rm -rf "$HOME/gpg_tmp"
   ```
   to remove the temporary directory and its contents.
6. As mentioned just before this list, repeat 1-5 for each of the copies of the
   files on the different backup drives.

For additional sanity, perform some operations without the `--homedir` flag
(e.g. encrypt some files) and then try to decrypt them before and after
importing the keys to the temporary directory (making sure to specify
`--homedir` with each of the decryption commands).

Now, depending on how "last resort" you want the backups to be, I would suggest
writing down the passphrase(s) for the keys and drives and storing these as
well. This means that you have a way of getting back in, should everything fail,
including you remembering your passphrase(s). Store these drives safely, ideally
storing at least one in a physically separate location you have access to, and
take them out once a year or something and re-confirm that the backups still
work. Having offsite backups can be a bit trickier as a private person, but one
option, if you have a cloud storage subscription, could be to create a
[VeraCrypt](https://veracrypt.fr/en/Home.html) volume as a file, storing the
backup files in it, and then upload the volume file to your cloud service. I'm
not 100% certain, but I can't immediately see why that shouldn't be safe.

Finally, in terms of the smartcard/token that needs replacing, buy **at least
2** new ones. I made the mistake of buying only one because I was impatient and
didn't want to wait until I could afford to buy 2. If you don't have the money
immediately, save up and buy 2 when you can do that, because it is not worth
having one break at a critical moment and being without a replacement.
Especially in a case like mine where the backups turned out to be slightly
misconfigured. Sure, the guide above minimises the risk of error in the backups,
but it can still happen and there is little gained for the much greater risk
that comes with not having a backup smartcard.

### Remember to update things

Given that you have just rotated all your subkeys, make sure to update anywhere
you used them. In my case, this was mainly Thunderbird and GitHub (and hence my
local `.gitconfig`), but wherever you've used and/or published your public key,
those places now need to be updated with your new public key. You can export it
as normal by running

```sh
gpg --output pubkey.asc --export <keyid>
```

(with `--armor` as the first flag, if you want it as plain ASCII), and then
uploading/distributing/emailing/etc the `pubkey.asc` file.

Annoying little sidenote about GitHub: It doesn't seem to have a concept of
subkeys, so I had to replace the entire GPG key because it thought I was
re-uploading the same one. This unfortunately means that my old commits,
although still sane and signed, appear as `unverified` on GitHub, because it
doesn't handle revoked subkeys (see
[this](https://github.com/isaacs/github/issues/1099) and
[this](https://github.community/t/gpg-pgp-subkey-rotation-revocation-and-verified-commits/183845)
for some discussion on the topic). If you need to, I believe you can verify them
locally by downloading
[my old public key](/files/2020-08-09_pubkey.asc).

### Summary of lessons learnt

- There's a reason most companies and people advise you to buy two
  smartcards/hardware tokens. Be smart and follow that advice, don't think
  you'll be fine with just one.
- Keep more than one backup and make sure you know where those backups are.
- Test your backups regularly to make sure they haven't been corrupted and/or
  that you haven't lost the memory of how they work.
- If you're being clever with passwords or encryption schemes, make sure you're
  being clever in a way that future you will be able to work out. Hacking your
  past self is fun, but only for so long/when your emails+data are not on the
  line.
- Optionally, make a "last resort/golden key" backup which contains _all_ the
  information to completely unlock everything. Then, store this in the most
  secure location you have. It can be risky, but it might also be what saves you
  if you've entirely forgotten (or lost) your passwords and setup.

As always, thanks for reading. If not entertaining, I hope that it could at
least be somewhat educational as to what _not_ to do ^^;


### P.S.: The wonders of technology

Nitrokey's support team got back saying it sounded like a hardware fault,
especially since the keys were supposed to last 5-10 years under daily use, but
that just to be certain, I should try plugging it in to a different computer if
I had one. I didn't think it would make a difference, but for some reason it
did: The red LED lit up and the card seemed to work as normal. Since this, it
has been working as normal without any hickups whatsoever. Isn't technology
marvellous? -_-

This didn't change much, since I'd already rotated keys and everything at this
point, but it did at least allow me to recover some encrypted files that I
thought I had lost the keys to forever. And despite reporting this back,
Nitrokey still offered to replace the smartcard, just to be on the safe side,
which I think is awesome! So 5/7, a perfect score, I guess: I learnt some
important lessons, didn't entirely permanently lose my data, and I found out
Nitrokey makes good hardware and have a great support team.

