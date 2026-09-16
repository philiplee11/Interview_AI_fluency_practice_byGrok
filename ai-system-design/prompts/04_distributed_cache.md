# Design a Distributed Cache

## Problem

Design a distributed in-memory cache that many Google-scale services can use as a shared layer (think Memcached / Redis at large scale, but you own the design).

**Functional**
- `get`, `set`, `delete`, optional TTL.
- Optional "get or compute" with single-flight.
- Basic stats (hit rate, eviction count).

**Non-functional**
- 10M+ ops/sec aggregate.
- p99 get < 1 ms in-region.
- Support for multi-tenant isolation (noisy neighbor).
- Eviction policy configurable per tenant (LRU, LFU, TTL).

## Your task (with AI)

1. Clarify consistency vs availability, replication factor, data size distribution.
2. Ask for architectures (consistent hashing + local caches, centralized, hybrid).
3. Focus on: cache stampede, hot keys, thundering herd after eviction, memory accounting.
4. Have the model draft the client library contract and the server-side eviction / admission logic.
5. Numbers: memory per node, number of nodes, network bandwidth under peak.

Time-box: 45–60 minutes.
