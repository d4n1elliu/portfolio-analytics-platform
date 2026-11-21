"""Scoring search and answers against the golden questions. No database is used."""

from datetime import date
from pathlib import Path

import pytest

from ai_fakes import scripted_chat_model
from app.ai.assistant import TokenCount
from app.ai.evals import (
    FOLLOW_UP,
    KEYWORDS,
    QUESTION,
    GoldenQuestion,
    JudgedAnswer,
    judge,
    load_golden_questions,
    of_kind,
    rank_of_expected,
    score_faithfulness,
    score_retrieval,
)
from app.ai.retrieval import RetrievedChunk
from scripts.run_evals import QUESTIONS_FILE
from scripts.seed_research import NOTES_DIR, read_note

GOLDEN = GoldenQuestion("Why did volumes improve?", "BHP", "rail upgrade is finished")


def chunk(ticker: str, text: str) -> RetrievedChunk:
    return RetrievedChunk(1, "A note", ticker, date(2026, 10, 12), 1, text)


def answer(supported: bool, used_tools: bool = True) -> JudgedAnswer:
    return JudgedAnswer("A question", "An answer", used_tools, supported, "A reason")


def test_the_rank_is_the_place_of_the_first_chunk_with_the_phrase():
    chunks = [chunk("BHP", "Costs were flat."), chunk("BHP", "The rail upgrade\nis finished.")]

    assert rank_of_expected(chunks, GOLDEN) == 2


def test_the_phrase_in_a_note_about_another_security_does_not_count():
    assert rank_of_expected([chunk("CBA", "The rail upgrade is finished.")], GOLDEN) is None


def test_hit_rate_and_mrr_are_worked_out_over_every_question():
    score = score_retrieval([1, 2, None, 4])

    assert score.questions == 4
    assert score.hit_rate == 0.75
    assert score.mrr == pytest.approx((1 + 1 / 2 + 1 / 4) / 4)


def test_no_questions_score_zero():
    assert score_retrieval([]).hit_rate == 0.0


@pytest.mark.parametrize(
    ("reply", "supported"),
    [
        ("SUPPORTED\nEvery figure is in the results.", True),
        ("supported\nEvery figure is in the results.", True),
        ("UNSUPPORTED\nThe 9% is not in the results.", False),
        ("I am not sure.", False),
    ],
    ids=["supported", "lower case", "unsupported", "no verdict"],
)
def test_the_judge_reply_is_read_as_a_verdict_and_a_reason(reply, supported):
    tokens_used = TokenCount()

    verdict, reason = judge(scripted_chat_model(reply), "Q", "A", ["results"], tokens_used)

    assert verdict is supported
    assert reason == reply.partition("\n")[2]
    assert (tokens_used.input_tokens, tokens_used.output_tokens) == (10, 5)


def test_an_answer_written_without_tools_counts_against_faithfulness():
    score = score_faithfulness([answer(True), answer(False), answer(False, used_tools=False)])

    assert score.answers == 3
    assert score.without_tools == 1
    assert score.faithfulness == pytest.approx(1 / 3)


def test_every_golden_phrase_is_in_the_sample_note_for_its_ticker():
    notes = {}
    for path in NOTES_DIR.glob("*.md"):
        _, ticker = read_note(path)
        notes[ticker] = path.read_text(encoding="utf-8")

    questions = load_golden_questions(Path(QUESTIONS_FILE))

    assert {golden.kind for golden in questions} == {QUESTION, KEYWORDS, FOLLOW_UP}
    assert all(golden.earlier for golden in of_kind(questions, FOLLOW_UP))
    for golden in questions:
        assert golden.phrase in notes[golden.ticker], golden.question
