# Physics Pairwise Findings Report Design

## Goal

Publish the five requested Physics Week 9 benchmark comparisons as one tracked,
bilingual Markdown report that can be reviewed in GitHub and shared with a
mentor. The report must explain both the numerical results and what can and
cannot be concluded from them.

## Output

Create `docs/reports/physics-grading-pairwise-findings.md`.

Each section will present Chinese first and its English counterpart immediately
afterward. Tables may use bilingual column headings to avoid duplicating the
same numbers. The report will remain readable without access to the ignored
`Data/` directory.

## Contents

1. Define the five runs used in the comparisons: G0, G2, G3, D1, and D2.
2. Define exact per-question agreement, total-score MAE, total error, the
   within-one-point rate, and percentage-point change.
3. Present these five comparisons on their common student sets:
   - G0 versus G2
   - G2 versus D1
   - G2 versus G3
   - D1 versus D2
   - G3 versus D2
4. For each comparison, give sample size, exact agreement, total-score MAE,
   within-one-point rate, signed bias where useful, the paired difference and
   bootstrap confidence interval, question-level gains/losses, and a cautious
   interpretation.
5. Close with the overall findings, recommended next experiments, and study
   limitations.

## Interpretation Rules

- Treat G0 as the historical direct-image baseline, while explicitly noting
  that its historical prompt and interaction conditions differ from later runs.
- Compare G2 with D1 as the closest model comparison on the same automatic
  transcripts.
- Treat comparisons involving G3 or D2 as exploratory because they contain
  only ten transcript-reviewed students.
- Do not call a small difference an improvement when its paired bootstrap
  confidence interval includes zero.
- Separate exact-agreement conclusions from total-score-error conclusions.
- State that one run per condition does not estimate model-run variance.

## Privacy And Scope

The tracked report may contain aggregate metrics, anonymous run labels, and
question IDs. It must not contain student names, student numbers, raw answers,
submission images, API keys, or private absolute paths. The report is limited
to Physics Week 9 and must not claim broad generalization beyond this dataset.

## Verification

Before committing the report:

- Recompute or cross-check every table value against the benchmark artifacts.
- Check that Chinese and English sections state the same conclusions.
- Scan for private paths and identifying student data.
- Confirm that only the intended documentation files are staged.
