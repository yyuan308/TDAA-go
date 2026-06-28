---
name: write-tests
description: Use when generating test, test.B, and validation files from a finalized learning sheet — ensures scope alignment, consistent structure, and all terms defined
argument-hint: "[week-number]"
---

# Write Tests

Week number N = `$ARGUMENTS`.

## Prerequisites

`weekN/N.learning-sheet.typ` must exist and be finalized before running this skill.

## Inputs (read all before writing)

1. `weekN/N.learning-sheet.typ` — the finalized learning sheet (source of all testable content)
2. `templates/week-template/N.test.typ` — test template (imports `templates/test.typ` shared lib)
3. `templates/week-template/N.test.B.typ` — alternative test template
4. `templates/week-template/N.validation.typ` — validation template
5. `coursedesign/weekly-materials-guide.md` — test/validation checklists
6. `week1/1.test.typ`, `week1/1.test.B.typ`, `week1/1.validation.typ` — canonical references (skip if writing tests for week 1 itself; rely on the three `templates/week-template/N.test*.typ` and `N.validation.typ` files — week 1 becomes canonical after approval)

## Output

Create 3 files in `weekN/`:
- `N.test.typ`
- `N.test.B.typ`
- `N.validation.typ`

## Constraints

- **130 points** total for each file
- **Validation defines scope** — test and test.B must not exceed validation scope
- **Same structure** — test.typ and test.B have identical part layout and point distribution
- **Different questions** — test.typ and test.B share concepts but use different specific questions
- **All terms defined** — every symbol/concept used must appear in the learning sheet
- **Solutions provided** — `hide-solution` toggle for all answers
- **Question types**: Part A (MC, 15-20 pts), Parts B-F (definitions, proofs, design, mixed)

## Process

1. Extract all definitions, theorems, and techniques from the learning sheet
2. Write `N.validation.typ` first — this establishes the full testable scope
3. Write `N.test.typ` — subset of validation scope, same structure
4. Write `N.test.B.typ` — same structure/difficulty as test, different questions
5. Cross-check: verify no term is used that isn't in the learning sheet
6. Compile all 3 files with `typst compile`
