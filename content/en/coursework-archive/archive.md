---
# An instance of the Portfolio widget.
# Documentation: https://wowchemy.com/docs/page-builder/
widget: portfolio

# This file represents a page section.
headless: true

# Order that this section appears on the page.
weight: 10

title: Coursework Archive
subtitle: 'Reports, essays, and github repos of coursework from my undergrad.<br>
           Out of respect for the academics who ran the modules and due to the UoStA "Good
           Academic Practice" policy, only coursework which I have explicitly obtained
           permission to publish has been published. I may be able to provide examples of
           other coursework on request, if you are not a student.
          '

content:
  # Page type to display. E.g. project.
  page_type: coursework

  # Default filter index (e.g. 0 corresponds to the first `filter_button` instance below).
  filter_default: 0

  # Filter toolbar (optional).
  # Add or remove as many filters (`filter_button` instances) as you like.
  # To show all items, set `tag` to "*".
  # To filter by a specific tag, set `tag` to an existing tag name.
  # To remove the toolbar, delete the entire `filter_button` block.
  filter_button:
  - name: All
    tag: '*'
  - name: Masters (5th year)
    tag: MSci coursework
  - name: Senior Honours (4th year)
    tag: SH coursework
  - name: Architecture
    tag: CS4202 Computer Architecture
  - name: Security
    tag: CS4203 Computer Security

design:
  # Choose how many columns the section has. Valid values: '1' or '2'.
  columns: '2'

  # Toggle between the various page layout types.
  #   1 = List
  #   2 = Compact
  #   3 = Card
  #   5 = Showcase
  view: 2

  # For Showcase view, flip alternate rows?
  flip_alt_rows: false
---

