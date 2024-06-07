---
# Documentation: https://docs.hugoblox.com/managing-content/

title: "First Go at Tildagon Development"
subtitle: ""
summary: ""
authors: [thomas-e-hansen]
tags: [emf2024,esp32,tildagon]
categories: [sprout]
date: 2024-06-05
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

The "Tildagon" is the badge which was first available at
[EMF 2024](https://emfcamp.org)
(which went to and also
[~~wrote~~ enthused about](/en/post/emf2024-was-incredible)).
It has an ESP32-S3 microcontroller, two USB-C ports, 6 "hexpansion" ports, and a
bunch of buttons and LEDs. Time to see what we can do with it!

## Flashing new firmware

First hurdle is to flash the latest firmware onto the badge. As per
[the documentation](https://tildagon.badge.emfcamp.org/using-the-badge/end-user-manual/#flash-your-badge)
this should be fairly straightforward. However -- as you may be familiar with if
you've read
[other](/en/post/adventures-in-linux-boot-debugging)
[posts](/en/post/recovering-from-a-broken-smartcard)
[here](/en/post/dualboot-arch-windows-encrypted) --
things are rarely straightforward on this hell of a system of my own creation
^^;;

And indeed, the first thing that happened was a "Failed to execute `open` on
`ttyACM0`: failed to open serial port" error. Well then. What info can we get
about `ttyACM0`?

```
$ ls -l /dev/ttyACM0
crw-rw---- 1 root uucp 166, 0 Jun  5 22:03 /dev/ttyACM0
```

Aha! That probably explains things: I am not in the `uucp` group, which might be
a problem. One

```
$ sudo usermod -aG uucp thomas
```

and a quick restart of my X session later (not sure if that was necessary, but
just restarting the browser didn't seem to fix things) the web flasher was a lot
happier. I even got this exciting diff of messages on `dmesg`:

### dmesg before:

```log
[ 1922.020701] cdc_acm 1-2:1.0: ttyACM0: USB ACM device
[ 2034.564555] usb 1-2: USB disconnect, device number 9
[ 2042.866145] usb 1-2: new full-speed USB device number 10 using xhci_hcd
[ 2043.007865] usb 1-2: New USB device found, idVendor=303a, idProduct=1001, bcdDevice= 1.01
[ 2043.007881] usb 1-2: New USB device strings: Mfr=1, Product=2, SerialNumber=3
[ 2043.007887] usb 1-2: Product: USB JTAG/serial debug unit
[ 2043.007892] usb 1-2: Manufacturer: Espressif
[ 2043.007897] usb 1-2: SerialNumber: 64:E8:33:72:09:64
```

### dmesg after:

```log
[ 2043.010922] cdc_acm 1-2:1.0: ttyACM0: USB ACM device
[ 2044.782506] usb 1-2: USB disconnect, device number 10
[ 2045.072881] usb 1-2: new full-speed USB device number 11 using xhci_hcd
[ 2045.224475] usb 1-2: New USB device found, idVendor=16d0, idProduct=120e, bcdDevice= 1.00
[ 2045.224491] usb 1-2: New USB device strings: Mfr=1, Product=2, SerialNumber=3
[ 2045.224498] usb 1-2: Product: TiLDAGON
[ 2045.224504] usb 1-2: Manufacturer: Electromagnetic Field
[ 2045.224509] usb 1-2: SerialNumber: 123456
```

Look at that! We now have the product correctly declared as "TilDAGON", the
manufacturer as "Electromagnetic Field", and the serial number as
~~nonsense~~ 123456. Neat!


## Setting up for simulation

Rather than running a buggy app directly on the hardware, the
[Tildagon software repo](https://github.com:emfcamp/badge-2024-software)
comes with a handy simulator. Once again however, I need to slightly change
things:

* It turns out I'm missing some libraries: `wasmer` -- "Universal Binaries
    Powered by WebAssembly". That one is easily fixable via `pacman -S
    wasmer`, thankfully.
* Unfortunately `pipenv` does not and will never support version ranges
    ([pipenv#1050](https://github.com/pypa/pipenv/issues/1050)), and `wasmer`
    wheels currently only build for up to `python3.10` (Arch ships `3.12.3` at
    the time of writing).  
    *sigh*  
    Turns out however, that `pyenv` is a thing which a allows you to easily
    manage multiple python installations. Well, somewhat easily: after running
    ```
    $ pyenv install 3.10 && pyenv local 3.10
    ```
    you then use the configured version by wrapping the command in `pyenv exec`.
    Not exactly seamless, but better than nothing I guess. It does lead to this
    mildly ridiculous invocation:
    ```
    $ pyenv exec pipenv run python run.py
    ```
    "Yo dawg, I heard you like running things, so I put running things in your
    things that run things."

At last, the simulator successfully runs.

