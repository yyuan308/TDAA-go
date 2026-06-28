---
name: pivot
description: Use when pivoting a finalized learning sheet's task and examples to a new real-world context, or when scrutinizing its reasoning for logical gaps
argument-hint: "[week-number]"
---

# Pivot Learning Sheet

Week number is provided as `$ARGUMENTS`. Replace N below with the week number.

## Inputs

Read these files before starting:

1. `weekN/N.learning-sheet.typ` — the finalized sheet to pivot
2. Relevant `textbook/*.md` chapters (check `coursedesign/schedule.typ` for assigned textbook sections)
3. `week1/1.learning-sheet.typ` — reference for how task boxes and examples are structured (skip if pivoting week 1 itself; use `templates/week-template/N.learning-sheet.typ` instead)

## Concern 1: Creative — Pivot Task & Examples

### Step 1: Catalog what exists

Extract from the current sheet:
- The **task box** (motivating problem, code snippet, closing question)
- Every **worked example** tied to the task context (not pure math examples — only those that reference the real-world framing)
- The **opening bridge** paragraphs connecting task to theory
- The **"Back to the task"** section at the end
- All **AI prompts** (`#badge-broader` and `#badge-deeper`) that reference the task context

### Step 2: Propose 2-3 alternative task framings

Generate candidate motivating tasks for the same theory. Each must be:
- A **different real-world context** (e.g., plagiarism detection, DNA analysis, network protocol validation, data compression)
- **Genuinely interesting** — a student should want to solve it
- **Naturally connected** to the week's theory — the theory should *actually* solve the task, not be a forced fit

**Brainstorming-style presentation:** Before presenting options, write a short analysis of the current task's strengths and weaknesses (e.g., which of the week's big ideas it covers vs. misses). Then present candidates using `AskUserQuestion` with `markdown` previews. Each option must include:
- A **concrete task box preview** (the actual text students would see, including code snippet)
- A **coverage checklist** showing which of the week's key concepts the framing naturally connects to (✓/✗)
- **Strengths and weaknesses** in the option's `description` field

Include the current task as one option (in case the user wants to keep it and only do the reasoning audit).

### Step 3: Rewrite each creative item with the user

Walk through **each** cataloged item from Step 1 **one by one**. For each item:

1. Show the user the **current version** (quote the relevant lines)
2. Present your **proposed rewrite** using the chosen task framing
3. Use `AskUserQuestion` to let the user approve, request changes, or skip

Process items in this order:
1. Task box (problem statement + code snippet + closing question)
2. Opening bridge paragraphs
3. Each worked example tied to the old context (one at a time)
4. Each AI prompt that references the old context (one at a time)
5. Any Part-opening sentences that reference the old context (one at a time)
6. "Back to the task" / summary section

Only apply each edit after the user approves it. If the user requests changes, revise and re-present before moving on.

**Do NOT change:**
- Definitions, theorems, proofs
- Pure math examples (not tied to the task context)
- Section structure or ordering

## Concern 2: Deep Reasoning — Flag Logical Gaps

Independently from the pivot, scrutinize every non-trivial reasoning chain in the sheet. This includes formal proofs, but also informal arguments like "a stack reverses, so PDAs can't do X" or "this is equivalent to Y because...".

For each argument, ask:
- Does each step follow from the previous one?
- Are there hidden assumptions?
- Is any claim stated without justification?
- Could a careful student poke a hole in this reasoning?
- Are edge cases handled?

### Output and confirmation

1. **Present the full audit** using this format:

```
## Reasoning Audit: Week N

### Argument 1: [name] (lines NN-NN)
- **Claim:** [what is being argued]
- **Status:** sound / has gap / uncertain
- **Gap (if any):** [what's missing or hand-wavy]
- **Suggestion:** [how to fix or strengthen]

### Argument 2: ...
(repeat for each non-trivial argument)

### Summary
- X/Y arguments are sound
- Gaps found: [list]
```

2. **List non-sound items** — collect all arguments with status "has gap" or "uncertain" into a numbered checklist for the user.

3. **Confirm each item one by one** — for each non-sound item, use `AskUserQuestion` with `markdown` previews to present:
   - The claim and the identified gap/concern in the question text
   - Options with **before/after previews**: "Apply fix" option shows the proposed new text in its `markdown` field; "Skip (no change)" option shows the current text in its `markdown` field
   - Explain *why* this matters (what a careful student might notice) in the option `description`

   Only apply fixes the user approves. Process items sequentially (one `AskUserQuestion` per item).

## Workflow

1. Read the sheet and textbook chapters
2. Run **Concern 2** (reasoning audit) first — report findings, then confirm fixes one by one
3. Run **Concern 1** (creative pivot) — propose alternatives, get user choice, rewrite
4. Output: the pivoted `.typ` file + the reasoning audit report
