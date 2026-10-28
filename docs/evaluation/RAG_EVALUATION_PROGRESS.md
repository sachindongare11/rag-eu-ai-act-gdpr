# RAG evaluation progress tracker

Last updated: 25 October 2026. Owner: Shalaka.

## Current milestone

**Working evaluation baseline completed; full architecture remains in progress.**

Latest verification reported from the Windows project: **328 passed, 10 skipped, 14 warnings; 98% statement coverage.** Coverage measures exercised code, not RAG accuracy. A fresh retrieval comparison passed all implemented checks with exit code 0.

## Status rules

- **Not started:** no implementation or verification evidence yet.
- **In progress:** some work exists, but exit criteria remain unmet.
- **Baseline complete:** the stated initial scope is implemented and checked; broader validation remains.
- **Complete:** all agreed exit criteria for the phase have evidence.
- **Blocked:** progress depends on a named unresolved dependency.

No overall percentage is assigned: tasks differ in effort and several require evidence quality, not merely code completion. A test passing or a script importing does not complete an entire phase.

## Phase dashboard

| Phase | Status | Evidence completed | Remaining exit criteria |
|---|---|---|---|
| 1. Baseline and provenance | In progress | Saved runs; document/chunk hashes; judge model, rubric and input hash captured | Repeatable manifests covering dataset expectations, corpus, settings, prompts and code version; compatibility checks |
| 2. Evaluation dataset | In progress | 26 questions: 20 answerable, 6 out of scope; expected-source labels; 4 robustness cases | Review expected sources and add reference answers/facts; identify corpus version; independent review and broader coverage |
| 3. Ingestion and chunks | Baseline complete | 1,154 structurally valid chunks; 2 PDFs readable; page bounds checked; 3 user-recorded fidelity samples passed | Broader risk-based sampling; article/paragraph assignment and boundary checks; corpus completeness checks; reusable validation commands |
| 4. Retrieval evaluation | Baseline complete | Hit rate, expected-source recall, complete-source coverage, missing sources, timing; fresh aggregate regression comparison passed | Per-question/rank-sensitive comparisons, provenance enforcement, broader dataset and repeatability analysis |
| 5. Answer and citation evaluation | In progress | Citation-match/refusal metrics; LLM judge; 26 assessments; report renderer; human-review workflow; 21 judge-focused tests passed | Reviewed reference-based correctness/completeness; supported-claim sampling; stronger judge calibration; human-review integration into report sections |
| 6. Robustness and security | In progress | 4 single-run user-input smoke cases executed and met expectations in assistant review of displayed outputs | Evidence-absent citation test; retrieved-document injection; repeated runs and broader adversarial coverage |
| 7. Performance and reliability | In progress | Retrieval/generation timing; CLI smoke timing; one fresh retrieval repeat | Define targets; measure warm/cold latency distributions, concurrency, timeouts/retries, cost and repeated generation stability |
| 8. Regression and delivery | In progress | Local aggregate retrieval gate; 16 gate tests; CLI exit codes; reusable report command; runbook; full suite passed | Correct report review placeholders; package remaining snippets; CI workflow; inspect skips/warnings; exercise failure exit codes through CLI |

## Measured baseline — preserve these findings

| Measure | Observed result | Interpretation |
|---|---|---|
| Retrieval hit rate@5 | 100% | At least one expected source found for each answerable question |
| Complete-source retrieval rate@5 | 65% | All expected sources found in 13/20 answerable cases |
| Mean expected-source recall@5 | Approximately 84% | Rounded display value; compare full precision in JSON |
| Expected-source citation match | 80% | Reference matching, not semantic correctness |
| False refusal rate | 10% | 2/20 answerable questions in the recorded full run |
| Out-of-scope refusal accuracy | 100% | 6/6 under the implemented refusal metric |
| Judge assessments | 26 valid | Valid output does not establish accurate judgment |
| Judge claim verdicts | 96 supported, 9 insufficient evidence | Provisional grounding judgments; 105 extracted claims |
| Judge-reported support | 91.4% | Not overall correctness, completeness, or release readiness |
| Structural/source issues | 0 in implemented checks | Does not prove extraction fidelity across the corpus |
| Fidelity samples | 3 recorded passes | Targeted sample only |
| Robustness smoke checks | 4 observed passes | One execution per case; limited coverage |

## Immediate backlog

## Immediate backlog

- [ ] Verify the regenerated report displays each claim’s actual human-review status, decision, and reason. Implementation is complete; final output verification remains.
- [x] Add focused checks for human-review/report integration — 19 report tests passed, including 12 new cases.
- [x] Save a reusable batch judge command with prompt/schema fingerprints and per-record checkpoints — saving, resuming, and changed-input rejection verified.
- [ ] NEXT: package chunk/source validation and robustness execution into reusable scripts; investigate captured CLI output encoding.
- [x] Exercise a deliberately degraded candidate through the regression CLI — all three metric declines detected; exit code 1 verified.
- [ ] Add reviewed reference facts for a small correctness/completeness pilot with explicit scope.
- [ ] Expand calibration to claims marked supported; keep assistant-assisted review distinct from independent human validation.
- [ ] Complete provenance enforcement and add per-question retrieval comparisons. Judge checkpoint provenance protection is implemented; retrieval comparison checks remain.
- [ ] Add evidence-absent citation and retrieved-document injection tests.
- [ ] Define and measure performance/reliability targets.
- [ ] Add CI after the required local commands and dependencies are reproducible.
- [ ] Investigate the 10 skipped tests and 14 warnings; record their disposition.
- [ ] Expand calibration — five supported claims reviewed in an assistant-assisted pilot; broader independent validation remains pending.
- [X] Investigate skips and warnings — latest suite: 370 passed; 10 model-download-gated contract cases classified; 14 unclosed SQLite connection warnings remain under investigation.
- [ ] Complete provenance enforcement — per-question retrieval comparisons are implemented and verified; corpus, retrieval settings, and expected-source compatibility checks remain pending.
- [X] Provenance enforcement and per-question comparisons — compatible version-2 runs passed end-to-end; automated rejection tests for altered manifests and results remain pending.
- [x] Add initial evidence-absent and retrieved-source injection checks — 5 deterministic tests passed; 4 controlled generation cases met expectations in assistant review of one live run. Broader attacks and repeated trials remain pending.
- [ ] Define and measure performance/reliability targets — warmed sequential retrieval baseline measured: 78 attempts, median 55.9 ms, p95 91.8 ms, maximum 114.9 ms; zero execution errors. Targets, generation/end-to-end timing, and concurrent load remain pending.
- [ ] Define and measure performance/reliability targets — retrieval and answer-pipeline baselines measured. Nine answer attempts: median pipeline 3.21 s, maximum 5.34 s; zero errors/refusals. Acceptance targets, concurrent load, timeout behaviour, and cost remain pending.


## Evidence map (paths relative to the Windows project root)

| Evidence | Path |
|---|---|
| Application answers and retrieved context | `eval/runs/judge-input-001/results.json` |
| Judge assessments | `eval/runs/judge-input-001/judge-batch-001.json` |
| Human reviews; authoritative recorded status | `eval/runs/judge-input-001/human-review-001.json` |
| Reusable report output | `eval/runs/judge-input-001/baseline-report-001.md` |
| Chunk structural validation | `eval/runs/chunk-validation-001.json` |
| PDF validation and hashes | `eval/runs/source-validation-001.json` |
| Manual fidelity review | `eval/runs/chunk-fidelity-review-001.md` |
| Robustness responses | `eval/runs/robustness-001/case-*.json` |
| Robustness review summary, if saved | `eval/runs/robustness-001/review-summary-001.json` |
| Fresh retrieval candidate | `eval/runs/retrieval-candidate-001/results.json` |
| Regression comparison | `eval/runs/regression-comparison-001.json` |
| Run instructions | `docs/evaluation/RUNBOOK.md` |

## Open findings and limitations

- The supplied AI Act PDF is the Parliament first-reading document; evaluation findings apply to that corpus, not an asserted current consolidated legal text.
- The answer generator and judge used the same configured model. Judge output remains advisory.
- Two summary-qualification findings need careful adjudication; do not infer their current recorded status without reading the latest human-review JSON.
- The report renderer still contains per-claim pending placeholders even when separate review records are filled.
- Corpus/settings/expected-source compatibility is not yet automatically enforced by the regression gate.
- Aggregate non-decline can hide regressions for individual questions.
- Captured robustness CLI output contains replacement characters; the cause is not established.
- No full load test, comprehensive security assessment, or production assurance claim has been completed.

## Update protocol

At each implementation milestone:

1. State the phase and exact task before starting.
2. Record the code/artifact and verification output after finishing.
3. Update only the affected task and phase status; keep failures and limitations visible.
4. Distinguish implemented, tested, reviewed, and independently validated.
5. Preserve earlier run evidence; use new output paths for new executions.
6. End with: completed this step, current phase status, remaining work, next action.

When continuing a later session, provide the latest local tracker and changed evidence. The assistant cannot automatically read edits on the Windows laptop.

## Milestone log

| Date | Milestone | Evidence/outcome |
|---|---|---|
| 2026-10-25 | Judge, batch runner and report tests | 21 focused tests passed |
| 2026-10-25 | Structural/source baseline | 1,154 chunks; 117 GDPR pages and 459 AI Act pages; no issues in implemented checks |
| 2026-10-25 | Fidelity sample review | User recorded 3 sample passes |
| 2026-10-25 | User-input robustness smoke run | 4 executions completed; displayed responses met stated expectations, with documented coverage limits |
| 2026-10-25 | Regression gate | 16 focused tests passed; self-comparison and fresh candidate comparison exited 0 |
| 2026-10-25 | Full verification and runbook | 328 passed, 10 skipped, 14 warnings; runbook reported saved |
| 2026-10-25 | Progress tracking introduced | This tracker establishes phase status, exit criteria and next task |
| 2026-10-25 | Checkpoint input protection | Changed-input dry run was rejected with exit code 1; existing checkpoints were not reused.
| 2026-10-28 | Warning cleanup verified | Full suite: 372 passed, 10 intentionally gated tests skipped, no warnings; 98% statement coverage. |
| 2026-10-28 | Per-question retrieval gate verified | 18 focused tests passed; saved candidate passed aggregate and per-question checks. Evidence: eval/runs/regression-per-question-001.json|
| 2026-10-28 | Version-2 provenance comparison verified | Logical/configuration compatibility passed; SQLite byte difference recorded diagnostically; all aggregate and per-question checks passed. Evidence: eval/runs/manifested-v2-comparison-001.json |
| 2026-10-28 | Provenance integration verified | Full suite: 412 passed, 10 model-download-gated tests skipped, no warnings; 97% statement coverage. |
| 2026-10-28 | Controlled generation security pilot | Empty-context refusal, unsupported-evidence refusal, clean control, and one injected-source case met expectations. Raw/final responses saved in eval/runs/generation-security-001/. |
| 2026-10-28 | Warm retrieval benchmark | 78 measured retrievals after 26 warm-ups; median 55.9 ms, p95 91.8 ms; zero errors, stable inputs, no observed chunk-ID ordering changes. Evidence: eval/runs/retrieval-performance-001/benchmark.json |
| 2026-10-28 | Answer performance pilot | Nine generation attempts across d01/c03/x05; median pipeline 3.21 s, maximum 5.34 s; zero errors/refusals; stable inputs. Evidence: eval/runs/answer-performance-001/benchmark.json |
| 2026-10-28 | Security/performance integration verified | Full suite: 426 passed, 10 model-download-gated tests skipped; 97% statement coverage. |
