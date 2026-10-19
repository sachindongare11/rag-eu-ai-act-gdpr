# Deploying the Streamlit app (Setup A: cloud)

What runs: the Streamlit UI in one Docker container. Embeddings are computed in the container with
ONNX `bge-small` (no PyTorch). The answer comes from OpenAI (`gpt-6-luna`). Login and run history use
Supabase. The search index (Chroma + BM25) is built inside the image from the two PDFs.

Status: the image was **built and run locally** (2026-10-19): healthy, sign-in page served, real
questions answered through OpenAI with the index inside the image. It has **not** been deployed to a
host. Sections marked "unverified" use platform commands from memory: check each platform's docs.

Measured locally (Docker Desktop, arm64): image 1.9 GB uncompressed, no PyTorch; the Streamlit
server idles at about 55-90 MB; one full ask (embedding model, Chroma, BM25, OpenAI call) peaked at
about 340 MB in its own process. Expect roughly 400-500 MB for the running app with one user, so a
1 GB instance should do for a small team and 512 MB would be tight. Not measured: several users
asking at once, or a signed-in browser session (it needs a password).

## 0. Before you start
- Supabase project set up as in [CLAUDE.md](CLAUDE.md) (SQL migration run, users created).
- OpenAI key with a monthly spending limit set in the OpenAI dashboard.
- The two PDFs in `data/raw/` (committed to the repo).

## 1. Build and test the image locally
```bash
docker build -t rag-eu-law:setup-a .
docker run --rm -p 8501:8501 --env-file docker.env rag-eu-law:setup-a
```
Open http://localhost:8501. Create `docker.env` with only the variables in section 2 (keep it out of
git, and never copy your whole `.env`: its `RAG_EMBEDDER=sentence-transformers` would override the
image's `fastembed` and the container would fail because PyTorch is not installed). Keys are passed
at run time; they are not inside the image (`.dockerignore` excludes `.env`). Check memory with
`docker stats --no-stream`.

## 2. Environment variables the container needs
| Variable | Value |
|---|---|
| `RAG_LLM_PROVIDER` | `openai` (set in the image) |
| `RAG_OPENAI_API_KEY` | your OpenAI key (secret) |
| `RAG_OPENAI_MODEL` | `gpt-6-luna` (default) |
| `RAG_OPENAI_REASONING_EFFORT` | `low` (default) |
| `RAG_RUN_STORE` | `supabase` |
| `RAG_SUPABASE_URL` | `https://<project>.supabase.co` |
| `RAG_SUPABASE_ANON_KEY` | the anon/publishable key (never the service_role key) |

Already set in the image: `RAG_EMBEDDER=fastembed`, `RAG_EMBEDDING_CACHE_DIR=/opt/models`.
Use the platform's secret store for the two keys.

## 3. Where the PDFs come from
The two PDFs are committed in `data/raw/` (public EU legislation, private repo), so a build from
GitHub (Render and similar) or from your machine (`fly deploy`, `docker build`) has them, and the
Dockerfile builds the index during the image build.
- `gcloud run deploy --source .` follows `.gitignore` unless a `.gcloudignore` exists; the PDFs are
  now un-ignored, so they are uploaded.
- The index (vectors, BM25 file, `chunks.jsonl`) is **not** committed: it is rebuilt from the PDFs
  in about 35 seconds during the build, identically each time, and Chroma's binary files would
  change on every rebuild and bloat the git history. If the PDFs change, rebuild the image.
- Before sharing the repo beyond your team, check the licence terms of each PDF (the GDPR file is a
  third-party web print, the AI Act file is the European Parliament's text).

## 4. Platforms (unverified commands)
Common settings: 1 instance only (or sticky sessions; Streamlit keeps state per session), at least
1 GB RAM (start with 2 GB, then measure), WebSocket support on, container port from `$PORT`
(the entrypoint reads it, default 8501), health check path `/_stcore/health`.

- **Fly.io:** `fly launch` (accept the Dockerfile), `fly secrets set RAG_OPENAI_API_KEY=... RAG_SUPABASE_URL=... RAG_SUPABASE_ANON_KEY=... RAG_RUN_STORE=supabase`, then `fly deploy`. Set `internal_port = 8501` and a 2 GB VM in `fly.toml`.
- **Google Cloud Run:** `gcloud run deploy rag-eu-law --source . --memory 2Gi --max-instances 1 --session-affinity --port 8501 --set-env-vars RAG_RUN_STORE=supabase,RAG_SUPABASE_URL=... --set-secrets RAG_OPENAI_API_KEY=...,RAG_SUPABASE_ANON_KEY=...`. The app has its own login, so the service itself can allow unauthenticated requests.
- **Render:** New Web Service from the GitHub repo, runtime Docker, instance with 2 GB RAM, add the environment variables in the dashboard (mark the keys secret). See section 3 for the PDFs.

## 5. After deploying
1. Open the URL, sign in with a Supabase user, ask a question, rate it.
2. Check the run appears in Supabase (`runs` table) and the History tab.
3. Watch OpenAI usage for a day; adjust the spending limit.
4. Keep the Supabase `service_role` key out of every environment variable of this app.

## Rebuilding the index
Re-run the image build whenever the PDFs change. The index version shown in the sidebar
(a hash of the ingested chunks) changes with it, and each saved run records it.
