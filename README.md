# TDAA-Go

[![Instructor guide](https://img.shields.io/badge/Instructor%20guide-open-2563eb)](https://giggleliu.github.io/TDAA-Go/instructor-guide.html)
[![Documentation](https://img.shields.io/badge/Documentation-GitHub%20Pages-brightgreen)](https://giggleliu.github.io/TDAA-Go/)

A forkable, ready-to-launch skeleton for **Test-Driven, AI-Assisted (TDAA)**
courses. Weekly learning sheets, closed-book tests, validation sets, and a
static website — all written in Typst, built by `make`, deployed to GitHub
Pages, and driven by Claude Code skills.

> **TDAA in one sentence.** Students may use AI to *prepare*, but frequent
> closed-book tests require them to think *unaided*. TDAA-Go is the
> course-materials harness that makes the gate livable for students and the
> production tractable for instructors.

> **Status:** TDAA-Go is under active development and not yet stable.
> Interfaces, skill names, and file layouts may change between releases.
> We welcome feedback, bug reports, and feature requests — please open an
> [issue](https://github.com/GiggleLiu/TDAA-Go/issues).

## Quick start

```bash
gh repo create my-course --private --template GiggleLiu/TDAA-Go --clone
cd my-course
claude              # then in Claude Code:
> /bootstrap        # asks a few questions, writes config.toml, extracts the textbook
> /generate-week 1
```

Need anything else installed (Typst, `uv`, `gh`)? `/bootstrap` probes and
offers the right install command for your platform.

## Skills

| Skill | When to use |
|-------|-------------|
| `/bootstrap` | Once, right after forking |
| `/generate-week N` | Full week pipeline (learning sheet + tests, with reviewer debate) |
| `/write-learning-sheet N` | Just the learning sheet |
| `/review-learning-sheet N` | Audit against pedagogical criteria |
| `/revise N` | Interactive chunk-by-chunk polish + test audit |
| `/write-tests N` | Generate tests from a finalized learning sheet |
| `/review-tests N` | Audit tests for scope and correctness |
| `/grade-homework` | Grade a folder of student submissions |
| `/homework-report` | PDF report from grading output |
| `/setup-zulip-grading` | Once: create a Zulip grading bot + bootstrap the student roster |
| `/zulip-mark-feedback N` | Per HW: pull DMs from the bot, grade, DM feedback back |
| `/learn N` | Student-side: walk through a learning sheet interactively |
| `/pivot N` | Re-skin a learning sheet's task to a new context |

## Citing TDAA

If TDAA-Go shapes a course you teach or a paper you write, please cite:

> Jin-Guo Liu, Shang-Qi Lu, Xin-Ran Shi, Long-Li Zheng and Wei Wang.
> *High-Frequency Test-Driven Learning with AI: Making Strict Quality Gates
> Acceptable and Scalable.* DSAA 3071, HKUST(GZ), Spring 2026.
