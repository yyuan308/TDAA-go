---
name: revise
description: Use when revising a learning sheet interactively — walks through chunk by chunk, checking intuition, rigor, and conciseness, then audits tests for scope/triviality issues
argument-hint: "[week-number]"
---

# Revise Learning Sheet

Week number N = `$ARGUMENTS`.

## Inputs (read all before starting)

1. `coursedesign/schedule.typ` — find textbook sections assigned to week N
2. `textbook/*.md` — extract definitions, theorems, and proof strategies from those sections. Note key steps for each proof — you will compare against the learning sheet.
3. `week1/1.learning-sheet.typ` — canonical quality reference (skip if revising week 1 itself; rely on `templates/learning-sheet.typ` + `coursedesign/weekly-materials-guide.md` — week 1 becomes canonical after approval)
4. `weekN/N.learning-sheet.typ` — the sheet to revise

## Startup

### Front Matter Check

Before chunk review, validate the opening section (everything before Part 1). Report issues with `AskUserQuestion` using the same interaction protocol as chunks.

**1. Video link correctness:**
- Read `coursedesign/schedule.typ` to find which MIT lecture videos are assigned to week N.
- For each YouTube link in the learning sheet's *Resources* section, check whether the **lecture topic** aligns with the week's **textbook sections**. Don't just check whether the schedule assigns it — the schedule itself may have errors (e.g., a complexity-theory lecture assigned to an undecidability week).
- Flag mismatched links. Propose replacements by scanning the schedule for lectures whose topics *do* match the week's textbook content.

**2. Task box fitness:**
- The task box (the blue `#block` at the top) frames the entire learning sheet. Check:
  - Does it relate to this week's topics?
  - Does it promise or tease concepts (theorems, techniques) that the learning sheet never formally covers? If so, flag the gap — either the task box should be toned down or the missing content should be added.
- Also check that learning objectives match the actual content of the Parts.

Present any front-matter issues to the user before moving to chunk review.

### Parse & Present Chunks

1. Parse the learning sheet into **Parts** (delimited by `= Part` headings).
2. Within each Part, identify **semantic chunks** — a chunk is one of:
   - A definition + its concrete example
   - A theorem + key insight/proof + example
   - A standalone key example or technique (e.g., a design method, a proof strategy)
3. Present the chunk list to the user:
   > "I found N chunks across K Parts. Here's the outline:
   > - Part 1: [title] — chunks 1-3
   >   1. [chunk title]
   >   2. [chunk title]
   >   ...
   > - Part 2: [title] — chunks 4-6
   >   ...
   >
   > Start from Part 1, Chunk 1? Or jump to a specific Part?"

   Let the user choose where to start. Default is Part 1, Chunk 1.

---

## Per-Chunk Review & Fix Cycle

For each chunk, apply three lenses in order:

### Lens 1 — Intuition

Does this chunk help a beginner build understanding?

- Is there a concrete example before or right after the formal definition?
- Would a student who skips the formal definition still get the idea from surrounding prose?
- Is the "what would you try?" moment present before the concept arrives?
- Does it connect to something the reader already knows (earlier chunks, real-world systems)?

**Note:** Not every chunk needs its own motivation. Motivation is checked at the **Part level** — see Part Transitions below.

### Lens 2 — Rigor

Is it mathematically correct and logically smooth?

- Do definitions and theorem statements match the textbook exactly?
- Does each proof step follow from the previous one? Any gaps?
- Are there hidden assumptions or hand-wavy claims?
- Are quantifiers correct ("for all" vs "there exists")?
- Does the proof strategy match the textbook? If simplified, is the simplification valid?
- Are all cases handled (e.g., pumping lemma proofs must handle *every* valid split)?
- Is every term defined before use? No forward references?

### Lens 3 — Writing Quality

Is the prose clear, well-structured, and appropriate for the audience?

- Conciseness: repeated explanations, filler phrases, redundant examples?
- Flow: do sentences connect naturally? Any jarring transitions?
- Clarity: would a student understand this on first read?
- Tone: appropriate for a learning sheet (not too formal, not too casual)?
- Structure: are paragraphs well-organized? Any wall-of-text issues?

### Interaction Protocol

Apply all three lenses internally. **Only present issues to the user** — do not narrate "Lens 1: no issues, Lens 2: no issues" etc. Keep output minimal:

- **No issues on all three lenses:** Give a one-line score summary and advance:
  > Chunk N: [title] — Intuition: 85, Rigor: 95, Writing: 90. No issues.

- **Issues found:** Use `AskUserQuestion` with `preview` fields showing the proposed edits. This lets the user compare options side-by-side and pick quickly.

  Always include the **original text under review** in the question text so the user can see what's being discussed without switching context.

  **Always recommend one option** by adding "(Recommended)" to its label and putting it first. Include a brief reason for the recommendation in the question text.

  - **Clear fix (one best approach):** Use `AskUserQuestion` with 2 options: "Apply fix (Recommended)" (preview shows the new text) and "Skip" (preview shows original text). Quote the original text and explain the issue + reason for the recommendation in the question text.

  - **Unsure or multiple valid approaches:** Use `AskUserQuestion` with 3 options + previews. Quote the original text and explain the concern in the question text. Each option label should be short (e.g., "Real-world application", "Research citation", "Failed approach"). Mark the recommended option with "(Recommended)" and put it first. Use `preview` to show the proposed replacement text for each option, and `description` for why this approach works. Include a "Skip (keep as is)" option.

  When motivation is lacking, **prioritize options that connect to real-world applications (machine learning, compilers, networking, bioinformatics, etc.) or cite research papers**. Use web search to find relevant papers and provide BibTeX entries for any cited work.

  If the user says "modify" or picks "Other" with custom input, revise the proposal and re-present.

**Edit the file immediately after approval**, then advance to the next chunk.

---

## Part Transitions

After all chunks in a Part are done:

### Motivation Check (Part-level)

The learning sheet's primary goal is **providing motivation**. Check at the Part level:

- Does this Part motivate **why** the reader should care about its concepts?
- Is there a real-world connection (compilers, machine learning, networking, bioinformatics, etc.)?
- Would a student understand **when and where** these concepts matter?

If motivation is weak for the Part, propose 3 options following the same interaction protocol — prioritize options that connect to **real-world applications** or **cite research papers** (use web search to find relevant papers and provide BibTeX entries).

### Part Summary

> **Part N summary:** Reviewed X chunks. Y issues found (Z intuition, W rigor, V writing). Motivation: [adequate / improved with fix]. All approved fixes applied.

Then continue to the next Part.

---

## Test Audit

After all learning sheet chunks are revised, audit the test files.

**If any of the files don't exist**, skip them and note which are missing.

Read whichever exist:
- `weekN/N.validation.typ`
- `weekN/N.test.typ`
- `weekN/N.test.B.typ`

### Length Check

Before per-question review, count the total number of questions in each test file. If any file has **more than 10 questions**, flag it:

> "N.test.typ has X questions — tests with >10 questions are too long. Recommend removing Y questions."

Use `AskUserQuestion` with options listing the weakest candidates for removal (trivial, overlapping, or lowest-value questions). Let the user pick which to cut. Perform deletions before continuing to per-question review.

### Per-Question Review

For each question across all files, check:

1. **Scope** — Does it use concepts or terms not defined in the (now-revised) learning sheet? Flag out-of-scope questions.
2. **Triviality** — Is it pure recall ("write down the definition of X") with no reasoning required? Flag trivial questions.
3. **Redundancy** — Do any two questions within the same file (or across test.typ / test.B.typ / validation.typ) test the same concept in essentially the same way? Flag redundant questions — they waste exam time and don't add assessment value.
4. **Other quality issues** — Ambiguous wording, missing point allocations, answer key errors, inconsistency between test.typ and test.B.typ difficulty, etc.

### Interaction Protocol (same two-case pattern)

- **Clear fix:** Present the issue, show proposed edit, ask to approve/modify/skip.
- **Unsure or multiple valid approaches:** Explain the concern, propose 3 options with previews, ask user to pick or skip.

Edit on approval.

---

## Final Assessment

After all revisions (learning sheet + tests):

### 1. Revision Summary

> **Revision complete.**
> - Learning sheet: X chunks reviewed, Y edits (A intuition, B rigor, C writing)
> - Tests: X questions audited, Y edits (A scope, B triviality, C quality)

### 2. Scores (10-point scale)

Rate the **revised** learning sheet:

| Dimension | Score | Justification |
|-----------|-------|---------------|
| **Intuition** | ?/10 | How well does the sheet build understanding for a beginner? |
| **Rigor** | ?/10 | Mathematical correctness, logical flow, textbook alignment |
| **Writing** | ?/10 | Clarity, flow, structure, and tone of the prose |
| **Overall** | ?/10 | Holistic assessment of the sheet as a learning tool |

### 3. Offer Follow-Up

> "Would you like me to run `/review-learning-sheet N` for a full structured review to double-check?"

---

## After All Edits

Compile all modified files to verify no Typst syntax errors:

```
typst compile weekN/N.learning-sheet.typ
typst compile weekN/N.test.typ        # if edited
typst compile weekN/N.test.B.typ      # if edited
typst compile weekN/N.validation.typ  # if edited
```

Report any compilation errors and fix them before presenting the final assessment.
