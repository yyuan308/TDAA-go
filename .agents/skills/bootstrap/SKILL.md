---
name: bootstrap
description: Use when setting up a new course from a forked template repo — gates on a canonical source (textbook or equivalent), ingests its title-page + ToC for metadata, optionally folds in supplementary syllabus/slides/notes, writes config.toml, extracts textbook chapters, creates the weekly schedule, and enables GitHub Pages deployment when possible
---

# Bootstrap Course

Run once after forking the template repo. Produces:

1. `textbook/*.md` (chapters extracted from the canonical source — the load-bearing input)
2. `config.toml` (course metadata, seeded from the canonical source's title page + ToC, optionally refined by supplementary refs; the checked-in `config.typ` shim loads it and re-exports the fields for Typst templates)
3. `reference/*.md` (any supplementary course materials the user supplied, converted to markdown)
4. `coursedesign/schedule.typ` (weekly section assignments, refined from the ToC draft)
5. Verified `.github/templates/*.html` placeholders intact (the Makefile substitutes them at build time; bootstrap does **not** edit the templates)
6. GitHub Pages configured to use the included `deploy-pages.yml` workflow, when the repository is already on GitHub and the authenticated user has permission

## Step 0: Verify system prerequisites (hard gate)

Before anything else, check that the tools the build pipeline depends on are
installed. **Bootstrap must not proceed if a required tool is missing.** Flag
each gap, ask the user via `AskUserQuestion` whether to install it now, and
only continue once the required set is present.

Required (hard gate — cannot proceed without these):

| Tool        | Probe command       | Purpose                                                                |
| ----------- | ------------------- | ---------------------------------------------------------------------- |
| `typst`     | `typst --version`   | Compiles every `.typ` → PDF                                            |
| `uv`        | `uv --version`      | Runs the bootstrap scripts under `scripts/`                            |
| `git`       | `git --version`     | The course lives in a git repo                                         |
| `make`      | `make --version`    | Drives `make build`, `make serve`, `make compile-tests`                |

Recommended (warn but allow proceed — bootstrap has a manual fallback):

| Tool   | Probe command  | What it unlocks                                                        |
| ------ | -------------- | ---------------------------------------------------------------------- |
| `gh`   | `gh --version` | Step 8 auto-enables GitHub Pages; without it, manual `Settings → Pages` |

**Do not probe skill-specific deps here.** Tools that are only needed by
particular downstream skills (`/grade-homework`, `/homework-report`, etc.)
must be checked **at the start of those skills**, not in bootstrap. That keeps
the gate honest: an instructor who never grades homework should not be asked
to install `pdftoppm`, `libreoffice`, `pandoc`, `chromium`, `inkscape`, etc.
just to bootstrap the course.

### Probe script

Run this once at the start of bootstrap:

```bash
missing_required=()
for cmd in typst uv git make; do
  command -v "$cmd" >/dev/null 2>&1 || missing_required+=("$cmd")
done

missing_recommended=()
command -v gh >/dev/null 2>&1 || missing_recommended+=("gh")

if [ ${#missing_required[@]} -eq 0 ] && [ ${#missing_recommended[@]} -eq 0 ]; then
  echo "OK: all prerequisites present"
else
  [ ${#missing_required[@]} -gt 0 ]    && echo "MISSING REQUIRED: ${missing_required[*]}"
  [ ${#missing_recommended[@]} -gt 0 ] && echo "MISSING RECOMMENDED: ${missing_recommended[*]}"
fi
```

### If anything is missing

Figure out the user's environment at runtime — don't follow a hardcoded
platform → command map. Inspect what's available:

```bash
uname -s                              # Darwin / Linux / MINGW… / etc.
for pm in brew apt dnf pacman zypper apk winget scoop choco; do
  command -v "$pm" >/dev/null 2>&1 && echo "available: $pm"
done
```

From that signal, pick the right install command for **each missing tool**
(`typst`, `uv`, `git`, `make`, `gh`). Some tools aren't in some package
managers (e.g. `typst` isn't in `apt`/`dnf` yet) — fall back to the official
installer or a prebuilt binary in that case:
- `typst`: https://github.com/typst/typst/releases or https://typst.app
- `uv`: https://docs.astral.sh/uv/getting-started/installation/
- `gh`: https://cli.github.com
- `git`, `make`: native package manager, Xcode Command Line Tools on macOS,
  or WSL on Windows.

Present the proposed commands to the user via `AskUserQuestion` for approval
before running anything. If the environment is unfamiliar (no known package
manager detected, or `uname` reports something exotic), do not guess — show
the user the official installer URLs and let them install manually.

### Permission flow

After the probe, present results via `AskUserQuestion`:

- If `missing_required` is empty and `missing_recommended` is empty → continue
  to Step 1.
- If anything is missing, ask:
  > "Detected missing prerequisites: REQUIRED=`[...]`, RECOMMENDED=`[...]`.
  > Detected environment: `<uname + package managers>`. Install now?"
  > - **Install all missing via the detected package manager** — propose the
  >   commands you've worked out and run them after confirmation
  > - **Show me the install commands so I can run them in another terminal**
  >   — print them, then wait for the user to confirm "done" before re-probing
  > - **Skip recommended, install required only**
  > - **Abort bootstrap** — bail out cleanly

- After installation, **re-run the probe** to confirm. Do not trust that the
  install succeeded; verify with `command -v`.
- Required-tool gate: if any required tool is still missing after the chosen
  action, stop bootstrap with a clear message. Do not silently proceed.
- Recommended-tool gate: warn but proceed. Note in the final summary which
  recommended tools were skipped so the user knows what they're giving up.

## Step 1: Require a canonical source

Bootstrap **requires a canonical written source** for the course's definitions,
theorems, proofs, and examples. The downstream skills — `write-learning-sheet`,
`review-learning-sheet`, `write-tests`, `review-tests` — all anchor against
`textbook/*.md` to verify fidelity (see AGENTS.md pitfall #4 and the M6/P7
rubric criteria in `review-learning-sheet`). Without a canonical source, the
generators have nothing to write against and the reviewers have nothing to
verify against.

Acceptable canonical sources:
- A textbook (PDF) — the typical case
- Open-access lecture notes or a monograph
- A course pack / reading bundle
- The instructor's own draft notes (LaTeX/PDF/markdown)

Ask the user (via `AskUserQuestion`) for the path to their canonical source.
If they have none, **stop bootstrap** and explain why: the generator/reviewer
pipeline has no source-of-truth to operate against. Suggest they either pick
a textbook to follow, or write a notes draft, then re-run bootstrap.

Record the canonical-source path — Step 5 will extract chapters from it into
`textbook/*.md`. For metadata purposes (Step 2), also do an **inline read** of
the title page and table of contents now and note:

- Author, title, edition (from title page / copyright page)
- ISBN if visible
- Chapter list with section numbering (from ToC) — this seeds `num-weeks` and
  the weekly schedule in Step 6

Carry these forward as a draft metadata bundle for Step 2.

## Step 1b: Collect supplementary materials (optional)

Ask whether the user *also* has supplementary materials that can refine
metadata beyond what the canonical source provides:

- Course proposal or syllabus — best for course code, semester, instructor
- Past lecture slides (PPT/PPTX) — refines weekly topic coverage
- Past lecture notes or handouts (PDF/DOCX)
- Past exams or assignments — calibrates difficulty and scope

If yes, instruct them to place the files in `reference/` and wait for
confirmation. See `reference/README.md`. These are optional — they refine
metadata in Step 2 but are not required. If the user has only the canonical
source, skip directly to Step 2 (the inline title-page + ToC read from Step 1
is enough to start).

Scan and convert `reference/` contents:

```bash
uv sync
uv run python -m scripts.scan_references reference/
uv run python -m scripts.convert_references reference/
```

After conversion, report converted count and any errors. The `.md` files stay
in `reference/` alongside the originals (binaries are gitignored, `.md` is
checked in).

> **`uv.lock` is checked in.** The template commits `uv.lock` so every fork
> gets reproducible bootstrap-script installs. If `uv sync` updates the lock
> (e.g. after a `pyproject.toml` edit), commit the new `uv.lock` alongside
> the change — do **not** add it to `.gitignore`.

## Step 2: Gather metadata

Two metadata sources to merge:

1. **Canonical source (always available)** — the title-page + ToC draft you
   read inline in Step 1. Tag each field with `canonical-source` and confidence
   `high` for title/author/edition/ISBN; `medium` for the ToC-derived
   `num-weeks` estimate and draft weekly topics (the user may want fewer or
   more weeks than the textbook has chapters).
2. **Supplementary refs (if Step 1b populated `reference/`)** — run the
   script:

   ```bash
   uv run python -m scripts.extract_metadata reference/
   ```

   This pulls course code, course name, textbook (incl. ISBN as written in
   the syllabus), instructor, institution, num-weeks, semester, and weekly
   topics from the converted markdown — each tagged with its source file and
   confidence (`high`, `medium`, `uncertain`, `possibly outdated`). Note: the
   script is regex-based on `.md`/`.txt` in `reference/` and was designed for
   syllabus-style mentions ("Textbook: X"); it does not re-scan the
   canonical-source PDF, so canonical metadata comes from the inline read in
   Step 1.

Merge the two: if both sources name the textbook, prefer the canonical
source's self-description over the syllabus's mention. If supplementary refs
fill in course-code / instructor / institution fields that the canonical
source can't know, use those.

Present the merged extractions to the user via `AskUserQuestion`, clearly marking:
- **Extracted fields** — show value + source (e.g. `Course code: PHYS 2071 (from syllabus.md)`, `Textbook author: Sipser (from canonical-source title page)`)
- **Missing fields** — ask the user to provide
- **Possibly-outdated fields** — items flagged from past semesters (old instructor names, last year's dates) need confirmation or update
- **Conflicting values** — when multiple sources disagree, show all and ask which is correct

If supplementary refs are absent and the canonical-source read didn't reveal a field (e.g. course code, semester, instructor — these aren't in textbooks), ask each missing field directly. One question per field, "Other" for free text:

| Field | Example |
|-------|---------|
| Course code | `DSAA 3071`, `PHYS 2071` |
| Course name (tagline) | `Theories in Computing`, `Quantum Physics` |
| Textbook author | `Sipser`, `Griffiths` |
| Textbook title | `Introduction to the Theory of Computation` |
| Textbook edition | `3rd ed.` |
| Number of weeks | `13` |
| Instructor | `Jane Doe` |
| Institution | `HKUST(GZ)` |
| Zulip stream (optional) | `DSAA3071-2026-Spring` — leave blank to skip the release workflow entirely (Step 7 then doesn't apply) |

The Zulip stream is the only optional field. If the user doesn't say they want Zulip drip-release, do not prompt for it — leave it blank and move on. It can be filled in later by editing `config.toml`; the workflow self-disables while it's empty.

## Step 3: Write `config.toml`

Copy `config.toml.example` to `config.toml` and fill in the values:

```toml
course-code      = "DSAA 3071"
course-name      = "Theories in Computing"
textbook-author  = "Sipser"
textbook-title   = "Introduction to the Theory of Computation"
textbook-edition = "3rd ed."
instructor       = "Jin-Guo Liu"
institution      = "HKUST(GZ)"
zulip-stream     = ""   # optional; "" disables the release workflow. Set only if user opted in.
textbook-short   = ""   # empty → falls back to textbook-author
```

Do **not** edit `config.typ` — it's a checked-in shim that just calls
`toml("config.toml")` and re-exports each field, so existing template imports
(`#import "../config.typ": course-code, ...`) keep working unchanged.

## Step 4: Verify HTML placeholders (do NOT edit templates)

**Do not edit `.github/templates/*.html`.** The Makefile's `SUB_HTML` rule
substitutes `{{COURSE_CODE}}`, `{{COURSE_NAME}}`, `{{TEXTBOOK_INFO}}`,
`{{TEXTBOOK_SHORT}}`, and `{{INSTITUTION}}` at build time from `config.toml`.
Baking values into the templates here would freeze them — future `config.toml`
edits wouldn't propagate. The `release-materials.yml` workflow likewise reads
`zulip-stream` from `config.toml` at runtime.

Just verify the placeholders are still present in the templates so build-time
substitution will work:

```bash
grep -rE '\{\{(COURSE_CODE|COURSE_NAME|TEXTBOOK_INFO|TEXTBOOK_SHORT|INSTITUTION)\}\}' .github/templates/ \
  > /dev/null \
  && echo "OK: placeholders intact, Makefile will substitute at build" \
  || echo "WARN: placeholders missing — Makefile substitution won't run"
```

Then confirm a real build resolves them. After `make build`, no course-level
`{{...}}` token should remain in `_site/` (per-build placeholders like
`{{WEEK}}`, `{{TITLE}}`, `{{FILENAME}}`, `{{PAGES_JSON}}` are filled by the
Makefile per page):

```bash
make build
grep -rE '\{\{(COURSE_CODE|COURSE_NAME|TEXTBOOK_INFO|TEXTBOOK_SHORT|INSTITUTION)\}\}' _site/ \
  && echo "ERROR: course-level placeholders survived build" \
  || echo "OK: build output is clean"
```

## Step 5: Ingest textbook

Use the canonical-source path you recorded in Step 1 (re-ask only if it's a
multi-volume work and additional PDFs cover other chapters). For each PDF,
extract chapters into `textbook/NN.md`. Each file:

```markdown
# Chapter N: [Title]

## N.1 [Section Title]

**Definition N.1 ([Name])**
[formal statement]

**Theorem N.2 ([Name])**
[statement]

*Proof.* [proof text]

**Example N.3**
[worked example]
```

Rules:
- Preserve the textbook's numbering exactly (Definition 2.1, Theorem 3.4, etc.)
- Extract ALL definitions, theorems, lemmas, corollaries, proofs, and key examples
- Omit exercises, historical notes, and filler prose
- Keep mathematical notation in LaTeX-compatible form

After extraction, summarize for the user: chapters, definitions, theorems, proofs per chapter. Let them verify before proceeding.

## Step 6: Create schedule

Start from the ToC-derived draft you produced in Step 1. Refine it by reading
all `textbook/*.md` (now extracted in Step 5) — section grouping, prerequisite
ordering, and per-week volume can only be judged once you've seen the actual
content, not just the ToC. Use `coursedesign/schedule.example.typ` as a
structural reference.

Schedule format:

```typst
#show link: set text(blue)

= Course schedule

#align(center, text(10pt)[#table(columns: 4, inset: 7pt,
  table.header([*Week*], [*Sections*], [*Topics*], [*Resources*]),
  [1], [§1.1, §1.2], [Topic A], align(left)[- resource link],
  // ...
)])
```

Guidelines:
- Each week covers a coherent topic (don't split a concept across weeks)
- Earlier weeks build foundations; later weeks use them
- Balance content volume roughly evenly
- Group related sections

Present the schedule to the user, let them adjust ordering/grouping/week count, then write to `coursedesign/schedule.typ`.

## Step 7: (optional) Seed `coursedesign/release-schedule.json`

Skip this entire step if `zulip-stream` is blank in `config.toml` — the workflow self-disables and no schedule file is needed.

If the user enabled Zulip release, copy `coursedesign/release-schedule.example.json` to `coursedesign/release-schedule.json` and seed the first few entries. Format:

```json
[
  {"date": "2026-02-15", "time": "09:00", "week": 1, "action": "learning-sheet"},
  {"date": "2026-02-19", "time": "18:00", "week": 1, "action": "validation"},
  {"date": "2026-02-22", "time": "23:00", "week": 1, "action": "test-answer"}
]
```

Times are Beijing time. The hourly cron job picks up matching entries.

## Step 8: Configure GitHub Pages

The template already includes:
- `.github/templates/` — static website templates for the course index, PDF viewer, setup guide, and styles
- `.github/workflows/deploy-pages.yml` — a workflow that runs `make build`, uploads `_site/`, and deploys it to GitHub Pages

GitHub Pages itself still has to be enabled once for the course repository. If the repository has a GitHub `origin` remote and `gh` is authenticated, ask the user whether to enable Pages automatically. If they agree, first identify the repository:

```bash
gh repo view --json nameWithOwner -q .nameWithOwner
```

Then check whether Pages is already enabled:

```bash
gh api "repos/OWNER/REPO/pages" --jq '{html_url, build_type}'
```

In all `gh api` commands below, replace `OWNER/REPO` with the repository returned by `gh repo view`. If this returns an existing site whose `build_type` is `workflow`, report the Pages URL and continue. If Pages is not enabled, create it with the GitHub Actions workflow build type:

```bash
gh api --method POST "repos/OWNER/REPO/pages" -f build_type=workflow
```

If Pages exists but uses another build type, update it:

```bash
gh api --method PUT "repos/OWNER/REPO/pages" -f build_type=workflow
```

If any command fails because the repository is not on GitHub, `gh` is not authenticated, or the user lacks repository administrator / "manage GitHub Pages settings" permission, do not fail bootstrap. Report the manual fallback:

1. Push the repository to GitHub.
2. Open the repository page.
3. Go to `Settings -> Pages`.
4. Set `Source` to `GitHub Actions`.

After Pages is enabled, the included `deploy-pages.yml` workflow publishes on pushes to `main` that touch weekly Typst files, `.github/templates/**`, `config.toml`, the Makefile, or the workflow itself.

## After bootstrap

The repo is ready. The user can now run:
- `/generate-week N` — full pipeline for week N
- `/write-learning-sheet N` — single learning sheet
- `/review-learning-sheet N` — review against quality criteria

Verify the build works:

```bash
make build
```

For local preview, run `make serve`.
