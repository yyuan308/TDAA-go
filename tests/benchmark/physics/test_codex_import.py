import json
import tempfile
import unittest
from pathlib import Path

from benchmark.physics.codex_import import (
    import_codex_packet,
    parse_transcript_output,
)
from benchmark.physics.schema import QUESTION_IDS


class CodexImportTests(unittest.TestCase):
    def _payload(self, student_id: str = "S008") -> dict:
        return {
            "student_id": student_id,
            "answers": [
                {
                    "question_id": question_id,
                    "text": f"visible answer for {question_id}",
                    "unclear": False,
                }
                for question_id in QUESTION_IDS
            ],
        }

    def _packet(self, root: Path, payload: dict | None = None) -> Path:
        packet = root / "packet"
        (packet / "outputs").mkdir(parents=True)
        (packet / "manifest.json").write_text(
            json.dumps(
                {
                    "run_id": "T1-dev-r1",
                    "condition": "T1",
                    "split": "dev",
                    "repetition": 1,
                    "provider": "codex-plus-interactive",
                    "display_model": "GPT-5.5",
                    "student_ids": ["S008"],
                    "prompt_hash": "prompt-hash",
                    "rubric_hash": None,
                    "input_hashes": {"S008": "input-hash"},
                }
            ),
            encoding="utf-8",
        )
        if payload is not None:
            (packet / "outputs" / "S008.json").write_text(
                json.dumps(payload), encoding="utf-8"
            )
        return packet

    def test_imports_complete_t1_packet(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            benchmark_root = root / "benchmark"
            packet = self._packet(root, self._payload())

            run_dir = import_codex_packet(packet, benchmark_root)

            self.assertEqual(run_dir.name, "T1-dev-r1")
            frozen = (
                benchmark_root
                / "transcripts"
                / "automatic"
                / "T1-dev-r1"
                / "S008.json"
            )
            self.assertTrue(frozen.exists())
            rows = (run_dir / "transcripts.jsonl").read_text(
                encoding="utf-8"
            ).splitlines()
            self.assertEqual(len(rows), 12)
            normalized = [json.loads(row) for row in rows]
            self.assertEqual(
                {row["question_id"] for row in normalized}, set(QUESTION_IDS)
            )
            manifest = json.loads(
                (run_dir / "manifest.json").read_text(encoding="utf-8")
            )
            self.assertEqual(manifest["provider"], "codex-plus-interactive")
            self.assertIsNotNone(manifest["end_time"])

    def test_rejects_incomplete_or_duplicate_transcript(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "S008.json"
            payload = self._payload()
            payload["answers"].pop()
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "exactly 12"):
                parse_transcript_output(path, "S008")

            payload = self._payload()
            payload["answers"][-1]["question_id"] = "Q1a"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "exactly once"):
                parse_transcript_output(path, "S008")

    def test_rejects_wrong_student_and_malformed_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "S008.json"
            path.write_text(json.dumps(self._payload("S009")), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "student_id does not match"):
                parse_transcript_output(path, "S008")

            path.write_text("{not-json", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "invalid transcript JSON"):
                parse_transcript_output(path, "S008")

    def test_unclear_answer_requires_marker(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "S008.json"
            payload = self._payload()
            payload["answers"][0]["unclear"] = True
            path.write_text(json.dumps(payload), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, r"\[UNCLEAR\]"):
                parse_transcript_output(path, "S008")

    def test_import_requires_exact_packet_students_before_creating_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            benchmark_root = root / "benchmark"
            packet = self._packet(root, self._payload())
            (packet / "outputs" / "S009.json").write_text(
                json.dumps(self._payload("S009")), encoding="utf-8"
            )

            with self.assertRaisesRegex(ValueError, "do not match packet"):
                import_codex_packet(packet, benchmark_root)

            self.assertFalse((benchmark_root / "runs" / "T1-dev-r1").exists())


if __name__ == "__main__":
    unittest.main()
