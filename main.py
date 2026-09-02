"""
main.py
Production FastAPI backend for the Kubernetes RAG application.

Architecture:
    Streamlit
        ↓ HTTP
    FastAPI
        ↓
    final_rag_response.py
        ↓
    Hybrid Retrieval → Cross-Encoder Reranking → Grounded LLM

Run:
    uv run uvicorn main:app --reload
"""

from __future__ import annotations

import logging
import re
import time
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from Notebooks.final_rag_application import final_rag_response


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("kubernetes-rag-api")


# ============================================================
# APP
# ============================================================

app = FastAPI(
    title="Kubernetes Knowledge Intelligence API",
    description="Production API for the Kubernetes RAG system.",
    version="1.0.0",
)

# Development-friendly CORS.
# Restrict allow_origins before public deployment.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# MODELS
# ============================================================

class QueryRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=2,
        max_length=5000,
        description="Question for the Kubernetes knowledge base.",
    )
    mode: str = Field(
        default="Detailed",
        pattern=r"^(Simple|Detailed)$",
    )


class Source(BaseModel):
    document: str
    page: int | str


class QueryMetadata(BaseModel):
    latency_ms: int
    mode: str
    pipeline: str


class QueryResponse(BaseModel):
    question: str
    answer: str
    sources: list[Source]
    metadata: QueryMetadata


# ============================================================
# CONSTANTS
# ============================================================

FALLBACK_ANSWER = (
    "The provided context does not contain enough information "
    "to answer this question."
)


# ============================================================
# RESPONSE NORMALIZATION
# ============================================================

def _coerce_response(raw_response: Any) -> str:
    """Convert LangChain/model output into plain text."""
    if raw_response is None:
        return ""

    if isinstance(raw_response, str):
        return raw_response

    # Defensive support if the RAG function is later changed
    # to return an AIMessage-like object.
    content = getattr(raw_response, "content", None)
    if content is not None:
        if isinstance(content, str):
            return content
        return str(content)

    return str(raw_response)


def clean_answer(raw_response: Any) -> str:
    """
    Return only the user-facing answer.

    The LLM is instructed to return:
        Response: ...
        Sources:
        - document, page N

    This function also protects the UI from <think> blocks.
    """

    text = _coerce_response(raw_response)

    if not text.strip():
        return FALLBACK_ANSWER

    # Remove complete reasoning blocks.
    text = re.sub(
        r"<think>.*?</think>",
        "",
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )

    # Protect against an unmatched opening reasoning tag.
    text = re.sub(
        r"<think>.*$",
        "",
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )

    # Remove model's "Response:" heading.
    text = re.sub(
        r"^\s*Response\s*:\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )

    # Everything after Sources belongs to citation parsing.
    text = re.split(
        r"\n\s*Sources?\s*:\s*",
        text,
        maxsplit=1,
        flags=re.IGNORECASE,
    )[0]

    # Remove accidental markdown source lines if any.
    text = re.sub(
        r"\n\s*[-*]\s*[^,\n]+,\s*page\s+\d+\s*$",
        "",
        text,
        flags=re.IGNORECASE | re.MULTILINE,
    )

    text = re.sub(r"\n{3,}", "\n\n", text).strip()

    return text or FALLBACK_ANSWER


def parse_sources(raw_response: Any) -> list[Source]:
    """
    Parse the source format produced by final_rag_response.py:

        Sources:
        - Concepts.pdf, page 152
        - Reference.pdf, page 33
    """

    text = _coerce_response(raw_response)

    if not text:
        return []

    source_match = re.search(
        r"(?:^|\n)\s*Sources?\s*:\s*(.*)$",
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )

    if not source_match:
        return []

    source_block = source_match.group(1)

    sources: list[Source] = []

    for line in source_block.splitlines():
        line = line.strip()

        if not line:
            continue

        # Supports -, *, or bullet characters.
        line = re.sub(r"^[-*•]\s*", "", line).strip()

        match = re.match(
            r"(.+?),\s*page\s+(\d+)\s*$",
            line,
            flags=re.IGNORECASE,
        )

        if not match:
            continue

        document = match.group(1).strip()
        page = int(match.group(2))

        if document:
            sources.append(
                Source(
                    document=document,
                    page=page,
                )
            )

    # Stable de-duplication by document + page.
    # We intentionally do not deduplicate retrieval chunks by page
    # inside the RAG pipeline.
    unique_sources: list[Source] = []
    seen: set[tuple[str, str]] = set()

    for source in sources:
        key = (
            source.document.casefold(),
            str(source.page),
        )

        if key not in seen:
            seen.add(key)
            unique_sources.append(source)

    return unique_sources


# ============================================================
# RAG SERVICE WRAPPER
# ============================================================

def execute_rag(question: str, mode: str) -> QueryResponse:
    started = time.perf_counter()

    try:
        logger.info(
            "RAG query | mode=%s | question=%s",
            mode,
            question,
        )

        raw_response = final_rag_response(question)

    except Exception as exc:
        logger.exception("RAG execution failed")

        raise HTTPException(
            status_code=500,
            detail=(
                "The RAG pipeline failed while processing the question."
            ),
        ) from exc

    answer = clean_answer(raw_response)
    sources = parse_sources(raw_response)

    # The existing RAG prompt already controls answer quality.
    # Simple mode is a presentation-level reduction and does not
    # modify retrieval or generation.
    if mode == "Simple" and answer != FALLBACK_ANSWER:
        paragraphs = [
            paragraph.strip()
            for paragraph in answer.split("\n\n")
            if paragraph.strip()
        ]

        if len(paragraphs) > 2:
            answer = "\n\n".join(paragraphs[:2])

    latency_ms = round(
        (time.perf_counter() - started) * 1000
    )

    return QueryResponse(
        question=question,
        answer=answer,
        sources=sources,
        metadata=QueryMetadata(
            latency_ms=latency_ms,
            mode=mode,
            pipeline="Hybrid Retrieval → Cross-Encoder → Grounded LLM",
        ),
    )


# ============================================================
# ROOT / HEALTH
# ============================================================

@app.get("/")
def root():
    return {
        "service": "Kubernetes Knowledge Intelligence API",
        "status": "online",
        "version": app.version,
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "Kubernetes Knowledge Intelligence API",
        "version": app.version,
    }


@app.get("/ready")
def ready():
    return {
        "status": "ready",
        "service": "Kubernetes Knowledge Intelligence API",
        "version": app.version,
    }


# ============================================================
# INFORMATION
# ============================================================

@app.get("/api/v1/info")
def info():
    return {
        "name": "Kubernetes Knowledge Intelligence API",
        "version": app.version,
        "pipeline": [
            "BGE-large embeddings",
            "Chroma vector retrieval",
            "BM25 retrieval",
            "Hybrid retrieval",
            "Cross-Encoder reranking",
            "Grounded LLM generation",
        ],
        "endpoints": {
            "health": "/health",
            "ready": "/ready",
            "query": "/api/v1/query",
            "regenerate": "/api/v1/regenerate",
            "suggestions": "/api/v1/suggestions",
        },
    }


@app.get("/api/v1/suggestions")
def suggestions():
    return {
        "suggestions": [
            "What is the default number of replicas for a Deployment?",
            "What is the difference between a Deployment and a ReplicaSet?",
            "How does a Service select the Pods that receive traffic?",
            "What happens when a Pod managed by a ReplicaSet is deleted?",
            "What are maxUnavailable and maxSurge?",
            "How does Kubernetes maintain the desired state?",
        ]
    }


# ============================================================
# QUERY
# ============================================================

@app.post(
    "/api/v1/query",
    response_model=QueryResponse,
)
def query(request: QueryRequest):
    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=422,
            detail="Question cannot be empty.",
        )

    return execute_rag(
        question=question,
        mode=request.mode,
    )


# ============================================================
# REGENERATE
# ============================================================

@app.post(
    "/api/v1/regenerate",
    response_model=QueryResponse,
)
def regenerate(request: QueryRequest):
    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=422,
            detail="Question cannot be empty.",
        )

    logger.info(
        "RAG regeneration | question=%s",
        question,
    )

    return execute_rag(
        question=question,
        mode=request.mode,
    )
