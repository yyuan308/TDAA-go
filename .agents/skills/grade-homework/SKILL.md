---
name: grade-homework
description: Use when the user wants to grade a folder of student homework submissions against a teacher-provided solutions document — handles mixed formats (PDF, JPG, DOCX), produces a grades CSV and per-student English feedback with explicit flagging of ambiguous items for teacher review. Triggers on phrases like "grade the homework", "mark HW9", "批作业".
---

# grade-homework

## When to use

- User wants to grade a folder of student submissions.
- A solutions document is present (either auto-discoverable by filename or provided explicitly).
- Student filenames follow `<student>_..._<original>.<ext>`.

Do NOT use for: single-file grading (just read it inline), plagiarism detection, or rewriting the solutions doc.

## What this skill produces

- `<working_dir>/grades/grades.csv` — one row per student, per-question columns, total, flags.
- `<working_dir>/grades/feedback/<student>.md` — English feedback, per-question breakdown, flags summary.

## Prerequisites (conditional on submission formats)

Only `.docx` submissions need an external conversion toolchain. PDF and image
submissions go through Python alone, so most courses won't need anything
beyond `uv`.

Probe at the start of Step 1 (after `discover.py` reports what's present):

```bash
# Only if discover.py finds any .docx submissions
if ls "$PWD"/*.docx >/dev/null 2>&1; then
  if ! command -v libreoffice >/dev/null 2>&1 && ! command -v soffice >/dev/null 2>&1; then
    if ! { command -v pandoc >/dev/null 2>&1 \
        && { command -v google-chrome >/dev/null 2>&1 \
          || command -v chromium     >/dev/null 2>&1; }; }; then
      echo "MISSING: docx toolchain (need libreoffice OR pandoc+browser)"
    fi
  fi
fi
```

If the toolchain is missing, ask via `AskUserQuestion` whether to install
before grading begins. Without it, `.docx` submissions are silently flagged
`needs_manual_review` and grading proceeds for the rest — call out exactly
how many students that affects so the user can make an informed choice.

When the user says yes, figure out the right install command for their
environment at runtime (inspect `uname -s` and which of `brew`/`apt`/`dnf`/
`pacman`/`winget`/etc. is available — see `bootstrap` Step 0 for the
detection pattern), and propose the commands via `AskUserQuestion` before
running them. Notes on package naming:

- `libreoffice` may be `libreoffice-fresh` on Arch and `--cask libreoffice`
  on Homebrew; on Windows use `TheDocumentFoundation.LibreOffice` via winget.
- Headless browser for the fallback path: `google-chrome` or `chromium` —
  either works.
- `inkscape` is only needed by the fallback path when a `.docx` embeds WMF/EMF
  images. Install on demand if `to_images.py` flags missing inkscape during a
  run; otherwise leave it alone.

## Workflow

Skill root: `~/.Codex/skills/grade-homework/`. Run helper scripts from that root.

### Step 1 — Discover

Run `discover.py` on the working directory containing submissions. Parse the JSON:

```bash
python ~/.Codex/skills/grade-homework/scripts/discover.py "$PWD"
```

If `solutions_error` is non-null, surface it to the user and stop. If the user passed a solutions path explicitly, use that instead of auto-discovery.

`discover.py` recurses into subdirectories (so `./submissions/` is picked up automatically) and skips hidden files/dirs. The JSON also includes a `late_students` list — student names whose filename contains `_LATE_` (case-insensitive). Surface the list to the user before grading so they can decide whether to apply a late-submission policy.

### Step 2 — Load the grading prompt and parse the rubric

Read `~/.Codex/skills/grade-homework/references/grading-prompt.md` and follow it.

Convert the solutions file to page images:

```bash
python ~/.Codex/skills/grade-homework/scripts/to_images.py <solutions_file> /tmp/grade-homework/solutions/
```

View the solutions images, parse the `[N pts]` allocations into a rubric table, and **confirm with the user before continuing**. If no `[N pts]` markers are found, stop and ask for point allocations.

### Step 3 — Grade students one at a time

For each student (in alphabetical order unless the user specifies otherwise):

1. Convert each of that student's files to images:

   ```bash
   python ~/.Codex/skills/grade-homework/scripts/to_images.py "<student_file>" /tmp/grade-homework/<student>/
   ```

   If any file returns exit code 3 (`docx_unsupported`), include a `needs_manual_review` flag for that student and skip that file — do not block the whole run.

2. View the student's page images and score per the grading prompt. Produce the JSON record.

3. Pipe the record into `write_outputs.py`:

   ```bash
   echo "$RECORD_JSON" | python ~/.Codex/skills/grade-homework/scripts/write_outputs.py "$PWD/grades"
   ```

4. After every 3 students, briefly summarize progress to the user so they can course-correct early.

### Step 4 — Recovery

If `grades/grades.csv` already exists at the start of a run, `write_outputs.py` will skip any student already present. To re-grade a student, delete their row from the CSV and their feedback file before running.

### Step 5 — Handoff

When all students are graded, list:

- Any students skipped (with reason).
- The total number of flagged items and which questions they concentrate on — this is what the teacher should spot-check before publishing grades.

## Failure modes

- **No solutions file / multiple candidates** → stop, ask user.
- **No `[N pts]` markers** → stop, ask user for allocations.
- **DOCX submission with no conversion toolchain** → `to_images.py` tries `libreoffice`/`soffice` first, then `pandoc + google-chrome/chromium` (extracts WMF/EMF → PNG via `inkscape` if present, converts HTML→PDF via headless Chrome). If neither path works, the student is flagged `needs_manual_review` and grading continues.
- **CSV header mismatch mid-run** (`write_outputs.py` exit 4) → rubric changed; stop and reconcile with user.

## Quality bar

This skill does single-pass grading with conservative flagging. It is **not** a substitute for teacher review — spot-check at least 3 students against your own grading before publishing, and always review flagged items.
