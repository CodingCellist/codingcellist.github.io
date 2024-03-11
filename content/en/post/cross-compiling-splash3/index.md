---
# Documentation: https://wowchemy.com/docs/managing-content/

title: "Cross-Compiling Splash-3"
subtitle: "How to cross-compile the Splash-3 benchmark for use with gem5"
summary: "Cross-compiling can be a bit difficult to put it mildly. This should
          hopefully be straightforward to follow and help you if you're looking
          to cross-compile Splash-3 for use with gem5 or a similar simulator."
authors: [thomas-e-hansen]
tags: [cross-compiling, benchmarks, simulation, gem5, ARMv8]
categories: []  # [guide, gem5]
date: 2021-03-10
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

Something happened which I never thought would: Someone was trying to use my
MSci project for similar work. I always assumed the project would only ever be
read by my supervisor and the second marker, so having someone else be
interested was really exciting!

As part of this, the person ran into the same problems I had, e.g. gem5 can be
finicky to set up, configuring the Linux kernel is a daunting task, and
cross-compiling is more like repeatedly hitting things with a hammer until it
eventually (hopefully) works.

When I was doing my MSci project, I used the
[Splash-3](https://github.com/sakalisc/splash-3) benchmark. However, I also
cheated a bit in terms of cross-compiling it: I had a native ARMv8 dev-board
available which, when cross-compiling got difficult, I used to compile the
benchmark and then simply copied over the files, thereby avoiding
cross-compiling altogether.  This is obviously not always an option, so I
decided to have a more serious go at trying to get this working. After all,
papers seemed to use it with similar setups to mine, so it had to be possible,
right?


### Preparation and initial setup

Before we get started, the following setup is assumed:

- OS: Linux of some variant
- Guest platform (where we are cross-compiling from): x86_64
- Host platform (where we are cross-compiling to): ARMv8
- Some sort of cross-compiling toolchain, e.g. the
    [GNU cross-toolchain for A-profile cores](https://developer.arm.com/tools-and-software/open-source-software/developer-tools/gnu-toolchain/gnu-a/downloads),
    stored in its own directory (I keep mine in `$HOME/xtools`).

For convenience, I also like to
```bash
export ARMv8_XTOOLS="$HOME/xtools/gcc-arm-10.2-2020.11-x86_64-aarch64-none-linux-gnu/bin/aarch64-none-linux-gnu-"
```
which defines an environment variable `ARMv8_XTOOLS` to more easily be able to
access the toolchain. (The exact value will be different if you're using a
different cross-compiling toolchain). With this, to run `gcc` simply run:

```bash
$ ${ARMv8_XTOOLS}gcc --version
```

It should give you:

```none
aarch64-none-linux-gnu-gcc (GNU Toolchain for the A-profile Architecture 10.2-2020.11 (arm-10.16)) 10.2.1 20201103
Copyright (C) 2020 Free Software Foundation, Inc.
This is free software; see the source for copying conditions.  There is NO
warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
```

Clone the Splash-3 benchmark and `cd` into the top directory:

```bash
$ git clone git@github.com:SakalisC/Splash-3
$ cd Splash-3
```

You used to have to make some changes to a number of Makefiles, but this has
been fixed as of [this PR](https://github.com/SakalisC/Splash-3/pull/12) and
so the repository should be mostly be good to go immediately. However, the
`volrend` benchmark is extra finicky to get working, so we need to do something
else first.


### Cross-compiling `libtiff`

The `volrend` benchmark relies on `libtiff`. Unfortunately, the version included
with Splash-3 does not like being cross-compiled. This can be fixed by
downloading and cross-compiling a version from the official website (thanks to
[Chris Sakalis](https://github.com/SakalisC/Splash-3/pull/12#issuecomment-792714144)
for that idea).

From the root of the Splash-3 repo, start by `cd`-ing into the
`codes/apps/volrend/` directory. Then download, copy, and unzip a recent version
of `libtiff` from
[the official download page](https://download.osgeo.org/libtiff/).

This extracts a `tiff-`_`version`_ directory, which I like to rename to
`libtiff-`_`version`_, just to keep things consistent:

```bash
$ mv -v {,lib}tiff-<version>
$ cd libtiff-<version>
```

(Replacing `<version>` with the version number you downloaded.)

Create an install directory in which to put the cross-compiled library (the name
doesn't matter, as long as you keep it consistent):

```bash
$ mkdir install_dir
```

To configure `libtiff` for cross-compiling, without shared libraries, and using
a custom install path, run:

```bash
$ PATH="$(dirname ${ARMv8_XTOOLS}):${PATH}" \
    ./configure --disable-shared --host="aarch64-none-linux-gnu" \
    prefix="${PWD}/install_dir" exec_prefix="${PWD}/install_dir"
```

Explanation:

- `PATH="$(dirname ${ARMv8_XTOOLS}):${PATH}"` -- sets the `PATH` (where the
    shell looks for executables, checking the first path first) to include the
    cross-compile toolchain directory (obtained using `dirname`). We could
    `export` this new `PATH` and then restore it when we're done, but since it's
    only for a couple of instructions, I prefer to do this.
- `./configure` -- runs the included `configure` script.
- `--disable-shared` -- disables the use of shared libraries. This can be
    critical for use with things like gem5 where the shared libraries may not be
    available on the virtual disk.
- `--host="aarch64-none-linux-gnu"` -- specifies the name of the platform we are
    cross-compiling for. A useful hint is the prefix of all the executables in
    the cross-compile toolchain.
- `prefix="${PWD}/install_dir" exec_prefix="${PWD}/install_dir"` -- specifies
    that we want the results to be installed in the `install_dir` directory in
    the current directory.

Then, to actually compile and install, run:

```bash
$ PATH="$(dirname ${ARMv8_XTOOLS}):${PATH}" \
    make prefix="${PWD}/install_dir" exec_prefix="${PWD}/install_dir"

$ PATH="$(dirname ${ARMv8_XTOOLS}):${PATH}" \
    make install prefix="${PWD}/install_dir" exec_prefix="${PWD}/install_dir"
```

Depending on your hardware, the initial `make` may take a couple of minutes.


### Patching `volrend`

To use the new `libtiff` with `volrend`, we need to make a couple of changes:

- If you haven't already, `cd` back up from `libtiff-<version>` to `volrend`:
    ```bash
    $ cd ..
    ```
- Delete (or move, if you prefer that) the **old** `libtiff`:
    ```bash
    $ rm -rf libtiff
    ```
    (**note the omission of** `<version>`**, do not delete your new version!**)
- Create a symlink to the custom `libtiff` install directory so that
    `volrend` still finds the expected libraries (this is slightly hacky, but it
    works):
    ```bash
    $ ln -sv libtiff-<version>/install_dir/lib libtiff
    ```
- Modify the `volrend` Makefile to not destroy the work we just did, and to
    correctly compile and link against the new `libtiff`:
    - Remove `libtiff/libtiff.a` from `OBJS`.
    - In `CFLAGS`, change `-I./libtiff` to `-I./libtiff/../include` (not the
        prettiest, I know; feel free to leave a comment in the website repo
        discussion if you have a better idea) and append to the end of line:
        `-ltiff -lm`.
    - In `LDFLAGS`, append to the end of the line: `-lm`.
    - Remove the `libtiff/libtiff.a` target and its recipe.
    - Add an `all` target depending on `$(OBJS)` which compiles `VOLREND`:
        ```makefile
        all: $(OBJS)
          $(MAKE) VOLREND
        ```
    - Remove the `$(MAKE) -C libtiff clean` line from the `clean` target's
      recipe.
    - (If you feel unsure about making the changes above yourself,
        [here is a patch](/uploads/splash3-volrend-makefile-patch.diff) you can apply
        by copying it to the `codes` directory and running
        ```bash
        $ patch -p0 < splash3-volrend-makefile-patch.diff
        ```
        from the `codes` directory.)


### Cross-compiling Splash-3 (finally)

Having configured and cross-compiled an entirely different, but necessary, thing
and made some modifications to integrate it, we can now finally cross-compile
Splash-3.

If you haven't already, `cd` back up to the `codes` directory.

As with `libtiff`, we need to disable shared libraries since they may not be
available on gem5. To do this, append `-static` to `CFLAGS` in
`Makefile.config`.

Now we then get to reap the fruits of doing the tedious setup: Just run

```bash
$ TOOLCHAIN_PREFIX="${ARMv8_XTOOLS}" make
```

And everything should (hopefully) just compile nicely.


I hope this was helpful. Trying to figure out other people's build process in
order to do something slightly convoluted can be frustrating, but then finally
seeing the `make` output just scroll by without any problems is great!  ^^

