import argparse
import csv
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from collections.abc import Sequence

from .gold import create_score_template
from .privacy import assert_privacy_approved


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
    assert_privacy_approved(_read_privacy_rows(root))


def run_condition(root: Path, condition: str, split: str, repetition: int) -> None:
    if repetition <= 0:
        raise ValueError("repetition must be positive")
    assert_privacy_approved(_read_privacy_rows(root))
    if split == "test" and not (root / "freeze.json").exists():
        raise ValueError("held-out split is sealed until freeze.json exists")
    _require_api_key(condition)


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
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


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
