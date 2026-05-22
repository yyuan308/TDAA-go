// Advanced Learning Sheet Template Library
// Research-track companion to learning-sheet.typ — adds gedanken,
// pause-and-think, wrong-path, author's take, margin notes, highlights,
// and an appendix Q&A system.
//
// Usage:
//   #import "../templates/advanced-learning-sheet.typ": *
//   #show: advanced-learning-sheet-template.with(week: 8, title: "Topic Title")
//   // ... content ...

#import "@preview/fletcher:0.5.8" as fletcher: diagram, node, edge
#import "@preview/ctheorems:1.1.3": *
#import "../config.typ": course-code, course-name

// =============================================================================
// PALETTE — Deep indigo
// =============================================================================

#let accent-color = rgb("#1a237e")
#let accent-light = rgb("#e8eaf6")
#let wrong-path-fill = rgb("#fbe9e7")
#let wrong-path-stroke = rgb("#d32f2f")
#let gedanken-fill = rgb("#fff8e1")
#let gedanken-stroke = rgb("#f9a825")
#let opinion-fill = rgb("#e8eaf6")
#let pause-fill = rgb("#e0f2f1")

// =============================================================================
// THEOREM ENVIRONMENTS
// =============================================================================

#let definition = thmbox("definition", "Definition", base: none,
  fill: accent-light, stroke: none, inset: (x: 12pt, y: 10pt))
#let theorem = thmbox("theorem", "Theorem", base: none,
  fill: accent-light, stroke: none, inset: (x: 12pt, y: 10pt))
#let lemma = thmbox("lemma", "Lemma", base: none,
  fill: accent-light, stroke: none, inset: (x: 12pt, y: 10pt))
#let proof = thmproof("proof", "Proof")

// Key-result box for non-axiomatic courses (physics, engineering, empirical
// sciences). Same styling as `theorem`; intended for named laws / postulates
// / principles. Pair with `derivation` instead of `proof` when relevant.
#let keyresult = thmbox("keyresult", "Key Result", base: none,
  fill: accent-light, stroke: none, inset: (x: 12pt, y: 10pt))
#let derivation = thmproof("derivation", "Derivation")

#let example(title, body) = block(
  width: 100%, inset: (left: 0pt, y: 8pt),
  stroke: none
)[
  #text(weight: "bold")[Example (#title).] #body
]

#let remark(body) = block(
  width: 100%, inset: (left: 16pt, y: 8pt),
  stroke: (left: 2pt + accent-color)
)[
  #text(weight: "bold")[Remark.] #body
]

// =============================================================================
// NEW ENVIRONMENTS
// =============================================================================

// Toggle with: typst compile --root . --input invert-solution=false ...
#let invert-solution = {
  let val = sys.inputs.at("invert-solution", default: "true")
  val == "true"
}
#let _invert = invert-solution

// 1. Gedankenexperiment — dashed amber border, warm fill
#let gedankenexperiment(title, body) = block(
  width: 100%,
  fill: gedanken-fill,
  stroke: (
    dash: "dashed",
    paint: gedanken-stroke,
    thickness: 1.5pt,
  ),
  inset: 12pt,
  radius: 4pt,
)[
  #text(weight: "bold", fill: gedanken-stroke)[Gedankenexperiment: #title]
  #v(4pt)
  #body
]

// 2. Pause-and-Think — teal left border, three-part structure.
// Answer is shown upside-down by default (invert-solution=true).
#let pause-and-think(question, hint, answer) = block(
  width: 100%,
  fill: pause-fill,
  stroke: (left: 3pt + rgb("#00897b")),
  inset: (left: 12pt, right: 12pt, y: 10pt),
  radius: (right: 4pt),
)[
  #text(weight: "bold", fill: rgb("#00897b"))[Pause and Think]
  #v(4pt)
  #question
  #v(6pt)
  #text(size: 9pt, fill: luma(100))[_Hint:_ #hint]
  #v(6pt)
  #block(
    width: 100%,
    inset: (left: 10pt, y: 6pt),
    stroke: (left: 1pt + luma(180)),
  )[
    #if _invert [
      #scale(x: -100%, y: -100%)[#text(size: 9.5pt)[#answer]]
    ] else [
      #text(size: 9.5pt)[#answer]
    ]
  ]
]

// 3. Wrong Path — red left border, red-tinted fill
#let wrong-path(title, body) = block(
  width: 100%,
  fill: wrong-path-fill,
  stroke: (left: 3pt + wrong-path-stroke),
  inset: (left: 12pt, right: 12pt, y: 10pt),
  radius: (right: 4pt),
)[
  #text(weight: "bold", fill: wrong-path-stroke)[Wrong Path: #title]
  #v(4pt)
  #body
]

// 4. Author's Take — indigo left bar, italicized body
#let authors-take(body) = block(
  width: 100%,
  fill: opinion-fill,
  stroke: (left: 3pt + accent-color),
  inset: (left: 12pt, right: 12pt, y: 10pt),
  radius: (right: 4pt),
)[
  #text(weight: "bold", fill: accent-color)[The Author's Take]
  #v(4pt)
  #emph[#body]
]

// =============================================================================
// MARGIN NOTE SYSTEM — stateful, non-overlapping
// =============================================================================

// Tracks the bottom y-coordinate of the last margin note (page-relative).
#let _margin-bottom = state("margin-bottom", 0pt)

#let margin-note(body) = context {
  let note = block(width: 2.8cm, text(size: 8pt, fill: luma(100))[#body])
  let note-height = measure(note).height
  let here-y = here().position().y
  let prev = _margin-bottom.get()
  // Detect page break: if current y is far above the previous note's bottom,
  // we must be on a new page — reset and place at natural position.
  let on-new-page = prev > here-y + 200pt
  let target-y = if on-new-page or here-y >= prev { here-y } else { prev }
  let dy = target-y - here-y
  place(dx: 100% + 0.3cm, dy: dy, note)
  _margin-bottom.update(target-y + note-height + 6pt)
}

// =============================================================================
// HELPERS
// =============================================================================

// Challenge box — indigo-accented opening challenge (replaces task-box)
#let challenge-box(body) = block(
  width: 100%,
  stroke: 1.5pt + accent-color,
  inset: 12pt,
  radius: 5pt,
  fill: accent-light,
)[#body]

// Annotated bibliography entry
#let reading-entry(source, annotation) = block(
  width: 100%, inset: (left: 16pt, y: 4pt),
  stroke: none,
)[
  #text(weight: "bold")[#source] \
  #text(size: 9.5pt, fill: luma(80))[#annotation]
]

// AI prompt block
#let prompt(body) = block(
  width: 100%, fill: rgb("#f7f7f7"), inset: 12pt, radius: 0pt,
  stroke: (top: 2pt + accent-color)
)[#body]

// AI prompt badges
#let badge-deeper = box(fill: rgb("#e8f5e9"), inset: (x: 4pt, y: 2pt), radius: 2pt,
  text(size: 7pt, fill: rgb("#2e7d32"), weight: "bold")[DEEPER])
#let badge-broader = box(fill: rgb("#e3f2fd"), inset: (x: 4pt, y: 2pt), radius: 2pt,
  text(size: 7pt, fill: rgb("#1565c0"), weight: "bold")[BROADER])
#let badge-research = box(fill: rgb("#f3e5f5"), inset: (x: 4pt, y: 2pt), radius: 2pt,
  text(size: 7pt, fill: rgb("#7b1fa2"), weight: "bold")[RESEARCH])

// Unified state node for automata diagrams
#let state(pos, label, name: none, accept: false, fill: none) = node(
  pos, label, shape: circle, name: name, radius: 1.5em,
  extrude: if accept { (0, -4) } else { (0, 0) },
  fill: fill
)

// Python code block
#let pythoncode(body) = block(
  width: 100%, fill: rgb("#f5f5f5"),
  inset: 10pt, radius: 0pt,
  stroke: (y: 0.5pt + luma(200))
)[#body]

#let hide-section = true

// =============================================================================
// HIGHLIGHT SYSTEM — toggled by compile-time variable show-highlights
// =============================================================================

// Toggle with: typst compile --root . --input show-highlights=false ...
#let show-highlights = {
  let val = sys.inputs.at("show-highlights", default: "true")
  val == "true"
}

#let hl(body) = if show-highlights {
  highlight(fill: yellow)[#body]
} else {
  body
}

// =============================================================================
// USER-QUESTION SYSTEM — margin notes with appendix cross-references
// =============================================================================

// Insert a numbered user question as a margin note.
// Visually distinct from plain margin-note: amber left border, amber label,
// question-mark icon. Usage: #user-question(label: "[Q1]")[Did the author prove this constructively?]
#let user-question(label: "", body) = context {
  let note = block(
    width: 2.8cm,
    inset: (left: 5pt, right: 3pt, y: 4pt),
    stroke: (left: 2pt + rgb("#f9a825")),
    fill: rgb("#fffde7"),
    radius: (right: 3pt),
  )[
    #text(size: 7.5pt, weight: "bold", fill: rgb("#f57f17"))[#label ❓]\
    #text(size: 7.5pt, fill: luma(60))[#body]
  ]
  let note-height = measure(note).height
  let here-y = here().position().y
  let prev = _margin-bottom.get()
  let on-new-page = prev > here-y + 200pt
  let target-y = if on-new-page or here-y >= prev { here-y } else { prev }
  let dy = target-y - here-y
  place(dx: 100% + 0.3cm, dy: dy, note)
  _margin-bottom.update(target-y + note-height + 6pt)
}

// Single Q&A entry for the appendix.
#let appendix-entry(label, question, answer) = block(
  width: 100%,
  inset: (left: 8pt, y: 4pt),
  stroke: (left: 2pt + accent-color),
)[
  #text(weight: "bold", fill: accent-color)[#label] #question \
  #text(style: "italic")[A:] #answer
  #v(0.4em)
]

// Section header for the appendix. Call once at end of document, then follow
// with #appendix-entry(...) calls for each Q&A pair.
#let appendix-questions-header() = [
  #v(1em)
  #line(length: 100%, stroke: 0.5pt + luma(180))
  #text(weight: "bold", size: 12pt)[Reader Questions & Answers]
  #v(0.5em)
]

// =============================================================================
// MAIN TEMPLATE FUNCTION
// =============================================================================

#let advanced-learning-sheet-template(
  week: 1,
  title: "Topic Title",
  body
) = {
  show link: set text(blue)
  show: thmrules.with(qed-symbol: $square$)

  set document(title: "Week " + str(week) + " - " + title, author: course-code)
  set text(font: "New Computer Modern", size: 10.5pt)
  set par(justify: true, leading: 0.65em)
  set page(
    paper: "a4",
    margin: (left: 2cm, right: 3.5cm, top: 2cm, bottom: 2cm),
    footer: context align(center, text(size: 9pt, fill: gray)[
      Page #counter(page).display() of #counter(page).final().first()
    ]),
  )

  // Title block
  align(center)[
    #text(size: 22pt, weight: "bold", fill: accent-color)[Week #week: #title]
    #v(2pt)
    #text(size: 10pt, fill: gray)[#course-code · #course-name · Advanced Learning Sheet]
  ]

  v(5pt)

  body
}
