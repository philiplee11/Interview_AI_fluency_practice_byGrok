# Example session notes (Rate Limiter)

*This is a template of the kind of notes you might keep during a timed practice.*

## Clarifying questions I asked the AI
- Burst allowance vs pure sustained rate?
- Do we need strict global correctness or is "rarely exceed by 2×" acceptable?
- Multi-region: active-active or primary + replicas?

## Alternatives the model proposed
1. Centralized Redis cluster + token bucket per key
2. Local token buckets + periodic gossip / reconciliation
3. Hybrid: local for most traffic, Redis for global hard limits

## My choice and why
Hybrid — most keys are not globally hot; local gives latency, Redis gives the hard ceiling for the keys that matter.

## Numbers I validated
- 1M QPS → ~200 Redis nodes if each does 5k QPS of check traffic (I pushed back; model initially said 20 nodes).
- Memory: 100 bytes/key × 100M active keys ≈ 10 GB working set → fits in a small cluster with headroom.

## Failure modes we walked through
- Region partition → local still enforces, global limit temporarily relaxed (documented).
- Hot key → key-specific shard + optional local admission control.

## Self-critique
I accepted the first memory estimate too quickly; forced a recalculation. Still weak on exact Redis command sequence for sliding window.
