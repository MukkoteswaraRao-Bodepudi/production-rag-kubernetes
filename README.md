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

```

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

# Day 6 — RAG Reranking with Cross-Encoder

## Overview

Day 6 focuses on improving the retrieval quality of the RAG pipeline using Cross-Encoder reranking.

The pipeline first retrieves candidate chunks using Vector Search + BM25 Hybrid Search. A Cross-Encoder then evaluates the query and each retrieved candidate together and assigns a relevance score. The candidates are reordered based on these scores before the most relevant chunks are passed to the LLM for answer generation.

The retrieval pipeline was also revalidated after changing the document chunking configuration from 1000/200 to 700/100.

---

# Objectives

- [x] Implement Cross-Encoder reranking
- [x] Compare relevant and irrelevant candidate chunks
- [x] Evaluate reranking on Kubernetes queries
- [x] Integrate reranking into the RAG pipeline
- [x] Generate answers using reranked context
- [x] Verify generated answers against retrieved context
- [x] Optimize document chunking
- [x] Revalidate retrieval after rechunking
- [x] Evaluate final answers for grounding and unsupported claims

---

# Cross-Encoder Reranking

The current reranker uses:

    from sentence_transformers import CrossEncoder

    reranker = CrossEncoder(
        "cross-encoder/ms-marco-MiniLM-L-6-v2"
    )

The Cross-Encoder is applied after the initial retrieval stage.

Unlike a bi-encoder, which independently encodes the query and documents, the Cross-Encoder evaluates the query and candidate document together and produces a relevance score.

Conceptually:

    Query + Candidate Chunk
              ↓
        Cross-Encoder
              ↓
        Relevance Score
              ↓
          Re-ranking

The highest-scoring candidates are selected as the final context for the LLM.

---

# Reranking Architecture

    User Query
        ↓
    ┌─────────────────────────────┐
    │       Vector Search         │
    └─────────────┬───────────────┘
                  │
                  ├──────────────┐
                  │              │
                  ↓              ↓
          Semantic Results    BM25 Results
                  │              │
                  └──────┬───────┘
                         ↓
                  Hybrid Search
                         ↓
                  Candidate Chunks
                         ↓
                  Cross-Encoder
                         ↓
                    Re-ranking
                         ↓
                      Top-K = 5
                         ↓
                  Context Construction
                         ↓
                        LLM
                         ↓
                   Final Answer
                         ↓
                  Sources / Citations

---

# Why Reranking?

Initial retrieval methods are optimized for efficiently finding potentially relevant documents.

However, the initial top-K results may contain:

- Highly relevant chunks
- Partially relevant chunks
- Chunks containing only keywords
- Semantically related but less useful chunks
- Duplicate or overlapping information

The Cross-Encoder provides an additional relevance-ranking stage before the context is sent to the LLM.

    Initial Retrieval
           ↓
    Broad Candidate Set
           ↓
       Cross-Encoder
           ↓
    More Relevant Ordering
           ↓
       Final Context
           ↓
           LLM

---

# Evaluation Queries

The reranking pipeline was tested using Kubernetes-related queries.

## Primary Queries

1. What is a Kubernetes Deployment?
2. What is a Kubernetes Pod?
3. What is a Kubernetes Service?
4. What is a ReplicaSet?
5. What is a ConfigMap?

## Additional Queries

6. Deployment spec replicas desired state status
7. Pod containers shared network storage node
8. Service clusterIP selector endpoints Pods
9. How does Kubernetes keep the required number of application instances running?
10. How does Kubernetes provide stable access when Pod IP addresses change?
11. How is a Deployment related to a ReplicaSet?
12. How does a ReplicaSet maintain Pods?
13. How can an application consume configuration without putting it inside the container image?
14. What happens when a Pod managed by a Deployment fails?
15. What is the difference between a Pod and a Deployment?

These queries cover both direct concept questions and relationship/detail-oriented questions.

---

# Reranking Evaluation

The reranking stage was evaluated by comparing the relevance of retrieved candidate chunks before and after Cross-Encoder scoring.

The evaluation focuses on whether relevant chunks are promoted and less relevant chunks are moved down in the ranking.

Example:

    Query:
    What is a Kubernetes Deployment?

    Initial Candidates:

    Chunk A → Deployment status
    Chunk B → Pod definition
    Chunk C → Deployment desired state
    Chunk D → Service definition
    Chunk E → ReplicaSet

                 ↓
           Cross-Encoder
                 ↓

    Reranked Candidates:

    Chunk C → Deployment desired state
    Chunk A → Deployment status
    Chunk E → ReplicaSet
    Chunk B → Pod definition
    Chunk D → Service definition

The reranked candidates are then used to construct the final LLM context.

---

# Document Rechunking

Document chunking was also optimized during the retrieval experiments.

## Previous Configuration

    chunk_size = 1000
    chunk_overlap = 200

## Current Configuration

    chunk_size = 700
    chunk_overlap = 100

The 700/100 configuration produces more focused chunks while maintaining overlap between neighboring chunks.

After rechunking, the retrieval pipeline was revalidated using the Kubernetes evaluation queries.

The purpose of this experiment was to determine whether more focused chunks improve the relevance of retrieved context and provide better evidence for downstream reranking and generation.

---

# Final RAG Response Verification

Retrieval quality is not evaluated only through retrieval metrics.

The final generated responses are also checked against the retrieved context.

The evaluation includes:

- Answer correctness
- Retrieved-context support
- Source correctness
- Page-number correctness
- Citation relevance
- Unsupported claims
- Context-to-answer alignment
- Groundedness / faithfulness

The objective is to ensure that the LLM does not introduce information that is unsupported by the retrieved documents.

---

# Example: Grounded Answer

## Question

    What is a Kubernetes Deployment?

## Retrieved Context

    A Deployment is an object that can represent an application
    running on the cluster and specifies the desired number of replicas.

## Generated Answer

    A Kubernetes Deployment is a Kubernetes object that represents
    an application running on the cluster and maintains the desired
    number of application replicas.

## Evaluation

    Answer Correctness:           Supported
    Context Support:              Yes
    Unsupported Claims:           None identified
    Context-to-Answer Alignment:  Good

The generated answer is a concise paraphrase of the retrieved evidence.

---

# Grounding and Hallucination Check

A key part of the evaluation is distinguishing between supported information and unsupported information.

## Supported Information

Information that is explicitly present in the retrieved context.

    Retrieved Context:
    A Deployment specifies the desired number of replicas.

    Answer:
    A Deployment specifies the desired number of replicas.

    Result:
    Supported

## Unsupported Information

Information that may be generally correct but is not supported by the retrieved context.

    Retrieved Context:
    A Deployment specifies the desired number of replicas.

    Answer:
    Deployments support rolling updates and automatic rollback.

    Result:
    Unsupported by the retrieved context

For a strict RAG system, generally correct external knowledge should not automatically be treated as grounded evidence.

---

# Out-of-Context Query Handling

The RAG system was also tested with questions for which the retrieved documents did not contain sufficient information. 

Example:

    Question:
    What is a ConfigMap?

When the provided documents contain only references to ConfigMap but not an actual definition, the system should avoid inventing a definition.

Expected behavior:

    I don't have information based on the Provided Documents.

This behavior is important for evaluating grounded generation and reducing unsupported responses.

---

# Current RAG Pipeline

                    User Query
                        ↓
              ┌──────────────────┐
              │  Vector Search   │
              └────────┬─────────┘
                       │
                       +
              ┌────────▼─────────┐
              │    BM25 Search   │
              └────────┬─────────┘
                       │
                       ↓
                Hybrid Search
                       ↓
               Candidate Chunks
                       ↓
              Cross-Encoder
                       ↓
                  Re-ranking
                       ↓
                  Top-K = 5
                       ↓
             Context Construction
                       ↓
                      LLM
                       ↓
                Final Answer
                       ↓
              Sources / Citations

---

# Evaluation Methodology

The same Kubernetes query set is used throughout the retrieval optimization process to maintain consistency between experiments.

The evaluation is performed at multiple stages.

## 1. Retrieval Evaluation

Determine whether relevant chunks are retrieved in the initial candidate set.

    Query
      ↓
    Vector + BM25
      ↓
    Top-K Candidates
      ↓
    Relevant Chunk Present?

## 2. Reranking Evaluation

Determine whether the Cross-Encoder improves the ordering of relevant candidates.

    Candidate Chunks
          ↓
      Cross-Encoder
          ↓
      Relevance Scores
          ↓
      Reranked Candidates

---

# Reproducibility

RAG experiments can produce different final responses between runs if retrieval candidates, ranking order, or LLM generation are not deterministic.

Therefore, when comparing different RAG configurations, the following should remain unchanged whenever possible:

- Evaluation queries
- Source documents
- Chunking configuration
- Embedding model
- Vector database
- BM25 configuration
- Initial retrieval top_k
- Cross-Encoder model
- Reranking top_k
- LLM model
- Prompt
- Generation parameters

Intermediate retrieval and reranking results should also be recorded.

    Query
      ↓
    Retrieved Chunk IDs
      ↓
    Reranked Chunk IDs
      ↓
    Reranker Scores
      ↓
    Final Context
      ↓
    Generated Answer

This makes it possible to identify whether a change originated from retrieval, reranking, or generation.

---

# Key Takeaways

- Implemented Cross-Encoder reranking using cross-encoder/ms-marco-MiniLM-L-6-v2.
- Integrated Cross-Encoder reranking after Hybrid Search.
- Evaluated reranking using multiple Kubernetes queries.
- Used the reranked Top-5 chunks as LLM context.
- Added final answer verification against retrieved context.
- Rechunked documents from 1000/200 to 700/100.
- Revalidated retrieval after rechunking.
- Added grounding and unsupported-claim checks.
- Tested out-of-context questions to evaluate conservative RAG behavior.
- Established a multi-stage evaluation approach covering retrieval, reranking, and generation.

## Day 7 — Retrieval Evaluation 2: Cross-Encoder Reranking

Day 7 focused on evaluating the impact of Cross-Encoder reranking on the existing Hybrid Search retrieval pipeline.

The goal was to compare:

1. Hybrid Search retrieval
2. Hybrid Search + Cross-Encoder Reranking

The reranker used was:

`cross-encoder/ms-marco-MiniLM-L-6-v2`

### Retrieval Evaluation Pipeline

```text
User Query
    ↓
Hybrid Search
    ↓
Candidate Chunks
    ↓
Cross-Encoder Reranker
    ↓
Top-5 Ranked Chunks
    ↓
Context Construction
    ↓
LLM
    ↓
Final Answer
```


### Day 8 — RAG Application

Day 8 focused on building the complete RAG application by connecting the retrieval, reranking, context construction, LLM generation, and source citation components into an end-to-end pipeline.

#### Objectives

- [x] Build the end-to-end RAG application
- [x] Connect hybrid retrieval with the reranking stage
- [x] Use the reranked top-K chunks as the final retrieval context
- [x] Build context from retrieved documents
- [x] Pass the constructed context to the LLM through a prompt
- [x] Generate answers grounded in the Kubernetes documentation
- [x] Add source metadata and page-level citations
- [x] Test factual and conceptual Kubernetes queries
- [x] Test multi-document questions
- [x] Test relationship-based questions
- [x] Verify generated responses against retrieved sources
- [x] Configure LangSmith tracing for the RAG application

#### RAG Application Architecture

```text
                         User Query
                              │
                              ▼
                    ┌──────────────────┐
                    │ Hybrid Retrieval │
                    │ Vector + BM25    │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │   Reranker       │
                    │ Cross-Encoder     │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │   Top-K Chunks   │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Context Builder  │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │     Prompt       │
                    │ Query + Context  │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │       LLM        │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Final Response   │
                    │ + Citations      │
                    └──────────────────┘

```

# Day 9 — RAG Optimization and Grounded Responses

## Overview

Day 9 focused on improving and testing the complete RAG application.

We already had:

- Hybrid Retrieval
- Cross-Encoder Reranking

In Day 9, we focused on what happens after reranking:

- [x] Building the context
- [x] Passing the context to the LLM
- [x] Creating source-aware prompts
- [x] Generating grounded answers
- [x] Handling unsupported questions
- [x] Checking source citations
- [x] Testing the complete RAG pipeline

The RAG application uses the Kubernetes documentation dataset containing approximately 12,694 chunks.

---

## RAG Pipeline

```text
User Query
    ↓
Hybrid Retrieval
    ↓
Cross-Encoder Reranking
    ↓
Top Relevant Chunks
    ↓
Context Building
    ↓
Source-Aware Prompt
    ↓
LLM
    ↓
Answer + Sources