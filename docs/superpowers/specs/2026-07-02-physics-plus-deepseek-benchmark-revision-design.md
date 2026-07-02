# Physics Plus and DeepSeek Benchmark Revision

## Status

- Date: 2026-07-02
- Target completion: 2026-07-03 afternoon (Asia/Shanghai)
- Working branch: `codex/physics-grading-accuracy`
- Dataset: Physics Week 9 under private `Data/physics`
- Supersedes: the model-access strategy and experiment matrix in the
  2026-07-01 Physics Grading Accuracy Benchmark Design

The original gold-standard, frozen split, privacy, metric, and report-design
decisions remain unchanged. This revision removes paid OpenAI API usage and
adapts the model experiments to the subscriptions and credentials available to
the user.

## Decision Summary

1. Do not use or fund the OpenAI API.
2. Use GPT-5.5 through fresh Codex App threads covered by the user's ChatGPT
   Plus access.
3. Use the instructor-provided DeepSeek API key with `deepseek-v4-pro`.
4. Remove `G1`, the new GPT API direct-image condition.
5. Keep `G0` as the only direct-image comparator.
6. Run every retained GPT and DeepSeek grading condition once.
7. Treat the failed private `G1-dev-r1` OpenAI API run as an infrastructure
   failure and exclude it from accuracy metrics.

## Revised Experiment Matrix

| ID | Input and grader | Population | Purpose |
| --- | --- | ---: | --- |
| `G0` | Existing ChatGPT Plus/Codex direct-image grades | 26 | Historical direct-workflow baseline |
| `T1` | Anonymous images transcribed by GPT-5.5 in a fresh Codex thread | 26 | Frozen machine transcript source |
| `G2` | `T1` transcripts graded by GPT-5.5 in a fresh Codex thread | 26 | New staged GPT/Codex workflow |
| `D1` | The same `T1` transcripts graded by DeepSeek V4-Pro API | 26 | Model comparison on identical machine text |
| `H1` | Human-corrected `T1` transcripts | Stratified 10 | Transcript gold standard |
| `G3` | `H1` transcripts graded by GPT-5.5 in a fresh Codex thread | Stratified 10 | GPT grading without machine-transcription error |
| `D2` | `H1` transcripts graded by DeepSeek V4-Pro API | Stratified 10 | DeepSeek grading without machine-transcription error |

`G0` is a historical single run. It was produced under different thread and
prompt conditions from `G2`, so `G0 -> G2` measures the overall difference
between the historical direct workflow and the revised staged workflow. The
difference must not be attributed solely to transcription.

## Blind Codex Execution

Every GPT-5.5 condition runs in a new Codex App thread with no prior benchmark
conversation. The thread opens a condition-specific blind packet as its
workspace. A blind packet contains only:

- anonymous IDs and the selected split;
- approved anonymous images for `T1`, or frozen anonymous transcripts for
  `G2` and `G3`;
- the frozen rubric when grading is required;
- one condition-specific prompt;
- a manifest containing condition, split, displayed model name, creation time,
  prompt hash, rubric hash, and input hashes;
- an empty output directory and JSON output schema.

The packet must not contain or link to gold scores, historical predictions,
metrics, reports, identity mappings, source filenames, or student names. The
blind thread is explicitly prohibited from traversing outside the packet or
reading any other project data.

The displayed model name is recorded as `GPT-5.5`. Because Codex Plus is an
interactive product rather than a pinned API snapshot, no API model snapshot,
system fingerprint, temperature, or token-level reproducibility is claimed.

## Data Flow

### Development Split

1. Build a `T1-dev-r1` blind packet for the frozen eight-student development
   split.
2. Run GPT-5.5 transcription in a fresh Codex thread. Transcribe all 12 question
   IDs and preserve equations and units. Use `[UNCLEAR]` instead of inference.
3. Import and validate `T1-dev-r1` without exposing gold scores to the blind
   thread.
4. The teacher corrects the four preselected development transcripts to create
   `H1-dev`.
5. Build separate `G2-dev-r1`, `D1-dev-r1`, `G3-dev-r1`, and `D2-dev-r1`
   packets or API inputs.
6. Run each retained grading condition once and compute development metrics.
7. Freeze the selected staged workflow, prompt hashes, rubric hash, input
   preparation, GPT display name, and DeepSeek model ID before any held-out
   model error is inspected.

### Held-Out Split

1. Build held-out blind packets only after `freeze.json` exists.
2. Repeat `T1`, `G2`, and `D1` without changing prompts or preprocessing.
3. Correct the six preselected held-out transcripts to create `H1-test`.
4. Run `G3-test-r1` and `D2-test-r1` on the same human-corrected text.
5. Compute held-out metrics before combined all-26 summaries.

## Comparisons and Claims

The report uses these comparisons:

- `G0 vs G2`: historical direct workflow versus revised staged workflow;
- `G2 vs D1`: GPT-5.5 versus DeepSeek V4-Pro on identical machine transcripts;
- `G2 vs G3`: GPT sensitivity to machine-transcription errors on the ten-person
  transcript subset;
- `D1 vs D2`: DeepSeek sensitivity to machine-transcription errors on the same
  subset;
- `G3 vs D2`: GPT-5.5 versus DeepSeek V4-Pro on identical human-corrected text.

All primary metrics remain subquestion exact agreement, total-score MAE, and
the proportion of total-score errors no greater than one point. The report also
retains question-level agreement, bias, failure counts, and paired student-level
confidence intervals where meaningful. Because each model condition runs once,
the report does not estimate model-run variance.

## Validation and Failure Handling

- A `T1` result must contain all 12 question IDs for every expected anonymous
  student and must use `[UNCLEAR]` for unresolved content.
- A grading result must contain exactly 12 unique question IDs, quarter-point
  scores within each question maximum, evidence, confidence, flags, and a total
  equal to the sum of subquestion scores.
- The importer rejects missing students, duplicate questions, out-of-range
  scores, invalid increments, inconsistent totals, and non-anonymous labels.
- A Codex formatting failure receives one format-only repair in the same blind
  thread. The repair may not reconsider scores unless validation requires it.
- DeepSeek receives at most two retries for transient connection, server, or
  rate-limit failures. Authentication, permission, and insufficient-quota
  failures are terminal.
- Persistent failures remain missing and never become zero scores.
- Every imported run is immutable and records raw responses, failures, hashes,
  timestamps, and available usage metadata.
- The held-out packet builder refuses to run before workflow freeze.

## Required Tests

Implementation tests must prove that:

1. blind packets contain no gold path, identity mapping, historical prediction,
   source filename, student name, metric, or report;
2. packet manifests and input hashes are deterministic;
3. Codex transcript and grading imports enforce the frozen schemas;
4. grading validation enforces all 12 score ranges, quarter-point increments,
   and totals;
5. DeepSeek receives text only and uses `deepseek-v4-pro`;
6. held-out packets remain sealed until `freeze.json` exists;
7. the failed OpenAI API `G1-dev-r1` is classified as infrastructure-only and
   excluded from accuracy aggregation;
8. reports label `G0` as historical and GPT-5.5 as an interactive Codex Plus
   run rather than an API snapshot.

## Delivery Impact

The revised sequence for the remaining time is:

1. implement blind-packet creation and validated Codex result import;
2. run `T1-dev-r1` in a fresh GPT-5.5 Codex thread;
3. create the four human-corrected development transcripts;
4. run and evaluate `G2-dev-r1`, `D1-dev-r1`, `G3-dev-r1`, and `D2-dev-r1`;
5. freeze the staged workflow;
6. run the same frozen workflow on held-out data;
7. generate the anonymous report, update the grading skill from the observed
   evidence, verify the branch, and request merge approval.

The OpenAI provider code may remain as tested inactive infrastructure, but no
OpenAI credential, billing step, or OpenAI API run is part of the active plan.
