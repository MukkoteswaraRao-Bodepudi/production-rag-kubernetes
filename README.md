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
```

### Day 2 — RAG Citations

- [x] Added source metadata to retrieved context
- [x] Added PDF filename and page number
- [x] Added programmatic source extraction
- [x] Prevented duplicate sources
- [x] Tested citation output

Example:

Question:
What is a Kubernetes Deployment?

Answer:
A Kubernetes Deployment is a Kubernetes object that represents
an application running on a cluster...

Sources:
- Tutorials.pdf — Page 9
- Concepts.pdf — Page 5


### Day 3 — RAG Evaluation

- [x] Created RAG evaluation prompt
- [x] Evaluated Faithfulness
- [x] Evaluated Answer Relevance
- [x] Evaluated Context Relevance
- [x] Tested 5 Kubernetes queries
- [x] Calculated average evaluation scores

| Metric | Average Score |
|---|---:|
| Faithfulness | 1.00 |
| Answer Relevance | 1.00 |
| Context Relevance | 1.00 |


### Day 4 — LangSmith

- [x] Configured LangSmith tracing
- [x] Connected LangSmith to the existing RAG pipeline
- [x] Traced RAG execution
- [x] Traced document retrieval
- [x] Traced LLM execution
- [x] Tested multiple Kubernetes queries
- [x] Verified traces for Deployment, Pod, Service, ReplicaSet, and ConfigMap
- [x] Inspected RAG execution in LangSmith



### Day 5 — BM25 Retrieval

- [x] Implemented BM25 lexical retrieval
- [x] Used existing document chunks for BM25 indexing
- [x] Tested exact keyword/lexical matching
- [x] Compared BM25 retrieval with vector retrieval
- [x] Evaluated BM25 retrieval using Recall@5
- [x] Evaluated BM25 retrieval using Precision@5
- [x] Evaluated BM25 retrieval using MRR

BM25 provides lexical/keyword-based retrieval and complements
semantic vector retrieval.

---

### Day 5 — Hybrid Search

Hybrid Search combines semantic vector retrieval with BM25 lexical retrieval.


#### Hybrid Search Architecture

```text
                         ┌───────────────┐
                         │  User Query   │
                         └───────┬───────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
                    ▼                         ▼
           ┌────────────────┐        ┌────────────────┐
           │ Vector Search  │        │  BM25 Search   │
           │   Semantic     │        │    Keyword     │
           └───────┬────────┘        └───────┬────────┘
                   │                         │
                   │                         │
                   └───────────┬─────────────┘
                               ▼
                    ┌────────────────────┐
                    │  Hybrid Ranking    │
                    │                    │
                    │ Vector = 0.8       │
                    │ BM25   = 0.2       │
                    └──────────┬─────────┘
                               │
                               ▼
                    ┌────────────────────┐
                    │    Top-K Chunks    │
                    └──────────┬─────────┘
                               │
                               ▼
                    ┌────────────────────┐
                    │      Context       │
                    └──────────┬─────────┘
                               │
                               ▼
                    ┌────────────────────┐
                    │        LLM         │
                    └──────────┬─────────┘
                               │
                               ▼
                    ┌────────────────────┐
                    │ Answer + Citations │
                    └────────────────────┘

```text

#### Hybrid Search Configuration

- Vector Search Weight: 0.8
- BM25 Weight: 0.2

#### Hybrid Retrieval Evaluation

| Query | Recall@5 | Precision@5 | MRR |
|---|---:|---:|---:|
| Deployment | 1.00 | 0.40 | 0.50 |
| Pod | 1.00 | 0.20 | 1.00 |
| Service | 1.00 | 0.40 | 1.00 |
| ReplicaSet | 1.00 | 0.60 | 1.00 |
| ConfigMap | 1.00 | 0.60 | 1.00 |
| **Average** | **1.00** | **0.44** | **0.90** |

#### Final Response Verification

Retrieval metrics were not used as the only evaluation criteria.

The final RAG responses were manually verified for:

- [x] Answer correctness
- [x] Retrieved context support
- [x] Source correctness
- [x] Page-number correctness
- [x] Citation relevance
- [x] Unsupported claims

The five test queries produced relevant final answers with verified source citations.

---

## Current Retrieval Pipeline

The current pipeline combines semantic and lexical retrieval:

Query
    ↓
Vector Search
    +
BM25 Search
    ↓
Hybrid Search
    ↓
Top-K Relevant Chunks
    ↓
Context Construction
    ↓
LLM
    ↓
Final Answer
    ↓
Sources / Citations

---

## Evaluation Methodology

The same five Kubernetes queries are used to evaluate the retrieval pipeline:

1. What is a Kubernetes Deployment?
2. What is a Kubernetes Pod?
3. What is a Kubernetes Service?
4. What is a ReplicaSet?
5. What is a ConfigMap?

### Retrieval Metrics

**Recall@5**

Measures whether the relevant pages are retrieved within the top 5 results.

**Precision@5**

Measures how many of the retrieved top-5 results are relevant.

**MRR**

Mean Reciprocal Rank measures the position of the first relevant result in the retrieved ranking.

