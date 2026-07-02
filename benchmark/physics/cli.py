import argparse
import csv
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from collections.abc import Sequence
from typing import Any

from .gold import create_score_template
from .privacy import assert_anonymous_name, assert_privacy_approved
from .providers import OpenAIProvider
from .runner import (
    ValidationFailure,
    create_run_directory,
    run_student_with_retries,
)
from .schema import ProviderResult, ScoreRecord, validate_score_records


PRIVATE_DIRECTORIES = (
    "manifest",
    "rubric",
    "gold",
    "anonymized",
    "transcripts/automatic",
    "transcripts/human",
    "runs",
    "reports",
)


def initialize_workspace(
    root: Path,
    student_ids: list[str],
    *,
    force: bool = False,
) -> None:
    protected_files = (
        root / "gold" / "primary_scores.csv",
        root / "gold" / "reviewer_scores.csv",
    )
    existing = [path for path in protected_files if path.exists() and path.stat().st_size]
    if existing and not force:
        names = ", ".join(str(path) for path in existing)
        raise FileExistsError(f"refusing to overwrite non-empty gold files: {names}")

    for relative in PRIVATE_DIRECTORIES:
        (root / relative).mkdir(parents=True, exist_ok=True)
    create_score_template(student_ids, protected_files[0])
    create_score_template(student_ids, protected_files[1])
    review = root / "manifest" / "privacy_review.csv"
    if force or not review.exists() or not review.stat().st_size:
        review.write_text(
            "page,approved,reviewer,reviewed_at\n",
            encoding="utf-8",
        )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="physics-benchmark")
    subparsers = parser.add_subparsers(dest="command", required=True)
    init_parser = subparsers.add_parser("init", help="initialize private workspace")
    init_parser.add_argument("--root", type=Path, required=True)
    init_parser.add_argument("--students", type=int, required=True)
    init_parser.add_argument("--force", action="store_true")

    validate_parser = subparsers.add_parser("validate", help="validate private workspace")
    validate_parser.add_argument("--root", type=Path, required=True)

    subparsers.add_parser("import-baseline", help="import historical G0 baseline").add_argument(
        "--root", type=Path, required=True
    )

    run_parser = subparsers.add_parser("run", help="run a benchmark condition")
    run_parser.add_argument("--root", type=Path, required=True)
    run_parser.add_argument("--condition", choices=("G1", "T1", "G2", "D1"), required=True)
    run_parser.add_argument("--split", choices=("dev", "test"), required=True)
    run_parser.add_argument("--repetition", type=int, required=True)

    freeze_parser = subparsers.add_parser("freeze", help="seal the held-out workflow")
    freeze_parser.add_argument("--root", type=Path, required=True)
    freeze_parser.add_argument("--candidate", required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    try:
        args = _build_parser().parse_args(argv)
        if args.command == "init":
            if args.students <= 0:
                raise ValueError("students must be positive")
            student_ids = [f"S{index:03d}" for index in range(1, args.students + 1)]
            initialize_workspace(args.root, student_ids, force=args.force)
        elif args.command == "validate":
            validate_workspace(args.root)
        elif args.command == "import-baseline":
            raise NotImplementedError("import-baseline command is not implemented yet")
        elif args.command == "run":
            run_condition(args.root, args.condition, args.split, args.repetition)
        elif args.command == "freeze":
            freeze_workflow(args.root, args.candidate)
        return 0
    except SystemExit as error:
        return int(error.code)
    except Exception as error:
        print(str(error), file=sys.stderr)
        return 1


def validate_workspace(root: Path) -> None:
    privacy_rows = _read_privacy_rows(root)
    assert_privacy_approved(privacy_rows)


def run_condition(
    root: Path,
    condition: str,
    split: str,
    repetition: int,
    *,
    provider: Any | None = None,
) -> Path:
    if repetition <= 0:
        raise ValueError("repetition must be positive")
    privacy_rows = _read_privacy_rows(root)
    assert_privacy_approved(privacy_rows)
    if split == "test" and not (root / "freeze.json").exists():
        raise ValueError("held-out split is sealed until freeze.json exists")
    if condition != "G1":
        _require_api_key(condition)
        raise NotImplementedError(f"{condition} execution is not implemented yet")

    config = _load_config()
    if provider is None:
        raise ValueError("OpenAI API conditions are inactive in the revised benchmark")
    model = getattr(provider, "model", config["gpt_display_model"])

    student_ids = _load_split_student_ids(root, split)
    rubric_path = root / "rubric" / "rubric_v1.json"
    rubric = json.loads(rubric_path.read_text(encoding="utf-8"))
    prompt_path = Path(__file__).with_name("prompts") / "grade_structured.txt"
    prompt_template = prompt_path.read_text(encoding="utf-8")
    image_paths = {
        student_id: sorted((root / "anonymized" / student_id).glob("*.jpg"))
        for student_id in student_ids
    }
    missing = [student_id for student_id, paths in image_paths.items() if not paths]
    if missing:
        raise FileNotFoundError(f"anonymous images missing for: {', '.join(missing)}")
    approved_pages = {row["page"] for row in privacy_rows}
    upload_paths = [path for paths in image_paths.values() for path in paths]
    for path in upload_paths:
        assert_anonymous_name(path)
    unapproved = sorted(path.name for path in upload_paths if path.name not in approved_pages)
    if unapproved:
        raise ValueError(f"privacy approval missing for: {', '.join(unapproved)}")

    run_id = f"{condition}-{split}-r{repetition}"
    manifest = {
        "condition": condition,
        "split": split,
        "repetition": repetition,
        "provider": "openai",
        "model": model,
        "student_ids": student_ids,
        "prompt_hash": _file_hash(prompt_path),
        "rubric_hash": _file_hash(rubric_path),
        "input_hashes": {
            student_id: _hash_files(paths)
            for student_id, paths in image_paths.items()
        },
        "parameters": {"structured_output": True},
    }
    run_dir = create_run_directory(root / "runs", run_id, manifest=manifest)
    usage: dict[str, int | float] = {}
    successful_students = 0
    for student_id in student_ids:
        images = [path.read_bytes() for path in image_paths[student_id]]
        base_prompt = _grading_prompt(prompt_template, student_id, rubric)

        def operation(attempt: int) -> ProviderResult:
            prompt = base_prompt
            if attempt > 1:
                prompt += (
                    "\nThe previous response failed validation. Return one corrected "
                    "JSON object only, following the required schema exactly."
                )
            result = provider.complete_images(prompt, images)
            try:
                _parse_grading_response(result.raw_text, student_id)
            except ValidationFailure as error:
                raise ValidationFailure(str(error), result=result) from error
            return result

        result = run_student_with_retries(
            run_dir,
            student_id,
            operation,
            max_retries=config["max_retries"],
        )
        if result is None:
            continue
        records = _parse_grading_response(result.raw_text, student_id)
        _append_predictions(run_dir / "predictions.csv", records)
        _merge_usage(usage, result.usage)
        successful_students += 1

    _finish_manifest(run_dir / "manifest.json", usage)
    if successful_students == 0:
        raise RuntimeError(
            f"{run_id} produced no predictions; see {run_dir / 'failures.jsonl'}"
        )
    return run_dir


def freeze_workflow(root: Path, candidate: str) -> None:
    root.mkdir(parents=True, exist_ok=True)
    freeze = {
        "candidate": candidate,
        "timestamp": _utc_now(),
        "prompt_hashes": _prompt_hashes(),
        "model_ids": _model_ids(),
        "rubric_hash": _optional_file_hash(root / "rubric" / "rubric_v1.json"),
    }
    (root / "freeze.json").write_text(
        json.dumps(freeze, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _read_privacy_rows(root: Path) -> list[dict[str, str]]:
    path = root / "manifest" / "privacy_review.csv"
    if not path.exists():
        raise ValueError(f"privacy approval missing for: {path}")
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def _load_config() -> dict[str, Any]:
    path = Path(__file__).with_name("configs") / "physics_week9.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _load_split_student_ids(root: Path, split: str) -> list[str]:
    split_data = json.loads(
        (root / "manifest" / "split.json").read_text(encoding="utf-8")
    )
    field = "development_student_ids" if split == "dev" else "heldout_student_ids"
    return list(split_data[field])


def _grading_prompt(template: str, student_id: str, rubric: dict[str, Any]) -> str:
    context = {
        "student_id": student_id,
        "rubric": rubric,
    }
    return (
        template
        + f"\n\nOutput student_id must be {student_id}. "
        "The ID in the JSON shape above is only an example."
        "\nBenchmark context:\n"
        + json.dumps(context, ensure_ascii=True, sort_keys=True)
    )


def _parse_grading_response(raw_text: str, student_id: str) -> list[ScoreRecord]:
    try:
        payload = json.loads(raw_text)
        if payload["student_id"] != student_id:
            raise ValueError("student_id does not match request")
        records = []
        for item in payload["scores"]:
            if not isinstance(item["extracted_evidence"], str):
                raise ValueError("extracted_evidence must be text")
            flags = item["flags"]
            if not isinstance(flags, list) or not all(
                isinstance(flag, str) for flag in flags
            ):
                raise ValueError("flags must be a list of strings")
            records.append(
                ScoreRecord(
                    student_id=student_id,
                    question_id=item["question_id"],
                    score=float(item["score"]),
                    confidence=item["confidence"],
                    evidence=item["evidence"],
                    flags=tuple(flags),
                )
            )
        calculated_total = validate_score_records(records)
        if abs(float(payload["total"]) - calculated_total) > 1e-9:
            raise ValueError("reported total does not match question scores")
        return records
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
        raise ValidationFailure(f"invalid grading response: {error}") from error


def _append_predictions(path: Path, records: list[ScoreRecord]) -> None:
    with path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=(
                "student_id",
                "question_id",
                "score",
                "confidence",
                "evidence",
                "ambiguity_code",
            ),
        )
        for record in records:
            writer.writerow(
                {
                    "student_id": record.student_id,
                    "question_id": record.question_id,
                    "score": record.score,
                    "confidence": record.confidence,
                    "evidence": record.evidence,
                    "ambiguity_code": ";".join(record.flags),
                }
            )


def _hash_files(paths: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in paths:
        digest.update(path.name.encode("utf-8"))
        digest.update(path.read_bytes())
    return digest.hexdigest()


def _merge_usage(total: dict[str, int | float], usage: dict[str, Any]) -> None:
    for key, value in usage.items():
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            total[key] = total.get(key, 0) + value


def _finish_manifest(path: Path, usage: dict[str, int | float]) -> None:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest["end_time"] = _utc_now()
    manifest["usage"] = usage
    path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _require_api_key(condition: str) -> None:
    variable = "DEEPSEEK_API_KEY" if condition == "D1" else "OPENAI_API_KEY"
    if not os.environ.get(variable):
        raise ValueError(f"{variable} is required")


def _prompt_hashes() -> dict[str, str]:
    prompt_dir = Path(__file__).with_name("prompts")
    return {
        path.stem: _file_hash(path)
        for path in sorted(prompt_dir.glob("*.txt"))
    }


def _model_ids() -> dict[str, str]:
    config_path = Path(__file__).with_name("configs") / "physics_week9.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    return {
        "openai": config["openai_model"],
        "deepseek": config["deepseek_model"],
    }


def _optional_file_hash(path: Path) -> str | None:
    if not path.exists():
        return None
    return _file_hash(path)


def _file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


if __name__ == "__main__":
    raise SystemExit(main())
