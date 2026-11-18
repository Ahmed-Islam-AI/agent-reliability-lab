# Changelog

All notable changes to this project are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Phase N of the build plan is released as version `0.N.0`.

## [Unreleased]

## [0.1.0] - 2026-11-18

Phase 1: Foundation. The evaluation pipeline works end to end for one support task, without any model.

### Added
- `lab` command line: `lab db migrate`, `lab dataset import <folder>`, `lab run-task <task_id> --agent scripted:<script>`.
- PostgreSQL 17.12 via Docker Compose, with separate development and test databases.
- Database schema (migration `0001`): datasets, dataset versions, task versions, agent configs, experiments, runs, attempts, trace events, tool calls, scores. Constraints and indexes are enforced by the database.
- Immutable, content-hashed dataset versions. Re-importing the same content is a no-op; changed content under an existing version is refused.
- Tool gateway: allowlist, strict schema validation, server-side identity, and separate recording of attempted calls and executed effects.
- Crash-safe tracing: every event and tool call is persisted as it happens.
- Separate execution status and evaluation status. Agent crashes become `infrastructure_error`; evaluator crashes become `evaluation_error`.
- Customer-support domain pack: orders, returns, approvals, refunds, a simulated refund reviewer, 4 tools (`get_order`, `get_return_status`, `request_refund_approval`, `issue_refund`) and an outcome evaluator with reason codes.
- Scripted agent with 4 scripts (`correct_refund`, `wrong_amount`, `unapproved_refund`, `false_success`) for model-free testing.
- Support dataset v1 with task `refund_eligible_001`.
- 63 automated tests, including migration-drift and isolation tests against real Postgres.
