# 物理评分成对比较结果 / Physics Grading Pairwise Findings

本报告以隐私安全的汇总结果比较五种物理作业评分运行，为后续模型与流程改进提供依据。

This report compares five physics-grading runs using privacy-safe aggregate results to guide subsequent model and workflow improvements.

## 运行定义 / Run Definitions

- **G0：** 历史 GPT 直接图像基线，覆盖全部 26 名学生。
  **G0:** Historical GPT direct-image baseline covering all 26 students.
- **G2：** GPT 对自动转录文本评分，覆盖全部 26 名学生。
  **G2:** GPT scoring automatic transcripts for all 26 students.
- **D1：** DeepSeek 对与 G2 相同的自动转录文本评分，覆盖全部 26 名学生。
  **D1:** DeepSeek scoring the same automatic transcripts as G2 for all 26 students.
- **G3：** GPT 对人工复核转录文本评分，覆盖 10 名学生子集。
  **G3:** GPT scoring human-reviewed transcripts for a 10-student subset.
- **D2：** DeepSeek 对与 G3 相同的人工复核转录文本评分，覆盖同一子集。
  **D2:** DeepSeek scoring the same human-reviewed transcripts as G3 for the same subset.

G0 的历史提示词与交互方式不同于新运行，因此不能把 G0 与文本流程之间的差异视为纯粹的图像/文本消融。G3 和 D2 均为探索性运行（N=10）。

G0 used a different historical prompt and interaction pattern from the new runs, so differences between G0 and the text workflows are not a pure image-versus-text ablation. G3 and D2 are exploratory runs (N=10).

## 指标定义 / Metric Definitions

- **完全一致率 / Exact agreement：** 预测的小题分数与人工金标准分数完全相同。
  The predicted subquestion score exactly equals the human gold score.
- **总分误差 / Total error：** 预测总分减去金标准总分；该指标保留正负号。
  Predicted total minus gold total; the sign is retained.
- **总分平均绝对误差 / Total MAE：** 每名学生总分误差绝对值的平均值，单位为每名学生的分数点。
  The mean absolute total error across students, measured in score points per student.
- **误差不超过 1 分 / Within 1：** 总分误差的绝对值不超过 1，即 `abs(total error) <= 1`。
  The absolute total error is at most 1, i.e. `abs(total error) <= 1`.
- **偏差 / Bias：** 每个评分单元（小题）“预测分数减去金标准分数”的有符号平均值，单位为每个评分单元的分数点；负值表示整体少给分。
  The mean signed error per scoring unit (subquestion), predicted score minus gold score, measured in score points per scoring unit; a negative value indicates overall undergrading.
- **百分点 / Percentage point (pp)：** 两个比率的直接差值，不是作业分值，也不是相对百分比。
  The direct difference between two rates, not assignment points or a relative percentage.

## 方法与来源 / Method and Provenance

汇总指标来自 `benchmark.physics.metrics`。置信区间使用按学生配对的 bootstrap：以随机种子 `20260701` 进行 10,000 次确定性的学生有放回重抽样，并取 bootstrap 分布的百分位数边界。来源提交 `4bb8e15` 仅固定纳入版本控制的指标代码；本报告使用的私有输入被忽略，未包含在该提交中。

Aggregate metrics come from `benchmark.physics.metrics`. Confidence intervals use a paired student bootstrap: seed `20260701` produces 10,000 deterministic student resamples with replacement, with percentile bounds taken from the bootstrap distribution. Source commit `4bb8e15` pins only the version-controlled metric code; the private inputs used by this report are ignored and are not included in that commit.

为在不披露数据的情况下固定输入快照，本报告给出覆盖恰好 1 个金标准 CSV 和 G0/G2/D1/G3/D2 所用 9 个预测 CSV 的聚合 SHA-256 摘要。稳定标签按序数词典序排列：`d1-dev`、`d1-test`、`d2-dev`、`d2-test`、`g0-all`、`g2-dev`、`g2-test`、`g3-dev`、`g3-test`、`gold`。先对每个文件的原始字节计算小写十六进制 SHA-256；再按排序后的每个标签拼接 UTF-8（无 BOM）序列 `label + " " + file_digest + LF`；最后对完整序列计算 SHA-256。聚合摘要为 `b7fa350200e79b09f253a965281dc33121e69bb4c6160d4f53384c79a625811d`。

To pin the input snapshot without disclosing data, this report provides an aggregate SHA-256 digest covering exactly one gold CSV and the nine prediction CSVs used by G0/G2/D1/G3/D2. Stable labels are sorted in ordinal lexicographic order: `d1-dev`, `d1-test`, `d2-dev`, `d2-test`, `g0-all`, `g2-dev`, `g2-test`, `g3-dev`, `g3-test`, `gold`. First compute the lowercase hexadecimal SHA-256 of each file's raw bytes; then, for each sorted label, concatenate the UTF-8 (no BOM) sequence `label + " " + file_digest + LF`; finally compute SHA-256 over the complete sequence. The aggregate digest is `b7fa350200e79b09f253a965281dc33121e69bb4c6160d4f53384c79a625811d`.

输入审计已通过：没有重复键；每名纳入学生均有 12 道题；共同队列符合预期，完整队列为 26 名学生、312 个评分单元，子集为 10 名学生、120 个评分单元，均无缺失或额外键。

The input audit passed: there were no duplicate keys; every included student had 12 questions; and the common cohorts matched expectations at 26 students and 312 scoring units for the full cohort and 10 students and 120 scoring units for the subset, with no missing or extra keys.

以下完全一致率差值与置信区间基于未四舍五入的底层结果；表中展示值经过四舍五入。

The exact-agreement differences and confidence intervals below use the unrounded underlying results; displayed table values are rounded.

## 1. G0 与 G2 / G0 vs G2

**共同队列 / Common cohort:** 26 名学生 / 26 students; 312 个评分单元 / 312 scoring units

| 运行 / Run | 完全一致率 / Exact | 总分 MAE（分数点/学生） / Total MAE (score points/student) | 误差不超过 1 分 / Within 1 | 偏差（分数点/评分单元） / Bias (score points/scoring unit) |
|---|---:|---:|---:|---:|
| G0 | 91.35% | 0.41 | 88.46% | +0.030 |
| G2 | 88.46% | 1.13 | 61.54% | -0.027 |

| 比较 / Contrast | 完全一致率差值 / Exact difference | 95% 配对 bootstrap 区间 / 95% paired bootstrap CI |
|---|---:|---:|
| G2 - G0 | -2.88 pp | [-6.41, +0.64] pp |

按题目看，G2 相对 G0 在 Q3a 提高 +11.54 pp、Q3c 提高 +3.85 pp，但在 Q2a 降低 -19.23 pp、Q1d 降低 -15.38 pp。综合完全一致率、总分 MAE 和误差不超过 1 分的比例，G2 未超过 G0；同时，由于 G0 的历史提示词与交互条件不同，这不是纯粹的图像/文本消融。

By question, G2 gains +11.54 pp on Q3a and +3.85 pp on Q3c relative to G0, but loses -19.23 pp on Q2a and -15.38 pp on Q1d. Considering exact agreement, total MAE, and within-1 rate together, G2 does not beat G0; because G0 used different historical prompting and interaction conditions, this is not a pure image-versus-text ablation.

## 2. G2 与 D1 / G2 vs D1

**共同队列 / Common cohort:** 26 名学生 / 26 students; 312 个评分单元 / 312 scoring units

| 运行 / Run | 完全一致率 / Exact | 总分 MAE（分数点/学生） / Total MAE (score points/student) | 误差不超过 1 分 / Within 1 | 偏差（分数点/评分单元） / Bias (score points/scoring unit) |
|---|---:|---:|---:|---:|
| G2 | 88.46% | 1.13 | 61.54% | -0.027 |
| D1 | 80.45% | 2.45 | 38.46% | -0.169 |

| 比较 / Contrast | 完全一致率差值 / Exact difference | 95% 配对 bootstrap 区间 / 95% paired bootstrap CI |
|---|---:|---:|
| D1 - G2 | -8.01 pp | [-14.10, -2.56] pp |

D1 没有在任何题目上提高完全一致率；它在 Q1c 和 Q3d 上各降低 -23.08 pp，在 Q3b 和 Q3f 上各降低 -11.54 pp。在本数据集与本次运行中，G2 明显优于 D1；D1 的负偏差更大，显示其少给分倾向更强。

D1 improves exact agreement on no question; it loses -23.08 pp on both Q1c and Q3d and -11.54 pp on both Q3b and Q3f. On this dataset and run, G2 clearly outperformed D1; D1's more negative bias indicates greater undergrading.

## 3. G2 与 G3 / G2 vs G3

**共同队列 / Common cohort:** 同 10 名学生 / same 10 students; 120 个评分单元 / 120 scoring units

| 运行 / Run | 完全一致率 / Exact | 总分 MAE（分数点/学生） / Total MAE (score points/student) | 误差不超过 1 分 / Within 1 | 偏差（分数点/评分单元） / Bias (score points/scoring unit) |
|---|---:|---:|---:|---:|
| G2 | 87.50% | 1.33 | 50.00% | -0.060 |
| G3 | 78.33% | 1.58 | 40.00% | -0.119 |

| 比较 / Contrast | 完全一致率差值 / Exact difference | 95% 配对 bootstrap 区间 / 95% paired bootstrap CI |
|---|---:|---:|
| G3 - G2 | -9.17 pp | [-11.67, -6.67] pp |

G3 相对 G2 在 Q2b 提高 +10 pp，但在 Q1c 降低 -50 pp、Q3f 降低 -20 pp，并在 Q2a、Q1d、Q3b、Q3d、Q3e 上各降低 -10 pp。本次 GPT 运行中，人工复核没有改善结果；但每个条件只有一次独立模型运行，转录文本效应与模型运行波动相互混杂，因此不能据此声称人工复核文本有害。

G3 gains +10 pp on Q2b relative to G2, but loses -50 pp on Q1c, -20 pp on Q3f, and -10 pp on each of Q2a, Q1d, Q3b, Q3d, and Q3e. Human review did not improve this GPT run; however, one independent model run per condition confounds the transcript effect with model-run variance, so these results do not support a claim that human-reviewed transcripts are harmful.

## 4. D1 与 D2 / D1 vs D2

**共同队列 / Common cohort:** 同 10 名学生 / same 10 students; 120 个评分单元 / 120 scoring units

| 运行 / Run | 完全一致率 / Exact | 总分 MAE（分数点/学生） / Total MAE (score points/student) | 误差不超过 1 分 / Within 1 | 偏差（分数点/评分单元） / Bias (score points/scoring unit) |
|---|---:|---:|---:|---:|
| D1 | 78.33% | 2.20 | 30.00% | -0.154 |
| D2 | 79.17% | 1.95 | 30.00% | -0.154 |

| 比较 / Contrast | 完全一致率差值 / Exact difference | 95% 配对 bootstrap 区间 / 95% paired bootstrap CI |
|---|---:|---:|
| D2 - D1 | +0.83 pp | [-10.00, +15.83] pp |

D2 相对 D1 在 Q2b、Q3a、Q3b、Q3c、Q3d、Q3e 上各提高 +10 pp，但在 Q1c 降低 -30 pp，并在 Q1d 和 Q3f 上各降低 -10 pp。人工复核使总分 MAE 略有下降，但没有带来可靠的完全一致率提升。

D2 gains +10 pp on each of Q2b, Q3a, Q3b, Q3c, Q3d, and Q3e relative to D1, but loses -30 pp on Q1c and -10 pp on both Q1d and Q3f. Human review slightly lowers total MAE but does not produce a reliable exact-agreement gain.

## 5. G3 与 D2 / G3 vs D2

**共同队列 / Common cohort:** 同 10 名学生 / same 10 students; 120 个评分单元 / 120 scoring units

| 运行 / Run | 完全一致率 / Exact | 总分 MAE（分数点/学生） / Total MAE (score points/student) | 误差不超过 1 分 / Within 1 | 偏差（分数点/评分单元） / Bias (score points/scoring unit) |
|---|---:|---:|---:|---:|
| G3 | 78.33% | 1.58 | 40.00% | -0.119 |
| D2 | 79.17% | 1.95 | 30.00% | -0.154 |

| 比较 / Contrast | 完全一致率差值 / Exact difference | 95% 配对 bootstrap 区间 / 95% paired bootstrap CI |
|---|---:|---:|
| D2 - G3 | +0.83 pp | [-7.50, +7.50] pp |

D2 相对 G3 在 Q2a 提高 +30 pp，并在 Q3b 和 Q3e 上各提高 +10 pp；它在 Q3d、Q3a、Q3c、Q3f 上各降低 -10 pp。两者完全一致率的点估计几乎相同，但置信区间过宽，无法确立等价性或胜者；G3 的总分 MAE 更低，误差不超过 1 分的比例更高。

D2 gains +30 pp on Q2a and +10 pp on both Q3b and Q3e relative to G3; it loses -10 pp on each of Q3d, Q3a, Q3c, and Q3f. The exact-agreement point estimates are nearly identical, but the confidence interval is too wide to establish equivalence or a winner; G3 has lower total MAE and a higher within-1 rate.

## 总体发现 / Overall Findings

- 在已观察的运行中，G0 仍然最强。
  G0 remains the strongest observed run.
- 在本数据集与本次运行中，新的文本评分流程里 G2 优于 D1。
  In this dataset and run, among the new text-scoring workflows, G2 outperforms D1.
- 人工转录纠正没有显示稳定收益；评分提示词与评分标准解释是下一步应优先检验的假设。
  Human transcript correction shows no stable gain; the scoring prompt and rubric interpretation are higher-priority hypotheses to test next.
- 在扩大人工转录投入之前，应优先澄清 Q2a、Q1d、Q1c、Q3d 的评分标准，或为这些题增加二次检查。
  Before scaling manual transcription, prioritize rubric clarification or second-pass checks for Q2a, Q1d, Q1c, and Q3d.

## 局限性 / Limitations

- 每个条件仅运行一次，无法分离流程效应与单次模型运行波动。
  Each condition was run once, so workflow effects cannot be separated from single-run model variance.
- 交互式 GPT Plus 并非固定版本的 API 快照，可复现性有限。
  Interactive GPT Plus is not a pinned API snapshot, which limits reproducibility.
- G0 的历史提示词与交互方式不匹配新运行，限制了跨模态因果解释。
  G0's historical prompt and interaction pattern do not match the new runs, limiting causal interpretation across modalities.
- 金标准主要来自一名人工评分者，未测量评分者间一致性。
  The gold standard primarily comes from one human rater, and inter-rater agreement was not measured.
- 本次分析未收集证据定位或歧义标注，无法判断错误来自转录、推理还是评分标准解释。
  This analysis did not collect evidence localization or ambiguity labels, so errors cannot be attributed to transcription, reasoning, or rubric interpretation.
- 数据仅来自一个物理课程第 9 周、26 名学生，不能广泛推广到其他课程、任务或学生群体。
  The dataset covers one Physics Week 9 cohort of 26 students and does not support broad generalization to other courses, tasks, or student populations.
