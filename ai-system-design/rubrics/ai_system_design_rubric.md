# AI System Design Rubric (self-score)

Score each dimension 1–4. Target ≥ 3 on every dimension for a solid practice session.

## 1. Requirements & Clarification (with AI)
- 1: Jumped straight into boxes
- 2: Asked a couple of questions, still ambiguous
- 3: Clear functional + non-functional requirements after dialogue with AI
- 4: Explicitly prioritized requirements and called out open questions

## 2. Exploration of Alternatives
- 1: Single design, no alternatives
- 2: Mentioned one alternative but dismissed it quickly
- 3: Two or more architectures compared on concrete axes (latency, cost, complexity, consistency)
- 4: Chose one and documented why the others were worse for *this* problem

## 3. Interface & Data Model Quality
- 1: Vague boxes only
- 2: Some APIs / schemas but incomplete
- 3: Clear request/response shapes, key entities, ownership of data
- 4: Interfaces that handle versioning, errors, and pagination / streaming where relevant

## 4. Numbers & Capacity
- 1: No numbers
- 2: Ballpark only, arithmetic not checked
- 3: QPS, storage, latency budgets with rough but correct math
- 4: Sensitivity analysis (what if 10× traffic?) and cost implications

## 5. Failure Modes & Operability
- 1: Happy path only
- 2: Named a few failures without mitigations
- 3: Concrete failure modes + how the design detects and recovers
- 4: Monitoring, SLOs, and back-pressure / degradation strategy

## 6. AI Fluency (how you used the model)
- 1: Treated the model as an oracle; accepted output uncritically
- 2: Some validation, but still copied large chunks blindly
- 3: Targeted prompts, verified numbers and edge cases, owned final design
- 4: Used the model to stress-test *your* ideas; visible course-correction when the model was wrong

**Total / 24**  
Write 3 sentences of self-critique after every session.
