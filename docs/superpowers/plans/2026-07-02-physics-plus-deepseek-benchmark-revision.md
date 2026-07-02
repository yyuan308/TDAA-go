# Physics Plus and DeepSeek Benchmark Revision Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the inactive paid OpenAI API experiment with blind GPT-5.5 Codex App transcription and grading runs, retain DeepSeek V4-Pro API grading, and finish the Physics Week 9 benchmark without exposing gold data to model threads.

**Architecture:** Condition-specific blind packets copy only approved anonymous inputs, frozen prompts, schemas, and hashes into private packet directories. Fresh GPT-5.5 Codex threads write JSON outputs into those packets; the main benchmark validates and imports them into immutable run directories. DeepSeek V4-Pro grades the same frozen text through the existing retry runner, after which development-only selection is frozen before held-out execution.

**Tech Stack:** Python 3.12, standard-library `csv/json/hashlib/shutil`, Pillow-backed existing image pipeline, OpenAI Python SDK pointed at the DeepSeek-compatible endpoint, `unittest`, private file artifacts under `Data/physics/benchmark`.

---

## File Map

- `benchmark/physics/configs/physics_week9.json`: active interactive GPT and DeepSeek model labels, one-run policy, and excluded infrastructure runs.
- `benchmark/physics/packets.py`: deterministic blind-packet construction, manifest hashing, freeze gate, and forbidden-content audit.
- `benchmark/physics/codex_import.py`: transcript and grading JSON validation plus immutable Codex run import.
- `benchmark/physics/deepseek_runs.py`: text-only `D1/D2` execution over frozen transcripts.
- `benchmark/physics/evaluation.py`: load gold and predictions, exclude infrastructure failures, compute condition metrics, and freeze the development selection.
- `benchmark/physics/report.py`: anonymous benchmark Markdown renderer with required limitations.
- `benchmark/physics/cli.py`: thin command wiring for packet build, Codex import, DeepSeek run, freeze, evaluate, and report.
- `benchmark/physics/prompts/transcribe.txt`: frozen `T1` instructions.
- `benchmark/physics/prompts/grade_structured.txt`: frozen `G2/G3/D1/D2` instructions.
- `tests/benchmark/physics/test_packets.py`: packet isolation and determinism.
- `tests/benchmark/physics/test_codex_import.py`: transcript and score import validation.
- `tests/benchmark/physics/test_deepseek_runs.py`: identical-text DeepSeek execution and terminal failures.
- `tests/benchmark/physics/test_evaluation.py`: run exclusion, metrics, and freeze gate.
- `tests/benchmark/physics/test_report.py`: anonymous claims and limitation language.
- `tests/benchmark/physics/test_cli_revision.py`: end-to-end command routing with fake providers.

Private runtime artifacts remain ignored by Git:

```text
Data/physics/benchmark/
  blind_packets/
  transcripts/automatic/
  transcripts/human/
  runs/
  reports/
  freeze.json
```

### Task 1: Activate the Revised Model Configuration

**Files:**
- Modify: `benchmark/physics/configs/physics_week9.json`
- Modify: `tests/benchmark/physics/test_providers.py`

- [ ] **Step 1: Write the failing configuration test**

Replace the old frozen-config assertions with:

```python
def test_revised_config_uses_interactive_gpt_and_one_run():
    path = Path("benchmark/physics/configs/physics_week9.json")
    config = json.loads(path.read_text(encoding="utf-8"))

    assert config["gpt_execution"] == "codex-plus-interactive"
    assert config["gpt_display_model"] == "GPT-5.5"
    assert config["deepseek_model"] == "deepseek-v4-pro"
    assert config["runs_per_condition"] == 1
    assert config["excluded_run_ids"] == ["G1-dev-r1"]
    assert "openai_model" not in config
```

- [ ] **Step 2: Run the test and verify the old configuration fails**

Run:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.benchmark.physics.test_providers.ProviderTests.test_revised_config_uses_interactive_gpt_and_one_run -v
```

Expected: failure because `gpt_execution` and `excluded_run_ids` are absent.

- [ ] **Step 3: Replace the active configuration**

Write exactly these active fields while retaining the existing dataset, seed,
bootstrap count, and retry count:

```json
{
  "dataset": "physics_week9",
  "gpt_execution": "codex-plus-interactive",
  "gpt_display_model": "GPT-5.5",
  "deepseek_model": "deepseek-v4-pro",
  "runs_per_condition": 1,
  "split_seed": 20260701,
  "bootstrap_samples": 10000,
  "max_retries": 2,
  "excluded_run_ids": ["G1-dev-r1"]
}
```

- [ ] **Step 4: Run the provider/config tests**

```powershell
.\.venv\Scripts\python.exe -m unittest tests.benchmark.physics.test_providers -v
```

Expected: all provider tests pass; the OpenAI adapter unit tests remain as inactive infrastructure tests.

- [ ] **Step 5: Commit the revised configuration**

```powershell
git add benchmark/physics/configs/physics_week9.json tests/benchmark/physics/test_providers.py
git commit -m "config: activate Codex Plus benchmark strategy"
```

### Task 2: Build Deterministic Blind Packets

**Files:**
- Create: `benchmark/physics/packets.py`
- Create: `tests/benchmark/physics/test_packets.py`

- [ ] **Step 1: Write failing packet isolation tests**

Create a temporary benchmark root with one approved anonymous page, a split,
and a rubric. The test must call this intended interface:

```python
packet = build_blind_packet(
    benchmark_root=root,
    condition="T1",
    split="dev",
    repetition=1,
    output_root=root / "blind_packets",
)
manifest = json.loads((packet / "manifest.json").read_text(encoding="utf-8"))

self.assertEqual(packet.name, "T1-dev-r1")
self.assertEqual(manifest["display_model"], "GPT-5.5")
self.assertEqual(manifest["student_ids"], ["S008"])
self.assertTrue((packet / "inputs" / "S008" / "S008-p01.jpg").exists())
self.assertTrue((packet / "outputs").is_dir())
self.assertEqual(audit_blind_packet(packet), [])
```

Add tests proving:

```python
with self.assertRaisesRegex(ValueError, "held-out split is sealed"):
    build_blind_packet(root, "T1", "test", 1, root / "blind_packets")

first = json.loads((packet / "manifest.json").read_text(encoding="utf-8"))
second = json.loads((rebuild / "manifest.json").read_text(encoding="utf-8"))
self.assertEqual(first["input_hashes"], second["input_hashes"])
```

The fixture must place strings such as `gold`, `grades.csv`, a source surname,
and `reports` outside the packet and assert none appears in packet paths or text.

- [ ] **Step 2: Run the packet tests and verify import failure**

```powershell
.\.venv\Scripts\python.exe -m unittest tests.benchmark.physics.test_packets -v
```

Expected: import failure for `benchmark.physics.packets`.

- [ ] **Step 3: Implement packet construction**

Implement these public interfaces:

```python
FORBIDDEN_PACKET_TERMS = (
    "gold",
    "grades.csv",
    "primary_scores",
    "reviewer_scores",
    "predictions.csv",
    "metrics",
    "reports",
    "student_map",
)

def build_blind_packet(
    benchmark_root: Path,
    condition: str,
    split: str,
    repetition: int,
    output_root: Path,
) -> Path:
    if condition not in {"T1", "G2", "G3"}:
        raise ValueError(f"unsupported Codex condition: {condition}")
    if split == "test" and not (benchmark_root / "freeze.json").exists():
        raise ValueError("held-out split is sealed until freeze.json exists")
    split_data = json.loads(
        (benchmark_root / "manifest" / "split.json").read_text(encoding="utf-8")
    )
    if condition == "G3":
        key = "development_student_ids" if split == "dev" else "heldout_student_ids"
        student_ids = split_data["transcript_gold"][key]
    else:
        key = "development_student_ids" if split == "dev" else "heldout_student_ids"
        student_ids = split_data[key]
    packet = output_root / f"{condition}-{split}-r{repetition}"
    packet.mkdir(parents=True, exist_ok=False)
    (packet / "inputs").mkdir()
    (packet / "outputs").mkdir()
    copy_condition_inputs(benchmark_root, packet, condition, split, student_ids)
    write_packet_prompt_and_schema(packet, condition)
    write_packet_manifest(packet, condition, split, repetition, student_ids)
    findings = audit_blind_packet(packet)
    if findings:
        raise ValueError("blind packet audit failed: " + "; ".join(findings))
    return packet

def audit_blind_packet(packet: Path) -> list[str]:
    findings = []
    for path in packet.rglob("*"):
        relative = path.relative_to(packet).as_posix().lower()
        for term in FORBIDDEN_PACKET_TERMS:
            if term.lower() in relative:
                findings.append(f"forbidden path term {term}: {relative}")
        if path.suffix.lower() in {".json", ".md", ".txt", ".csv"}:
            text = path.read_text(encoding="utf-8").lower()
            for term in FORBIDDEN_PACKET_TERMS:
                if term.lower() in text:
                    findings.append(f"forbidden text term {term}: {relative}")
    return sorted(set(findings))
```

Required behavior:

```python
if condition not in {"T1", "G2", "G3"}:
    raise ValueError(f"unsupported Codex condition: {condition}")
if split == "test" and not (benchmark_root / "freeze.json").exists():
    raise ValueError("held-out split is sealed until freeze.json exists")
packet = output_root / f"{condition}-{split}-r{repetition}"
packet.mkdir(parents=True, exist_ok=False)
```

For `T1`, copy approved anonymous JPEG bytes into per-student input folders. For
`G2`, copy frozen automatic transcripts; for `G3`, copy only the preselected
human transcripts. Copy files rather than creating symlinks. Write
`prompt.txt`, `output.schema.json`, `INSTRUCTIONS.md`, and `manifest.json`.
Exclude wall-clock time from the deterministic hash comparison; store it in a
separate `created_at` manifest field.

The packet instructions must contain:

```text
Work only inside this packet. Do not inspect parent directories or any other
workspace. Do not read gold scores, historical grades, predictions, metrics,
reports, or identity mappings. Write one JSON file per expected anonymous
student into outputs/. Do not rename anonymous IDs.
```

- [ ] **Step 4: Run packet tests and privacy audit**

```powershell
.\.venv\Scripts\python.exe -m unittest tests.benchmark.physics.test_packets -v
```

Expected: all packet tests pass, including forbidden-content and held-out gates.

- [ ] **Step 5: Commit packet support**

```powershell
git add benchmark/physics/packets.py tests/benchmark/physics/test_packets.py
git commit -m "feat: build isolated Codex benchmark packets"
```

### Task 3: Import and Validate Codex Transcripts

**Files:**
- Create: `benchmark/physics/codex_import.py`
- Create: `tests/benchmark/physics/test_codex_import.py`

- [ ] **Step 1: Write failing `T1` import tests**

Use one file per student with this exact shape:

```json
{
  "student_id": "S008",
  "answers": [
    {"question_id": "Q1a", "text": "E = 0.087 V/m", "unclear": false}
  ]
}
```

The valid fixture must contain all 12 IDs. Assert:

```python
run_dir = import_codex_packet(packet, benchmark_root)
self.assertEqual(run_dir.name, "T1-dev-r1")
self.assertEqual(len(list((benchmark_root / "transcripts" / "automatic" / "T1-dev-r1").glob("S*.json"))), 1)
self.assertEqual(len((run_dir / "transcripts.jsonl").read_text(encoding="utf-8").splitlines()), 12)
```

Add rejection tests for a missing question, duplicate question, wrong student
ID, unexpected student, malformed JSON, and `unclear=true` without `[UNCLEAR]`
in the text.

- [ ] **Step 2: Run the tests and verify import failure**

```powershell
.\.venv\Scripts\python.exe -m unittest tests.benchmark.physics.test_codex_import -v
```

Expected: import failure for `benchmark.physics.codex_import`.

- [ ] **Step 3: Implement transcript parsing and immutable import**

Implement:

```python
def parse_transcript_output(path: Path, expected_student_id: str) -> list[TranscriptAnswer]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload["student_id"] != expected_student_id:
        raise ValueError("student_id does not match packet manifest")
    answers = [
        TranscriptAnswer(
            question_id=row["question_id"],
            text=row["text"],
            unclear=bool(row["unclear"]),
        )
        for row in payload["answers"]
    ]
    validate_transcript_answers(answers)
    return answers

def import_codex_packet(packet: Path, benchmark_root: Path) -> Path:
    manifest = json.loads((packet / "manifest.json").read_text(encoding="utf-8"))
    run_id = manifest["run_id"]
    run_dir = create_run_directory(
        benchmark_root / "runs",
        run_id,
        manifest={**manifest, "provider": "codex-plus-interactive"},
    )
    expected = manifest["student_ids"]
    output_files = {path.stem: path for path in (packet / "outputs").glob("S*.json")}
    if set(output_files) != set(expected):
        raise ValueError("Codex outputs do not match packet student IDs")
    if manifest["condition"] == "T1":
        frozen = benchmark_root / "transcripts" / "automatic" / run_id
        frozen.mkdir(parents=True, exist_ok=False)
        transcript_path = run_dir / "transcripts.jsonl"
        transcript_path.write_text("", encoding="utf-8")
        for student_id in expected:
            answers = parse_transcript_output(output_files[student_id], student_id)
            shutil.copy2(output_files[student_id], frozen / f"{student_id}.json")
            append_transcript_rows(transcript_path, student_id, answers)
    else:
        for student_id in expected:
            records = parse_grading_output(output_files[student_id], student_id)
            append_prediction_rows(run_dir / "predictions.csv", records)
            append_raw_codex_output(run_dir / "raw_responses.jsonl", output_files[student_id])
    finish_import_manifest(run_dir / "manifest.json")
    return run_dir
```

`validate_transcript_answers` must require exactly the 12 IDs from
`QUESTION_IDS`, reject duplicates, reject blank text, and enforce `[UNCLEAR]`
when `unclear` is true. The importer must call `create_run_directory` before
writing runtime records, copy validated student JSON to the frozen transcript
directory, write one normalized answer per `transcripts.jsonl` line, and refuse
to overwrite an existing run.

- [ ] **Step 4: Run the transcript import tests**

```powershell
.\.venv\Scripts\python.exe -m unittest tests.benchmark.physics.test_codex_import -v
```

Expected: all transcript import and immutability tests pass.

- [ ] **Step 5: Commit transcript import**

```powershell
git add benchmark/physics/codex_import.py tests/benchmark/physics/test_codex_import.py
git commit -m "feat: import validated Codex transcripts"
```

### Task 4: Create the Human Transcript Review Artifact

**Files:**
- Modify: `benchmark/physics/codex_import.py`
- Modify: `tests/benchmark/physics/test_codex_import.py`

- [ ] **Step 1: Write a failing human-review export test**

Call:

```python
review_path = create_human_review_csv(
    benchmark_root=root,
    split="dev",
    output=root / "transcripts" / "human" / "H1-dev.csv",
)
rows = list(csv.DictReader(review_path.open(newline="", encoding="utf-8")))
self.assertEqual(len(rows), 4 * 12)
self.assertEqual(
    tuple(rows[0]),
    ("student_id", "question_id", "automatic_text", "human_text", "reviewed"),
)
```

Use the four IDs already frozen under
`split.json -> transcript_gold.development_student_ids`. Add a test that
`validate_human_review_csv` rejects blank `human_text` or `reviewed != true`.

- [ ] **Step 2: Run the focused test and verify failure**

```powershell
.\.venv\Scripts\python.exe -m unittest tests.benchmark.physics.test_codex_import.CodexImportTests.test_creates_human_review_for_frozen_subset -v
```

Expected: failure because `create_human_review_csv` does not exist.

- [ ] **Step 3: Implement human-review export and validation**

Implement:

```python
HUMAN_REVIEW_FIELDS = (
    "student_id",
    "question_id",
    "automatic_text",
    "human_text",
    "reviewed",
)

def create_human_review_csv(benchmark_root: Path, split: str, output: Path) -> Path:
    split_data = json.loads(
        (benchmark_root / "manifest" / "split.json").read_text(encoding="utf-8")
    )
    key = "development_student_ids" if split == "dev" else "heldout_student_ids"
    student_ids = split_data["transcript_gold"][key]
    source = benchmark_root / "transcripts" / "automatic" / f"T1-{split}-r1"
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=HUMAN_REVIEW_FIELDS)
        writer.writeheader()
        for student_id in student_ids:
            answers = parse_transcript_output(source / f"{student_id}.json", student_id)
            for answer in answers:
                writer.writerow({
                    "student_id": student_id,
                    "question_id": answer.question_id,
                    "automatic_text": answer.text,
                    "human_text": "",
                    "reviewed": "",
                })
    return output

def validate_human_review_csv(path: Path, expected_student_ids: list[str]) -> None:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    expected_pairs = {
        (student_id, question_id)
        for student_id in expected_student_ids
        for question_id in QUESTION_IDS
    }
    actual_pairs = {(row["student_id"], row["question_id"]) for row in rows}
    if actual_pairs != expected_pairs or len(rows) != len(expected_pairs):
        raise ValueError("human transcript rows do not match frozen subset")
    if any(not row["human_text"].strip() for row in rows):
        raise ValueError("human transcript text is incomplete")
    if any(row["reviewed"].strip().lower() != "true" for row in rows):
        raise ValueError("human transcript review is incomplete")
```

The export pre-fills `automatic_text`, leaves `human_text` and `reviewed`
empty, and preserves the frozen student/question order. Validation requires
all expected rows, `reviewed=true`, nonblank human text, and no extra IDs.

- [ ] **Step 4: Run the full Codex import tests**

```powershell
.\.venv\Scripts\python.exe -m unittest tests.benchmark.physics.test_codex_import -v
```

Expected: transcript import and human-review tests pass.

- [ ] **Step 5: Commit human transcript support**

```powershell
git add benchmark/physics/codex_import.py tests/benchmark/physics/test_codex_import.py
git commit -m "feat: prepare human transcript review"
```

### Task 5: Import Codex Grading Results

**Files:**
- Modify: `benchmark/physics/codex_import.py`
- Modify: `tests/benchmark/physics/test_codex_import.py`

- [ ] **Step 1: Write failing grading-import tests**

Use the existing grading JSON shape from `grade_structured.txt`. Assert:

```python
run_dir = import_codex_packet(packet, benchmark_root)
with (run_dir / "predictions.csv").open(newline="", encoding="utf-8") as handle:
    rows = list(csv.DictReader(handle))
self.assertEqual(len(rows), 12)
self.assertEqual({row["student_id"] for row in rows}, {"S008"})
self.assertEqual(json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))["provider"], "codex-plus-interactive")
```

Add tests rejecting non-quarter scores, question-specific range violations,
duplicate IDs, inconsistent totals, and output students not listed in the
packet manifest.

- [ ] **Step 2: Run the focused tests and verify failure**

```powershell
.\.venv\Scripts\python.exe -m unittest tests.benchmark.physics.test_codex_import.CodexImportTests.test_imports_g2_grading_packet -v
```

Expected: failure because grading conditions are not implemented by the importer.

- [ ] **Step 3: Implement grading import by reusing score validation**

Extract the existing private score parser from `cli.py` into
`codex_import.py` as:

```python
def parse_grading_output(path: Path, expected_student_id: str) -> list[ScoreRecord]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    records = score_records_from_payload(payload, expected_student_id)
    calculated = validate_score_records(records)
    if abs(float(payload["total"]) - calculated) > 1e-9:
        raise ValueError("reported total does not match question scores")
    return records
```

Write normalized score rows to `predictions.csv`, retain the original JSON in
`raw_responses.jsonl`, record the displayed model as `GPT-5.5`, and keep the run
directory immutable.

- [ ] **Step 4: Run import and existing CLI tests**

```powershell
.\.venv\Scripts\python.exe -m unittest tests.benchmark.physics.test_codex_import tests.benchmark.physics.test_cli_run -v
```

Expected: all Codex import and prior runner tests pass.

- [ ] **Step 5: Commit Codex grading import**

```powershell
git add benchmark/physics/codex_import.py benchmark/physics/cli.py tests/benchmark/physics/test_codex_import.py tests/benchmark/physics/test_cli_run.py
git commit -m "feat: import blind Codex grading runs"
```

### Task 6: Run DeepSeek on Frozen Text

**Files:**
- Create: `benchmark/physics/deepseek_runs.py`
- Create: `tests/benchmark/physics/test_deepseek_runs.py`
- Modify: `benchmark/physics/cli.py`

- [ ] **Step 1: Write failing fake-provider tests**

Use a fake `DeepSeekProvider` that records text prompts and returns valid score
JSON. Assert:

```python
run_dir = run_deepseek_condition(
    benchmark_root=root,
    condition="D1",
    split="dev",
    repetition=1,
    provider=fake,
)
self.assertEqual(run_dir.name, "D1-dev-r1")
self.assertEqual(len(fake.prompts), 1)
self.assertNotIn("image", fake.prompts[0].lower())
self.assertIn("E = 0.087 V/m", fake.prompts[0])
self.assertEqual(len(list(csv.DictReader((run_dir / "predictions.csv").open()))), 12)
```

Add a `D2` test proving it reads the human transcript and a test proving
`repetition=2` is rejected by the one-run policy.

- [ ] **Step 2: Run the tests and verify import failure**

```powershell
.\.venv\Scripts\python.exe -m unittest tests.benchmark.physics.test_deepseek_runs -v
```

Expected: import failure for `benchmark.physics.deepseek_runs`.

- [ ] **Step 3: Implement text-only DeepSeek execution**

Implement:

```python
def run_deepseek_condition(
    benchmark_root: Path,
    condition: str,
    split: str,
    repetition: int,
    provider: DeepSeekProvider,
) -> Path:
    if condition not in {"D1", "D2"}:
        raise ValueError(f"unsupported DeepSeek condition: {condition}")
    if repetition != 1:
        raise ValueError("revised benchmark permits one run per condition")
    student_text = load_condition_transcripts(benchmark_root, condition, split)
    rubric = json.loads(
        (benchmark_root / "rubric" / "rubric_v1.json").read_text(encoding="utf-8")
    )
    prompt_template = (
        Path(__file__).with_name("prompts") / "grade_structured.txt"
    ).read_text(encoding="utf-8")
    run_id = f"{condition}-{split}-r{repetition}"
    run_dir = create_run_directory(
        benchmark_root / "runs",
        run_id,
        manifest=deepseek_manifest(run_id, condition, split, student_text, rubric),
    )
    successes = 0
    for student_id, answers in student_text.items():
        prompt = compose_text_grading_prompt(
            prompt_template, student_id, answers, rubric
        )
        result = run_student_with_retries(
            run_dir,
            student_id,
            lambda attempt: validated_deepseek_call(provider, prompt, student_id),
            max_retries=2,
        )
        if result is not None:
            append_prediction_rows(
                run_dir / "predictions.csv",
                score_records_from_payload(json.loads(result.raw_text), student_id),
            )
            successes += 1
    finish_run_manifest(run_dir / "manifest.json")
    if successes == 0:
        raise RuntimeError(f"{run_id} produced no predictions")
    return run_dir
```

`D1` reads the exact frozen `T1` transcript for the split. `D2` reads validated
human text for the frozen transcript subset. Compose a text prompt containing
the student ID, all 12 answers, the frozen rubric, and
`grade_structured.txt`. Call `run_student_with_retries`, parse with the shared
score parser, and append normalized predictions. Never send image bytes,
source filenames, names, gold scores, or prior predictions.

- [ ] **Step 4: Wire the CLI and test credential handling**

Add:

```text
physics-benchmark run-deepseek --root ROOT --condition D1 --split dev --repetition 1
physics-benchmark run-deepseek --root ROOT --condition D2 --split dev --repetition 1
```

The command reads only `DEEPSEEK_API_KEY`, constructs
`DeepSeekProvider.from_api_key`, and never prints or persists the key.

- [ ] **Step 5: Run DeepSeek and CLI tests**

```powershell
.\.venv\Scripts\python.exe -m unittest tests.benchmark.physics.test_deepseek_runs tests.benchmark.physics.test_cli_run -v
```

Expected: fake-provider execution passes without network calls.

- [ ] **Step 6: Commit DeepSeek execution**

```powershell
git add benchmark/physics/deepseek_runs.py benchmark/physics/cli.py tests/benchmark/physics/test_deepseek_runs.py
git commit -m "feat: grade frozen transcripts with DeepSeek"
```

### Task 7: Add Revised CLI Commands

**Files:**
- Modify: `benchmark/physics/cli.py`
- Create: `tests/benchmark/physics/test_cli_revision.py`

- [ ] **Step 1: Write failing CLI routing tests**

Test these commands with temporary roots and fake or patched providers:

```text
physics-benchmark build-packet --root ROOT --condition T1 --split dev --repetition 1
physics-benchmark import-codex --root ROOT --packet PACKET
physics-benchmark human-review --root ROOT --split dev
physics-benchmark run-deepseek --root ROOT --condition D1 --split dev --repetition 1
physics-benchmark import-baseline --root Data/physics
```

Assert the obsolete active command fails clearly:

```python
code = main(["run", "--root", str(root), "--condition", "G1", "--split", "dev", "--repetition", "2"])
self.assertNotEqual(code, 0)
self.assertIn("OpenAI API conditions are inactive", stderr.getvalue())
```

- [ ] **Step 2: Run the tests and verify missing commands**

```powershell
.\.venv\Scripts\python.exe -m unittest tests.benchmark.physics.test_cli_revision -v
```

Expected: parser failures for the new subcommands.

- [ ] **Step 3: Implement thin command routing**

Keep parsing and user-facing errors in `cli.py`; delegate packet, import, and
DeepSeek behavior to their focused modules. The `run G1` path must not request
`OPENAI_API_KEY` and must return the explicit inactive-condition error.

Wire the existing `import-baseline` command to read
`Data/physics/grades/grades.csv` and
`Data/physics/benchmark/manifest/student_map.csv`. Map every source label to an
anonymous ID, validate all 12 historical scores with
`baseline.row_to_score_records`, and create immutable run `G0-all-r1`. Store
only anonymous IDs in that run and refuse to overwrite it.

- [ ] **Step 4: Run all CLI tests**

```powershell
.\.venv\Scripts\python.exe -m unittest tests.benchmark.physics.test_cli_init tests.benchmark.physics.test_cli_run tests.benchmark.physics.test_cli_revision -v
```

Expected: all old safety gates and revised commands pass.

- [ ] **Step 5: Commit CLI revision**

```powershell
git add benchmark/physics/cli.py tests/benchmark/physics/test_cli_revision.py
git commit -m "feat: orchestrate revised blind benchmark"
```

### Task 8: Evaluate Development Runs and Freeze

**Files:**
- Create: `benchmark/physics/evaluation.py`
- Create: `tests/benchmark/physics/test_evaluation.py`
- Modify: `benchmark/physics/cli.py`

- [ ] **Step 1: Write failing exclusion and freeze tests**

Create fixture runs `G0`, `G2-dev-r1`, `D1-dev-r1`, `G3-dev-r1`, and
`D2-dev-r1`, plus a failed `G1-dev-r1`. Assert:

```python
result = evaluate_conditions(root, split="dev")
self.assertNotIn("G1", result["conditions"])
self.assertEqual(result["excluded_runs"], ["G1-dev-r1"])
self.assertEqual(result["conditions"]["G2"]["n_students"], 8)
```

Add:

```python
freeze = freeze_revised_workflow(root, candidate="staged_v1")
self.assertEqual(freeze["gpt_display_model"], "GPT-5.5")
self.assertEqual(freeze["deepseek_model"], "deepseek-v4-pro")
self.assertEqual(freeze["runs_per_condition"], 1)
self.assertIn("T1", freeze["prompt_hashes"])
```

The freeze function must reject missing `G2-dev-r1` or `D1-dev-r1`.

- [ ] **Step 2: Run tests and verify import failure**

```powershell
.\.venv\Scripts\python.exe -m unittest tests.benchmark.physics.test_evaluation -v
```

Expected: import failure for `benchmark.physics.evaluation`.

- [ ] **Step 3: Implement evaluation and freeze**

Load private primary gold scores and normalized predictions by anonymous ID.
Use existing `compute_metrics` and `paired_bootstrap_difference`. Keep the
26-person and transcript-subset metrics separate. If independent reviewer
scores remain incomplete, label the reference as `single_primary_rater` and
omit human-agreement metrics rather than fabricating adjudication.

Write `metrics-dev.json` and then `freeze.json` with:

```json
{
  "candidate": "staged_v1",
  "gpt_execution": "codex-plus-interactive",
  "gpt_display_model": "GPT-5.5",
  "deepseek_model": "deepseek-v4-pro",
  "runs_per_condition": 1,
  "excluded_run_ids": ["G1-dev-r1"],
  "prompt_hashes": {},
  "rubric_hash": "sha256",
  "input_policy": "frozen anonymous transcript workflow",
  "timestamp": "UTC ISO-8601"
}
```

- [ ] **Step 4: Wire `evaluate` and revised `freeze` commands**

```text
physics-benchmark evaluate --root ROOT --split dev
physics-benchmark freeze --root ROOT --candidate staged_v1
```

- [ ] **Step 5: Run metrics, evaluation, and CLI tests**

```powershell
.\.venv\Scripts\python.exe -m unittest tests.benchmark.physics.test_metrics tests.benchmark.physics.test_evaluation tests.benchmark.physics.test_cli_revision -v
```

Expected: deterministic metrics, explicit G1 exclusion, and freeze gates pass.

- [ ] **Step 6: Commit evaluation support**

```powershell
git add benchmark/physics/evaluation.py benchmark/physics/cli.py tests/benchmark/physics/test_evaluation.py tests/benchmark/physics/test_cli_revision.py
git commit -m "feat: evaluate and freeze revised benchmark"
```

### Task 9: Development Runtime Checkpoint

**Private runtime outputs only:**
- `Data/physics/benchmark/blind_packets/T1-dev-r1/`
- `Data/physics/benchmark/transcripts/automatic/T1-dev-r1/`
- `Data/physics/benchmark/transcripts/human/H1-dev.csv`
- `Data/physics/benchmark/runs/G2-dev-r1/`
- `Data/physics/benchmark/runs/D1-dev-r1/`
- `Data/physics/benchmark/runs/G3-dev-r1/`
- `Data/physics/benchmark/runs/D2-dev-r1/`
- `Data/physics/benchmark/metrics-dev.json`
- `Data/physics/benchmark/freeze.json`

- [ ] **Step 1: Build and audit the development transcription packet**

```powershell
.\.venv\Scripts\physics-benchmark.exe build-packet --root Data/physics/benchmark --condition T1 --split dev --repetition 1
```

Expected: `T1-dev-r1` contains eight anonymous students and no audit findings.

- [ ] **Step 2: Human checkpoint - run GPT-5.5 transcription**

Open `T1-dev-r1` as a new Codex App workspace, select GPT-5.5, start a fresh
thread, and give it only `INSTRUCTIONS.md`. The thread writes eight JSON files
under `outputs/`. Do not open the main TDAA-Go workspace in that thread.

- [ ] **Step 3: Import T1 and create the human-review CSV**

```powershell
.\.venv\Scripts\physics-benchmark.exe import-codex --root Data/physics/benchmark --packet Data/physics/benchmark/blind_packets/T1-dev-r1
.\.venv\Scripts\physics-benchmark.exe human-review --root Data/physics/benchmark --split dev
```

Expected: automatic transcripts freeze and `H1-dev.csv` contains 48 rows.

- [ ] **Step 4: Human checkpoint - correct four transcripts**

For every row in `H1-dev.csv`, copy or correct `automatic_text` into
`human_text`, set `reviewed=true`, and preserve anonymous IDs and question IDs.

- [ ] **Step 5: Build, run, and import GPT grading packets**

```powershell
.\.venv\Scripts\physics-benchmark.exe build-packet --root Data/physics/benchmark --condition G2 --split dev --repetition 1
.\.venv\Scripts\physics-benchmark.exe build-packet --root Data/physics/benchmark --condition G3 --split dev --repetition 1
```

Run each packet in a separate fresh GPT-5.5 Codex thread, then import each:

```powershell
.\.venv\Scripts\physics-benchmark.exe import-codex --root Data/physics/benchmark --packet Data/physics/benchmark/blind_packets/G2-dev-r1
.\.venv\Scripts\physics-benchmark.exe import-codex --root Data/physics/benchmark --packet Data/physics/benchmark/blind_packets/G3-dev-r1
```

- [ ] **Step 6: Human checkpoint - enter the DeepSeek key securely**

Use one PowerShell session. Never paste the key into chat or a file:

```powershell
$secure = Read-Host "DeepSeek API key" -AsSecureString
$bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
try {
  $env:DEEPSEEK_API_KEY = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)
} finally {
  [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
}
```

- [ ] **Step 7: Run D1 and D2 once, then remove the key**

```powershell
.\.venv\Scripts\physics-benchmark.exe run-deepseek --root Data/physics/benchmark --condition D1 --split dev --repetition 1
.\.venv\Scripts\physics-benchmark.exe run-deepseek --root Data/physics/benchmark --condition D2 --split dev --repetition 1
Remove-Item Env:DEEPSEEK_API_KEY
```

- [ ] **Step 8: Evaluate development and freeze**

```powershell
.\.venv\Scripts\physics-benchmark.exe import-baseline --root Data/physics
.\.venv\Scripts\physics-benchmark.exe evaluate --root Data/physics/benchmark --split dev
.\.venv\Scripts\physics-benchmark.exe freeze --root Data/physics/benchmark --candidate staged_v1
```

Expected: development metrics exist, `G1-dev-r1` is excluded, and
`freeze.json` seals the held-out workflow.

### Task 10: Render the Anonymous Benchmark Report

**Files:**
- Create: `benchmark/physics/report.py`
- Create: `tests/benchmark/physics/test_report.py`
- Modify: `benchmark/physics/cli.py`

- [ ] **Step 1: Write failing report tests**

Assert the rendered Markdown contains:

```python
self.assertIn("# Physics Week 9 Internal Grading Benchmark", report)
self.assertIn("Historical direct workflow", report)
self.assertIn("Codex Plus interactive run", report)
self.assertIn("single run", report.lower())
self.assertIn("G0", report)
self.assertIn("G2", report)
self.assertIn("D1", report)
self.assertNotIn("chenyujin", report.lower())
self.assertNotIn("OPENAI_API_KEY", report)
self.assertNotIn("G1-dev-r1", report.split("Accuracy Results")[1])
```

Also test that a supplied student label not matching `S\d{3}` is rejected.

- [ ] **Step 2: Run the tests and verify import failure**

```powershell
.\.venv\Scripts\python.exe -m unittest tests.benchmark.physics.test_report -v
```

Expected: import failure for `benchmark.physics.report`.

- [ ] **Step 3: Implement the report renderer**

Render held-out results before combined results. Include exact agreement,
question-macro agreement, total MAE, within-one rate, bias, missing counts,
paired intervals, transcript-subset comparisons, and anonymous error
categories. Include these exact limitations:

```text
G0 is a historical single-run baseline produced under different prompt and
thread conditions; G0-to-G2 differences represent the overall workflow change.
GPT-5.5 was run interactively through Codex Plus and is not a pinned API
snapshot. Each retained model condition was run once, so model-run variance was
not estimated. Primary human evidence and ambiguity fields were not collected.
```

If reviewer adjudication remains incomplete, add:

```text
The score reference is a single primary-rater standard; independent human
agreement is not available for this release.
```

- [ ] **Step 4: Add the `report` CLI command and run tests**

```powershell
.\.venv\Scripts\python.exe -m unittest tests.benchmark.physics.test_report tests.benchmark.physics.test_cli_revision -v
```

Expected: anonymous report tests and command routing pass.

- [ ] **Step 5: Commit report support**

```powershell
git add benchmark/physics/report.py benchmark/physics/cli.py tests/benchmark/physics/test_report.py tests/benchmark/physics/test_cli_revision.py
git commit -m "feat: report revised grading benchmark"
```

### Task 11: Held-Out Runtime and Final Report

**Private runtime outputs only:**
- `Data/physics/benchmark/blind_packets/*-test-r1/`
- `Data/physics/benchmark/transcripts/automatic/T1-test-r1/`
- `Data/physics/benchmark/transcripts/human/H1-test.csv`
- `Data/physics/benchmark/runs/*-test-r1/`
- `Data/physics/benchmark/metrics-test.json`
- `Data/physics/benchmark/reports/physics_week9_benchmark.md`

- [ ] **Step 1: Verify freeze before creating held-out packets**

```powershell
.\.venv\Scripts\physics-benchmark.exe validate --root Data/physics/benchmark
```

Expected: privacy approved, split and rubric frozen, development runs complete,
and `freeze.json` present.

- [ ] **Step 2: Run held-out T1 in a fresh GPT-5.5 thread and import it**

```powershell
.\.venv\Scripts\physics-benchmark.exe build-packet --root Data/physics/benchmark --condition T1 --split test --repetition 1
.\.venv\Scripts\physics-benchmark.exe import-codex --root Data/physics/benchmark --packet Data/physics/benchmark/blind_packets/T1-test-r1
.\.venv\Scripts\physics-benchmark.exe human-review --root Data/physics/benchmark --split test
```

Correct all 72 rows for the frozen six-student held-out transcript subset.

- [ ] **Step 3: Run held-out G2 and G3 in separate fresh GPT-5.5 threads**

```powershell
.\.venv\Scripts\physics-benchmark.exe build-packet --root Data/physics/benchmark --condition G2 --split test --repetition 1
.\.venv\Scripts\physics-benchmark.exe build-packet --root Data/physics/benchmark --condition G3 --split test --repetition 1
```

Import both completed packet outputs without changing prompts or manifests.

- [ ] **Step 4: Run held-out D1 and D2 once**

Enter the instructor DeepSeek key in the active PowerShell session using the
secure conversion from Task 9, then run:

```powershell
.\.venv\Scripts\physics-benchmark.exe run-deepseek --root Data/physics/benchmark --condition D1 --split test --repetition 1
.\.venv\Scripts\physics-benchmark.exe run-deepseek --root Data/physics/benchmark --condition D2 --split test --repetition 1
Remove-Item Env:DEEPSEEK_API_KEY
```

- [ ] **Step 5: Evaluate test and combined results, then render the report**

```powershell
.\.venv\Scripts\physics-benchmark.exe evaluate --root Data/physics/benchmark --split test
.\.venv\Scripts\physics-benchmark.exe evaluate --root Data/physics/benchmark --split all
.\.venv\Scripts\physics-benchmark.exe report --root Data/physics/benchmark
```

Expected: held-out metrics appear first in the anonymous report; no workflow
field changes after freeze.

### Task 12: Update the Grading Skill from Evidence

**Files:**
- Modify: `.claude/skills/grade-homework/SKILL.md`
- Modify: `.agents/skills/grade-homework/SKILL.md`
- Create: `tests/benchmark/physics/test_skill_sync.py`

- [ ] **Step 1: Write the failing mirror and workflow tests**

```python
class SkillSyncTests(unittest.TestCase):
    def test_claude_and_agent_skills_match(self):
        claude = Path(".claude/skills/grade-homework/SKILL.md").read_text(encoding="utf-8")
        agent = Path(".agents/skills/grade-homework/SKILL.md").read_text(encoding="utf-8")
        self.assertEqual(claude, agent)

    def test_skill_requires_frozen_evidence_first_workflow(self):
        text = Path(".agents/skills/grade-homework/SKILL.md").read_text(encoding="utf-8").lower()
        for phrase in ("page ordering", "rubric", "evidence", "confidence", "second-pass", "do not guess"):
            self.assertIn(phrase, text)
```

- [ ] **Step 2: Run tests and verify failure**

```powershell
.\.venv\Scripts\python.exe -m unittest tests.benchmark.physics.test_skill_sync -v
```

Expected: mirrored files differ or required workflow language is absent.

- [ ] **Step 3: Update both skill copies identically**

The workflow must require deterministic page preparation, rubric freeze,
evidence extraction before scoring, quarter-point/range/total validation,
low-confidence second-pass review, explicit unreadable flags, and immutable
benchmark records. Only incorporate changes supported by development and
held-out error evidence; do not claim general accuracy beyond Physics Week 9.

- [ ] **Step 4: Run skill and full benchmark tests**

```powershell
.\.venv\Scripts\python.exe -m unittest tests.benchmark.physics.test_skill_sync -v
.\.venv\Scripts\python.exe -m unittest discover -s tests/benchmark/physics -v
```

Expected: mirror test and all benchmark tests pass.

- [ ] **Step 5: Commit the evidence-based skill**

```powershell
git add .claude/skills/grade-homework/SKILL.md .agents/skills/grade-homework/SKILL.md tests/benchmark/physics/test_skill_sync.py
git commit -m "feat: strengthen homework grading from benchmark evidence"
```

### Task 13: Final Verification and Integration Handoff

**Files:**
- Verify all tracked benchmark, test, design, plan, and skill files.

- [ ] **Step 1: Run complete tests and syntax compilation**

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests/benchmark/physics -v
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m compileall -q benchmark scripts
```

Expected: zero failures and errors.

- [ ] **Step 2: Validate private runtime artifacts**

```powershell
.\.venv\Scripts\physics-benchmark.exe validate --root Data/physics/benchmark
```

Expected: 26 students, 312 reference scores, 8 development students, 18
held-out students, 10 reviewed transcript students, approved anonymous pages,
frozen workflow, complete retained runs, and explicit exclusion of
`G1-dev-r1`.

- [ ] **Step 3: Audit privacy and report claims**

Search the final report and every blind packet for source student names and
private source filenames from `student_map.csv`. Expected: no match. Confirm
the report contains `Physics Week 9 Internal Grading Benchmark`, labels `G0`
historical, labels GPT-5.5 interactive, and does not estimate run variance.

- [ ] **Step 4: Run Git checks**

```powershell
git diff --check main...HEAD
git status --short
git log --oneline main..HEAD
git diff --stat main...HEAD
git check-ignore -v Data/physics/benchmark/runs/G2-dev-r1/predictions.csv
```

Expected: no whitespace errors; `Data/` remains ignored; only the known
user-owned `.gitignore`, `.agents/`, and `tmp/` state remains outside commits.

- [ ] **Step 5: Use branch-finishing workflow**

Invoke `superpowers:requesting-code-review`, fix all critical or important
findings, rerun verification, then invoke
`superpowers:finishing-a-development-branch`. Present the verified branch and
report to the user. Merge into `main` only after explicit user approval.
