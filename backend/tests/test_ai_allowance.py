"""When an AI limit counts as reached. No database is used."""

from app.ai.usage import Allowance


def allowance(requests_used: int = 0, tokens_used: int = 0) -> Allowance:
    return Allowance(requests_used, 20, tokens_used, 200_000)


def test_no_limit_is_reached_below_both():
    assert allowance(requests_used=19, tokens_used=199_999).limit_reached is None


def test_the_request_limit_is_reached_at_the_limit():
    assert allowance(requests_used=20).limit_reached == (
        "You have reached the limit of 20 AI requests an hour."
    )


def test_the_token_limit_is_reached_at_the_cap():
    assert allowance(tokens_used=200_000).limit_reached == (
        "You have reached the limit of 200,000 AI tokens a day."
    )
