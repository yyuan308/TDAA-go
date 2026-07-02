import csv
import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from unittest.mock import patch

from benchmark.physics.cli import main
from benchmark.physics.gold import SCORE_FIELDS
from benchmark.physics.schema import QUESTION_IDS


class RevisedCliTests(unittest.TestCase):
    def _packet_workspace(self, root: Path) -> Path:
        benchmark_root = root / "benchmark"
        (benchmark_root / "manifest").mkdir(parents=True)
        (benchmark_root / "rubric").mkdir()
        images = benchmark_root / "anonymized" / "S008"
        images.mkdir(parents=True)
        (images / "S008-p01.jpg").write_bytes(b"anonymous-jpeg")
        (benchmark_root / "manifest" / "privacy_review.csv").write_text(
            "page,approved,reviewer,reviewed_at\n"
            "S008-p01.jpg,true,teacher,2026-07-02\n",
            encoding="utf-8",
        )
        (benchmark_root / "manifest" / "split.json").write_text(
            json.dumps(
                {
                    "development_student_ids": ["S008"],
                    "heldout_student_ids": ["S009"],
                    "transcript_gold": {
                        "development_student_ids": ["S008"],
                        "heldout_student_ids": ["S009"],
                    },
                }
            ),
            encoding="utf-8",
        )
        (benchmark_root / "rubric" / "rubric_v1.json").write_text(
            json.dumps({"rubric_version": "rubric_v1", "questions": []}),
            encoding="utf-8",
        )
        return benchmark_root

    def _evaluation_workspace(self, root: Path) -> Path:
        benchmark_root = root / "benchmark"
        (benchmark_root / "manifest").mkdir(parents=True)
        (benchmark_root / "gold").mkdir()
        (benchmark_root / "rubric").mkdir()
        (benchmark_root / "runs").mkdir()
        (benchmark_root / "manifest" / "split.json").write_text(
            json.dumps(
                {
                    "development_student_ids": ["S008"],
                    "heldout_student_ids": ["S009"],
                    "transcript_gold": {
                        "development_student_ids": ["S008"],
                        "heldout_student_ids": ["S009"],
                    },
                }
            ),
            encoding="utf-8",
        )
        for filename, score in (("primary_scores.csv", "1"), ("reviewer_scores.csv", "")):
            with (benchmark_root / "gold" / filename).open(
                "w", newline="", encoding="utf-8"
            ) as handle:
                writer = csv.DictWriter(handle, fieldnames=SCORE_FIELDS)
                writer.writeheader()
                for question_id in QUESTION_IDS:
                    writer.writerow(
                        {
                            "student_id": "S008",
                            "question_id": question_id,
                            "score": score,
                            "confidence": "high" if score else "",
                            "evidence": "",
                            "ambiguity_code": "",
                        }
                    )
        (benchmark_root / "rubric" / "rubric_v1.json").write_text(
            json.dumps({"rubric_version": "rubric_v1"}), encoding="utf-8"
        )
        for run_id in ("G0-all-r1", "G2-dev-r1", "D1-dev-r1"):
            run_dir = benchmark_root / "runs" / run_id
            run_dir.mkdir()
            (run_dir / "manifest.json").write_text(
                json.dumps({"run_id": run_id, "end_time": "2026-07-02T00:00:00Z"}),
                encoding="utf-8",
            )
            with (run_dir / "predictions.csv").open(
                "w", newline="", encoding="utf-8"
            ) as handle:
                writer = csv.DictWriter(handle, fieldnames=SCORE_FIELDS)
                writer.writeheader()
                for question_id in QUESTION_IDS:
                    writer.writerow(
                        {
                            "student_id": "S008",
                            "question_id": question_id,
                            "score": "1",
                            "confidence": "high",
                            "evidence": "",
                            "ambiguity_code": "",
                        }
                    )
        return benchmark_root

    def test_build_packet_command(self):
        with tempfile.TemporaryDirectory() as tmp:
            benchmark_root = self._packet_workspace(Path(tmp))

            code = main(
                [
                    "build-packet",
                    "--root",
                    str(benchmark_root),
                    "--condition",
                    "T1",
                    "--split",
                    "dev",
                    "--repetition",
                    "1",
                ]
            )

            self.assertEqual(code, 0)
            self.assertTrue(
                (benchmark_root / "blind_packets" / "T1-dev-r1").exists()
            )

    def test_import_baseline_command_anonymizes_source_labels(self):
        with tempfile.TemporaryDirectory() as tmp:
            physics_root = Path(tmp) / "physics"
            grades_dir = physics_root / "grades"
            manifest_dir = physics_root / "benchmark" / "manifest"
            grades_dir.mkdir(parents=True)
            manifest_dir.mkdir(parents=True)
            fields = ["student", *QUESTION_IDS]
            with (grades_dir / "grades.csv").open(
                "w", newline="", encoding="utf-8"
            ) as handle:
                writer = csv.DictWriter(handle, fieldnames=fields)
                writer.writeheader()
                writer.writerow(
                    {"student": "source-name", **{qid: "0" for qid in QUESTION_IDS}}
                )
            (manifest_dir / "student_map.csv").write_text(
                "student_id,student,source_file\n"
                "S008,source-name,submissions/source-name.pdf\n",
                encoding="utf-8",
            )

            code = main(["import-baseline", "--root", str(physics_root)])

            self.assertEqual(code, 0)
            run_dir = physics_root / "benchmark" / "runs" / "G0-all-r1"
            with (run_dir / "predictions.csv").open(
                newline="", encoding="utf-8"
            ) as handle:
                predictions = list(csv.DictReader(handle))
            self.assertEqual(len(predictions), 12)
            self.assertEqual({row["student_id"] for row in predictions}, {"S008"})
            self.assertNotIn(
                "source-name",
                (run_dir / "predictions.csv").read_text(encoding="utf-8"),
            )

    def test_legacy_g1_command_is_inactive(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = root / "manifest"
            manifest.mkdir(parents=True)
            (manifest / "privacy_review.csv").write_text(
                "page,approved,reviewer,reviewed_at\n"
                "S008-p01.jpg,true,teacher,2026-07-02\n",
                encoding="utf-8",
            )
            stderr = io.StringIO()

            with redirect_stderr(stderr):
                code = main(
                    [
                        "run",
                        "--root",
                        str(root),
                        "--condition",
                        "G1",
                        "--split",
                        "dev",
                        "--repetition",
                        "1",
                    ]
                )

            self.assertNotEqual(code, 0)
            self.assertIn("OpenAI API conditions are inactive", stderr.getvalue())

    def test_run_deepseek_requires_environment_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            stderr = io.StringIO()
            with patch.dict(os.environ, {}, clear=True), redirect_stderr(stderr):
                code = main(
                    [
                        "run-deepseek",
                        "--root",
                        tmp,
                        "--condition",
                        "D1",
                        "--split",
                        "dev",
                        "--repetition",
                        "1",
                    ]
                )

            self.assertNotEqual(code, 0)
            self.assertIn("DEEPSEEK_API_KEY is required", stderr.getvalue())

    def test_evaluate_command_writes_split_metrics(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._evaluation_workspace(Path(tmp))

            code = main(["evaluate", "--root", str(root), "--split", "dev"])

            self.assertEqual(code, 0)
            self.assertTrue((root / "metrics-dev.json").exists())

    def test_freeze_command_uses_revised_workflow(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._evaluation_workspace(Path(tmp))

            code = main(
                ["freeze", "--root", str(root), "--candidate", "staged_v1"]
            )

            self.assertEqual(code, 0)
            freeze = json.loads((root / "freeze.json").read_text(encoding="utf-8"))
            self.assertEqual(freeze["gpt_display_model"], "GPT-5.5")
            self.assertEqual(
                freeze["input_policy"], "frozen anonymous transcript workflow"
            )


if __name__ == "__main__":
    unittest.main()
