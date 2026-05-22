# TDAA-Go

A forkable, ready-to-launch skeleton for **Test-Driven, AI-Assisted (TDAA)**
courses. Weekly learning sheets, closed-book tests, validation sets, and a
static website — all written in Typst, built by `make`, deployed to GitHub
Pages, and driven by Claude Code skills.

> **TDAA in one sentence.** Students may use AI to *prepare*, but frequent
> closed-book tests require them to think *unaided*. TDAA-Go is the
> course-materials harness that makes the gate livable for students and the
> production tractable for instructors.

## What you get

- **Weekly materials pipeline** — learning sheet, test, test variant B, and
  validation set per week; optional research-track advanced learning sheet
- **Claude Code skills** — `/bootstrap`, `/generate-week`, `/write-learning-sheet`,
  `/review-learning-sheet`, `/write-tests`, `/review-tests`, `/revise`,
  `/grade-homework`, `/homework-report`, `/learn`, `/pivot`
- **Build infrastructure** — `make build` compiles learning sheets to PDF and
  creates the GitHub Pages viewer; `make compile-tests` builds assessments;
  `make serve` previews locally
- **Optional Zulip release workflow** — drip-release materials by date/time
- **Optional GitHub Pages deployment** on push to `main`

## Instructor Guide — step by step

### Step 0. Prerequisites

You need these on your `$PATH` before running `/bootstrap`:

- **Required:** `typst`, `uv`, `git`, `make`, and the Claude Code CLI
- **Recommended:** `gh` (lets `/bootstrap` auto-enable GitHub Pages;
  otherwise you'll flip the switch manually in the repo settings)

Install whichever are missing using your platform's native package manager
(Homebrew on macOS, apt/dnf/pacman on Linux, winget/scoop on Windows) or the
official installer from each project's website. If you'd rather not figure
it out yourself, just start `/bootstrap` — it probes for these on first run
and offers to install anything missing with the right command for your
environment.

Skills that grade homework (`/grade-homework`, `/homework-report`) have their
own runtime checks for `pdftoppm`, `libreoffice`, etc. — those are not
required for bootstrap or weekly material generation.

You'll also need a **textbook PDF** (or equivalent canonical source: open
lecture notes, course pack, instructor draft) and a GitHub account.
Optionally, gather any existing course materials you have (syllabus, past
lecture slides, past exams) — `/bootstrap` can extract course metadata from
them so you don't have to type everything by hand.

### Step 1. Fork the template

Pick **one** of these:

```bash
# Option A: fresh clone (recommended)
gh repo create my-course --private --template GiggleLiu/TDAA-Go --clone
cd my-course

# Option B: copy locally if the repo isn't on GitHub yet
cp -r path/to/TDAA-Go ~/my-course
cd ~/my-course
git init -b main && git add -A && git commit -m "fork from TDAA-Go"
```

### Step 2. Bootstrap the course

Open the repo in Claude Code and run the bootstrap skill:

```bash
claude
```

```
> /bootstrap
```

First, `/bootstrap` asks whether you have existing course materials. If yes,
drop them into `reference/` (syllabus, lecture slides, past exams as PDF /
PPTX / DOCX / MD); the skill converts them to markdown and extracts course
code, name, textbook, instructor, institution, and weekly topics, each tagged
with its source file and a confidence level. You confirm or correct the
extracted values, and only missing fields are asked manually. See
`reference/README.md` for the list of valuable inputs.

If you have no reference materials, `/bootstrap` falls back to asking every
field directly: course code, course name, textbook author/title/edition,
week count, instructor, institution, and (optionally) a Zulip stream name.
Then you'll be asked for your **textbook PDF path(s)**.

What `/bootstrap` produces:
- `reference/*.md` (existing materials converted to markdown)
- `config.toml` (course metadata; the checked-in `config.typ` shim loads it
  and re-exports each field, so every Typst template imports from `config.typ`
  but the values you edit live in `config.toml`)
- Substituted placeholders in `.github/templates/*.html` and
  `.github/workflows/release-materials.yml`
- `textbook/01.md`, `02.md`, … (extracted definitions, theorems, proofs,
  examples — review and correct these before continuing)
- `coursedesign/schedule.typ` (weekly section assignments — adjust before
  continuing)

Verify: `grep -r '{{' .github/` should print nothing (no unfilled placeholders).

### Step 3. Generate your first week

```
> /generate-week 1
```

This runs the full pipeline: writer + reviewer debate for the learning sheet,
then writer + reviewer for the test, test variant B, and validation set. You'll
end up with `week1/1.learning-sheet.typ`, `1.test.typ`, `1.test.B.typ`, and
`1.validation.typ`.

If you want finer control, use the smaller skills:
- `/write-learning-sheet 1` — just the learning sheet
- `/review-learning-sheet 1` — review against quality criteria
- `/revise 1` — interactive chunk-by-chunk revision
- `/write-tests 1` — generate tests from a finalized learning sheet
- `/review-tests 1` — review tests for scope/correctness

### Step 4. Build and preview locally

```bash
make serve   # builds, then opens http://localhost:8000
```

The site lists every weekly learning sheet with a built-in PDF viewer.
Single-file iteration:

```bash
typst compile --root . week1/1.learning-sheet.typ
```

### Step 5. Push to GitHub & enable Pages

```bash
git add -A && git commit -m "week 1 materials"
git push origin main
```

Then on GitHub: **Settings → Pages → Source: GitHub Actions**. The
`deploy-pages.yml` workflow rebuilds and publishes on every push to `main` that
touches `.typ`, `.html`, or the Makefile.

### Step 6. (Optional) Wire up Zulip drip release

If you set a `zulip-stream` in `config.toml`, the `release-materials.yml`
workflow runs hourly and releases learning sheets / validation answers / test
answers per a schedule you control.

1. Repo **Settings → Secrets and variables → Actions** → add three secrets:
   - `ZULIP_BOT_EMAIL`
   - `ZULIP_BOT_API_KEY`
   - `ZULIP_SITE` (e.g. `https://yourorg.zulipchat.com`)
2. Copy the example schedule and edit dates/times (Beijing time):

   ```bash
   cp coursedesign/release-schedule.example.json coursedesign/release-schedule.json
   $EDITOR coursedesign/release-schedule.json
   git add coursedesign/release-schedule.json && git commit -m "release schedule" && git push
   ```

### Step 7. Iterate weekly

For each subsequent week:

```
> /generate-week 2
> /review-learning-sheet 2     # if you skipped the full pipeline
> /revise 2                    # polish prose, audit tests
```

```bash
make build                     # build before pushing
# optional local preview: make serve
git add week2/ && git commit -m "week 2" && git push
```

### Step 8. Grade homework

When students submit homework (mixed PDF / JPG / DOCX in a folder):

```
> /grade-homework
> /homework-report             # builds a teacher-facing PDF report
```

Produces a grades CSV plus per-student feedback, with explicit flags on items
that need teacher review.

### Step 8b. (Optional) Zulip-based submission and feedback

If your students already use Zulip, you can skip the "manage a folder of
files" workflow entirely: students DM a course-specific bot with photos of
their homework, you run one command to pull + grade + DM feedback back.

```
> /setup-zulip-grading         # one-time: creates the bot, writes .zuliprc, seeds roster
> /zulip-mark-feedback N       # per homework: pulls DMs, grades, sends feedback
```

`/setup-zulip-grading` walks you through getting a personal Zulip API key,
creates a generic bot in your realm via the API (no manual UI clicks unless
your realm restricts bot creation), and bootstraps `coursedesign/roster.csv`
(committed; the Zulip-email → student-id mapping).

`/zulip-mark-feedback N` has four checkpointed phases:

1. **Pull** — fetches DMs in the active window, drops attachments into
   `weekN/submissions/` with the filename convention `/grade-homework` expects.
2. **Grade** — delegates to the unchanged `/grade-homework`.
3. **Report** — optionally delegates to `/homework-report`.
4. **Send** — DMs each student their `feedback/<student_id>.md` back via the
   bot. Default is "preview locally first" — nothing goes out until you say so.

State files (`.zuliprc`, `week*/submissions/`, `week*/zulip-*.json`) are
gitignored. The roster is committed.

---

### Quick reference — the full skill list

| Skill | When to use |
|-------|-------------|
| `/bootstrap` | Once, right after forking |
| `/generate-week N` | Generate a full week (learning sheet + tests) |
| `/write-learning-sheet N` | Just write the learning sheet |
| `/review-learning-sheet N` | Review against pedagogical criteria |
| `/revise N` | Interactive polish + test audit |
| `/write-tests N` | Generate tests from a finalized learning sheet |
| `/review-tests N` | Audit tests for scope & correctness |
| `/grade-homework` | Grade a folder of student submissions |
| `/homework-report` | PDF report from grading output |
| `/setup-zulip-grading` | Once: create a Zulip grading bot + bootstrap the student roster |
| `/zulip-mark-feedback N` | Per HW: pull DMs from the bot, grade, DM feedback back |
| `/learn N` | Student-side: walk through a learning sheet interactively |
| `/pivot N` | Re-skin a learning sheet's task to a new context |

## Layout

```
config.toml.example                  # Edit (or run /bootstrap) → config.toml
config.typ                           # Shim that loads config.toml for templates
Makefile                             # `make build` / `make serve`
templates/                           # Typst libraries (do not edit per-week)
├── learning-sheet.typ               # Shared lib: theorem envs, prompt blocks
├── advanced-learning-sheet.typ      # Research-track lib (deep dives, gedanken)
├── test.typ                         # Shared lib: question counter, solution toggle
└── week-template/                   # Copy to weekN/ to start a week
coursedesign/
├── weekly-materials-guide.md        # Pedagogical principles & checklists
├── schedule.example.typ             # Example schedule (bootstrap fills in real one)
└── release-schedule.example.json    # Example Zulip release schedule
.github/
├── templates/{index,viewer,setup-guide}.html, styles.css
└── workflows/
    ├── deploy-pages.yml             # Build PDFs + viewer; deploy to Pages
    └── release-materials.yml        # Hourly Zulip drip release (optional)
.claude/
├── CLAUDE.md                        # Project instructions for Claude Code
├── rules/typst.md                   # Typst writing conventions
└── skills/                          # Slash commands
```

After bootstrap, you'll also have:

```
config.toml                          # Course metadata (filled by /bootstrap)
textbook/NN.md                       # Extracted textbook chapters
coursedesign/schedule.typ            # Weekly section assignments
weekN/                               # Per-week materials (created by /generate-week)
```

## Design principles

1. **Flatten the learning curve** — break content into weekly chunks with clear
   objectives
2. **Remove uncertainty** — pair every test with a validation set that defines
   the test boundary
3. **Enable AI-assisted study** — every learning sheet ships with copy-paste
   prompts students run against any LLM

## Build commands

```bash
make build              # Build entire site (PDFs + HTML viewers)
make compile-tests      # Compile all test and validation files
make dump-solutions     # Compile tests/validations with solutions visible
make serve              # Build then serve locally at http://localhost:8000
make serve-only         # Serve without rebuilding
make clean              # Remove _site/
```

Single-file compile:

```bash
typst compile weekN/N.learning-sheet.typ
```

## Requirements

- [Typst](https://typst.app) (latest)
- Python 3 (for `make serve` and bootstrap scripts)
- [`uv`](https://docs.astral.sh/uv/) (for installing bootstrap script deps)
- Optional: [`entr`](https://github.com/eradman/entr) for `make watch`

## Citing TDAA

If TDAA-Go shapes a course you teach or a paper you write, please cite the
methodology paper this template was extracted from:

> Jin-Guo Liu, Shang-Qi Lu, Xin-Ran Shi, Long-Li Zheng and Wei Wang.
> *High-Frequency Test-Driven Learning with AI: Making Strict Quality Gates
> Acceptable and Scalable.* DSAA 3071, HKUST(GZ), Spring 2026.
