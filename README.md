# Production RAG — Kubernetes Documentation

A production-oriented Retrieval-Augmented Generation (RAG) application built using Kubernetes documentation.

The project is being developed incrementally, with each stage evaluated before moving toward a production deployment.

## Tech Stack

- Python
- uv
- LangChain
- Hugging Face Embeddings
- 1024-dimensional embeddings
- ChromaDB
- Jupyter Notebook
- LLM

## Architecture

Kubernetes Documents
        ↓
Document Ingestion
        ↓
Document Splitting
        ↓
1024D Embeddings
        ↓
Batch Processing
        ↓
ChromaDB
        ↓
Similarity Retrieval
        ↓
Context
        ↓
LLM
        ↓
Generated Answer

## Current Progress

### Day 1 — RAG Baseline

- [x] Load Kubernetes documents
- [x] Document splitting
- [x] Generate 1024-dimensional embeddings
- [x] Batch embedding generation
- [x] Store vectors in ChromaDB
- [x] Similarity search
- [x] Retrieval evaluation
- [x] Recall@5
- [x] Precision@5
- [x] MRR
- [x] Basic RAG generation

## Retrieval Evaluation

| Metric | Score |
|---|---:|
| Recall@5 | 1.00 |
| Precision@5 | 0.73 |
| MRR | 0.90 |

Evaluation queries included:

- What is a Kubernetes Deployment?
- What is a Kubernetes Pod?
- What is a Kubernetes Service?
- What is a ReplicaSet?
- What is a ConfigMap?

## Project Structure

```text
production-rag-kubernetes/
│
├── Notebooks/
│   ├── 01_Document_Ingestion.ipynb
│   ├── 02_Document_Splitting.ipynb
│   ├── 03_Retrieval.ipynb
│   ├── 04_Retrieval_Evaluation.ipynb
│   ├── 05_Retrieval_Metrics.ipynb
│   └── 06_RAG_Generation.ipynb
│
├── kubernetes/
├── vectorstore/
├── .env.example
├── .gitignore
├── .python-version
├── main.py
├── pyproject.toml
├── README.md
└── uv.lock