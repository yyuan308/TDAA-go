---
name: write-learning-sheet
description: Use when writing a new learning sheet from scratch for a specific week — reads textbook sections, follows templates, and produces a single learning-sheet.typ file
argument-hint: "[week-number]"
---

# Write Learning Sheet

Week number N = `$ARGUMENTS`.

## Inputs (read all before writing)

1. `coursedesign/schedule.typ` — find textbook sections assigned to week N
2. `textbook/*.md` — extract ALL definitions and theorems from those sections
3. `templates/week-template/N.learning-sheet.typ` — start from this template (structural comments embedded)
4. `week1/1.learning-sheet.typ` — **canonical reference** for prose quality (skip if generating week 1 itself; rely on `templates/learning-sheet.typ` + `coursedesign/weekly-materials-guide.md` — week 1 becomes canonical after approval)
5. `weekN/plan.md` — specific requirements (if exists)
6. `week{N-1}/*` — ensure NO content overlap with previous week

## Output

Create `weekN/N.learning-sheet.typ`.

## Hard Rules

- Include EVERY definition and **key result** (theorems for math/CS; laws, postulates, principles, governing equations for physics / engineering / empirical sciences) from assigned textbook sections
- Define before use — no forward references
- FIDS is a mindset, NOT explicit boxes
- Blog-like prose, not fragmented bullets
- No page breaks between parts (only first page has pagebreak)
- No author footnotes

### Which environment to use

The template provides two parallel sets of boxed environments, same visual style:

| Course type | Box for named result | Box for justification |
|-------------|----------------------|-----------------------|
| Math / CS / theory | `#theorem(...)[...]` | `#proof[...]` |
| Physics / engineering / empirical | `#keyresult(numbering: none, title: [Newton's Second Law])[...]` | `#derivation[...]` |

Pick one set per course (read `textbook/*.md` and `weekN/plan.md` to decide — if the source material proves things from axioms, use theorem/proof; if it states laws and derives consequences, use keyresult/derivation). The "Proof Quality" criteria in `CLAUDE.md` apply identically to `#derivation` — read *key insight* as *physical insight*, *why non-trivial* as *what naïve picture this overturns*.

---

## Writing Craft Guide

The template (`templates/week-template/N.learning-sheet.typ`) tells you **what goes where** via structural comments. This section tells you **how to write it well**. Read both.

### Task Box

- **Open-ended:** multiple reasonable approaches possible; no single "right answer" visible at first glance
- **Clued by the theory:** after completing the sheet, students see how this week's concepts provide a principled approach
- **Self-test:** can you return to this problem in the Summary? If not, redesign.
- Generate 3 candidate task framings internally, then pick the best one

### Bridge

The 2 paragraphs after the task box are the most important prose in the sheet. Use Tao's "ladder of failures": the reader should feel stuck before the concept arrives, then feel relief when it's named.

### Opening Prose (per Part)

The goal is to make the reader *want* the upcoming definition. Two craft moves:

- **Terminology inventory** (Bendersky): name every component of the definition informally before the formal box. If the definition has 5 parts, the prose must introduce all 5.
- **"What would you try?"** (Gowers): pose the question the concept answers. Show what breaks without it.

### Formal Definitions & Theorems

**Critical rule:** every component must have been named in the preceding prose. The formal box should feel like a summary of what the reader already understands, not new information.

### Worked Examples

The example should make the definition *click*, not just illustrate it. Use Kun's concrete-first approach: the reader should understand the concept from the example even if they skip the formal definition.

### Proofs

Two anti-patterns to avoid:
1. **Rabbit-out-of-hat:** every construction must be motivated by what a solver would naturally try
2. **Unmotivated key step:** name the key insight *before* the proof body ("The trick is...")

Structure: plain-English goal → key insight callout → formal proof → remark on what would break without a hypothesis.

### AI Prompts

- **DEEPER** (~2-3 per Part): escalate in difficulty within a Part
- **BROADER** (~1 per Part): connect to real world or frontier research
- Each must be directly copy-pasteable into an AI chat

### Summary

Use Aaronson's "ceiling-hitting": celebrate what this week's model can do, then show its limit as the teaser for next week.

---

## Advanced Techniques (reference — use when natural)

| Technique | When to use | Example from week 1 |
|-----------|-------------|---------------------|
| **Ladder of failures** (Tao) | Bridge and Part transitions | "You might try parsing manually... but this gets messy fast" |
| **Proof as algorithm** (Gowers) | Deeper Mechanics subsections | "Put yourself in the machine's place" |
| **Ceiling-hitting** (Aaronson) | Summary "What's next?" | "Are all languages regular? No." |
| **Confession of confusion** (Kun) | Before complex definitions/proofs | "This looks intimidating, but the idea is simple..." |
| **Structural metaphors** (Aaronson) | When a real-world system maps 1:1 | "automatic door = DFA with two states" |

---

## After Writing

Compile with `typst compile weekN/N.learning-sheet.typ` to verify no Typst errors.
