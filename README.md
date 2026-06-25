# TDAA-Go

[![arXiv](https://img.shields.io/badge/arXiv-2606.23315-b31b1b)](https://arxiv.org/abs/2606.23315)
[![Instructor guide](https://img.shields.io/badge/Instructor%20guide-open-2563eb)](https://tdaa-go.github.io/TDAA-Go/instructor-guide.html)
[![Demo site](https://img.shields.io/badge/Demo%20site-live-brightgreen)](https://tdaa-go.github.io/TDAA-Go/)

A forkable, ready-to-launch skeleton for **Test-Driven, AI-Assisted (TDAA)**
courses. Weekly learning sheets, closed-book tests, validation sets, and a
static website — all written in Typst, built by `make`, deployed to GitHub
Pages, and driven by Claude Code skills.

The approach and a 13-week classroom evaluation are reported in our paper,
*Test-Driven, AI-Assisted Learning: Replacing Lectures with Weekly Closed-Book
Tests* ([arXiv:2606.23315](https://arxiv.org/abs/2606.23315)).

> **TDAA in one sentence.** Students may use AI to *prepare*, but frequent
> closed-book tests require them to think *unaided*. TDAA-Go is the
> course-materials harness that makes the gate livable for students and the
> production tractable for instructors.

> **Status:** TDAA-Go is under active development and not yet stable.
> Interfaces, skill names, and file layouts may change between releases.
> We welcome feedback, bug reports, and feature requests — please open an
> [issue](https://github.com/TDAA-Go/TDAA-Go/issues).

## Quick start

```bash
gh repo create my-course --private --template TDAA-Go/TDAA-Go --clone
cd my-course
claude              # then in Claude Code:
> /bootstrap        # asks a few questions, writes config.toml, extracts the textbook
> /generate-week 1
```

Need anything else installed (Typst, `uv`, `gh`)? `/bootstrap` probes and
offers the right install command for your platform.

## Skills

The bundled Claude Code skills, grouped by where they sit in the weekly workflow.

**Setup** — run once
- `/bootstrap` — right after forking: asks a few questions, writes `config.toml`, extracts the textbook

**Author a week**
- `/generate-week N` — full pipeline: learning sheet + tests, with reviewer debate
- `/write-learning-sheet N` — just the learning sheet
- `/write-tests N` — tests from a finalized learning sheet

**Review & revise**
- `/review-learning-sheet N` — audit against pedagogical criteria
- `/review-tests N` — audit tests for scope and correctness
- `/revise N` — interactive chunk-by-chunk polish + test audit

**Grade & give feedback**
- `/grade-homework` — grade a folder of student submissions
- `/homework-report` — PDF report from grading output

**Use as a student**
- `/learn N` — walk through a learning sheet interactively

## Citing TDAA

If TDAA-Go shapes a course you teach or a paper you write, please cite our paper
([arXiv:2606.23315](https://arxiv.org/abs/2606.23315)):

> Jin-Guo Liu, Shang-Qi Lu, Xin-Ran Shi, Long-Li Zheng, and Wei Wang.
> *Test-Driven, AI-Assisted Learning: Replacing Lectures with Weekly Closed-Book
> Tests.* arXiv:2606.23315, 2026.

```bibtex
@misc{liu2026tdaa,
  title         = {Test-Driven, AI-Assisted Learning: Replacing Lectures with Weekly Closed-Book Tests},
  author        = {Liu, Jin-Guo and Lu, Shang-Qi and Shi, Xin-Ran and Zheng, Long-Li and Wang, Wei},
  year          = {2026},
  eprint        = {2606.23315},
  archivePrefix = {arXiv},
  primaryClass  = {cs.CY},
  url           = {https://arxiv.org/abs/2606.23315}
}
```

The same entry lives in [`CITATION.bib`](CITATION.bib) at the repo root.
