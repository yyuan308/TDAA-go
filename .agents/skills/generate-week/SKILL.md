---
name: generate-week
description: Use when generating a complete week of materials, including learning sheets and test bundles, through adversarial writer-vs-reviewer debate
argument-hint: "[week-number]"
---

# Generate Week

Week number N = `$ARGUMENTS`.

Generates all materials for a week:
1. Learning sheet — via adversarial writer/reviewer debate
2. Tests (test, test.B, validation) — via writer + reviewer

Tests normally cover only week N. If the immediately previous week has no
complete test bundle, confirm with the user whether week N's test should cover
multiple weeks before generating tests.

## Execution mode: subagents vs. inline

The phases below describe a **multi-agent** flow (separate writer/reviewer/verifier
subagents). If the active environment doesn't permit subagent delegation, or the
user prefers everything in one session, use the **single-agent fallback**:

- Skip every `Spawn a ... agent` step.
- Instead, invoke the named skill directly in *this* session:
  - "Writer" → invoke `write-learning-sheet` / `write-tests`
  - "Reviewer" → invoke `review-learning-sheet` / `review-tests`
  - "Verifier" → fact-check inline using textbook reads + web search
- Keep the same loop structure: write → review → revise (up to 3 rounds for the
  learning sheet, 2 rounds for tests). The reviewer-output verdicts
  (`APPROVED` / `REVISE` / `ESCALATE`) and escalation triggers still apply.
- Before each "review" pass, clear short-term assumptions: re-read the artifact
  from disk so the review isn't biased by what was just written.

Pick subagent mode when the user explicitly opts in or has it enabled by default;
otherwise default to the single-agent fallback.

## Pre-Work

1. Read `weekN/*` — if good materials exist, confirm with user before regenerating
2. Read `weekN/plan.md` if it exists
3. Read `week{N-1}/*` — note content to avoid overlap
4. **Previous-week test gate** — if N > 1, check whether the immediately
   previous week has a complete test bundle:
   - `week{N-1}/{N-1}.test.typ`
   - `week{N-1}/{N-1}.test.B.typ`
   - `week{N-1}/{N-1}.validation.typ`
5. If all three previous-week test files exist, set `Test scope = week N only`.
6. If any previous-week test file is missing, stop before Phase 2 and ask the
   user:

   > `week{N-1}` does not have a complete test bundle. Should the week N test
   > cover both week {N-1} and week N, or only week N?

   Do not assume multi-week scope without confirmation.
   - If the user chooses multi-week scope, set `Test scope = week {N-1} through week N`.
   - If the user chooses week N only, set `Test scope = week N only`.
   - If more than one consecutive previous week lacks tests, mention that fact
     and ask the user to confirm the exact week range to include.
7. **Pick a motivating task** — the writer agent internally generates 3 candidate task framings, then picks the one that is most interesting, real-world-connected, and suited for group discussion

---

## Phase 1: Learning Sheet

### Round 1

**Step 1a — Writer**: Spawn a general-purpose agent:

> You are a course materials writer for this course. Read AGENTS.md for design principles.
> Follow the instructions in `.Codex/skills/write-learning-sheet/SKILL.md`.
> Generate `weekN/N.learning-sheet.typ` for week N.

**Step 1b — Reviewer**: Spawn a separate general-purpose agent:

> You are a course materials reviewer for this course. Read AGENTS.md for quality criteria.
> Follow the instructions in `.Codex/skills/review-learning-sheet/SKILL.md`.
> Review `weekN/N.learning-sheet.typ`.
> End your review with exactly one of:
> - `APPROVED` — all must-have criteria pass, good-to-have ≥ 5
> - `REVISE: <numbered list of issues with file:line references>`
> - `ESCALATE: <blocker requiring human decision>`

### Rounds 2-3 (if REVISE)

Feed the reviewer's critique back to the writer:

> Here is the reviewer's feedback. Revise `weekN/N.learning-sheet.typ` to address each issue.
> Do NOT remove content that wasn't criticized. Only fix what was flagged.

Re-run the reviewer. Max 3 rounds total.

### After APPROVED — Fact-check

Spawn a verification agent:

> Verify `weekN/N.learning-sheet.typ` for correctness:
> - Fact-check theorem numbers, dates, citations via web search
> - Verify each proof step-by-step against the textbook (`textbook/*.md`)
> - Check logical flow and consistency
> Output: `VERIFIED` or `ISSUES: <list with file:line, type, fix>`

If ISSUES, feed back to writer for one more revision, then re-verify.

Compile: `typst compile weekN/N.learning-sheet.typ`

---

## Phase 2: Tests

### Step 2a — Writer

Spawn a general-purpose agent:

> You are a test writer for this course. Read AGENTS.md for design principles.
> Follow the instructions in `.Codex/skills/write-tests/SKILL.md`.
> Test scope: `week N only` unless the user explicitly confirmed a multi-week
> scope in Pre-Work. If multi-week scope was confirmed, read every finalized
> learning sheet in the confirmed scope and treat that combined content as the
> source of testable material; this overrides the single-learning-sheet input
> assumption in `write-tests`.
> Generate `weekN/N.test.typ`, `weekN/N.test.B.typ`, and `weekN/N.validation.typ`.

### Step 2b — Reviewer

Spawn a separate general-purpose agent:

> You are a test reviewer for this course.
> Follow the instructions in `.Codex/skills/review-tests/SKILL.md`.
> Review the tests against the confirmed test scope. If multi-week scope was
> confirmed, every tested term must appear in one of the finalized learning
> sheets in that scope, and the validation sheet must make the combined boundary
> clear to students.
> Review `weekN/N.test.typ`, `weekN/N.test.B.typ`, and `weekN/N.validation.typ`.
> End with: `APPROVED`, `REVISE: <issues>`, or `ESCALATE: <blocker>`.

### Round 2 (if REVISE)

Feed critique back to test writer. Re-run reviewer. Max 2 rounds for tests.

### Final

Compile all files:
```
typst compile weekN/N.test.typ
typst compile weekN/N.test.B.typ
typst compile weekN/N.validation.typ
```

---

## Escalation Triggers

Stop and present to user when:
- 3 learning sheet debate rounds without APPROVED
- 2 test debate rounds without APPROVED
- Ambiguous textbook content
- Unverifiable facts or proof errors
