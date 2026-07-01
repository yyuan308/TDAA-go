# Physics Grading Accuracy Benchmark Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and run a private, reproducible Physics Week 9 benchmark that measures whether anonymization, structured transcription, explicit rubrics, and verification improve 12-subquestion grading accuracy across GPT and DeepSeek.

**Architecture:** Tracked Python modules under `benchmark/physics` own schemas, privacy gates, model adapters, run manifests, metrics, and reports. Student files, identity mappings, gold labels, transcripts, model outputs, and reports remain under ignored `Data/physics/benchmark`. All model calls pass through injectable providers so unit tests never contact an API.

**Tech Stack:** Python 3.10+, standard-library `csv`/`json`/`hashlib`/`statistics`, Pillow, OpenAI Python SDK, `unittest`, OpenAI Responses API, DeepSeek OpenAI-compatible Chat Completion API.

---

## File Map

Tracked files to create:

- `benchmark/__init__.py`: package marker.
- `benchmark/physics/__init__.py`: Physics benchmark public exports.
- `benchmark/physics/schema.py`: question constants, score/transcript/run dataclasses, and validation.
- `benchmark/physics/gold.py`: private rubric and gold-template creation and validation.
- `benchmark/physics/manifest.py`: student aliases, source mapping, stratified split, and CSV I/O.
- `benchmark/physics/privacy.py`: redaction application, anonymous filenames, and approval gate.
- `benchmark/physics/baseline.py`: import the existing `grades.csv` as immutable `G0` predictions.
- `benchmark/physics/metrics.py`: exact agreement, MAE, bias, score bands, and paired bootstrap.
- `benchmark/physics/providers.py`: GPT image/text and DeepSeek text provider adapters.
- `benchmark/physics/runner.py`: condition execution, retries, validation, and immutable run directories.
- `benchmark/physics/report.py`: anonymous Markdown benchmark report.
- `benchmark/physics/cli.py`: `init`, `prepare-images`, `validate`, `run`, `evaluate`, and `report` commands.
- `benchmark/physics/configs/physics_week9.json`: pinned model and experiment configuration.
- `benchmark/physics/prompts/transcribe.txt`: image-to-12-answer transcription prompt.
- `benchmark/physics/prompts/grade_minimal.txt`: minimal grading control.
- `benchmark/physics/prompts/grade_structured.txt`: evidence-first rubric grading prompt.
- `benchmark/physics/prompts/review.txt`: low-confidence second-pass prompt.
- `tests/benchmark/physics/*.py`: focused unit and integration tests.

Tracked files to modify:

- `pyproject.toml`: add `openai`, `Pillow`, and the `physics-benchmark` console entry point.
- `.claude/skills/grade-homework/SKILL.md`: document the frozen best workflow after development experiments.
- `.agents/skills/grade-homework/SKILL.md`: mirror the final skill for Codex discovery.

Private files created at runtime:

- `Data/physics/benchmark/manifest/students.csv`
- `Data/physics/benchmark/manifest/split.json`
- `Data/physics/benchmark/manifest/redactions.json`
- `Data/physics/benchmark/manifest/privacy_review.csv`
- `Data/physics/benchmark/rubric/rubric_v1.json`
- `Data/physics/benchmark/gold/primary_scores.csv`
- `Data/physics/benchmark/gold/reviewer_scores.csv`
- `Data/physics/benchmark/gold/adjudication.csv`
- `Data/physics/benchmark/gold/gold_scores_v1.csv`
- `Data/physics/benchmark/anonymized/S001/*.jpg` (and the other anonymous IDs)
- `Data/physics/benchmark/transcripts/automatic/*.json`
- `Data/physics/benchmark/transcripts/human/*.json`
- `Data/physics/benchmark/runs/G1-dev-r1/*` (one immutable directory per run)
- `Data/physics/benchmark/reports/physics_week9_benchmark.md`

## Day 1: Freeze the Benchmark

### Task 1: Package Skeleton and Dependencies

**Files:**
- Create: `benchmark/__init__.py`
- Create: `benchmark/physics/__init__.py`
- Modify: `pyproject.toml`
- Test: `tests/benchmark/physics/test_imports.py`

- [ ] **Step 1: Write the failing import test**

```python
import unittest


class BenchmarkImportTests(unittest.TestCase):
    def test_physics_package_imports(self):
        from benchmark import physics

        self.assertEqual(physics.__name__, "benchmark.physics")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test and verify it fails**

Run:

```powershell
python -m unittest tests.benchmark.physics.test_imports -v
```

Expected: `ModuleNotFoundError: No module named 'benchmark'`.

- [ ] **Step 3: Add dependencies and package markers**

Add to `pyproject.toml` dependencies:

```toml
"openai>=1.70",
"Pillow>=10.0",
```

Add to `[project.scripts]`:

```toml
physics-benchmark = "benchmark.physics.cli:main"
```

Create `benchmark/__init__.py` and `benchmark/physics/__init__.py` as empty
package marker files. Task 2 exports `QUESTION_IDS` after `schema.py` exists.

- [ ] **Step 4: Create the local environment and install the project**

Run:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
```

Expected: editable install completes and imports `openai`, `PIL`, and
`benchmark.physics`.

- [ ] **Step 5: Run the import test**

Run:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.benchmark.physics.test_imports -v
```

Expected: `OK` with 1 test.

- [ ] **Step 6: Commit the package skeleton**

```powershell
git add pyproject.toml benchmark/__init__.py benchmark/physics/__init__.py tests/benchmark/physics/test_imports.py
git commit -m "build: add physics benchmark package"
```

### Task 2: Score and Transcript Schemas

**Files:**
- Create: `benchmark/physics/schema.py`
- Test: `tests/benchmark/physics/test_schema.py`

- [ ] **Step 1: Write failing schema tests**

```python
import unittest

from benchmark.physics.schema import ScoreRecord, validate_score_records


class ScoreSchemaTests(unittest.TestCase):
    def test_accepts_all_twelve_quarter_point_scores(self):
        records = [
            ScoreRecord("S001", "Q1a", 2.0, "high", "correct"),
            ScoreRecord("S001", "Q1b", 2.0, "high", "correct"),
            ScoreRecord("S001", "Q1c", 3.0, "high", "correct"),
            ScoreRecord("S001", "Q1d", 3.0, "high", "correct"),
            ScoreRecord("S001", "Q2a", 7.0, "high", "correct"),
            ScoreRecord("S001", "Q2b", 3.0, "high", "correct"),
            ScoreRecord("S001", "Q3a", 1.5, "high", "correct"),
            ScoreRecord("S001", "Q3b", 1.5, "high", "correct"),
            ScoreRecord("S001", "Q3c", 1.5, "high", "correct"),
            ScoreRecord("S001", "Q3d", 1.5, "high", "correct"),
            ScoreRecord("S001", "Q3e", 2.0, "high", "correct"),
            ScoreRecord("S001", "Q3f", 2.0, "high", "correct"),
        ]

        self.assertEqual(validate_score_records(records), 30.0)

    def test_rejects_out_of_range_score(self):
        with self.assertRaisesRegex(ValueError, "Q3a score"):
            ScoreRecord("S001", "Q3a", 2.0, "high", "invalid")

    def test_rejects_non_quarter_increment(self):
        with self.assertRaisesRegex(ValueError, "quarter-point"):
            ScoreRecord("S001", "Q2a", 6.1, "high", "invalid")
```

- [ ] **Step 2: Run the tests and verify failure**

Run:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.benchmark.physics.test_schema -v
```

Expected: import failure for `benchmark.physics.schema`.

- [ ] **Step 3: Implement the schema**

Create `benchmark/physics/schema.py` with:

```python
from dataclasses import dataclass, field
from typing import Any

QUESTION_MAX = {
    "Q1a": 2.0, "Q1b": 2.0, "Q1c": 3.0, "Q1d": 3.0,
    "Q2a": 7.0, "Q2b": 3.0,
    "Q3a": 1.5, "Q3b": 1.5, "Q3c": 1.5, "Q3d": 1.5,
    "Q3e": 2.0, "Q3f": 2.0,
}
QUESTION_IDS = tuple(QUESTION_MAX)
CONFIDENCE_LEVELS = {"high", "medium", "low"}


@dataclass(frozen=True)
class ScoreRecord:
    student_id: str
    question_id: str
    score: float
    confidence: str
    evidence: str
    flags: tuple[str, ...] = ()

    def __post_init__(self):
        if self.question_id not in QUESTION_MAX:
            raise ValueError(f"unknown question: {self.question_id}")
        if not 0 <= self.score <= QUESTION_MAX[self.question_id]:
            raise ValueError(f"{self.question_id} score is out of range")
        if round(self.score * 4) != self.score * 4:
            raise ValueError("score must use a quarter-point increment")
        if self.confidence not in CONFIDENCE_LEVELS:
            raise ValueError(f"invalid confidence: {self.confidence}")


@dataclass(frozen=True)
class TranscriptAnswer:
    question_id: str
    text: str
    unclear: bool = False


@dataclass(frozen=True)
class ProviderResult:
    raw_text: str
    model: str
    usage: dict[str, Any] = field(default_factory=dict)
    system_fingerprint: str | None = None


def validate_score_records(records: list[ScoreRecord]) -> float:
    if len(records) != len(QUESTION_IDS):
        raise ValueError("expected exactly 12 score records")
    question_ids = [record.question_id for record in records]
    if set(question_ids) != set(QUESTION_IDS) or len(question_ids) != len(set(question_ids)):
        raise ValueError("each question must appear exactly once")
    student_ids = {record.student_id for record in records}
    if len(student_ids) != 1:
        raise ValueError("records must belong to one student")
    return round(sum(record.score for record in records), 2)
```

- [ ] **Step 4: Run schema tests**

Run:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.benchmark.physics.test_schema -v
```

Expected: `OK` with 3 tests.

- [ ] **Step 5: Commit schemas**

```powershell
git add benchmark/physics/schema.py benchmark/physics/__init__.py tests/benchmark/physics/test_schema.py
git commit -m "feat: validate physics benchmark records"
```

### Task 3: Gold Templates and Adjudication Validation

**Files:**
- Create: `benchmark/physics/gold.py`
- Test: `tests/benchmark/physics/test_gold.py`

- [ ] **Step 1: Write failing template and adjudication tests**

```python
import csv
import tempfile
import unittest
from pathlib import Path

from benchmark.physics.gold import create_score_template, validate_adjudication


class GoldTests(unittest.TestCase):
    def test_template_has_312_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "scores.csv"
            create_score_template([f"S{i:03d}" for i in range(1, 27)], output)
            with output.open(newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(len(rows), 312)

    def test_disagreement_requires_adjudicated_score_and_reason(self):
        row = {
            "primary_score": "1.5",
            "reviewer_score": "1.0",
            "adjudicated_score": "",
            "reason": "",
        }
        with self.assertRaisesRegex(ValueError, "adjudication"):
            validate_adjudication(row)
```

- [ ] **Step 2: Run tests and verify failure**

```powershell
.\.venv\Scripts\python.exe -m unittest tests.benchmark.physics.test_gold -v
```

Expected: import failure for `benchmark.physics.gold`.

- [ ] **Step 3: Implement gold helpers**

Create `benchmark/physics/gold.py`:

```python
import csv
from pathlib import Path

from .schema import QUESTION_IDS

SCORE_FIELDS = (
    "student_id", "question_id", "score", "confidence", "evidence", "ambiguity_code"
)


def create_score_template(student_ids: list[str], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=SCORE_FIELDS)
        writer.writeheader()
        for student_id in student_ids:
            for question_id in QUESTION_IDS:
                writer.writerow({"student_id": student_id, "question_id": question_id})


def validate_adjudication(row: dict[str, str]) -> None:
    primary = row["primary_score"].strip()
    reviewer = row["reviewer_score"].strip()
    if primary != reviewer:
        if not row["adjudicated_score"].strip() or not row["reason"].strip():
            raise ValueError("score disagreement requires adjudication and reason")
```

- [ ] **Step 4: Run tests**

```powershell
.\.venv\Scripts\python.exe -m unittest tests.benchmark.physics.test_gold -v
```

Expected: `OK` with 2 tests.

- [ ] **Step 5: Commit gold helpers**

```powershell
git add benchmark/physics/gold.py tests/benchmark/physics/test_gold.py
git commit -m "feat: add gold scoring templates"
```

### Task 4: Student Manifest and Held-Out Split

**Files:**
- Create: `benchmark/physics/manifest.py`
- Test: `tests/benchmark/physics/test_manifest.py`

- [ ] **Step 1: Write failing split tests**

```python
import unittest

from benchmark.physics.manifest import assign_split


class ManifestTests(unittest.TestCase):
    def test_split_is_deterministic_and_disjoint(self):
        rows = [
            {
                "student_id": f"S{i:03d}",
                "clarity": ("clear", "medium", "difficult")[i % 3],
                "format": ("pdf", "jpg", "docx")[i % 3],
                "score_band": ("low", "medium", "high")[i % 3],
            }
            for i in range(1, 27)
        ]
        first = assign_split(rows, dev_size=8, seed=20260701)
        second = assign_split(rows, dev_size=8, seed=20260701)
        self.assertEqual(first, second)
        self.assertEqual(sum(row["split"] == "dev" for row in first), 8)
        self.assertEqual(sum(row["split"] == "test" for row in first), 18)
```

- [ ] **Step 2: Run tests and verify failure**

```powershell
.\.venv\Scripts\python.exe -m unittest tests.benchmark.physics.test_manifest -v
```

Expected: import failure for `benchmark.physics.manifest`.

- [ ] **Step 3: Implement deterministic stratified assignment**

Create `benchmark/physics/manifest.py`:

```python
import random
from collections import defaultdict


def assign_split(rows: list[dict[str, str]], dev_size: int, seed: int) -> list[dict[str, str]]:
    if dev_size <= 0 or dev_size >= len(rows):
        raise ValueError("dev_size must leave both splits non-empty")
    rng = random.Random(seed)
    strata: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        key = (row["clarity"], row["format"], row["score_band"])
        strata[key].append(dict(row))
    ordered: list[dict[str, str]] = []
    for key in sorted(strata):
        group = strata[key]
        rng.shuffle(group)
        ordered.extend(group)
    selected = {row["student_id"] for row in ordered[::3][:dev_size]}
    if len(selected) < dev_size:
        for row in ordered:
            selected.add(row["student_id"])
            if len(selected) == dev_size:
                break
    result = []
    for row in sorted(rows, key=lambda item: item["student_id"]):
        item = dict(row)
        item["split"] = "dev" if item["student_id"] in selected else "test"
        result.append(item)
    return result
```

- [ ] **Step 4: Run manifest tests**

```powershell
.\.venv\Scripts\python.exe -m unittest tests.benchmark.physics.test_manifest -v
```

Expected: `OK` with 1 test.

- [ ] **Step 5: Commit the manifest code**

```powershell
git add benchmark/physics/manifest.py tests/benchmark/physics/test_manifest.py
git commit -m "feat: create held-out physics split"
```

### Task 5: Anonymous Image Preparation and Privacy Gate

**Files:**
- Create: `benchmark/physics/privacy.py`
- Test: `tests/benchmark/physics/test_privacy.py`

- [ ] **Step 1: Write failing redaction and gate tests**

```python
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from benchmark.physics.privacy import apply_redactions, assert_privacy_approved


class PrivacyTests(unittest.TestCase):
    def test_redaction_masks_configured_rectangle(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source.jpg"
            output = Path(tmp) / "S001-p01.jpg"
            Image.new("RGB", (20, 20), "white").save(source)
            apply_redactions(source, output, [(0, 0, 10, 10)])
            with Image.open(output) as image:
                self.assertEqual(image.getpixel((5, 5)), (0, 0, 0))

    def test_unapproved_page_blocks_upload(self):
        rows = [{"page": "S001-p01.jpg", "approved": "false"}]
        with self.assertRaisesRegex(ValueError, "privacy approval"):
            assert_privacy_approved(rows)
```

- [ ] **Step 2: Run tests and verify failure**

```powershell
.\.venv\Scripts\python.exe -m unittest tests.benchmark.physics.test_privacy -v
```

Expected: import failure for `benchmark.physics.privacy`.

- [ ] **Step 3: Implement redaction and approval checks**

Create `benchmark/physics/privacy.py`:

```python
from pathlib import Path

from PIL import Image, ImageDraw


def apply_redactions(source: Path, output: Path, rectangles: list[tuple[int, int, int, int]]) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source).convert("RGB") as image:
        draw = ImageDraw.Draw(image)
        for rectangle in rectangles:
            draw.rectangle(rectangle, fill="black")
        image.save(output, quality=95)


def assert_privacy_approved(rows: list[dict[str, str]]) -> None:
    rejected = [row["page"] for row in rows if row.get("approved", "").lower() != "true"]
    if rejected:
        raise ValueError(f"privacy approval missing for: {', '.join(rejected)}")


def assert_anonymous_name(path: Path) -> None:
    if not path.stem.startswith("S") or "_" in path.name:
        raise ValueError(f"non-anonymous filename: {path.name}")
```

- [ ] **Step 4: Run privacy tests**

```powershell
.\.venv\Scripts\python.exe -m unittest tests.benchmark.physics.test_privacy -v
```

Expected: `OK` with 2 tests.

- [ ] **Step 5: Commit privacy preparation**

```powershell
git add benchmark/physics/privacy.py tests/benchmark/physics/test_privacy.py
git commit -m "feat: gate anonymous homework images"
```

### Task 6: Initialize the Private Benchmark Workspace

**Files:**
- Create: `benchmark/physics/cli.py`
- Test: `tests/benchmark/physics/test_cli_init.py`
- Runtime output: `Data/physics/benchmark/**`

- [ ] **Step 1: Write a failing CLI initialization test**

```python
import tempfile
import unittest
from pathlib import Path

from benchmark.physics.cli import initialize_workspace


class CliInitTests(unittest.TestCase):
    def test_initialize_creates_private_templates(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            initialize_workspace(root, ["S001", "S002"])
            self.assertTrue((root / "gold" / "primary_scores.csv").exists())
            self.assertTrue((root / "manifest" / "privacy_review.csv").exists())
            self.assertTrue((root / "runs").is_dir())
```

- [ ] **Step 2: Run the test and verify failure**

```powershell
.\.venv\Scripts\python.exe -m unittest tests.benchmark.physics.test_cli_init -v
```

Expected: import or attribute failure for `initialize_workspace`.

- [ ] **Step 3: Implement `initialize_workspace` and `init` command**

The function must create `manifest`, `rubric`, `gold`, `anonymized`,
`transcripts/automatic`, `transcripts/human`, `runs`, and `reports`. It must
call `create_score_template` for primary and reviewer CSVs and must refuse to
overwrite non-empty gold files unless `--force` is supplied.

```python
def initialize_workspace(root: Path, student_ids: list[str]) -> None:
    for relative in (
        "manifest", "rubric", "gold", "anonymized",
        "transcripts/automatic", "transcripts/human", "runs", "reports",
    ):
        (root / relative).mkdir(parents=True, exist_ok=True)
    create_score_template(student_ids, root / "gold" / "primary_scores.csv")
    create_score_template(student_ids, root / "gold" / "reviewer_scores.csv")
    review = root / "manifest" / "privacy_review.csv"
    review.write_text("page,approved,reviewer,reviewed_at\n", encoding="utf-8")
```

- [ ] **Step 4: Run the CLI test**

```powershell
.\.venv\Scripts\python.exe -m unittest tests.benchmark.physics.test_cli_init -v
```

Expected: `OK` with 1 test.

- [ ] **Step 5: Initialize the real private workspace**

Run only after the manifest maps the 26 source students to `S001` through
`S026`:

```powershell
.\.venv\Scripts\python.exe -m benchmark.physics.cli init --root Data/physics/benchmark --students 26
```

Expected: private directories and two 312-row score templates are created.

- [ ] **Step 6: Human checkpoint - freeze rubric and primary scores**

The instructor fills `rubric_v1.json` and all 312 rows in
`primary_scores.csv` without opening existing model grades. The second grader
fills every medium/low/ambiguous item and the selected 20 percent audit sample.
No API experiment may start before adjudication validation passes.

- [ ] **Step 7: Commit CLI initialization**

```powershell
git add benchmark/physics/cli.py tests/benchmark/physics/test_cli_init.py
git commit -m "feat: initialize private benchmark workspace"
```

## Day 2: Build, Develop, and Freeze

### Task 7: Import the Historical `G0` Baseline

**Files:**
- Create: `benchmark/physics/baseline.py`
- Test: `tests/benchmark/physics/test_baseline.py`

- [ ] **Step 1: Write a failing legacy-column import test**

```python
import unittest

from benchmark.physics.baseline import row_to_score_records


class BaselineTests(unittest.TestCase):
    def test_imports_twelve_scores_without_recomputing_them(self):
        row = {
            "student": "alice", "Q1a": "2", "Q1b": "2", "Q1c": "3", "Q1d": "3",
            "Q2a": "7", "Q2b": "3", "Q3a": "1.5", "Q3b": "1.5",
            "Q3c": "1.5", "Q3d": "1.5", "Q3e": "2", "Q3f": "2",
        }
        records = row_to_score_records(row, "S001")
        self.assertEqual(len(records), 12)
        self.assertEqual(sum(record.score for record in records), 30.0)
```

- [ ] **Step 2: Run the test and verify failure**

```powershell
.\.venv\Scripts\python.exe -m unittest tests.benchmark.physics.test_baseline -v
```

Expected: import failure for `benchmark.physics.baseline`.

- [ ] **Step 3: Implement immutable baseline import**

```python
from .schema import QUESTION_IDS, ScoreRecord


def row_to_score_records(row: dict[str, str], student_id: str) -> list[ScoreRecord]:
    return [
        ScoreRecord(
            student_id=student_id,
            question_id=question_id,
            score=float(row[question_id]),
            confidence="medium",
            evidence="historical gpt_direct_v0 import",
            flags=("historical_single_run",),
        )
        for question_id in QUESTION_IDS
    ]
```

The importer writes a new private run directory and never modifies
`Data/physics/grades/grades.csv`.

- [ ] **Step 4: Run baseline tests and commit**

```powershell
.\.venv\Scripts\python.exe -m unittest tests.benchmark.physics.test_baseline -v
git add benchmark/physics/baseline.py tests/benchmark/physics/test_baseline.py
git commit -m "feat: import historical grading baseline"
```

Expected: test passes, then one focused commit.

### Task 8: Metrics and Student-Level Bootstrap

**Files:**
- Create: `benchmark/physics/metrics.py`
- Test: `tests/benchmark/physics/test_metrics.py`

- [ ] **Step 1: Write failing metric tests**

```python
import unittest

from benchmark.physics.metrics import evaluate_scores


class MetricsTests(unittest.TestCase):
    def test_exact_agreement_mae_and_bias(self):
        gold = {("S001", "Q1a"): 2.0, ("S002", "Q1a"): 1.0}
        predicted = {("S001", "Q1a"): 2.0, ("S002", "Q1a"): 2.0}
        result = evaluate_scores(gold, predicted)
        self.assertEqual(result["exact_agreement"], 0.5)
        self.assertEqual(result["subquestion_mae"], 0.5)
        self.assertEqual(result["mean_signed_error"], 0.5)

    def test_missing_prediction_is_an_error_not_zero(self):
        gold = {("S001", "Q1a"): 2.0}
        with self.assertRaisesRegex(ValueError, "missing predictions"):
            evaluate_scores(gold, {})
```

- [ ] **Step 2: Run tests and verify failure**

```powershell
.\.venv\Scripts\python.exe -m unittest tests.benchmark.physics.test_metrics -v
```

Expected: import failure for `benchmark.physics.metrics`.

- [ ] **Step 3: Implement core metrics**

```python
from statistics import fmean


def evaluate_scores(gold: dict[tuple[str, str], float], predicted: dict[tuple[str, str], float]) -> dict[str, float]:
    missing = sorted(set(gold) - set(predicted))
    if missing:
        raise ValueError(f"missing predictions: {missing}")
    errors = [predicted[key] - gold[key] for key in sorted(gold)]
    return {
        "exact_agreement": fmean(error == 0 for error in errors),
        "subquestion_mae": fmean(abs(error) for error in errors),
        "mean_signed_error": fmean(errors),
    }
```

Add total-score MAE, within-1-point rate, severe-error rate, per-question
accuracy, macro accuracy, confidence slices, and a deterministic
`paired_student_bootstrap(..., seed=20260701, samples=10000)`.

- [ ] **Step 4: Add a deterministic bootstrap test**

The test calls the bootstrap twice with the same seed and asserts identical
lower and upper bounds. It also asserts the lower bound is positive when every
student improves.

- [ ] **Step 5: Run and commit metrics**

```powershell
.\.venv\Scripts\python.exe -m unittest tests.benchmark.physics.test_metrics -v
git add benchmark/physics/metrics.py tests/benchmark/physics/test_metrics.py
git commit -m "feat: evaluate grading accuracy"
```

Expected: all metric tests pass.

### Task 9: Provider Adapters and Frozen Prompts

**Files:**
- Create: `benchmark/physics/providers.py`
- Create: `benchmark/physics/configs/physics_week9.json`
- Create: `benchmark/physics/prompts/transcribe.txt`
- Create: `benchmark/physics/prompts/grade_minimal.txt`
- Create: `benchmark/physics/prompts/grade_structured.txt`
- Create: `benchmark/physics/prompts/review.txt`
- Test: `tests/benchmark/physics/test_providers.py`

- [ ] **Step 1: Write failing provider tests with fake clients**

```python
import unittest

from benchmark.physics.providers import OpenAIProvider, DeepSeekProvider


class FakeResponses:
    def create(self, **kwargs):
        self.kwargs = kwargs
        return type("Response", (), {
            "output_text": '{"student_id":"S001","scores":[]}',
            "model": kwargs["model"],
            "usage": None,
        })()


class ProviderTests(unittest.TestCase):
    def test_openai_image_request_uses_input_image(self):
        responses = FakeResponses()
        client = type("Client", (), {"responses": responses})()
        provider = OpenAIProvider(client, model="gpt-5.4")
        provider.complete_images("grade", [b"jpeg-bytes"])
        content = responses.kwargs["input"][0]["content"]
        self.assertEqual(content[1]["type"], "input_image")
        self.assertTrue(content[1]["image_url"].startswith("data:image/jpeg;base64,"))
```

Add a DeepSeek fake-client test that asserts text-only messages,
`response_format={"type": "json_object"}`, and no image field.

- [ ] **Step 2: Run tests and verify failure**

```powershell
.\.venv\Scripts\python.exe -m unittest tests.benchmark.physics.test_providers -v
```

Expected: import failure for `benchmark.physics.providers`.

- [ ] **Step 3: Implement provider adapters**

The OpenAI adapter base64-encodes each approved JPEG and calls
`client.responses.create` with `input_text` and `input_image` content items.
The DeepSeek adapter calls `client.chat.completions.create` against
`https://api.deepseek.com`, passes text only, and enables JSON output.

```python
class OpenAIProvider:
    def __init__(self, client, model: str):
        self.client = client
        self.model = model

    def complete_images(self, prompt: str, images: list[bytes]):
        content = [{"type": "input_text", "text": prompt}]
        for image in images:
            encoded = base64.b64encode(image).decode("ascii")
            content.append({
                "type": "input_image",
                "image_url": f"data:image/jpeg;base64,{encoded}",
            })
        return self.client.responses.create(
            model=self.model,
            input=[{"role": "user", "content": content}],
        )
```

The checked-in configuration is:

```json
{
  "dataset": "physics_week9",
  "openai_model": "gpt-5.4",
  "deepseek_model": "deepseek-v4-pro",
  "runs_per_condition": 3,
  "split_seed": 20260701,
  "bootstrap_samples": 10000,
  "max_retries": 2
}
```

Every grading prompt explicitly requires 12 question IDs, quarter-point
scores, evidence, confidence, flags, total, and valid JSON. The transcription
prompt requires the 12 question IDs, preserves equations and units, and uses
`[UNCLEAR]` rather than inference.

- [ ] **Step 4: Run provider tests**

```powershell
.\.venv\Scripts\python.exe -m unittest tests.benchmark.physics.test_providers -v
```

Expected: all fake-client tests pass and no network call occurs.

- [ ] **Step 5: Commit adapters and prompts**

```powershell
git add benchmark/physics/providers.py benchmark/physics/configs benchmark/physics/prompts tests/benchmark/physics/test_providers.py
git commit -m "feat: add GPT and DeepSeek benchmark adapters"
```

### Task 10: Immutable Experiment Runner

**Files:**
- Create: `benchmark/physics/runner.py`
- Test: `tests/benchmark/physics/test_runner.py`

- [ ] **Step 1: Write failing runner tests**

```python
import tempfile
import unittest
from pathlib import Path

from benchmark.physics.runner import create_run_directory


class RunnerTests(unittest.TestCase):
    def test_run_directory_is_immutable(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_run_directory(root, "G1-dev-r1")
            with self.assertRaisesRegex(FileExistsError, "already exists"):
                create_run_directory(root, "G1-dev-r1")
```

Add tests that two retryable failures followed by success produce three
attempt records, and that persistent failure is recorded as missing rather
than a zero score.

- [ ] **Step 2: Run tests and verify failure**

```powershell
.\.venv\Scripts\python.exe -m unittest tests.benchmark.physics.test_runner -v
```

Expected: import failure for `benchmark.physics.runner`.

- [ ] **Step 3: Implement run creation and retry policy**

Each run directory contains:

```text
manifest.json
predictions.csv
raw_responses.jsonl
failures.jsonl
```

`manifest.json` records condition, split, repetition, provider, model, prompt
hash, rubric hash, input hashes, parameters, start/end time, and usage.
`create_run_directory` must use `mkdir(exist_ok=False)`. Retry only timeout,
connection, rate-limit, and server errors, with at most two retries. Schema or
score validation gets one format-repair attempt and then a recorded failure.

- [ ] **Step 4: Run runner tests and commit**

```powershell
.\.venv\Scripts\python.exe -m unittest tests.benchmark.physics.test_runner -v
git add benchmark/physics/runner.py tests/benchmark/physics/test_runner.py
git commit -m "feat: record immutable benchmark runs"
```

Expected: all runner tests pass.

### Task 11: Development Ablation CLI

**Files:**
- Modify: `benchmark/physics/cli.py`
- Test: `tests/benchmark/physics/test_cli_run.py`

- [ ] **Step 1: Write a failing CLI safety test**

The test builds an unapproved privacy CSV, calls the `run` command for `G1`,
and asserts a nonzero exit plus `privacy approval missing`. A second test calls
`run --split test` before the freeze marker exists and asserts
`held-out split is sealed`.

- [ ] **Step 2: Run the tests and verify failure**

```powershell
.\.venv\Scripts\python.exe -m unittest tests.benchmark.physics.test_cli_run -v
```

Expected: CLI does not yet implement the run safety gates.

- [ ] **Step 3: Implement CLI run conditions**

Supported commands:

```text
physics-benchmark validate --root Data/physics/benchmark
physics-benchmark import-baseline --root Data/physics
physics-benchmark run --condition G1 --split dev --repetition 1
physics-benchmark run --condition T1 --split dev --repetition 1
physics-benchmark run --condition G2 --split dev --repetition 1
physics-benchmark run --condition D1 --split dev --repetition 1
physics-benchmark freeze --candidate S4
```

The `run` command loads API keys from `OPENAI_API_KEY` or `DEEPSEEK_API_KEY`,
requires all inputs to pass the privacy gate, and refuses test-split access
until `freeze.json` records the candidate, prompt hashes, model IDs, rubric
hash, and timestamp.

- [ ] **Step 4: Run CLI tests and commit**

```powershell
.\.venv\Scripts\python.exe -m unittest tests.benchmark.physics.test_cli_run -v
git add benchmark/physics/cli.py tests/benchmark/physics/test_cli_run.py
git commit -m "feat: orchestrate grading ablations"
```

Expected: both safety tests pass.

- [ ] **Step 5: Human checkpoint - supply keys and approve uploads**

The user sets keys in the current PowerShell session:

```powershell
$env:OPENAI_API_KEY = Read-Host "Enter OPENAI_API_KEY" -MaskInput
$env:DEEPSEEK_API_KEY = Read-Host "Enter DEEPSEEK_API_KEY" -MaskInput
```

Before any request, the user opens every anonymized page and marks its private
`privacy_review.csv` row `approved=true`. Do not print or persist either key.

- [ ] **Step 6: Run development conditions and compact ablations**

Run `G1`, `T1`, `G2`, and `D1` three times on the eight-student development
set. Run the compact `V0/V1/V2/V4` and `S0/S1/S2/S4/S5` sequence. Record all
conditions even when they fail the 3-point advancement gate.

- [ ] **Step 7: Freeze the best workflow by end of Day 2**

Use only development metrics. Write the selected prompt hashes, provider
models, rubric hash, preprocessing options, and second-pass rule to the private
`freeze.json`. After this point, no held-out result may change the workflow.

### Task 12: Update the Grading Skill from Development Evidence

**Files:**
- Modify: `.claude/skills/grade-homework/SKILL.md`
- Modify: `.agents/skills/grade-homework/SKILL.md`
- Test: `tests/benchmark/physics/test_skill_sync.py`

- [ ] **Step 1: Write a failing mirror test**

```python
from pathlib import Path
import unittest


class SkillSyncTests(unittest.TestCase):
    def test_claude_and_agent_skills_match(self):
        claude = Path(".claude/skills/grade-homework/SKILL.md").read_text(encoding="utf-8")
        agent = Path(".agents/skills/grade-homework/SKILL.md").read_text(encoding="utf-8")
        self.assertEqual(claude, agent)
```

- [ ] **Step 2: Run the test and verify failure**

```powershell
.\.venv\Scripts\python.exe -m unittest tests.benchmark.physics.test_skill_sync -v
```

Expected: the current mirrored files differ.

- [ ] **Step 3: Rewrite the skill to match the frozen workflow**

The final skill must require, in order:

1. deterministic image orientation, page ordering, and readability checks;
2. rubric freeze before grading;
3. structured per-question evidence extraction;
4. score assignment only after evidence extraction;
5. score-range, total, and JSON validation;
6. low-confidence second-pass review;
7. explicit flags instead of guessed unreadable content;
8. preservation of baseline and immutable run metadata in benchmark mode.

Remove stale references to absent helper scripts unless those scripts are
created and tested in this branch. Use repo-relative commands. Write identical
content to both skill paths.

- [ ] **Step 4: Run the mirror test and relevant benchmark tests**

```powershell
.\.venv\Scripts\python.exe -m unittest tests.benchmark.physics.test_skill_sync -v
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Expected: mirror test passes and the full suite is green.

- [ ] **Step 5: Commit the evidence-based skill**

```powershell
git add .claude/skills/grade-homework/SKILL.md .agents/skills/grade-homework/SKILL.md tests/benchmark/physics/test_skill_sync.py
git commit -m "feat: strengthen homework grading workflow"
```

## Day 3 Half-Day: Evaluate, Report, and Merge

### Task 13: Anonymous Report Generation

**Files:**
- Create: `benchmark/physics/report.py`
- Test: `tests/benchmark/physics/test_report.py`

- [ ] **Step 1: Write a failing report test**

```python
import unittest

from benchmark.physics.report import render_markdown_report


class ReportTests(unittest.TestCase):
    def test_report_contains_metrics_and_no_source_names(self):
        report = render_markdown_report(
            dataset="Physics Week 9",
            conditions={"G0": {"exact_agreement": 0.8}},
            limitations=["Single assignment, 26 students"],
        )
        self.assertIn("# Physics Week 9 Grading Benchmark", report)
        self.assertIn("Exact agreement", report)
        self.assertNotIn("chenyujin", report.lower())
```

- [ ] **Step 2: Run tests and verify failure**

```powershell
.\.venv\Scripts\python.exe -m unittest tests.benchmark.physics.test_report -v
```

Expected: import failure for `benchmark.physics.report`.

- [ ] **Step 3: Implement the report**

The Markdown report contains:

- gold-standard quality and human agreement;
- held-out results before all-26 results;
- `G0/G1/G2/D1/G3/D2` tables;
- exact agreement, macro agreement, MAE, within-1 rate, bias, failures, cost;
- paired confidence intervals;
- transcription-error contribution;
- compact component-ablation table;
- anonymous representative error categories;
- limitations and permitted claims.

The renderer rejects any supplied student label that does not match `S\d{3}`.

- [ ] **Step 4: Run and commit report tests**

```powershell
.\.venv\Scripts\python.exe -m unittest tests.benchmark.physics.test_report -v
git add benchmark/physics/report.py tests/benchmark/physics/test_report.py
git commit -m "feat: render anonymous grading report"
```

Expected: report test passes.

### Task 14: Held-Out Evaluation

**Files:**
- Runtime output only: `Data/physics/benchmark/runs/**`
- Runtime output only: `Data/physics/benchmark/reports/physics_week9_benchmark.md`

- [ ] **Step 1: Verify freeze and privacy gates**

Run:

```powershell
.\.venv\Scripts\physics-benchmark.exe validate --root Data/physics/benchmark
```

Expected: 26 students, 312 gold scores, 8 development students, 18 test
students, 10 transcript-gold students, approved anonymous pages, and a frozen
workflow. Any mismatch stops evaluation.

- [ ] **Step 2: Run held-out conditions three times**

Run frozen `G1`, `T1`, `G2`, and `D1` on the 18 test students. Run `G3` and
`D2` on the six held-out human-transcript students. Import `G0` without a new
model call. Do not modify prompts, rubric, model IDs, or preprocessing after
the first test run starts.

- [ ] **Step 3: Evaluate and render the report**

```powershell
.\.venv\Scripts\physics-benchmark.exe evaluate --root Data/physics/benchmark
.\.venv\Scripts\physics-benchmark.exe report --root Data/physics/benchmark
```

Expected: metrics JSON and anonymous Markdown report are produced with no
student names, source filenames, or API keys.

- [ ] **Step 4: Run focused removal ablations**

Remove only the three highest-impact development components from the frozen
workflow, one at a time. Treat these as attribution experiments, not new model
selection. Record their held-out deltas in the report.

### Task 15: Final Verification and Branch Integration

**Files:**
- Modify: `README.md` only if a short benchmark command is needed.
- Verify: all tracked benchmark and skill files.

- [ ] **Step 1: Run the complete test suite**

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Expected: all existing and benchmark tests pass with zero failures and errors.

- [ ] **Step 2: Run syntax compilation and Git checks**

```powershell
.\.venv\Scripts\python.exe -m compileall benchmark scripts
git diff --check main...HEAD
git status --short
```

Expected: compilation succeeds; no whitespace errors; only known user-owned
`.gitignore`/scratch state remains outside the branch commits.

- [ ] **Step 3: Audit privacy and report claims**

Search private run payloads and the final report for every source student name
and source filename from the private manifest. Expected: no match outside the
identity mapping and raw-source directories. Confirm the report says
`Physics Week 9 internal benchmark` and does not generalize beyond it.

- [ ] **Step 4: Review branch commits**

```powershell
git log --oneline main..HEAD
git diff --stat main...HEAD
```

Expected: focused design, implementation, skill, and report-support commits;
no `Data/` files.

- [ ] **Step 5: Commit final tracked documentation**

```powershell
git add README.md benchmark tests .claude/skills/grade-homework/SKILL.md .agents/skills/grade-homework/SKILL.md
git commit -m "docs: document physics grading benchmark"
```

Skip this commit when there are no final tracked documentation changes.

- [ ] **Step 6: Merge only after verified review**

Use `superpowers:finishing-a-development-branch`, present the verified branch
summary to the user, and merge `codex/physics-grading-accuracy` into `main`
only after explicit approval. Preserve all user-owned dirty files throughout.

## Execution Checkpoints for the User

The user participates at four explicit gates:

1. **Gold gate:** fill the 312 primary score rows and arrange independent
   review/adjudication by July 2 noon.
2. **Privacy gate:** visually approve every anonymized page before API upload.
3. **Credential gate:** enter OpenAI and DeepSeek API keys in the active shell;
   never paste them into chat or a file.
4. **Merge gate:** review the held-out report and verified branch summary before
   integration into `main`.

## Official API References

- OpenAI image inputs via Responses API and base64 data URLs:
  `https://developers.openai.com/api/docs/guides/images-vision`
- OpenAI structured outputs:
  `https://developers.openai.com/api/docs/guides/structured-outputs`
- DeepSeek Chat Completion text schema:
  `https://api-docs.deepseek.com/api/create-chat-completion`
