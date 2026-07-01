import argparse
from pathlib import Path
from collections.abc import Sequence

from .gold import create_score_template


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
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.command == "init":
        if args.students <= 0:
            raise ValueError("students must be positive")
        student_ids = [f"S{index:03d}" for index in range(1, args.students + 1)]
        initialize_workspace(args.root, student_ids, force=args.force)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
