---
# Documentation: https://docs.hugoblox.com/managing-content/

title: "Auto Plotting Thesis Word Count"
subtitle: ""
summary: ""
authors: [thomas-e-hansen]
tags: [automation,gh-actions,ci,infovis]
categories: [sprout]
date: 2024-03-18
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

Procrastination time! By inspiration from my supervisor, who told me he did a
similar thing to procrastinate his thesis writing, I've decided to write a tiny
thing that automatically plots the word count of my thesis on a nightly basis.
In addition to being a fun little exercise, it'll probably also serve as a good
motivator / guilt mechanism to keep me writing  ^^;;


## What

* Wowchemy/HugoBlox w plotly json
* bc easy
* could have done PNG from some other thing, but that's less easy + nice to
    store

## How

* Edwin: cron job
* Don't have a server or permanently on machine which can write to my GH, so GH
    actions it is

* Considered triggering from push to thesis repo
* then looked into actions and discovered `scheduled`
  - well that seems convenient!

1. schedule nightly
   ```yaml
    on:
      schedule:
        - cron: '55 23 * * 1-5'
    ```
  - Oh look at that! It is `cron` after all!
  - 55th minute, 23rd hour, all days, all months, Monday-Friday (to avoid empty
      spaces on weekends; we'll see how long I can keep that up...)
  - 0-6 with 0 := Sunday and 6 := Saturday -- disgusting, but here we are
  - cron input files are really readably documented:
      [https://pubs.opengroup.org/onlinepubs/9699919799/utilities/crontab.html#tag_20_25_07](https://pubs.opengroup.org/onlinepubs/9699919799/utilities/crontab.html#tag_20_25_07)
2. clone (curr.y private) thesis repo
  - Some stuff w. Personal Access Tokens (PATs)
3. run the xwcount script to get current word count
4. subtract previous word count from today's
5. load data into python
6. plot
7. dump the plot into json


## Python

* plotly
  - saves me dumping the data into the right JSON format by hand
* setup-python action
  - caches things
* install dependencies
  - plotly for graphs and its json output
  - pandas for data reading, of course
* can we plot the words?
  - yes (assuming we've remembered to have a header line in the csv)
* what about the word-diff?
  - need the diff between each day, i.e. each row/entry
  - pandas has a function for this: `diff`! fantastic!  ^^
  - now we can also plot that
* okay, can we combine the two plots?
  - quick ddg search later: yes
  - the magic word is "subplots"
  - `from plotly.subplots import make_subplots`
* subplotting
  - dates are the same: `shared_xaxes=True` --- actually, scratch that; not as
      easily readable as I'd hoped / worth duplicating that data imo
  - one plot above the other: `rows=2, cols=1`
  - probably good to have some vertical spacing (remembering to fit the labels):
      `vertical_spacing=0.05`
  - need to "graph objects" instead of 'raw' express plots, it seems:
      `import plotly.graph_objects as go`
  - graph objects take an x and y series or dictionary, not a dataframe with x/y
      being keys into the dataframe
  - and there is a whole bunch of shenanigans to label the axes
  - At least not as bad as matplotlib -- eyoo


## Adding plot to website

* It is apparently easy: https://docs.hugoblox.com/reference/markdown/#charts
* It is never just easy.
  - Plotly docs: `print(fig)`
  - `Error: cannot access "data", chart is null`
* First look at the JSON: okay, the `Figure(...)` bit is not JSON, but I assumed
    it was a Plotly thing. Clearly not, rm that.
  - Still errors. Shoot.
* Opening the JSON in vim again: "Huh. The fields are single-quoted, resulting
    in them being highlighted in red. And it stops highlighting them when I
    change it to double-quotes. That's got to be it. And there's got to be a way
    to output 'correct' JSON"
* Plotly docs: "Figures also support `fig.to_json()`"
  - ohreally.png
  - `print(fig.to_json())`
  - well that looks a lot better!
* And now it works!

