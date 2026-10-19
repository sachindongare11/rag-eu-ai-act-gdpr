"""Streamlit Community Cloud entrypoint.

Set the app's main file to `cloud/streamlit_app.py`. There is no build step on that platform, so
the first start builds the search index from the PDFs in `data/raw` (about a minute) and keeps it in
memory and in a temporary folder. It is rebuilt whenever the app wakes up from sleep.
"""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

import streamlit as st

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))  # the repo uses a src layout and is not pip-installed

from rag_eu_law.app.bootstrap import ensure_index  # noqa: E402
from rag_eu_law.app.config import Settings  # noqa: E402
from rag_eu_law.app.container import Container  # noqa: E402
from rag_eu_law.app.ui import main  # noqa: E402

WORK_DIR = Path(tempfile.gettempdir()) / "rag-eu-law"
DEFAULTS = {
    "RAG_EMBEDDER": "fastembed",
    "RAG_EMBEDDING_BATCH_SIZE": "2",  # small batches keep peak memory low on a small host
    "RAG_VECTOR_STORE": "memory",  # 1,154 chunks: exact search in memory, no Chroma needed
    "RAG_LLM_PROVIDER": "openai",
    "RAG_RAW_DIR": str(REPO_ROOT / "data" / "raw"),
    "RAG_PROCESSED_DIR": str(WORK_DIR / "processed"),
    "RAG_EMBEDDING_CACHE_DIR": str(WORK_DIR / "models"),
    "RAG_HISTORY_DB_PATH": str(WORK_DIR / "history.sqlite"),
}


def apply_environment() -> None:
    """Copy platform secrets into the environment, then fill in the deployment defaults."""
    try:
        for key, value in st.secrets.items():
            if isinstance(value, str):
                os.environ.setdefault(key, value)
    except FileNotFoundError:  # no secrets configured (local run): rely on the environment
        pass
    for key, value in DEFAULTS.items():
        os.environ.setdefault(key, value)


@st.cache_resource(
    show_spinner="Building the search index. The first start takes about a minute..."
)
def prepared_container() -> Container:
    apply_environment()
    container = Container(Settings(_env_file=None))
    ensure_index(container)
    return container


main(prepared_container)
