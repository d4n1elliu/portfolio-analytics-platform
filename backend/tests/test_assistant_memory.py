"""What the assistant sends to the model from a long or cut-off conversation. No database is used."""

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from app.ai.assistant import MAX_MESSAGES_SENT, recent_messages, without_unanswered_tool_calls
from app.ai.conversations import title_from
from app.models.conversation import TITLE_LENGTH


def calling(tool_call_id: str) -> AIMessage:
    return AIMessage(
        content="", tool_calls=[{"name": "list_holdings", "args": {}, "id": tool_call_id}]
    )


def test_a_tool_call_with_its_result_is_kept():
    messages = [HumanMessage("What do I hold?"), calling("a"), ToolMessage("BHP", tool_call_id="a")]

    assert without_unanswered_tool_calls(messages) == messages


def test_a_tool_call_that_was_cut_off_before_its_result_is_left_out():
    question, cut_off, next_question = HumanMessage("One"), calling("a"), HumanMessage("Two")

    assert without_unanswered_tool_calls([question, cut_off, next_question]) == [
        question,
        next_question,
    ]


def test_only_the_most_recent_messages_are_sent_starting_from_a_question():
    turns = [
        message
        for number in range(MAX_MESSAGES_SENT)
        for message in (HumanMessage(f"Question {number}"), AIMessage(f"Answer {number}"))
    ]

    sent = recent_messages(turns)

    assert len(sent) == MAX_MESSAGES_SENT
    assert isinstance(sent[0], HumanMessage)
    assert sent[-1].text == f"Answer {MAX_MESSAGES_SENT - 1}"


def test_a_short_conversation_is_sent_whole():
    turns = [HumanMessage("What do I hold?"), AIMessage("BHP.")]

    assert recent_messages(turns) == turns


def test_a_conversation_is_titled_by_its_first_question_on_one_line():
    assert title_from("  What do\nI hold?  ") == "What do I hold?"


def test_a_long_first_question_is_cut_to_fit_the_title():
    title = title_from("word " * 40)

    assert len(title) == TITLE_LENGTH
    assert title.endswith("…")
