"""The golden questions run against stored research, with PostgreSQL behind them and fake models."""

from datetime import date

import pytest
from langgraph.checkpoint.memory import InMemorySaver

from ai_fakes import KeywordEmbeddings, scripted_chat_model, tool_call
from app.ai.assistant import Assistant, TokenCount
from app.ai.evals import GoldenQuestion, judged_answer, retrieval_ranks
from app.ai.retrieval import SearchOptions
from app.models import Role
from factories import add_note, make_security, make_user

EMBEDDINGS = KeywordEmbeddings("plasma", "iron")
PLASMA = GoldenQuestion("How is plasma going?", "CSL", "Plasma collection volumes rose")
IRON = GoldenQuestion("How is iron ore going?", "BHP", "Iron ore shipments rose")
MISSING = GoldenQuestion("How is plasma going?", "CSL", "a phrase no note contains")


@pytest.fixture
def library(db, save):
    uploader = save(make_user(Role.ANALYST))
    notes = [
        ("CSL", "CSL plasma", "Plasma collection volumes rose."),
        ("BHP", "BHP iron ore", "Iron ore shipments rose."),
    ]
    for ticker, title, text in notes:
        security = save(make_security(ticker))
        add_note(db, EMBEDDINGS, security, uploader, title, text, date(2026, 8, 20))


def assistant_saying(*scripted_answers) -> Assistant:
    return Assistant(scripted_chat_model(*scripted_answers), lambda: EMBEDDINGS, InMemorySaver())


def test_each_question_is_ranked_by_where_its_chunk_was_found(db, library):
    ranks = retrieval_ranks(db, EMBEDDINGS, [PLASMA, IRON, MISSING], 2, SearchOptions())

    assert ranks == [1, 1, None]


def test_an_answer_is_judged_against_what_its_tools_returned(db, library):
    assistant = assistant_saying(
        tool_call("search_research", question="plasma"),
        "Plasma collection volumes rose [1].",
        "SUPPORTED\nThe answer repeats the excerpt.",
    )
    tokens_used = TokenCount()

    judged = judged_answer(assistant, db, PLASMA.question, tokens_used)

    assert judged.answer == "Plasma collection volumes rose [1]."
    assert (judged.used_tools, judged.supported) == (True, True)
    assert judged.reason == "The answer repeats the excerpt."
    assert tokens_used.input_tokens == 30


def test_an_answer_written_without_a_tool_is_not_sent_to_the_judge(db, library):
    assistant = assistant_saying("Plasma is going well.", "This should never be said.")

    judged = judged_answer(assistant, db, PLASMA.question, TokenCount())

    assert (judged.used_tools, judged.supported) == (False, False)
    assert judged.reason == "The assistant called no tool."
