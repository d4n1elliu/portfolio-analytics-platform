"""Conversations with the assistant that are stored and carried on, with PostgreSQL behind them."""

import pytest
from langchain.agents import create_agent
from langchain_core.messages import AIMessage, HumanMessage
from sqlalchemy import select

from ai_fakes import scripted_chat_model, streamed_events, tool_call
from app.ai.memory import create_checkpoint_tables, get_checkpointer, stored_messages, thread
from app.ai.providers import get_chat_model
from app.main import app
from app.models import Conversation, Role
from factories import make_security, make_user, sign_in


@pytest.fixture
def signed_in(db, save, client_with_session, assistant_memory, monkeypatch):
    monkeypatch.setattr("app.routes.dependencies.AI_ENABLED", True)
    save(make_security("BHP"))
    users = iter(range(1, 10))

    def client_as(role: Role, *scripted_answers):
        save(make_user(role, user_id=next(users)))
        model = scripted_chat_model(*scripted_answers)
        app.dependency_overrides[get_chat_model] = lambda: model
        client = client_with_session(db)
        sign_in(client, role)
        return client

    return client_as


def ask(client, question: str, conversation_id: str | None = None):
    body = {"question": question, "conversation_id": conversation_id}
    return client.post("/ai/chat", json=body)


def conversation_id_of(response) -> str:
    return streamed_events(response)[0]["id"]


def test_a_first_question_starts_a_conversation_titled_by_it(signed_in):
    client = signed_in(Role.ANALYST, "You hold nothing.")

    started = streamed_events(ask(client, "What do I hold?"))[0]

    listed = client.get("/ai/conversations").json()
    assert [(found["id"], found["title"]) for found in listed] == [
        (started["id"], "What do I hold?")
    ]


def test_a_follow_up_is_answered_with_the_earlier_turns_in_mind(signed_in, assistant_memory):
    client = signed_in(Role.ANALYST, "You hold nothing.", "Still nothing.")
    conversation_id = conversation_id_of(ask(client, "What do I hold?"))

    ask(client, "And now?", conversation_id)

    stored = stored_messages(assistant_memory, conversation_id)
    assert [(type(message), message.text) for message in stored] == [
        (HumanMessage, "What do I hold?"),
        (AIMessage, "You hold nothing."),
        (HumanMessage, "And now?"),
        (AIMessage, "Still nothing."),
    ]
    assert len(client.get("/ai/conversations").json()) == 1


def test_a_stored_conversation_is_read_back_with_its_tools(signed_in):
    client = signed_in(Role.ANALYST, tool_call("list_securities"), "The fund can hold BHP.")
    conversation_id = conversation_id_of(ask(client, "What can I hold?"))

    conversation = client.get(f"/ai/conversations/{conversation_id}").json()

    question, answer = conversation["turns"]
    assert question == {"role": "user", "text": "What can I hold?"}
    assert answer["role"] == "assistant"
    assert [event["type"] for event in answer["events"]] == ["tool_call", "tool_result", "text"]
    assert answer["events"][-1] == {"type": "text", "text": "The fund can hold BHP."}


def test_a_user_cannot_read_carry_on_or_delete_the_conversation_of_another(signed_in):
    owner = signed_in(Role.ANALYST, "You hold nothing.")
    conversation_id = conversation_id_of(ask(owner, "What do I hold?"))
    other = signed_in(Role.OPERATIONS, "This should never be said.")
    not_found = {"detail": "You have no conversation with this id."}

    assert other.get("/ai/conversations").json() == []
    for response in (
        other.get(f"/ai/conversations/{conversation_id}"),
        other.delete(f"/ai/conversations/{conversation_id}"),
        ask(other, "And now?", conversation_id),
    ):
        assert response.status_code == 404
        assert response.json() == not_found


def test_deleting_a_conversation_removes_its_messages_too(signed_in, assistant_memory, db):
    client = signed_in(Role.ANALYST, "You hold nothing.")
    conversation_id = conversation_id_of(ask(client, "What do I hold?"))

    response = client.delete(f"/ai/conversations/{conversation_id}")

    assert response.status_code == 204
    assert db.scalars(select(Conversation)).all() == []
    assert stored_messages(assistant_memory, conversation_id) == []


def test_the_conversation_used_last_is_listed_first(signed_in):
    client = signed_in(Role.ANALYST, "One.", "Two.", "Three.")
    first = conversation_id_of(ask(client, "First conversation"))
    second = conversation_id_of(ask(client, "Second conversation"))

    ask(client, "Back to the first", first)

    assert [found["id"] for found in client.get("/ai/conversations").json()] == [first, second]


def test_messages_are_kept_in_postgres_by_the_real_checkpointer(migrated_engine):
    get_checkpointer.cache_clear()
    create_checkpoint_tables()
    memory = get_checkpointer()
    conversation = "test-" + "0" * 31
    agent = create_agent(scripted_chat_model("Stored for real."), [], checkpointer=memory)
    try:
        agent.invoke(
            {"messages": [{"role": "user", "content": "Is this kept?"}]}, thread(conversation)
        )

        assert [message.text for message in stored_messages(memory, conversation)] == [
            "Is this kept?",
            "Stored for real.",
        ]
    finally:
        memory.delete_thread(conversation)
        get_checkpointer.cache_clear()
    assert stored_messages(memory, conversation) == []


def test_building_the_checkpointer_inside_a_request_never_creates_tables(
    migrated_engine, monkeypatch
):
    def refuse(self):
        raise AssertionError("The tables must be created when the app starts, not in a request.")

    monkeypatch.setattr("langgraph.checkpoint.postgres.PostgresSaver.setup", refuse)
    get_checkpointer.cache_clear()
    try:
        get_checkpointer()
    finally:
        get_checkpointer.cache_clear()
