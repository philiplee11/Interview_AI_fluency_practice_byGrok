# Design a RAG Document Q&A System

## Problem

Design a retrieval-augmented generation system that lets employees ask natural-language questions over a large internal document corpus (wikis, PDFs, tickets, design docs).

**Functional**
- Ingest documents (incremental + batch).
- Answer questions with citations.
- Support filters (team, date, doc type).
- Admin tools for re-indexing and quality evaluation.

**Non-functional**
- Corpus: ~50M documents, growing.
- p95 answer latency < 3 s.
- Cost-aware (LLM tokens are expensive).
- Must have a measurable quality loop (eval set, regression detection).

## Your task (with AI)

1. Clarify: freshness requirements, security / ACL model, expected query types.
2. Force the model to propose at least two retrieval strategies (dense only, hybrid, multi-stage) and critique them.
3. Draft the indexing pipeline, the query path, and the eval harness at a high level.
4. Ask for capacity estimates: embedding cost, vector DB size, QPS, LLM cost per 1k queries.
5. Explicitly discuss failure modes: hallucination, stale index, ACL leaks, embedding model change.

This is an **AI-era** design problem — evaluation and cost are first-class.

Time-box: 50–60 minutes.
