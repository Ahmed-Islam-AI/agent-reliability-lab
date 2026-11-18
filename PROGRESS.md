# Progress

Current state only. The coding agent updates this at every phase stop. The full log is in `HISTORY.md`, user-facing changes in `CHANGELOG.md`, and per-file explanations in `docs/walkthroughs/`.

## Current phase

**Phase 1 complete (2026-11-18). Waiting for Ahmed's review before phase 2.**

## Phase checklist

Core path
- [x] Phase 1: foundation (one task, no model) — walkthrough: `docs/walkthroughs/phase_01.md`
- [ ] Ahmed: reviewed phase 1
- [ ] Phase 2: real agent on Groq, smoke run
- [ ] Phase 3: evaluation suite, 50 tasks drafted
- [ ] Ahmed: reviewed `datasets/support/v1`
- [ ] Phase 4: experiment service (API, worker, recovery)
- [ ] Phase 5: comparison, export, React dashboard
- [ ] Ahmed: ran baseline and prompt v1 vs v2
- [ ] Phase 6: Study 1 (loop, step, budget guards, escalation)
- [ ] Ahmed: ran Study 1 before/after
- [ ] Phase 7: Study 2 (duplicate refunds, idempotent payment service)
- [ ] Ahmed: ran Study 2 before/after
- [ ] Phase 8: README, full Docker stack, demo script

Extensions
- [ ] Phase 9: Study 3 (single vs multi-agent)
- [ ] Phase 10: τ²-bench (option a: official agent, imported results)
- [ ] Phase 11: IT helpdesk domain pack + HTTP agent adapter
- [ ] Phase 12: LLM judge and calibration

## What is left before phase 2 can start

- Ahmed reviews phase 1 (walkthrough + commands below) and confirms.
- Ahmed adds `GROQ_API_KEY` to `.env` (copy `.env.example` first). Phase 2 adds the Groq settings to `.env.example`.

## Open questions for Ahmed

- None blocking. Phase 2 will pick two Groq model ids with tool calling from Groq's current list. Say so now if you have preferred models.

## Measured results

<!-- Filled only from results/ via lab readme-tables. Never typed by hand. -->
None yet. Phase 1 makes no model calls.
