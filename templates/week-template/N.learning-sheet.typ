// Copy to weekN/N.learning-sheet.typ — edit all lines marked ← EDIT
// Canonical reference: week1/1.learning-sheet.typ (after you have one)
// Writing instructions: .claude/skills/write-learning-sheet/SKILL.md

#import "../templates/learning-sheet.typ": *

#show: learning-sheet-template.with(
  week: 0,                  // ← EDIT: week number
  title: "TOPIC TITLE",     // ← EDIT: topic title
)

// =============================================================================
// TASK BOX — Open-ended, real-world problem. Must be solvable with this week's
// theory. The Summary must return to this task.
// =============================================================================

#task-box[
  *Task:* ...  // ← EDIT
]

#v(5pt)

// =============================================================================
// BRIDGE — Exactly 2 paragraphs:
//   Paragraph 1: naive attempt that fails ("You might try... but...")
//   Paragraph 2: "What if we had [concept]?" — name it, describe it, impact
// =============================================================================

// ← EDIT: Bridge paragraphs

#setup-prompt()

#v(5pt)

*Learning objectives.* By the end of this guide, you will:
#set enum(numbering: "(1)")
// ← EDIT: 3-5 objectives, each starting with a verb (Define, Explain, Convert, Prove)
1. Objective 1
2. Objective 2
3. Objective 3

*Resources:*
// ← EDIT
- #link("https://example.com/...", [Lecture / Reference link])

#pagebreak()

// =============================================================================
// PART 1
// =============================================================================

= Part 1: CONCEPT NAME  // ← EDIT

// --- 7a. Opening prose (1-3 paragraphs) ---
// Connect to what came before. Explain WHY this concept matters.
// Name every component of the upcoming definition informally.
// NEVER open with a definition.

// ← EDIT: Opening prose

// --- 7b. Formal definition ---

#definition(numbering: none, title: [Textbook Def. X.Y])[  // ← EDIT: textbook ref
  // ← EDIT: Formal definition
]

#v(5pt)

// --- 7c. Worked example (must include a visual) ---

#example[TITLE][  // ← EDIT
  // ← EDIT: Concrete instance with diagram, table, or trace
]

#v(5pt)

// --- 7d. Deeper mechanics (optional) ---
// "How X computes" / "Designing X" — teach the reader to USE the concept.
// Name the explicit moves: "figure out what to remember → assign states → connect"

// ← EDIT (if applicable)

// --- 7e. Proof (if this Part has a theorem) ---
// Structure: plain-English goal → key insight → formal proof → remark

// ← EDIT (if applicable)

#v(8pt)

// --- 7f. AI prompts (2-4, mix deeper/broader) ---

#prompt[
  #badge-deeper *1.0 — TITLE*  // ← EDIT

  Prompt text. Inline math like $x^2 + 1$ typesets normally; do not wrap the
  prompt body in a code block (\`\`\`...\`\`\`) — that disables math rendering.
]

#prompt[
  #badge-broader *1.1 — TITLE*  // ← EDIT

  Prompt connecting to real-world applications.
]

// =============================================================================
// PART 2
// =============================================================================

= Part 2: CONCEPT NAME  // ← EDIT

// Repeat the pattern: 7a → 7b → 7c → 7d → 7e → 7f

// =============================================================================
// PART 3 (add more parts as needed)
// =============================================================================

= Part 3: CONCEPT NAME  // ← EDIT

// Repeat the pattern

// =============================================================================
// SUMMARY
// =============================================================================

= Summary

// Concept relationship diagram
#v(5pt)
#align(center, diagram(
  node-stroke: 0.8pt, edge-stroke: 0.6pt, spacing: 3em, label-sep: 0em,
  // ← EDIT: Nodes and edges showing how concepts connect
  node((0, 0), [*Concept A*], shape: rect, width: 4em, height: 2em, name: <a>, fill: box-fill),
  node((2, 0), [*Concept B*], shape: rect, width: 4em, height: 2em, name: <b>, fill: box-fill),
  edge(<a>, <b>, "->", [relationship]),
))

#v(8pt)

*The big picture:* // ← EDIT: 2-3 sentences connecting all Parts

#if not hide-section [
// ← EDIT: Return to the task box — show how the theory provides an approach
*Back to the problem.* Now you know—...

#pythoncode([
```python
# Solution code  // ← EDIT
```
])
]

// ← EDIT: Tease next week — frame as a limitation of this week's model
*What's next?* ...

#closing-prompts()
