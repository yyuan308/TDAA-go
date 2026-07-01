from .schema import QUESTION_IDS, ScoreRecord


def row_to_score_records(
    row: dict[str, str],
    student_id: str,
) -> list[ScoreRecord]:
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
