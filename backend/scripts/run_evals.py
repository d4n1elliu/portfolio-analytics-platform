"""Score research search, and optionally the assistant's answers, against the golden questions.

Run from the backend/ directory, after scripts.seed_research:
    python -m scripts.run_evals              search only: free, uses the local embedding model
    python -m scripts.run_evals --answers    also asks the chat model, which spends API credit

It only reads from the database.
"""

import argparse
import sys
from pathlib import Path

from app.ai import evals
from app.ai.providers import get_chat_model, get_embeddings
from app.ai.research import list_documents
from app.ai.retrieval import TOP_CHUNKS
from app.config import AI_CHAT_MODEL
from app.database import SessionLocal

QUESTIONS_FILE = (
    Path(__file__).resolve().parent.parent / "sample_data" / "evals" / "research_questions.json"
)
MODEL_CALLS_PER_ANSWER = 3


def main() -> int:
    options = _options()
    questions = evals.load_golden_questions(QUESTIONS_FILE)
    with SessionLocal() as db:
        missing = _tickers_without_research(db, questions)
        if missing:
            print(f"No research is loaded for {', '.join(missing)}. Run scripts.seed_research.")
            return 1
        _report_retrieval(db, questions, options.top)
        if options.answers:
            _report_faithfulness(db, questions[: options.limit])
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


def _report_retrieval(db, questions: list[evals.GoldenQuestion], top: int) -> None:
    ranks = evals.retrieval_ranks(db, get_embeddings(), questions, top)
    score = evals.score_retrieval(ranks)
    print(f"Research search, top {top} chunks, {score.questions} questions")
    print(f"  hit rate  {score.hit_rate:.1%}")
    print(f"  MRR       {score.mrr:.3f}")
    for golden, rank in zip(questions, ranks):
        if rank != 1:
            found = "not found" if rank is None else f"rank {rank}"
            print(f"  {found:>9}  {golden.ticker}  {golden.question}")


def _report_faithfulness(db, questions: list[evals.GoldenQuestion]) -> None:
    from langgraph.checkpoint.memory import InMemorySaver

    from app.ai.assistant import Assistant, TokenCount

    calls = len(questions) * MODEL_CALLS_PER_ANSWER
    print(f"\nAsking {AI_CHAT_MODEL} {len(questions)} questions, about {calls} model calls")
    assistant = Assistant(get_chat_model(), get_embeddings, InMemorySaver())
    tokens_used = TokenCount()
    answers = [
        evals.judged_answer(assistant, db, golden.question, tokens_used) for golden in questions
    ]
    score = evals.score_faithfulness(answers)
    print(f"  faithfulness   {score.faithfulness:.1%} of {score.answers} answers")
    print(f"  used no tool   {score.without_tools}")
    print(f"  tokens used    {tokens_used.input_tokens} in, {tokens_used.output_tokens} out")
    for answer in answers:
        if not answer.supported:
            print(f"  unsupported  {answer.question}\n               {answer.reason}")


if __name__ == "__main__":
    sys.exit(main())
