# AI System Design Practice

Practice architecting systems **while actively using AI** to:

- clarify requirements
- generate alternative designs
- draft interfaces and data models
- pressure-test edge cases and failure modes
- produce rough capacity / cost numbers

This mirrors the spirit of Google's evolving system-design expectations and the "AI fluency" signal they now score.

## How to run a session (45–60 min)

1. Pick one prompt from `prompts/`.
2. Open a fresh chat with your AI tool of choice.
3. Follow the **required interaction pattern** below.
4. After the session, score yourself with `rubrics/ai_system_design_rubric.md`.

### Required interaction pattern (forces AI fluency)

- **Clarify first**: Ask the model 3–5 clarifying questions *before* proposing architecture.
- **Alternatives**: Force the model to give you at least two distinct architectures, then critique them yourself.
- **Interfaces**: Have the model draft key APIs / schemas; you edit and own the final version.
- **Numbers**: Ask for capacity estimates (QPS, storage, latency budgets). Validate the arithmetic.
- **Failure modes**: Ask the model for the top failure modes and how the design handles them. Push back on hand-wavy answers.
- **Own the design**: At the end you must be able to redraw the design and defend every major trade-off without looking at the chat.

## Prompts (recommended order)

| # | File | Theme |
|---|------|-------|
| 1 | `01_rate_limiter.md` | Classic distributed systems + correctness under concurrency |
| 2 | `02_notification_service.md` | Multi-channel, reliability, fan-out |
| 3 | `03_rag_document_qa.md` | AI-era system (retrieval, eval, cost) |
| 4 | `04_distributed_cache.md` | Consistency, eviction, stampede |
| 5 | `05_llm_inference_proxy.md` | LLM serving, rate limits, fallbacks, cost |

## Anti-patterns to avoid

- Accepting the first architecture the model proposes.
- Copy-pasting interface code without understanding latency / consistency implications.
- Skipping numbers ("it scales").
- Never asking the model "what did you get wrong?" or "what are the risks?".
