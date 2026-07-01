import io
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path

from benchmark.physics.cli import main


class CliRunTests(unittest.TestCase):
    def test_run_blocks_unapproved_privacy_csv(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_dir = root / "manifest"
            manifest_dir.mkdir(parents=True)
            (manifest_dir / "privacy_review.csv").write_text(
                "page,approved,reviewer,reviewed_at\nS001-p01.jpg,false,,\n",
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
            self.assertIn("privacy approval missing", stderr.getvalue())

    def test_run_blocks_test_split_before_freeze_marker(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_dir = root / "manifest"
            manifest_dir.mkdir(parents=True)
            (manifest_dir / "privacy_review.csv").write_text(
                "page,approved,reviewer,reviewed_at\nS001-p01.jpg,true,teacher,2026-07-02\n",
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
                        "test",
                        "--repetition",
                        "1",
                    ]
                )

            self.assertNotEqual(code, 0)
            self.assertIn("held-out split is sealed", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
