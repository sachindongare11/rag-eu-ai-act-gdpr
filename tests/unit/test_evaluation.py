from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from rag_eu_law.app.cli import create_app
from rag_eu_law.app.config import Settings
from rag_eu_law.app.container import Container
from rag_eu_law.domain.constants import REFUSAL_MESSAGE
from rag_eu_law.domain.exceptions import EvaluationError, RetrievalError
from rag_eu_law.domain.models import Answer, Citation, Regulation, ScoredChunk, SearchFilter
from rag_eu_law.evaluation.loader import load_questions
from rag_eu_law.evaluation.metrics import summarize
from rag_eu_law.evaluation.models import EvalQuestion, ExpectedSource, QuestionType
from rag_eu_law.evaluation.report import render_markdown, write_report
from rag_eu_law.evaluation.runner import EvalRunner, score_question
from tests.fixtures import SAMPLE_CHUNKS, erasure_chunk

REAL_QUESTIONS = Path("eval/questions.yaml")


def _question(
    qid: str, kind: QuestionType, *expected: ExpectedSource, text: str = "q?"
) -> EvalQuestion:
    return EvalQuestion(id=qid, type=kind, question=text, expected=list(expected))


ERASURE = ExpectedSource(regulation=Regulation.GDPR, article="17")
CONTEXT = [ScoredChunk(chunk=erasure_chunk(), score=1.0)]


def _answer(citations: list[Citation]) -> Answer:
    text = "cited" if citations else REFUSAL_MESSAGE
    return Answer(answer=text, citations=citations, retrieved_chunks=CONTEXT, latency_ms=10.0)


ERASURE_CITATION = Citation(chunk_id="x", regulation=Regulation.GDPR, page=61, article="17")
OTHER_CITATION = Citation(chunk_id="y", regulation=Regulation.GDPR, page=5, article="6")


def test_shipped_question_set_is_valid_and_balanced() -> None:
    questions = load_questions(REAL_QUESTIONS)
    kinds = {q.type for q in questions}
    assert len(questions) >= 20
    assert kinds == set(QuestionType)
    assert sum(not q.answerable for q in questions) >= 5


def test_expected_source_needs_exactly_one_locator() -> None:
    with pytest.raises(ValueError, match="exactly one"):
        ExpectedSource(regulation=Regulation.GDPR)
    with pytest.raises(ValueError, match="exactly one"):
        ExpectedSource(regulation=Regulation.GDPR, article="1", recital="2")
    assert ExpectedSource(regulation=Regulation.GDPR, article=17).article == "17"


def test_question_expected_sources_must_fit_the_type() -> None:
    with pytest.raises(ValueError, match="must not list"):
        _question("o", QuestionType.OUT_OF_SCOPE, ERASURE)
    with pytest.raises(ValueError, match="at least one"):
        _question("d", QuestionType.DIRECT_LOOKUP)


def test_loader_reports_bad_files(tmp_path: Path) -> None:
    with pytest.raises(EvaluationError, match="Cannot read"):
        load_questions(tmp_path / "missing.yaml")
    bad = tmp_path / "bad.yaml"
    bad.write_text("key: value\n")
    with pytest.raises(EvaluationError, match="list of questions"):
        load_questions(bad)
    bad.write_text("- {id: a, type: concept, question: q}\n")
    with pytest.raises(EvaluationError, match="Invalid question"):
        load_questions(bad)
    bad.write_text("- {id: a, type: out_of_scope, question: q}\n")
    with pytest.raises(EvaluationError, match="at least 20"):
        load_questions(bad)


def test_loader_rejects_duplicate_ids(tmp_path: Path) -> None:
    path = tmp_path / "dup.yaml"
    path.write_text("- {id: a, type: out_of_scope, question: q}\n" * 2)
    with pytest.raises(EvaluationError, match="duplicate"):
        load_questions(path)


def test_score_question_hit_and_correct_citation() -> None:
    question = _question("d", QuestionType.DIRECT_LOOKUP, ERASURE)
    result = score_question(question, CONTEXT, _answer([ERASURE_CITATION]))
    assert (result.retrieval_hit, result.citation_correct, result.refused) == (True, True, False)
    assert result.retrieval_recall == 1.0
    assert result.citations == ["[GDPR Art. 17, p. 61]"]


def test_score_question_wrong_citation_and_partial_recall() -> None:
    other = ExpectedSource(regulation=Regulation.AI_ACT, article="5")
    question = _question("x", QuestionType.CROSS_REGULATION, ERASURE, other)
    result = score_question(question, CONTEXT, _answer([OTHER_CITATION]))
    assert result.retrieval_recall == 0.5
    assert result.citation_correct is False


def test_score_question_refusal_and_retrieval_only() -> None:
    oos = _question("o", QuestionType.OUT_OF_SCOPE)
    assert score_question(oos, CONTEXT, _answer([])).refused is True
    retrieval_only = score_question(_question("d", QuestionType.CONCEPT, ERASURE), CONTEXT, None)
    assert retrieval_only.refused is None
    assert retrieval_only.citation_correct is None


class StubRetriever:
    def __init__(self, fail_on: str | None = None) -> None:
        self._fail_on = fail_on

    def retrieve(
        self, query: str, top_k: int, search_filter: SearchFilter | None = None
    ) -> list[ScoredChunk]:
        if query == self._fail_on:
            raise RetrievalError("index broken")
        return CONTEXT


class StubGenerator:
    def generate(self, question: str, context: list[ScoredChunk]) -> Answer:
        cited = "erasure" in question
        return _answer([ERASURE_CITATION] if cited else [])


def _questions() -> list[EvalQuestion]:
    return [
        _question("d1", QuestionType.DIRECT_LOOKUP, ERASURE, text="erasure?"),
        _question("c1", QuestionType.CONCEPT, ERASURE, text="what else?"),
        _question("o1", QuestionType.OUT_OF_SCOPE, text="capital?"),
        _question("o2", QuestionType.OUT_OF_SCOPE, text="erasure of pasta?"),
    ]


def test_runner_and_summary_metrics() -> None:
    results = EvalRunner(StubRetriever(), StubGenerator(), top_k=5).run(_questions())
    summary = summarize(results)
    assert summary.answerable_questions == 2
    assert summary.out_of_scope_questions == 2
    assert summary.retrieval_hit_rate_at_k == 1.0
    assert summary.citation_accuracy == 0.5
    assert summary.false_refusal_rate == 0.5
    assert summary.refusal_accuracy == 0.5
    assert summary.mean_latency_ms == 10.0
    assert summary.by_type["direct_lookup"].retrieval_hit_rate == 1.0


def test_retrieval_only_leaves_answer_metrics_empty() -> None:
    summary = summarize(EvalRunner(StubRetriever(), None, top_k=5).run(_questions()))
    assert summary.retrieval_hit_rate_at_k == 1.0
    assert summary.citation_accuracy is None
    assert summary.refusal_accuracy is None
    assert summary.mean_latency_ms is None


def test_pipeline_errors_are_recorded_not_raised() -> None:
    results = EvalRunner(StubRetriever(fail_on="erasure?"), StubGenerator(), top_k=5).run(
        _questions()
    )
    assert results[0].error == "index broken"
    assert summarize(results).retrieval_hit_rate_at_k == 0.5


def test_report_files_and_failures(tmp_path: Path) -> None:
    results = EvalRunner(StubRetriever(), StubGenerator(), top_k=5).run(_questions())
    summary = summarize(results)
    report = write_report(results, summary, tmp_path / "out", top_k=5)
    text = report.read_text()
    assert "retrieval hit rate@5 | 100%" in text
    assert "## Failures" in text
    payload = json.loads((tmp_path / "out" / "results.json").read_text())
    assert len(payload["results"]) == 4
    assert "n/a" in render_markdown(results[:0], summarize([]), 5)


def test_eval_command_end_to_end(tmp_path: Path) -> None:
    questions = tmp_path / "q.yaml"
    questions.write_text(REAL_QUESTIONS.read_text())
    settings = Settings(
        _env_file=None,
        processed_dir=tmp_path / "processed",
        embedder="hashing",
        vector_store="memory",
    )
    container = Container(settings)
    container.indexing_pipeline.index(SAMPLE_CHUNKS)
    result = CliRunner().invoke(
        create_app(lambda: container),
        [
            "eval",
            "--questions",
            str(questions),
            "--output-dir",
            str(tmp_path / "e"),
            "--retrieval-only",
        ],
    )
    assert result.exit_code == 0, result.output
    assert "retrieval hit rate@5" in result.output
    assert (tmp_path / "e" / "report.md").is_file()
