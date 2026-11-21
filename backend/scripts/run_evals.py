"""Score research search, and optionally the assistant's answers, against the golden questions.

Run from the backend/ directory, after scripts.seed_research:
    python -m scripts.run_evals              search only: free, uses the local models
    python -m scripts.run_evals --answers    also asks the chat model, which spends API credit

It only reads from the database.
"""

import argparse
import sys
from pathlib import Path

from app.ai import evals
from app.ai.providers import get_chat_model, get_embeddings, get_reranker
from app.ai.research import list_documents
from app.ai.retrieval import TOP_CHUNKS, SearchOptions
from app.config import AI_CHAT_MODEL
from app.database import SessionLocal

QUESTIONS_FILE = (
    Path(__file__).resolve().parent.parent / "sample_data" / "evals" / "golden_questions.json"
)
KINDS = (evals.QUESTION, evals.KEYWORDS, evals.FOLLOW_UP)
MODEL_CALLS_PER_ANSWER = 3


def main() -> int:
    options = _options()
    questions = evals.load_golden_questions(QUESTIONS_FILE)
    with SessionLocal() as db:
        missing = _tickers_without_research(db, questions)
        if missing:
            print(f"No research is loaded for {', '.join(missing)}. Run scripts.seed_research.")
            return 1
        _report_search(db, questions, options.top)
        if options.answers:
            _report_answers(db, questions, options)
    return 0


def _options() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--top", type=int, default=TOP_CHUNKS, help="chunks fetched per question")
    parser.add_argument("--answers", action="store_true", help="also judge the assistant's answers")
    parser.add_argument("--limit", type=int, default=None, help="judge only the first N questions")
    return parser.parse_args()


def _tickers_without_research(db, questions: list[evals.GoldenQuestion]) -> list[str]:
    loaded = {document.security.ticker for document in list_documents(db)}
    return sorted({golden.ticker for golden in questions} - loaded)


def _search_methods() -> dict[str, SearchOptions]:
    methods = {
        "meaning only": SearchOptions(match_words=False),
        "meaning and words": SearchOptions(),
    }
    reranker = get_reranker()
    if reranker is not None:
        methods["meaning and words, reranked"] = SearchOptions(reranker=reranker)
    return methods


def _report_search(db, questions: list[evals.GoldenQuestion], top: int) -> None:
    print(f"Research search, top {top} chunks: hit rate and MRR")
    print(" " * 30 + "".join(f"{_heading(questions, kind):<22}" for kind in KINDS))
    methods = _search_methods()
    for label, options in methods.items():
        print(f"{label:<30}" + "".join(_cell(db, questions, kind, top, options) for kind in KINDS))
    print("Follow-ups are searched as asked, without the earlier questions.")
    _report_misses(db, questions, top, list(methods.values())[-1])


def _heading(questions: list[evals.GoldenQuestion], kind: str) -> str:
    return f"{kind} ({len(evals.of_kind(questions, kind))})"


def _cell(db, questions, kind: str, top: int, options: SearchOptions) -> str:
    ranks = evals.retrieval_ranks(
        db, get_embeddings(), evals.of_kind(questions, kind), top, options
    )
    return f"{_scores(ranks):<22}"


def _scores(ranks: list[int | None]) -> str:
    score = evals.score_retrieval(ranks)
    return f"{score.hit_rate:>4.0%}  {score.mrr:.3f}"


def _report_misses(db, questions, top: int, options: SearchOptions) -> None:
    ranks = evals.retrieval_ranks(db, get_embeddings(), questions, top, options)
    for golden, rank in zip(questions, ranks):
        if rank != 1:
            found = "not found" if rank is None else f"rank {rank}"
            print(f"  {found:>9}  {golden.ticker}  {golden.question}")


def _report_answers(db, questions: list[evals.GoldenQuestion], options) -> None:
    from langgraph.checkpoint.memory import InMemorySaver

    from app.ai.assistant import Assistant, TokenCount

    tokens_used = TokenCount()
    chat_model = get_chat_model()
    follow_ups = evals.of_kind(questions, evals.FOLLOW_UP)
    asked = evals.of_kind(questions, evals.QUESTION)[: options.limit]
    calls = len(follow_ups) + len(asked) * MODEL_CALLS_PER_ANSWER
    print(f"\nAsking {AI_CHAT_MODEL}, about {calls} model calls")

    search = SearchOptions(reranker=get_reranker())
    rewritten = evals.rewritten(chat_model, follow_ups, tokens_used)
    ranks = evals.retrieval_ranks(db, get_embeddings(), rewritten, options.top, search)
    print(f"  follow-ups, rewritten   {_scores(ranks)}")

    assistant = Assistant(chat_model, get_embeddings, InMemorySaver(), get_reranker)
    answers = [evals.judged_answer(assistant, db, golden.question, tokens_used) for golden in asked]
    score = evals.score_faithfulness(answers)
    print(f"  faithfulness            {score.faithfulness:.1%} of {score.answers} answers")
    print(f"  used no tool            {score.without_tools}")
    print(
        f"  tokens used             {tokens_used.input_tokens} in, {tokens_used.output_tokens} out"
    )
    for answer in answers:
        if not answer.supported:
            print(f"  unsupported  {answer.question}\n               {answer.reason}")


if __name__ == "__main__":
    sys.exit(main())
