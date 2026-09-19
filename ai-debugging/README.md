# AI Debugging Practice — "OrderFlow" Legacy Service

A deliberately messy multi-file Python service that processes orders, manages inventory, calculates prices, and runs background workers.

**Goal:** Use AI tools to find and fix real bugs under time pressure, the same way the Google AI-assisted Code Comprehension / AI Debugging round works.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest -q
```

## Known symptoms (start here)

See `docs/KNOWN_ISSUES.md`.

## Architecture (what little there is)

- `src/main.py` — entry point / simple HTTP-ish runner
- `src/models/` — data classes (inconsistent)
- `src/services/` — business logic (order, inventory, pricing, worker)
- `src/core/` — shared state, config, "database"
- `src/utils/` — helpers (some of which are broken)
- `src/legacy/` — old code that is still imported

There is global shared state. There is concurrency. There are incomplete tests. That is intentional.

## Practice rules

1. Time-box 45–60 min.
2. Use AI freely, but you must validate and own every change.
3. Prefer small patches + characterization tests over large rewrites.
4. Keep a short notes.md of your prompts and reasoning if you want interview-style practice.

## Solution

A worked fix for all six issues lives on the [`solution`](../../tree/solution) branch. Try the exercise yourself first — that branch is a spoiler.
