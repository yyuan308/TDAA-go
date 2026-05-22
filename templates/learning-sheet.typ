// Learning Sheet Template Library
//
// Usage:
//   #import "../templates/learning-sheet.typ": *
//   #show: learning-sheet-template.with(week: 1, title: "Topic Title")
//   // ... content ...

#import "@preview/fletcher:0.5.8" as fletcher: diagram, node, edge
#import "@preview/ctheorems:1.1.3": *
#import "../config.typ": course-code, course-name

// Journal-style palette (Nature/Science inspired)
#let rule-color = rgb("#cccccc")
#let box-fill = rgb("#f7f7f7")

// Theorem environments
#let definition = thmbox("definition", "Definition", base: none,
  fill: box-fill, stroke: none, inset: (x: 12pt, y: 10pt))
#let theorem = thmbox("theorem", "Theorem", base: none,
  fill: box-fill, stroke: none, inset: (x: 12pt, y: 10pt))
#let lemma = thmbox("lemma", "Lemma", base: none,
  fill: box-fill, stroke: none, inset: (x: 12pt, y: 10pt))
#let proof = thmproof("proof", "Proof")

// Key-result box for courses without theorems (physics, engineering,
// empirical sciences). Same visual style as `theorem` / `definition`, but
// used to present named laws / postulates / principles / equations.
// Pass `title:` with the actual physical name; pair with `derivation` instead
// of `proof` if you want a labeled justification block.
//   #keyresult(numbering: none, title: [Newton's Second Law])[$F = m a$ ...]
#let keyresult = thmbox("keyresult", "Key Result", base: none,
  fill: box-fill, stroke: none, inset: (x: 12pt, y: 10pt))
#let derivation = thmproof("derivation", "Derivation")

// Content elements
#let pythoncode(body) = block(
  width: 100%, fill: rgb("#f5f5f5"),
  inset: 10pt, radius: 0pt,
  stroke: (y: 0.5pt + rule-color)
)[#body]

#let prompt(body) = block(
  width: 100%, fill: box-fill, inset: 12pt, radius: 0pt,
  stroke: (top: 2pt + black)
)[#body]

#let example(title, body) = block(
  width: 100%, inset: (left: 0pt, y: 8pt),
  stroke: none
)[
  #text(weight: "bold")[Example (#title).] #body
]

#let remark(body) = block(
  width: 100%, inset: (left: 16pt, y: 8pt),
  stroke: (left: 2pt + black)
)[
  #text(weight: "bold")[Remark.] #body
]

// AI prompt badges
#let badge-deeper = box(fill: rgb("#e8f5e9"), inset: (x: 4pt, y: 2pt), radius: 2pt, text(size: 7pt, fill: rgb("#2e7d32"), weight: "bold")[DEEPER])
#let badge-broader = box(fill: rgb("#e3f2fd"), inset: (x: 4pt, y: 2pt), radius: 2pt, text(size: 7pt, fill: rgb("#1565c0"), weight: "bold")[BROADER])

// Unified state node for automata diagrams (used by some courses; harmless otherwise)
#let state(pos, label, name: none, accept: false, fill: none) = node(
  pos, label, shape: circle, name: name, radius: 1.5em,
  extrude: if accept { (0, -4) } else { (0, 0) },
  fill: fill
)

#let hide-section = true

// Main template function
#let learning-sheet-template(
  week: 1,
  title: "Topic Title",
  body
) = {
  show link: set text(blue)
  show: thmrules.with(qed-symbol: $square$)

  set document(title: "Week " + str(week) + " - " + title, author: course-code)
  set page(
    footer: context align(center, text(size: 9pt, fill: gray)[Page #counter(page).display() of #counter(page).final().first()])
  )

  align(center)[
    #text(size: 22pt, weight: "bold")[Week #week: #title]
    #v(2pt)
    #text(size: 10pt, fill: gray)[#course-code · #course-name · Learning Sheet]
  ]

  v(5pt)

  body
}

// Task box
#let task-box(body) = block(
  width: 100%, stroke: 1pt + rgb("#1565c0"), inset: 12pt, radius: 5pt, fill: rgb("#e3f2fd")
)[#body]

// AI setup prompt (standard across all weeks)
#let setup-prompt() = {
  prompt[
    *Setup.* Send the lecture note content to AI and type:

    Summarize.
  ]
  text(size: 9pt, fill: gray)[*How to use?* Start an AI chat and work through the exercises. #box(baseline: 2pt)[#badge-deeper] practice & theory · #box(baseline: 2pt)[#badge-broader] applications & frontiers]
}

// Summary closing prompts (standard across all weeks)
#let closing-prompts() = {
  v(8pt)
  prompt[
    #badge-broader *Open Problems*

    Are there unsolved problems in this area?
  ]
  v(10pt)
  line(length: 100%, stroke: 0.5pt + rule-color)
  v(8pt)
  prompt[
    *Wrap up.*

    Summarize our discussion in markdown.
  ]
}
