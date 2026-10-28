# RAG Evaluation Runbook

## Purpose

Evaluate the existing application without changing its behaviour or
expected sources to improve evaluation scores.

## Verified baseline

- Full suite: 328 passed, 10 skipped, 14 warnings.
- Statement coverage: 98%; this is not answer accuracy.
- Evaluation dataset: 26 questions, including 6 out-of-scope questions.
- Retrieval hit rate@5: 100%.
- Complete-source retrieval rate@5: 65%.
- Mean expected-source recall@5: approximately 84%.
- Expected-source citation match: 80%.
- False refusal rate: 10%.
- Out-of-scope refusal accuracy: 100%.
- Judge: 26 valid assessments; 96 supported and 9 insufficient-evidence claims.
- Judge-reported claim support: 91.4%; provisional, not overall correctness.
- Chunk structural checks: 1,154 records, no reported issues.
- Source readability and page-bound checks: no reported issues.
- Human-recorded chunk fidelity samples: 3 passed.
- User-input robustness smoke cases: 4 met their stated expectations
  in assistant review of displayed outputs.
- Fresh retrieval comparison: no aggregate regression detected.

## Run the software tests

From the project root in PowerShell:

```powershell
.\.venv\Scripts\python.exe -m pytest -q -x --tb=short
```

## Run retrieval evaluation

Use a new output directory for each execution.

```powershell
.\.venv\Scripts\rag-eu-law.exe eval `
    --retrieval-only `
    --output-dir eval/runs/retrieval-candidate-002
```

No answer-model or judge requests are made. The embedding library may
contact Hugging Face.

## Compare retrieval with the baseline

Keep question expectations, corpus, top-k, and retrieval settings unchanged.

```powershell
.\.venv\Scripts\python.exe .\scripts\check_retrieval_regression.py `
    --baseline .\eval\runs\judge-input-001\results.json `
    --candidate .\eval\runs\retrieval-candidate-002\results.json `
    --output .\eval\runs\regression-comparison-002.json

$LASTEXITCODE
```

Exit codes:
- 0: no measured aggregate regression.
- 1: regression or failed comparison check.
- 2: invalid input or command error.

The gate checks question identity, application errors, measurement
availability, hit rate, complete-source rate, and mean source recall.
It does not automatically verify corpus, settings, or expected-source
provenance. Aggregate improvements can also hide individual regressions.

## Rebuild the saved evaluation report

This makes no model requests.

```powershell
.\.venv\Scripts\python.exe .\scripts\build_evaluation_report.py `
    --run-dir .\eval\runs\judge-input-001 `
    --output .\eval\runs\judge-input-001\baseline-report-002.md
```

Existing output files are preserved; choose a new filename for another report.

## Evidence locations

- Application answers and captured chunks:
  eval/runs/judge-input-001/results.json
- Batch judge assessments:
  eval/runs/judge-input-001/judge-batch-001.json
- Human-review records:
  eval/runs/judge-input-001/human-review-001.json
- Chunk structural validation:
  eval/runs/chunk-validation-001.json
- PDF source validation:
  eval/runs/source-validation-001.json
- Manual chunk fidelity review:
  eval/runs/chunk-fidelity-review-001.md
- Robustness responses:
  eval/runs/robustness-001/case-*.json
- Retrieval regression comparison:
  eval/runs/regression-comparison-001.json

## Interpretation and limitations

- The same configured model generated and judged the baseline answers.
- Judge calibration is limited; scores remain advisory.
- Human review of flagged claims alone cannot establish judge accuracy.
- Citation matching does not establish semantic support.
- Standard refusal wording and omitted qualifications require separate review.
- Individual claim sections in the report still show pending placeholders;
  the human-review JSON is authoritative for recorded review status.
- Robustness testing used one execution per case.
- The citation-fabrication case did not exercise absent retrieved evidence.
- Replacement characters appeared in captured CLI output.
- Three fidelity samples do not establish corpus-wide extraction accuracy.
- The AI Act PDF is the Parliament first-reading document, not the final
  Official Journal text. Findings apply to the supplied corpus.
- Skipped tests and warnings have not been fully investigated.
- Several collection and validation workflows remain terminal snippets.

## Follow-up work

- Reviewed reference answers for correctness and completeness.
- Broader and independent judge calibration.
- Retrieved-document prompt injection and evidence-absent citation tests.
- Repeated-run, load, and cost measurements.
- Complete provenance checks and per-question regression detection.
- Reusable commands for remaining workflows.
- Human-review integration into individual report sections.
- CI integration; the local regression command is not yet a CI workflow.