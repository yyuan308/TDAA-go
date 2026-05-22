# CLAUDE.md

**TDAA-Go** — a forkable Test-Driven, AI-Assisted course-materials harness.
Written in Typst, compiled to PDFs, and served as a static website. Course
identity (code, name, textbook, instructor, institution) lives in
`config.toml`; `config.typ` is a thin shim that loads the TOML and re-exports
the fields for templates. Read `config.toml` before generating user-facing
content.

## Build Commands

```bash
make build              # Build entire site (PDFs + HTML viewers)
make compile-tests      # Compile all test and validation files
make serve              # Build then serve locally at http://localhost:8000
make clean              # Clean build artifacts
typst compile weekN/N.learning-sheet.typ   # Single file
```

## Repository Structure

```
config.toml               # Course metadata (course-code, course-name, textbook, instructor, institution)
config.typ                # Shim that loads config.toml and re-exports fields for Typst templates
pyproject.toml            # Python dep manifest used by /bootstrap
reference/                # Drop syllabus / past slides / past exams here before /bootstrap (binaries gitignored; converted *.md committed)
scripts/                  # Bootstrap utilities: scan_references, convert_references, extract_metadata
weekN/                    # Weekly materials (N = 1..num-weeks)
├── N.learning-sheet.typ  # AI-assisted learning guide
├── N.advanced-learning-sheet.typ  # Research-track guide (deep dives, inquiry-based)
├── N.test.typ            # Closed-book assessment (130 pts)
├── N.test.B.typ          # Alternative/make-up test
├── N.validation.typ      # Self-validation practice
└── plan.md               # Week-specific requirements (if exists)
templates/                # All Typst templates in one place
├── learning-sheet.typ    # Shared lib: styling, theorem envs, utilities
├── advanced-learning-sheet.typ  # Shared lib: deep indigo palette, inquiry envs
├── test.typ              # Shared lib: page setup, solution toggle, question counter
└── week-template/        # Copy this directory to start a new week
coursedesign/
├── schedule.typ          # Weekly topic → textbook section mapping (created by /bootstrap)
└── weekly-materials-guide.md  # Design guidelines and checklists
textbook/                 # Extracted textbook content in markdown (created by /bootstrap)
.claude/skills/           # Slash commands (see below)
```

## Skills

- `/bootstrap` — one-time: write `config.toml`, ingest textbook PDFs to `textbook/*.md`, create `coursedesign/schedule.typ`, fill in HTML/workflow placeholders
- `/generate-week N` — full pipeline: learning sheet (adversarial debate) + tests (write + review)
- `/write-learning-sheet N` — write a single learning sheet (no review)
- `/review-learning-sheet N` — review a learning sheet (must-have + good-to-have lens)
- `/write-tests N` — write test, test.B, and validation from a finalized learning sheet
- `/revise N` — interactive chunk-by-chunk revision (intuition, rigor, conciseness) + test audit
- `/review-tests N` — review tests for scope alignment, correctness, and consistency
- `/grade-homework` — grade a folder of student submissions against a teacher solutions doc; produces a CSV and per-student feedback
- `/homework-report` — after `/grade-homework`, build a teacher-facing PDF report with per-student marks and feedback
- `/setup-zulip-grading` — one-time: create a course grading bot on Zulip, write `.zuliprc`, bootstrap `coursedesign/roster.csv` (enables phone-photo submissions via DM)
- `/zulip-mark-feedback N` — pull homework photos students DM'd to the bot, delegate to `/grade-homework` + optional `/homework-report`, then DM per-student feedback back

## Working with Weekly Materials

When generating or editing, always check (in order):
1. `config.toml` — course-code, course-name, textbook reference
2. `coursedesign/schedule.typ` — textbook sections assigned to the week
3. `textbook/*.md` — definitions, theorems, examples to include
4. `weekN/plan.md` — specific requirements for this week (if it exists)
5. `week1/*` — canonical reference for style and quality (after week 1 has been generated)
6. Previous week — ensure no content overlap

## Typst Conventions

- `@preview/fletcher` for diagrams, `@preview/ctheorems` for theorem environments
- `#prompt[]` blocks with `#badge-deeper` / `#badge-broader` for AI prompts
- `definition`, `theorem`, `proof`, `example`, `remark` environments
- Document titles: `#set document(title: "Week N - Topic")`
- General Typst writing rules (math, CeTZ, plotting, etc.) are in `.claude/rules/typst.md`

## Design Principles

- **FIDS mindset** (Feel → Image → Do → Share): implicit pedagogy, NOT explicit boxes
- **Blog-like prose**: smooth narrative, not fragmented bullets
- **Define before use**: all symbols/concepts introduced before first use
- **No page breaks** between parts (only first page has pagebreak)
- **Test scope rule**: test.typ must not exceed validation.typ scope

## Pedagogical Quality Criteria

Two dimensions used by both generation and review:

**Motivation & Intuition** — for each concept, check:
- *What/Why*: clearly named, motivated (why care? what breaks without it?)
- *How*: concrete example *before* formal definition; intuition before formalism
- *When/Where*: real-world context (engineering, applications, research)
- *FIDS flow*: open with curiosity → build mental picture → practice via prompts → summarize

**Proof Quality** — for each proof/argument:
- *Self-contained*: uses only previously defined terms; no forward references
- *Key insight*: the "aha" moment is called out explicitly
- *Why non-trivial*: explains what's surprising or what naive approach fails
- *Examples for hard steps*: concrete illustration of abstract steps
- *Logical flow*: no gaps; each step follows clearly

## Common Pitfalls

1. **Undefined terms in tests**: every term in test/validation must be defined in learning-sheet
2. **Test/validation mismatch**: must have same structure and question count
3. **AI prompts too narrow**: include "broader" (frontiers, applications), not just "deeper"
4. **Textbook misalignment**: definitions/theorems/proofs must match the assigned textbook exactly
