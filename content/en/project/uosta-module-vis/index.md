---
# Documentation: https://sourcethemes.com/academic/docs/managing-content/

title: "University of St Andrews Module Visualisation"
summary: "An attempt at visualising the UG modules and requisites at the University of St Andrews."
authors: [thomas-e-hansen]
tags: [visualisation, internship]
categories: [internships, experience, en]
date: 2019-09-17T13:26:00+02:00

# Optional external URL for project (replaces project detail page).
external_link: ""

# Featured image
# To use, add an image named `featured.jpg/png` to your page's folder.
# Focal points: Smart, Center, TopLeft, Top, TopRight, Left, Right, BottomLeft, Bottom, BottomRight.
image:
  caption: ""
  focal_point: ""
  preview_only: false

# Custom links (optional).
#   Uncomment and edit lines below to show custom links.
links:
 - name: Full project on GitHub
   url: https://github.com/CodingCellist/UoStA-Module-Vis-2019
   icon_pack: fab
   icon: github

url_code: ""
url_pdf: "https://raw.githubusercontent.com/CodingCellist/UoStA-Module-Vis-2019/master/REPORT.pdf"
url_slides: ""
url_video: ""

# Slides (optional).
#   Associate this project with Markdown slides.
#   Simply enter your slide deck's filename without extension.
#   E.g. `slides = "example-slides"` references `content/slides/example-slides.md`.
#   Otherwise, set `slides = ""`.
slides: ""
---

# Overview
The aim of this project was to facilitate navigation and understanding of the
University of St Andrews undergraduate course catalogue. In its current form,
the course catalogue is a collection of PDF-documents split up by school and by
sub-honours and honours level. This makes it difficult for students and advisers
alike to figure out what modules students should be taking. Further complicating
the matter is that the list of tables in the PDFs give no indication of what
consequences module choices will have. For example not taking the 2000-level
networking module in Computer Science leads to not being able to take CS3102,
which further leads to not being able to take CS4103, CS4105, CS4302, and
CS5022, due to the "chaining" of pre-requisites. This consequence of not taking
a second-year, sub-honours module is cumbersome to figure out based on the PDFs,
as one would need to look through all the honours modules in second year, well
beyond the modules relevant for that year or even the next one, whichare listed
in a separate document from the one the student would be looking at, i.e. the
sub-honours document(s).

With joint honours, the difficulty increases even more, due to the large variety
of required modules for the programme in combination with the requirements of
other modules the student might be interested in.

This project aimed to solve these issues, or at least facilitate the planning
process, by visualising the modules and their requisites as a network of nodes
and edges respectively. It involved designing a database to store the module
information in, since the university never responded to requests for access to
their database. The database design was not trivial, as it had to be able to
store requirements in Conjunctive Normal Form, something which it turns out
relational databases do not lend themselves to nicely. The project also involved
designing visualisations in order to best show the relationships between
modules. In the end, a proof-of-concept was produced, along with an extensive
report which should allow future students to extend the project.

The project can be found on GitHub and is licensed under GPLv3. The final report
can be downloaded from GitHub or the top of this page.

# Acknowledgements
- Dr. Dharini Balasubramaniam, for creating and supervising this project  
- Dr. Ruth Letham, for help with the database design  
- Ms. Alice Lynch, for writing the base of the web-scrapers  
- Mr. Iain Carson, for help with D3 and the `returnNodes` method  
- Dr. Uta Hinrichs, for feedback and ideas concerning the visualisation
  designs

