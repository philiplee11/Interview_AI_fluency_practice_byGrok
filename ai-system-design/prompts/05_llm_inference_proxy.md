# Design an LLM Inference Proxy / Gateway

## Problem

Design a multi-tenant proxy that sits in front of multiple LLM providers (and internal models) and is used by hundreds of internal products.

**Functional**
- Unified API (OpenAI-compatible or similar).
- Routing by model name, latency class, cost class, or tenant policy.
- Rate limiting, quota, and budget enforcement per tenant.
- Streaming support.
- Fallback and retry across providers.
- Usage logging for billing and abuse detection.

**Non-functional**
- 50k+ requests/sec peak.
- Add < 10 ms overhead on the non-streaming path when healthy.
- Must not amplify cost when a client retries aggressively.
- Observability: latency, error rate, token usage, cost by tenant/model.

## Your task (with AI)

1. Clarify: streaming vs non-streaming SLOs, exactly-once vs at-least-once semantics for billing, provider SLAs.
2. Generate two designs (one more centralized control plane, one more data-plane oriented) and compare.
3. Draft the request path, the quota data model, and how fallback decisions are made.
4. Pressure-test: provider outage, token price change, a single tenant going 100× over quota, prompt injection / abuse.
5. Capacity and cost: proxy fleet size, Redis/DB for quotas, log volume.

Time-box: 50–60 minutes. Emphasize cost control and safety.
