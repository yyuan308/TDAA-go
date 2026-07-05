---
name: review-tests
description: Use when reviewing test, test.B, and validation files for scope alignment, correctness, and consistency with the learning sheet
argument-hint: "[week-number]"
---

# Review Tests

Week number N = `$ARGUMENTS`.

## Inputs

1. `weekN/N.learning-sheet.typ` — the source of all testable content
2. `weekN/N.test.typ`, `weekN/N.test.B.typ`, `weekN/N.validation.typ` — files under review
3. `week1/1.test.typ`, `week1/1.validation.typ` — canonical references (skip if reviewing week 1 itself; rely on `templates/week-template/N.test.typ` + `N.validation.typ` and the test-scope rule — week 1 becomes canonical after approval)

## Process

Review all three files against the checklist below.

---

## Checklist

### Scope Alignment

| ID | Check | How |
|----|-------|-----|
| **S1** | **All terms defined** | Every symbol, concept, and notation used in test/validation appears in the learning sheet |
| **S2** | **No scope creep** | Test does not ask about concepts beyond the learning sheet |
| **S3** | **Validation defines boundary** | Test and test.B do not exceed validation scope |
| **S4** | **Coverage** | All key definitions and theorems from the learning sheet are tested across validation + test |

### Structure Consistency

| ID | Check | How |
|----|-------|-----|
| **C1** | **Point totals** | Each file totals exactly 130 points |
| **C2** | **Same structure** | Test and test.B have identical Part layout and point distribution |
| **C3** | **Different questions** | Test and test.B cover the same concepts but with different specific questions |
| **C4** | **Difficulty match** | Test and test.B are comparable in difficulty |
| **C5** | **Question types** | Mix of MC, definitions, computation, design, proofs |

### Correctness

| ID | Check | How |
|----|-------|-----|
| **R1** | **Solutions correct** | Every solution is mathematically correct |
| **R2** | **Solutions complete** | Every question has a solution (check `hide-solution` toggle) |
| **R3** | **MC distractors** | Wrong MC options are plausible but clearly wrong; no ambiguous questions |
| **R4** | **Proof questions fair** | Proof questions test techniques taught in the learning sheet, not novel proofs |
| **R5** | **Point allocation** | Points match difficulty — harder questions get more points |
| **R6** | **No trivial recall** | No questions that simply ask to "write down the definition of X" or "state theorem Y." Every question must require *applying* a concept — tracing, designing, proving, computing, or comparing. Pure recall is not testing understanding. |

---

## Output Format

```
## Review: Week N Tests

### Scope Alignment
- S1 ✓/✗ — [finding with file:line]
- S2 ✓/✗ — ...
- S3 ✓/✗ — ...
- S4 ✓/✗ — ...

### Structure Consistency
- C1 ✓/✗ — test: X pts, test.B: X pts, validation: X pts
- C2 ✓/✗ — ...
- C3 ✓/✗ — ...
- C4 ✓/✗ — ...
- C5 ✓/✗ — ...

### Correctness
- R1 ✓/✗ — [any wrong solutions with file:line]
- R2 ✓/✗ — ...
- R3 ✓/✗ — ...
- R4 ✓/✗ — ...
- R5 ✓/✗ — ...
- R6 ✓/✗ — [any pure-recall questions with file:line]

### Verdict
[ ] **APPROVED** — all checks pass
[ ] **REVISE: <numbered list of issues with file:line>**
[ ] **ESCALATE: <blocker requiring human decision>**

### Fixes Needed (if REVISE)
1. [Most critical fix with file:line]
2. ...
```
