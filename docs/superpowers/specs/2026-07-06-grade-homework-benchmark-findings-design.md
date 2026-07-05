# Grade Homework Benchmark Findings Skill Update Design

## Goal

Update the grading workflow instructions so future use of `grade-homework` reflects
the Physics Week 9 benchmark findings without claiming a proven accuracy gain.

## Scope

This change updates the existing grading skill text. It does not change benchmark
data, grading outputs, provider APIs, or model execution code.

The implementation should modify:

- `.claude/skills/grade-homework/SKILL.md`
- `.agents/skills/grade-homework/SKILL.md`

The two files must remain byte-for-byte identical because the physics benchmark
test suite checks the local Codex mirror against the committed Claude skill.

## Design

The skill should keep its current evidence-first grading flow and make the
benchmark-derived safeguards more explicit:

1. Freeze the grading surface before student grading starts: page ordering,
   rubric, question IDs, point ranges, and quarter-point rules.
2. Preserve the evidence-first rule: record visible work, equations, text, or a
   blank-answer marker before assigning points.
3. Require targeted second-pass review for low confidence, unreadable regions,
   blank or apparently missing answers, total mismatches, and high-impact
   deductions.
4. Keep confidence and ambiguity flags as teacher-review tools rather than busy
   paperwork.
5. Avoid claiming that transcript-based grading is generally better than direct
   image grading. The current benchmark did not show a stable transcript-path
   improvement.
6. Treat Physics Week 9 error patterns as local guidance only. Mention the
   lowest-agreement questions as useful spot-check targets, not universal rules.
7. Keep private data out of the skill. Refer only to aggregate benchmark
   findings and never embed student names, source paths, or raw answers.

## User-Facing Behavior

When the skill is used later, Codex should:

- Ask the teacher to confirm the frozen rubric before grading.
- Be slower and more explicit on ambiguous items instead of guessing.
- Surface flagged items and their question concentration at handoff.
- Recommend spot-checking at least three students and all flagged items before
  publishing grades.

## Out of Scope

- Changing scoring schemas or CSV columns.
- Running new GPT or DeepSeek experiments.
- Uploading or committing any `Data/` contents.
- Adding automatic OCR/transcript generation as a default path.
- Changing the benchmark report PR.

## Verification

The change is acceptable when:

- The `.claude` and `.agents` skill files match exactly.
- `test_skill_requires_frozen_evidence_first_workflow` still passes.
- The physics benchmark unit tests pass.
- A privacy scan of the changed skill text finds no local `Data/` paths,
  student identifiers, or API-key-like strings.
