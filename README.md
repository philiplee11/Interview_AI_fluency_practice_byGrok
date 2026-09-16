# AI Fluency Practice Repo (Google-style SWE Interview Prep)

Practice repo for the two **AI Fluency** rounds Google is rolling out for SWE hiring:

1. **AI Debugging** — Drop into a messy legacy multi-file codebase. Use AI (Gemini / Claude / Cursor / etc.) to locate, diagnose, and patch complex bugs in real time.
2. **AI System Design** — Architect end-to-end systems while actively using AI to evaluate trade-offs, draft interfaces, and pressure-test edge cases.

This repo is intentionally imperfect. Treat it like an interview environment.

---

## Quick Start

```bash
git clone <this-repo>
cd ai-fluency-practice

# AI Debugging practice
cd ai-debugging
python -m venv .venv && source .venv/bin/activate   # or Windows equivalent
pip install -r requirements.txt
pytest -q                    # many tests currently fail — that's the point
python -m src.main           # run the "service"

# AI System Design practice
cd ../ai-system-design
# open prompts/ and follow the exercise instructions
```

---

## 1. AI Debugging Track

**Location:** `ai-debugging/`

### What you get
- A multi-module Python service that looks like it grew organically over years.
- Mixed styles, incomplete docs, partial tests, global state, concurrency issues, subtle logic bugs, off-by-ones, race conditions, resource leaks, and incorrect edge-case handling.
- A few "known symptoms" in `docs/KNOWN_ISSUES.md` (like a ticket backlog).
- No clean architecture — just enough structure that an AI can be useful if you prompt it well.

### How to practice (mimic the interview)
1. **Read the symptoms first** (`docs/KNOWN_ISSUES.md` and failing tests).
2. **Use AI aggressively** — but you own every change. The AI cannot edit files for you in the real interview; it only suggests.
3. Practice the loop:
   - Targeted prompts that give the model the right context window.
   - Validate every suggestion (run tests, reason about side effects).
   - Prefer small, verifiable patches over big rewrites.
   - Explain your reasoning out loud (or in a notes.md) as if an interviewer is watching.
4. Time-box: 45–60 minutes per session. Goal is diagnosis + 1–2 solid fixes, not a perfect rewrite.

### Suggested practice sessions
| Session | Focus | Starting point |
|---------|-------|----------------|
| 1 | Locate the concurrency bug that loses updates | `KNOWN_ISSUES.md` #1 + `tests/test_order_service.py` |
| 2 | Fix the subtle off-by-one + incorrect caching | Inventory + pricing paths |
| 3 | Resource leak + incorrect cleanup | Background worker |
| 4 | End-to-end: make the full test suite green with minimal changes | Whole repo |

### Rules of engagement (interview realism)
- You may use any AI tool (Gemini, Claude, Cursor, Aider, etc.).
- You must be able to defend every line the AI suggested.
- Prefer characterization tests before aggressive refactors.
- Do not delete the legacy code wholesale — the interview rewards surgical fixes + understanding.

---

## 2. AI System Design Track

**Location:** `ai-system-design/`

### What you get
- Realistic problem statements that mirror modern Google-style system design (including AI-adjacent systems).
- A lightweight rubric focused on **AI-assisted design**: how you use the model to explore trade-offs, generate interface sketches, and pressure-test edge cases.
- Example walkthroughs and anti-patterns.

### How to practice
1. Pick a prompt from `prompts/`.
2. Open a fresh AI chat.
3. Force yourself to:
   - Clarify requirements with the AI.
   - Ask the AI for 2–3 alternative architectures and critique them.
   - Have the AI draft key interfaces / data models, then improve them yourself.
   - Ask the AI to generate failure modes, capacity numbers, and monitoring plans — then validate the numbers.
4. After 45–60 minutes, write a short self-critique against the rubric in `rubrics/`.

### Recommended order
1. `01_rate_limiter.md`
2. `02_notification_service.md`
3. `03_rag_document_qa.md`
4. `04_distributed_cache.md`
5. `05_llm_inference_proxy.md`

---

## Repo Layout

```
ai-fluency-practice/
├── README.md
├── ai-debugging/
│   ├── README.md
│   ├── requirements.txt
│   ├── docs/
│   │   └── KNOWN_ISSUES.md
│   ├── src/
│   │   ├── main.py
│   │   ├── core/
│   │   ├── services/
│   │   ├── models/
│   │   ├── utils/
│   │   └── legacy/
│   ├── tests/
│   └── scripts/
└── ai-system-design/
    ├── README.md
    ├── prompts/
    ├── examples/
    └── rubrics/
```

---

## Tips for AI Fluency (what interviewers actually score)

**Prompting**
- Give the model the *right* context (file paths, failing test output, relevant invariants).
- Prefer "here is the symptom + here is the relevant code" over "fix everything".
- Ask for *explanation first*, then code.

**Validation**
- Never accept a patch you cannot explain.
- Always run the tests (or the specific reproduction) after applying a suggestion.
- Watch for AI hallucinations on concurrency, shared mutable state, and off-by-one errors — these are common failure modes.

**Communication**
- Narrate: "I am asking the model to locate all writers of this shared counter because the symptom is lost updates."
- When the model is wrong, say so and course-correct visibly.

Good luck. Ship the fix, not the rewrite.
