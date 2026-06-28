---
name: review-learning-sheet
description: Use when reviewing a weekly learning sheet for pedagogical quality — evaluates beginner motivation, intuition, example quality, and proof correctness
argument-hint: "[week-number]"
---

# Review Learning Sheet

Week number is provided as `$ARGUMENTS`. Replace N below with the week number.

## Inputs

1. `weekN/N.learning-sheet.typ` — file under review
2. `week1/1.learning-sheet.typ` — canonical quality reference (skip if reviewing week 1 itself; rely on `templates/learning-sheet.typ` + `coursedesign/weekly-materials-guide.md` and the must-have/good-to-have criteria — week 1 becomes canonical after approval)
3. Relevant `textbook/*.md` chapters (check `coursedesign/schedule.typ` for assigned sections)

## Process

**Step 1 — Read textbook proofs first.** Before opening the learning sheet, read the relevant `textbook/*.md` chapters. For every proof in those chapters, note the proof strategy and key steps. You will compare the learning sheet's proofs against these.

**Step 2 — Proof audit (top priority).** Read every proof/argument in the learning sheet. For each one, check Lens 1 (Proof Quality) below. This is the most important part of the review — an incorrect proof is worse than a missing section.

**Step 3 — Section-by-section review.** For each Part, evaluate against Lenses 2 and 3. Think like a beginner who has never seen this material.

Cite **line numbers** for every finding.

---

## Lens 1: Proof Quality (top priority — a wrong proof is worse than a missing section)

Check every proof, argument, and worked example. Compare against the textbook source. A proof that *looks* right but teaches wrong technique will be imitated by students.

| ID | Criterion | What to check |
|----|-----------|---------------|
| **P1** | **Mathematical correctness** | Every claim is true. Every logical step follows. Quantifiers are right ("for all" vs "there exists"). No showing one case when all cases are required (e.g., pumping lemma proofs must handle *every* valid split, not just one convenient example). |
| **P2** | **Self-contained** | Uses only previously defined terms; no forward references, no "it is well known", no rabbit-out-of-hat steps. |
| **P3** | **Logical flow** | No gaps; each step follows clearly from the previous one. The proof structure (contradiction, induction, construction) is stated upfront. No contradictory claims (e.g., "vxy must straddle the midpoint" followed by cases where it doesn't). |
| **P4** | **Key insight called out** | The "aha" moment is named explicitly — what's surprising, what breaks without it, what the naive approach misses. |
| **P5** | **Why non-trivial** | Explains what's hard about this proof. Why can't we just do X? What would go wrong with the obvious approach? |
| **P6** | **Examples for hard steps** | Abstract steps are illustrated with concrete instances. If a proof says "for all splits...", show at least one split concretely to ground the general argument. |
| **P7** | **Textbook match** | Proof strategy matches the textbook. If simplified, the simplification must be mathematically valid — not a lossy shortcut that hides a required case. |

---

## Lens 2: Must-Have (non-negotiable — reject if any is missing)

These are the structural bones. Without them the sheet fails as a learning tool.

| ID | Criterion | What to check |
|----|-----------|---------------|
| **M1** | **Define before use** | Every symbol, term, and notation introduced before first use. No forward references. |
| **M2** | **Motivation before formalism** | Every definition arrives *after* the reader wants it — through a failed approach, a puzzle, or a gap. Never a cold definition. |
| **M3** | **Concrete before abstract** | At least one worked example or visual *before or immediately after* each formal definition. |
| **M4** | **Narrative arc** | Hook → Build tools → Climax (main theorem) → Payoff (application). Not Definition → Theorem → Proof → Example. |
| **M5** | **Task box drives the theory** | Opening task is genuinely interesting and real-world; the theory developed *actually solves it*; the sheet returns to it at the end. |
| **M6** | **Textbook fidelity** | Definitions and theorem statements match the textbook. No invented terminology or altered theorems. |
| **M7** | **Smooth prose, not bullets** | Reads as connected paragraphs with transitions, not fragmented bullet lists or isolated blocks. No "hard transition" labels like "The intuition:", "Key distinction:", "Note that:" — weave the content into flowing sentences instead. |
| **M8** | **Cross-section flow** | Each Part opening connects to where the previous Part left off. No repeated explanations across sections (e.g., restating the adversary metaphor). Bridges should reference specific earlier results ("The $\{a^n b^n c^n\}$ proof was clean, but not all languages cooperate...") rather than generic transitions ("Now we move on to..."). |

---

## Lens 3: Good-to-Have (elevates from correct to excellent)

Craft elements that make the sheet memorable. Missing one is fine; missing all means the sheet is dry.

| ID | Criterion | What it looks like |
|----|-----------|-------------------|
| **G1** | **Week-to-week bridge** | Opening paragraph connects to last week's endpoint: what did we build, what can't it do, and why do we need something new? Motivates the current week as the natural next question, not an arbitrary topic change. |
| **G2** | **Failed approaches as pedagogy** | Show what breaks *without* the concept. "You might try X, but it fails because Y." Makes the real solution feel earned. |
| **G3** | **Surprise markers** | Explicitly flag non-obvious results: "This is surprising because...", "You might expect X, but in fact Y." |
| **G4** | **Metaphors that encode structure** | Not decorative — the metaphor mirrors the math. E.g., "automatic door" = DFA, "a hound catching its tail" = self-reference in the halting proof. |
| **G5** | **Multiple perspectives** | Same concept from 2+ angles (visual, algebraic, computational, physical). Redundancy in perspectives ≠ redundancy in content. |
| **G6** | **Epistemic honesty** | Acknowledge difficulty: "This step is subtle", "This is where most students get stuck." Normalizes struggle. |
| **G7** | **Reader-as-discoverer** | Frame the reader as someone making the discovery: "What would *you* try?" / "Put yourself in the machine's place." |
| **G8** | **Counterexamples for hypotheses** | After a theorem, show why each condition is necessary by constructing something that breaks without it. |
| **G9** | **Historical/real-world companionship** | Brief context (compilers, networking, DNA) that makes theory feel alive. A sentence or two, not a detour. |
| **G10** | **Forward momentum** | End with a teaser: what breaks next week? What can't this model do? Creates episodic feeling. |
| **G11** | **Playful voice** | Occasional wit, rhetorical questions, conversational asides — without undermining precision. |

---

## Output Format

```
## Review: Week N Learning Sheet

### Overall Assessment
[1-2 sentences: strongest aspect and biggest gap]
Proof quality: X/Y proofs pass · Must-have: X/8 · Good-to-have: Y/11

### Proof Audit (top priority)

#### Proof 1: [name, e.g., "{a^n b^n c^n} is not CFL"] (lines NN-NN)
- P1 (correctness) ✓/✗ — [Is the math right? Every case handled? Quantifiers correct?]
- P2 (self-contained) ✓/✗ — [Any undefined terms or forward references?]
- P3 (logical flow) ✓/✗ — [Any gaps or contradictory claims?]
- P4 (key insight) ✓/✗ — [Is the "aha" moment named?]
- P5 (why non-trivial) ✓/✗ — [Does it explain what's hard?]
- P6 (examples) ✓/✗ — [Abstract steps grounded with concrete instances?]
- P7 (textbook match) ✓/✗ — [Strategy matches the textbook? Simplification valid?]
**Verdict:** [correct / fixable / wrong — if wrong, explain the error precisely]

(repeat for each proof/argument)

### Part K: [Title]

**Must-have checklist:**
- M1 ✓/✗ — [specific finding with line number]
- M2 ✓/✗ — ...
- (only list items relevant to this section)

**Good-to-have notes:**
- G3 — [specific praise or suggestion with line number]
- ...

(repeat for each Part)

### Global Checks
- M4 (narrative arc): [assessment across the whole sheet]
- M5 (task box): [does the ending return to it?]
- M7 (prose flow): [hard transition labels? bullet-heavy sections?]
- M8 (cross-section flow): [repeated content across Parts? generic bridges?]

### Scorecard
| Lens | Score | Details |
|------|-------|---------|
| Proof quality | X/Y proofs pass | Wrong: [list], Fixable: [list] |
| Must-have | X/8 | Missing: M_, M_ |
| Good-to-have | Y/11 | Present: G_, G_, G_ |

### Verdict
[ ] **Publish** — all proofs correct, all must-haves pass, good-to-have ≥ 5
[ ] **Revise** — proof errors or must-have violations listed below
[ ] **Rewrite** — fundamental structural issues

### Top 3 Fixes (prioritized — proof correctness fixes always rank first)
1. [Most impactful fix with line numbers and concrete suggestion]
2. ...
3. ...

### Elevation Opportunities (pick 2-3 good-to-haves to add)
1. [Specific technique with where to apply it]
2. ...
```

## Guidelines

- **Proof correctness is the top priority** — any mathematically wrong proof is an automatic "Revise" verdict regardless of other scores. A wrong proof that students imitate causes more harm than any missing pedagogical element.
- **Be specific** — always cite line numbers; "Part 2 needs examples" is useless
- **Compare to week 1** — flag anything noticeably below that quality bar
- **Suggest, don't just critique** — for each proof error, write what the correct argument should be
- **Check textbook alignment** — read `textbook/*.md` chapters *before* the learning sheet; verify definitions, theorems, and proof strategies match the textbook
