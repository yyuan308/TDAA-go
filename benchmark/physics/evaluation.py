import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .metrics import evaluate_scores, paired_student_bootstrap
from .schema import QUESTION_IDS


FULL_SPLIT_CONDITIONS = ("G0", "G2", "D1")
TRANSCRIPT_SUBSET_CONDITIONS = ("G3", "D2")


def evaluate_conditions(benchmark_root: Path, split: str) -> dict[str, Any]:
    split_data = json.loads(
        (benchmark_root / "manifest" / "split.json").read_text(encoding="utf-8")
    )
    split_key = "development_student_ids" if split == "dev" else "heldout_student_ids"
    full_ids = split_data[split_key]
    transcript_ids = split_data["transcript_gold"][split_key]
    config = _load_config()
    gold = _load_scores(
        benchmark_root / "gold" / "primary_scores.csv", set(full_ids)
    )
    expected_gold_keys = {
        (student_id, question_id)
        for student_id in full_ids
        for question_id in QUESTION_IDS
    }
    if set(gold) != expected_gold_keys:
        raise ValueError("primary gold is incomplete for the requested split")

    conditions: dict[str, Any] = {}
    prediction_sets: dict[str, dict[tuple[str, str], float]] = {}
    for condition in (*FULL_SPLIT_CONDITIONS, *TRANSCRIPT_SUBSET_CONDITIONS):
        run_id = _run_id(condition, split)
        run_dir = benchmark_root / "runs" / run_id
        if not run_dir.exists():
            continue
        student_ids = full_ids if condition in FULL_SPLIT_CONDITIONS else transcript_ids
        expected_keys = {
            (student_id, question_id)
            for student_id in student_ids
            for question_id in QUESTION_IDS
        }
        condition_gold = {key: value for key, value in gold.items() if key in expected_keys}
        predictions = _load_scores(run_dir / "predictions.csv", set(student_ids))
        if set(predictions) != expected_keys:
            missing = sorted(expected_keys - set(predictions))
            extra = sorted(set(predictions) - expected_keys)
            raise ValueError(
                f"{run_id} predictions do not match expected split; "
                f"missing={missing}, extra={extra}"
            )
        prediction_sets[condition] = predictions
        conditions[condition] = {
            "run_id": run_id,
            "n_students": len(student_ids),
            "population": (
                "full_split"
                if condition in FULL_SPLIT_CONDITIONS
                else "transcript_subset"
            ),
            **evaluate_scores(condition_gold, predictions),
        }

    if "G0" not in conditions:
        raise ValueError("required baseline run is missing: G0-all-r1")

    paired_vs_g0 = {}
    for condition in ("G2", "D1"):
        if condition in prediction_sets:
            paired_vs_g0[condition] = paired_student_bootstrap(
                gold,
                prediction_sets["G0"],
                prediction_sets[condition],
                seed=config["split_seed"],
                samples=config["bootstrap_samples"],
            )

    excluded_runs = [
        run_id
        for run_id in config["excluded_run_ids"]
        if (benchmark_root / "runs" / run_id).exists()
    ]
    result = {
        "split": split,
        "reference_status": _reference_status(benchmark_root, full_ids),
        "excluded_runs": excluded_runs,
        "conditions": conditions,
        "paired_vs_g0": paired_vs_g0,
    }
    (benchmark_root / f"metrics-{split}.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return result


def freeze_revised_workflow(benchmark_root: Path, candidate: str) -> dict[str, Any]:
    for run_id in ("G2-dev-r1", "D1-dev-r1"):
        if not (benchmark_root / "runs" / run_id).exists():
            raise ValueError(f"required development run is missing: {run_id}")

    evaluate_conditions(benchmark_root, split="dev")
    config = _load_config()
    prompt_dir = Path(__file__).with_name("prompts")
    grade_hash = _file_hash(prompt_dir / "grade_structured.txt")
    freeze = {
        "candidate": candidate,
        "gpt_execution": config["gpt_execution"],
        "gpt_display_model": config["gpt_display_model"],
        "deepseek_model": config["deepseek_model"],
        "runs_per_condition": config["runs_per_condition"],
        "excluded_run_ids": config["excluded_run_ids"],
        "prompt_hashes": {
            "T1": _file_hash(prompt_dir / "transcribe.txt"),
            "G2": grade_hash,
            "G3": grade_hash,
            "D1": grade_hash,
            "D2": grade_hash,
        },
        "rubric_hash": _file_hash(benchmark_root / "rubric" / "rubric_v1.json"),
        "input_policy": "frozen anonymous transcript workflow",
        "timestamp": _utc_now(),
    }
    (benchmark_root / "freeze.json").write_text(
        json.dumps(freeze, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return freeze


def _run_id(condition: str, split: str) -> str:
    if condition == "G0":
        return "G0-all-r1"
    return f"{condition}-{split}-r1"


def _load_scores(path: Path, student_ids: set[str]) -> dict[tuple[str, str], float]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    scores: dict[tuple[str, str], float] = {}
    for row in rows:
        if row["student_id"] not in student_ids:
            continue
        key = (row["student_id"], row["question_id"])
        if key in scores:
            raise ValueError(f"duplicate score row in {path}: {key}")
        if not row["score"].strip():
            raise ValueError(f"blank score in {path}: {key}")
        scores[key] = float(row["score"])
    return scores


def _reference_status(benchmark_root: Path, student_ids: list[str]) -> str:
    path = benchmark_root / "gold" / "reviewer_scores.csv"
    if not path.exists():
        return "single_primary_rater"
    with path.open(newline="", encoding="utf-8-sig") as handle:
        rows = [row for row in csv.DictReader(handle) if row["student_id"] in student_ids]
    expected = len(student_ids) * len(QUESTION_IDS)
    if len(rows) != expected or any(not row["score"].strip() for row in rows):
        return "single_primary_rater"
    return "primary_and_reviewer_complete"


def _load_config() -> dict[str, Any]:
    path = Path(__file__).with_name("configs") / "physics_week9.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
