# Project summary for interviews (personal notes, not part of the public copy)

**One line:** a retrieval-augmented question-answering system over the GDPR and the EU AI Act where
every answer carries verifiable citations (regulation, article, paragraph, PDF page) and the system
refuses when the texts do not support an answer.

## 30-second pitch
Legal text punishes confident guessing, so the design goal was *verifiable* answers, not fluent ones.
I split the regulations by their legal structure instead of fixed windows, search with dense vectors
plus BM25 plus a direct lookup for "Article 22"-style questions, and check every citation the model
writes against the passages it was given. If nothing supports an answer, it says so. I measured it on
a 26-question set, compared a local 7B model with OpenAI's cheapest model, and deployed it for free
with login and run history.

## Numbers (own 26-question set: 20 answerable, 6 out of scope; top-5)
| | local `qwen2.5:7b` | OpenAI `gpt-6-luna` |
|---|---|---|
| Retrieval hit rate@5 | 100% | 100% |
| Citation accuracy | 90% (18/20) | 85% (17/20) |
| Correct refusals | 100% (6/6) | 100% (6/6) |
| False refusals | 5% (1/20) | 5% (1/20) |
| Median latency | 5.4 s | 3.9 s |

Cost estimate for Luna: about $0.0005 per question (estimated from token counts, not measured).
Index: 1,154 chunks (99 + 113 articles, 173 + 180 recitals, 13 annexes), rebuilt identically each run.

## Decisions worth explaining
1. **Chunk by legal structure.** One article, or one numbered paragraph of a long article; recitals and
   annexes separate; definitions split by number so `Art. 4(1)` is citable. Chunk ids are
   deterministic, so re-ingestion is idempotent (verified byte-identical output).
2. **A parser that accepts headings only in numeric order.** A plain regex found 121 "Article" lines in
   the GDPR for 99 real articles, because cross-references start lines too ("Article 290 TFEU should...").
3. **Hybrid search needs a third leg.** Dense and BM25 alone both failed on "What does Article 17
   say?" (the number matches everywhere). I added reference parsing: each named article, recital or
   annex gets its own filtered ranking with a higher weight in rank fusion. An unscoped "Article 22" is
   searched in both laws, since it exists in both.
4. **Citation verification, not trust.** Each citation tag is matched to a retrieved chunk. Wrong
   page numbers are repaired, invented articles removed, and an answer with no surviving citation
   becomes a refusal. This guarantees the cited place exists, **not** that the claim is faithful.
5. **ONNX embeddings for deployment.** Same `bge-small` model through ONNX: cosine 1.0 against the
   PyTorch version, 25 of 26 identical top-5 lists, no PyTorch in the image (1.9 GB image, 492 MB
   install for the cloud app).
6. **Cost and memory on a free host.** Building the index peaked at 2.5 GB with embedding batch 64;
   batch 2 brought it to 593 MB. The cloud entrypoint locks settings that depend on installed
   packages, after a stray `.env` line (`RAG_VECTOR_STORE=chroma`) broke a deployment.
7. **Row-level security.** Supabase: the app holds only the anon key; each user's requests run as
   that user; the team can read and rate all runs, insert only as themselves, and update only
   `rating` and `note` (column grant).

## What went wrong, and what I did
- **Tuning on a small eval set:** I tried scoping a named regulation to reference lookups only. One
  failing question got fixed, two others broke (citation accuracy 90% to 85%, then 80%). I reverted,
  re-ran the original to confirm the numbers were reproducible, and documented the open idea instead
  of fitting a 26-question set.
- **Real-platform surprises on first deploy:** the secrets box needs TOML, not `.env` format; a pasted
  `RAG_VECTOR_STORE=chroma` line overrode a cloud setting; Streamlit hides exception text. The last two
  were fixed in code with tests (locked settings, errors explained on the page); the first is documented.

## Honest limits (say these before they ask)
- The eval set is small and written by me; one run per model; no confidence intervals.
- Citation checking proves the cited location exists, not that the text supports the claim.
- The AI Act file is the European Parliament text of 13 March 2024, not the final Official Journal
  text. Footnotes (mostly OJ references) are dropped.
- A regulation named in a question filters the whole search (eval question x02 fails because of it).
- Not tested: the Anthropic client against the real API, the real cross-encoder reranker, a second
  Supabase user, many concurrent users.

## If asked "what next?"
Larger and independent eval set (with a faithfulness judge, not only citation matching); attribute a
regulation name to the nearest article reference; relevance threshold for refusals; export rated runs
from the history table into new eval questions; test the RLS rules with a second account.

## Likely questions, short answers
- *Why not just fine-tune or prompt a big model?* Answers must be traceable to exact provisions and
  updatable by swapping the PDFs; fine-tuning gives neither.
- *Why BM25 as well as embeddings?* Legal questions name articles and defined terms; keyword match
  handles those, embeddings handle paraphrase. Fusion by rank avoids calibrating scores.
- *How do you know it is not hallucinating?* I do not claim that. I check that citations exist in the
  retrieved text and refuse otherwise; faithfulness of the claim itself is the open gap.
- *Why swap the embedding runtime?* Deployment size; parity was measured, not assumed.
- *Why a local model by default?* Questions can contain client details; local keeps them in-house.
  OpenAI was added for the hosted demo, and the choice is a config switch.
- *How would you scale it?* Move vectors to pgvector, keep BM25 or move to Postgres full-text, add
  caching and a queue in front of the LLM; the interfaces are already swappable.

## About AI assistance
The project was built with an AI coding assistant. Be upfront about it and be ready to explain any
file: the design notes in `docs/DESIGN.md` list every decision with reasons. Do not claim results you
have not seen; the numbers above are from the saved reports in `eval/`.

## Résumé bullets
**Short:** Built a cited RAG assistant for the GDPR and EU AI Act (Python, FastAPI, Streamlit,
Supabase): structure-aware chunking, hybrid dense + BM25 retrieval, citation verification with
refusal. 100% hit rate@5 and 100% correct refusals on a 26-question eval; deployed free with login.

**Long:**
- Parsed regulation PDFs by legal structure (articles, paragraphs, recitals, annexes) into 1,154
  idempotent chunks; a sequence-aware heading parser removed false matches from cross-references.
- Added direct article-reference lookup to hybrid retrieval (dense + BM25 + rank fusion), fixing
  queries such as "Article 17" that neither method found alone.
- Verified every generated citation against retrieved passages and refused when none held;
  compared a local 7B model with OpenAI's cheapest model (90% vs 85% citation accuracy, same retrieval).
- Cut deployment size by switching embeddings to ONNX with identical retrieval (cosine 1.0) and
  reduced index-build memory from 2.5 GB to under 600 MB; deployed on Streamlit Community Cloud with
  Supabase auth, row-level security and run history.
