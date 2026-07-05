# Physics Grading Accuracy Benchmark Design

> **Execution revision:** The model-access strategy and experiment matrix in
> this document are superseded by
> [2026-07-02-physics-plus-deepseek-benchmark-revision-design.md](2026-07-02-physics-plus-deepseek-benchmark-revision-design.md).
> The gold-standard, split, privacy, metric, and reporting decisions below
> remain in force.

## Status

- Date: 2026-07-01
- Target completion: 2026-07-03 afternoon (Asia/Shanghai)
- Working branch: `codex/physics-grading-accuracy`
- Dataset: `Data/physics` only
- Scope: Physics Week 9 internal benchmark, not a general grading claim

## Objective

Improve grading accuracy for the 26 Physics Week 9 submissions while producing
a reproducible benchmark that separates four possible error sources:

1. image preparation and transcription errors;
2. rubric and partial-credit errors;
3. grading workflow and validation errors;
4. model-dependent errors.

The existing `Data/physics/grades/grades.csv` is preserved as the historical
`gpt_direct_v0` baseline. It must not be overwritten.

## Constraints

- All 26 students receive a human gold-standard score for 12 subquestions.
- Student identity and raw submissions remain under `Data/` and outside Git.
- GPT may receive images only after local redaction and human confirmation.
- DeepSeek receives anonymized structured text only.
- API keys are supplied through environment variables and never persisted.
- New controlled conditions run three independent times.
- The historical baseline remains a single-run observational result.
- No implementation starts until this design and its implementation plan are
  reviewed.

## Benchmark Conditions

| ID | Input and grader | Population | Purpose |
| --- | --- | ---: | --- |
| `G0` | Existing ChatGPT Plus/Codex direct image grades | 26 | Historical system baseline |
| `G1` | Anonymized images graded directly by one pinned GPT API model | 26 | Reproducible direct-grading baseline |
| `T1` | Anonymized images transcribed by the same pinned GPT model | 26 | Frozen machine transcript source |
| `G2` | `T1` transcripts graded by the same pinned GPT model | 26 | Controlled direct-vs-staged comparison with `G1` |
| `D1` | The same `T1` transcripts graded by the pinned DeepSeek API model | 26 | GPT-vs-DeepSeek comparison |
| `H1` | Human-corrected transcripts | Stratified 10 | Transcript gold standard |
| `G3` | `H1` transcripts graded by GPT | Stratified 10 | GPT grading ability without OCR error |
| `D2` | `H1` transcripts graded by DeepSeek | Stratified 10 | DeepSeek grading ability without OCR error |

The exact GPT and DeepSeek model IDs are execution-time configuration values.
They must be pinned in a checked-in run configuration before the first model
call and must not change within a comparison.

## Gold Standard

### Rubric freeze

Before human scoring, convert the teacher solution into `rubric_v1`, with one
entry per subquestion. Each entry defines:

- maximum score and allowed score increments;
- accepted answers and alternative valid methods;
- partial-credit rules;
- common mistakes and deductions;
- handling for illegible, incomplete, or contradictory work.

If a rubric defect is found later, issue a new rubric version and recheck every
affected response. Never apply a changed rule to only the current student.

### Primary blind scoring

Map students to `S001` through `S026`, randomize student order, and hide all
existing model grades and feedback. The primary teacher records one row per
student and subquestion:

- anonymous student ID;
- question ID;
- score;
- confidence (`high`, `medium`, or `low`);
- concise evidence;
- optional ambiguity code.

Totals are computed from the 12 subquestion scores and are never entered by
hand.

Confidence definitions:

- `high`: the work is clear and the rubric determines one score;
- `medium`: the work is readable but partial credit has interpretive room;
- `low`: handwriting, formulas, missing work, or the rubric create material
  uncertainty.

### Independent review and adjudication

The second qualified physics grader scores without seeing the primary score:

- every medium- or low-confidence item;
- every item with an ambiguity code;
- a stratified random 20 percent of high-confidence items.

The sample must cover all 12 questions and multiple score bands. Exact matches
are accepted. Disagreements are jointly adjudicated, while both initial scores,
the final score, and the reason are retained.

The gold-standard quality report includes human exact agreement, human MAE,
adjudication rate, per-question disagreement, and confidence distribution.

## Transcript Gold Subset

Select ten students before examining model errors:

- three clear submissions;
- four medium-clarity submissions;
- three difficult submissions;
- coverage of PDF, phone-photo, DOCX, and varied handwriting.

The subset is split between four development students and six held-out test
students. Human correction preserves formulas, values, units, reasoning steps,
and uncertainty markers. Ambiguous content is marked `[UNCLEAR]`, not guessed.

## Development and Held-Out Evaluation

After the gold standard is complete, make a stratified split:

- development: 8 students (96 scored items);
- held-out test: 18 students (216 scored items).

The split balances submission quality, source format, and score band. Only the
development set may be used for error analysis or prompt and skill changes.
The held-out error details remain sealed until the final workflow is frozen.

The final report shows both held-out and all-26 results, but improvement claims
are based on the held-out set.

## Metrics

### Primary metric

Subquestion exact agreement: the percentage of model subquestion scores that
exactly equal the adjudicated human score.

Also report the macro-average across the 12 questions so easy questions cannot
dominate the result.

### Secondary metrics

- subquestion MAE;
- total-score MAE across students;
- percentage of students whose total error is at most 1 point;
- mean signed error (over- versus under-scoring bias);
- percentage of total errors above 2 points;
- per-question accuracy;
- accuracy by human confidence level;
- valid-output rate, retries, latency, and API cost.

### Transcription metrics

On the ten-student subset, report:

- preservation of grading-relevant information;
- formula, numeric, and symbol error rates;
- percentage of subquestions with complete reasoning steps;
- percentage of scores changed by a transcription error.

Character error rate is secondary because a one-character physics error can
change the correct result.

### Statistics

- Report mean, standard deviation, and worst run for each new condition.
- Use a paired student-level bootstrap for 95 percent confidence intervals.
- Keep the 26-student and 10-student results separate.
- Label `G0` as a single-run historical baseline with no run variance.

## Improvement Gates

A candidate proceeds to the next development ablation when:

- exact agreement improves by at least 3 percentage points on average;
- all three runs beat the paired control;
- total-score MAE does not increase;
- all expected outputs are present and valid.

A final workflow is called an effective improvement only when:

- held-out exact agreement improves by at least 5 percentage points;
- the lower bound of the paired 95 percent confidence interval is above zero;
- the within-1-point total-score rate does not decline;
- no question loses more than 10 percentage points of accuracy;
- GPT and DeepSeek show improvement in the same direction.

## Ablation Sequence

### Vision and transcription track

Hold the GPT model and rubric fixed while adding one component at a time:

1. `V0`: anonymized input as currently rendered;
2. `V1`: orientation, crop, resolution, and page-order normalization;
3. `V2`: structured transcription by the 12 question IDs;
4. `V3`: explicit formula, value, and uncertainty preservation;
5. `V4`: independent transcript-to-image verification.

Measure both transcript fidelity and downstream grading accuracy.

### Text grading track

Hold the selected transcript fixed while adding one component at a time:

1. `S0`: minimal current grading prompt;
2. `S1`: explicit subquestion partial-credit rubric;
3. `S2`: evidence extraction before score assignment;
4. `S3`: rationale and confidence in structured output;
5. `S4`: schema, score-range, and total validation;
6. `S5`: independent second pass for low-confidence items.

Use DeepSeek for economical development screening. Confirm the frozen best
workflow with GPT. After freezing, run removal ablations for the highest-impact
components without using the held-out results to select another workflow.

## Repository and Private Data Layout

Tracked, reproducible assets:

```text
benchmark/physics/
|-- schemas/
|-- prompts/
|-- configs/
|-- scripts/
`-- tests/
```

Private assets under the already ignored `Data/` tree:

```text
Data/physics/benchmark/
|-- manifest/
|-- rubric/
|-- gold/
|-- anonymized/
|-- transcripts/
|   |-- automatic/
|   `-- human/
|-- runs/
`-- reports/
```

## Data Flow and Privacy Gate

```text
raw submission
-> render and orient pages
-> locally redact names, IDs, and identifying filenames
-> human anonymity check
-> GPT direct grading or GPT structured transcription
-> freeze anonymous transcript
-> GPT and DeepSeek text grading
-> schema and score validation
-> comparison with the gold standard
-> anonymous benchmark report
```

Raw submissions and identity mappings never leave the local machine. GPT sees
only human-approved anonymized images or text. DeepSeek sees only anonymized
text. A failed anonymity check is a hard stop.

## Failure Handling

- Missing pages, bad orientation, or conversion failure stops that submission.
- Uncertain transcription is marked `[UNCLEAR]`; the system must not guess.
- API timeouts receive at most two retries; persistent failure remains missing,
  never a zero score.
- Invalid JSON receives one format-repair retry, then manual review.
- Out-of-range subquestion scores or inconsistent totals are rejected.
- Empty, truncated, or refused responses are retained as explicit failures.
- Any gold or rubric version change invalidates affected cached evaluations.

Every run records model ID, provider, prompt hash, skill version, input hashes,
rubric version, parameters, time, cost, retry count, and failure log.

## Verification

Implementation tests must cover:

- all 12 score ranges and total calculation;
- anonymous ID mapping completeness;
- no overlap between development and held-out students;
- deterministic metric calculations on fixtures;
- prompt, rubric, input, and result hashing;
- privacy-gate failures;
- held-out-result access only after workflow freeze.

## Two-and-a-Half-Day Delivery Plan

### Day 1 - July 1: freeze the benchmark

- Create and commit this design and the implementation plan.
- Freeze `rubric_v1` and private data schemas.
- Create the anonymous manifest and stratified data split.
- Prepare anonymized images and gold-scoring templates.
- Primary teacher completes the 26-student blind score pass.
- Second teacher begins independent review.

Exit gate: rubric, split, templates, anonymity rules, and primary gold scores
exist in versioned private artifacts.

### Day 2 - July 2: build and develop

- Finish adjudication and freeze the gold standard by noon.
- Implement schemas, metrics, adapters, run manifests, and report generation.
- Run `G0`, `G1`, `T1`, `G2`, and `D1` on the development set.
- Run the compact vision and scoring ablations.
- Select and freeze the best workflow by end of day.

Exit gate: a tested benchmark runner and frozen workflow exist before any
held-out errors are inspected.

### Day 3 half-day - July 3: evaluate and merge

- Run the frozen workflow on the held-out 18 students.
- Compute metrics, paired bootstrap intervals, and error categories.
- Produce the anonymous benchmark report.
- Run tests, privacy checks, and reproduction checks.
- Commit the implementation and merge the feature branch into `main`.

Exit gate: verified benchmark report, reproducible commands, and merged code.

## Explicitly Deferred

To protect the deadline, the following are outside this delivery:

- RTX 2070 local vision-model experiments;
- expansion beyond Physics Week 9;
- a grading website or dashboard;
- exhaustive removal of every component on the held-out set;
- general claims about grading accuracy outside this internal benchmark.

## Deliverables

1. Frozen rubric and adjudicated private gold standard.
2. Updated grading skill and preprocessing workflow.
3. Reproducible GPT direct-versus-staged comparison.
4. GPT-versus-DeepSeek comparison on identical transcripts.
5. Focused ablation results and error taxonomy.
6. Anonymous benchmark report with cost and limitations.
7. Tested tracked code and documentation merged through the feature branch.
