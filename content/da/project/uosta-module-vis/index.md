---
# Documentation: https://sourcethemes.com/academic/docs/managing-content/

title: "University of St Andrews kursus-visualisering"
summary: "Et forsøg på, at visualisere forholdene mellem kurserne ved University
          of St Andrews."
authors: [thomas-e-hansen]
tags: [visualisation, internship]
categories: [internships, erfaring, da]
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
 - name: Se hele projektet på GitHub
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

# Oversigt
Målet med dette projekt var, at gøre det lettere at navigere og forstå
University of St Andrews' "undergraduate" (Bachelor- og Kandidat-niveau)
kursuskatalog. I øjeblikket er kataloget en samling af PDF-dokumenter: et per
fakultet og per "sub-honours" (første og andet år) og "honours" (tredje og
fjerde år) kurser som fakultet tilbyder. Dette gør det svært for studerende og
studievejledere, at finde ud af hvilke kurser de studerende burde tage. Desuden
har listerne i PDF-dokumenterne, ingen angivelse af, hvilke konsekvenser de
forskellige kursusvalg kan have. For eksempel: hvis en studerende ikke tager
2000-niveau (2. år) kurset om netværk på datalogi, så fører det til, at de ikke
kan tage CS3102 på tredje år. Dette resulterer videre i, at de ikke kan tage
hverken CS4103, CS4105, CS4302 eller CS5022, på grund af en dominoeffekt af
forudsætninger. Disse konsekvenser af, ikke at tage et specifikt kursus på andet
år, er besværligt at finde ud af ud fra PDF-dokumenterne. Man ville på andet år
skulle kigge både alle tredje- og fjerde-års kurserne igennem, hvilket er kurser
der kun kan ses i en anden PDF, end den den studerende ville have åben, når de
forsøgte at planlægge deres andet år.

Med "joint-honours" (uddannelser med 2 eller 3 hovedfag, f.eks. BSc i datalogi
og fysik) er det endnu sværere at hitte rundt i, takket være en øget varietet
af påkrævede kurser til hovedfagskombinationerne (som kan være på tværs af det
naturvidenskabelige og humaniora). Og alt dette oven i kurser som den
studerende derudover kunne være interesseret i at tage.

Målet med dette projekts var derfor, at løse disse problemer, eller i det
mindste at gøre det nemmere at planlægge uddannelsesforløbet, ved at
visualisere kurserne og deres krav som et netværk/en graf af punkter og kanter.
Projektet involverede design af en database, til at opbevare kursusdetaljerne
i, fordi universitetet aldrig svarede på anmodninger om adgang til deres
database. Det var ikke indlysende, at designe databasen, fordi den skulle kunne
opbevare krav formuleret på Konjunktiv Normalform. Det viser sig, at KN er svær
at modellere i relationelle databaser. Projektet involverede også design af
visualiseringer, for bedst at kunne illustrere forholdene mellem de forskellige
kurser. Ved udgangen af projektet var det lykkedes, at fremstille et
"proof-of-concept" samt en detaljeret rapport til brug af studerende i
fremtiden, så projektet kunne videreføres.

Projektet kan ses på GitHub og er udgivet under GPLv3-licens. Den endelige
rapport kan downloades fra GitHub, eller øverst her på siden.

# Tak til
- Dr. Dharini Balasubramaniam, for at have foreslået og overset projektet
- Dr. Ruth Letham, for hjælp med designet af databasen
- Alice Lynch, for udvikling af skelettet til diverse web-scrapers
- Iain Carson, for hjælp med D3 og `returnNodes` funktionen
- Dr. Uta Hinrichs, for feedback og ideer angående forskellige
  visualiseringsdesigns

