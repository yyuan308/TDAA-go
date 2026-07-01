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

    def test_initialize_refuses_to_overwrite_gold_scores(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            initialize_workspace(root, ["S001"])

            with self.assertRaisesRegex(FileExistsError, "refusing to overwrite"):
                initialize_workspace(root, ["S001"])


if __name__ == "__main__":
    unittest.main()
