# Design a Distributed Rate Limiter

## Problem

Design a rate-limiting service that can be used by many internal microservices at a company the size of Google.

**Functional**
- Support multiple algorithms (at least token bucket and sliding window).
- Per-key limits (user id, API key, IP, etc.).
- Limits can be configured dynamically (e.g. 100 req/min, 10k req/day).
- Synchronous check: `allow(key, cost=1) → {allowed: bool, remaining, reset_at}`.

**Non-functional**
- 1M+ checks per second globally.
- p99 latency < 5 ms for the check path.
- Strong enough consistency that a user cannot significantly exceed their limit under normal conditions (define "significantly").
- Multi-region.

## Your task (with AI)

1. Clarify requirements with the model (burst vs sustained, consistency model, etc.).
2. Ask for 2–3 architecture options (centralized Redis, local + gossip, hybrid, etc.).
3. Pick one and have the model draft the core data structures and the `allow` API.
4. Pressure-test: what happens when a region is partitioned? When Redis is overloaded? When a single key is extremely hot?
5. Produce rough capacity numbers (how many Redis nodes / shards, memory per key, etc.).

Time-box: 45–60 minutes. Own the final design.
