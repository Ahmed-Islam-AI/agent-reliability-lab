# Working history

One entry per working session, newest first: what was done, decisions and their reasons, problems and how they were solved, deviations from the spec. Current status lives in `PROGRESS.md`; user-facing changes in `CHANGELOG.md`.

---

## 2026-11-18 — Phase 1: Foundation

**Done**
- Project skeleton: uv (Python 3.12.12), ruff, mypy with the pydantic plugin, pytest + pytest-asyncio, Typer CLI `lab`.
- Postgres 17.12 in Docker Compose (localhost only) with separate `agentlab` and `agentlab_test` databases.
- 10 tables in Alembic migration `0001` with all constraints and indexes.
- Domain-free platform: contracts, shared models, tool gateway, event recorder with per-event persistence, attempt executor and runner, dataset loader and idempotent importer, registry.
- Support domain pack: 5 records, 4 tools, environment with a simulated reviewer, outcome evaluator, 4 scripted-agent scripts.
- Dataset `support` v1 with one task (`refund_eligible_001`).
- 63 tests (unit + integration on real Postgres), all passing. Ruff, format and mypy clean.
- Walkthrough: `docs/walkthroughs/phase_01.md`.

**Decisions and reasons**
- **Reviewer approves eligible proposals** instead of only the task's exact expected action (Notion's design). With an exact-match reviewer, a wrong-amount refund could never be executed, so the evaluator could never catch one. The reviewer judges eligibility; evaluators judge correctness. Tasks can still force `rejected` or `pending`.
- **The reviewer is a method** (`SupportEnvironment.decide_approval`), not a `ReviewerSimulator` class. It's a one-line rule; a class would add a file and nothing else.
- **`authenticated_user_id`** instead of Notion's `authenticated_customer_id`, so the platform task schema has no support-domain words. Domain-specific settings go under `scenario`.
- **Another customer's order returns the same "not found" as a missing order**, recorded as `denied`. The agent can't probe which ids exist, and the platform still counts it as an unsafe attempt.
- **Every blocked refund is `denied`** (not `error`), because it is an attempted action that policy stopped. This prepares phase 3's "unsafe attempt" vs "executed violation" metrics.
- **Strict JSON-mode argument validation.** `"249900"` or `249900.0` for an integer amount is rejected. Sloppy model output shows up as a schema-validity problem instead of being silently fixed.
- **No `relationship()` in ORM tables.** Explicit joins avoid async lazy-loading errors and keep queries visible.
- **Enums stored as VARCHAR** (non-native), so adding a status later needs no migration.
- **Mutable defaults written as `= []` / `= {}` with `Annotated`** instead of `Field(default_factory=...)`. Pydantic copies them per instance (checked), and the mypy plugin understands this form.
- **Test doubles live in `tests/fakes/`, one class per file**, to keep Ahmed's one-class-per-file rule everywhere, tests included.

**Problems and fixes**
- *psycopg async on Windows*: it refuses Windows' default Proactor event loop. Fixed with `run_async()` (selector loop on Windows) for the CLI and Alembic, and a `pytest_asyncio_loop_factories` hook for tests. A sync test that used an async fixture still hit it, so the migration-drift test was made async.
- *CLI hung when Postgres was down*: there was no connect timeout. Added a 10-second `connect_timeout` to the app engine and the Alembic engine. Now it fails in about 11 s with a one-line message.
- *Model dumps*: trace rows were first built from JSON-mode dumps (UUID and datetime as strings). Changed to Python-mode dumps, since payloads are already JSON-safe.

**Spec deviations** (spec files updated to match)
- `Ticket` record moved to phase 2 (no phase 1 tool uses it).
- `RequiredCall` and `evaluation.required_calls` moved to phase 3 (no phase 1 evaluator reads them).
- Task YAML uses `scenario: {reviewer_decision: ...}` instead of a top-level `reviewer` block.

---

## 2026-11-18 — Spec merge

**Done**
- Merged the original 3-project lab plan and the Notion guide "Build an AI Agent Evaluation Platform" into one spec: root `CLAUDE.md` and `specs/phase_01` to `phase_12`. Source plans are archived in `docs/source_plans/` (renamed so Claude Code no longer loads them as instructions).

**Decisions from Ahmed**
- Domain-agnostic platform with domain packs, plus a full-stack portfolio with a React + Vite + TypeScript frontend.
- IT helpdesk domain pack and HTTP agent adapter as extensions.
- Langfuse dropped. τ²-bench instead of BFCL, starting with option (a): official agent, imported results. Local only.
- Groq free tier now, paid provider later. Cost is estimated from list prices.
- LangGraph over Google ADK: the platform must own every model call for cost and step accounting.
- Shorter core path (phases 1–8). Per-file walkthrough after every phase.
- Smoke runs allowed. Ahmed makes all commits.
- One class per file; `Annotated` schemas; simple code; enterprise-level, production-ready architecture.
- Added `HISTORY.md` and `CHANGELOG.md`.

**Deviations from the source plans**
- Single-use approvals dropped from the default payment service, and partial refunds required, so Study 2 has a real "before". (The balance check alone blocks a duplicate full refund.)
- `search_orders` searches the signed-in customer's own orders by product name, because the access rule makes name search across customers impossible.
- Escalations are environment records created through the gateway, so they're traced and kept in snapshots.
- LLM judge moved to an extension (phase 12).
- Study 3 gained a no-budget diagnostic run and a `single_easy` run with matching flags.
