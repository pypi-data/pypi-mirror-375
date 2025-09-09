# Suggestions

Maintain at least two suggestions per section. Move completed items to the `Completed` section and backfill new ideas.

## Core Functionality

  - [ ] S201 - Add circuit breaker for repeated API failures (temporarily suppress outbound attempts after N failures, with cooldown); include unit tests simulating failures.

  - [ ] S202 - Make success-email sending togglable per endpoint and globally via config/env; document behavior and add tests.

  - [ ] S221 - Expose configurable throttle key: allow choosing identity for dedup (e.g., exception type + route + normalized message) via a hook/config to reduce noisy near-duplicates.

## Configuration & Defaults

  - [ ] S204 - Centralize configuration schema/validation with clear error messages and defaults printed by `__repr__`-like helper (no secrets).

  - [ ] S216 - Add runtime diagnostics for effective config (log applied ignore patterns on startup; small CLI to print current defaults without secrets).

## Security

  - [ ] S205 - Mask credentials everywhere: ensure SMTP passwords/API keys are redacted in logs, errors, and config dumps; add regression tests.

  - [ ] S206 - Add CI security checks: secrets scanning (Gitleaks or detect-secrets) and dependency auditing (pip-audit); document local usage and allowlist flow.

## Formatting

  - [ ] S215 - Raise docstring completeness: enforce parameter/returns sections for public APIs (pydocstyle checks); add README examples.

  - [ ] S218 - Add CI job to run `pre-commit` (ruff/black/docformatter) and fail on diffs.

  - [ ] S219 - Add `make format` and `make lint` helpers that run black/ruff/docformatter locally.

## Efficiency/Readability/Docs

  - [ ] S209 - Extract email rendering helpers (subject/body composition, template selection) to reduce duplication; add targeted unit tests.

  - [ ] S210 - Expand README: Flask integration quickstart, troubleshooting matrix, and common patterns for success/error emails.

## New Features

  - [ ] S211 - Jinja-based email templates with preset themes and variables; ship a minimal theme set.

  - [ ] S212 - Webhook adapters (Slack/Teams) with simple interface; allow sending success/error notifications alongside email.

## Tests

  - [ ] S213 - Broaden unit tests: cover ignore patterns, custom templates, success-email flow, and utils/encryption extras.

  - [ ] S214 - Property-based tests for `redact_text` and `obfuscate_sensitive_info` using Hypothesis to catch edge cases.

  - [ ] S222 - Stress-test Flask interception under parallel clients to validate single email per unique error within throttle window.

## Completed

  - [x] (P1) S117 - Fix indentation bug in `send_error_email`: correct try/except nesting to resolve `IndentationError` and restore imports/tests.

  - [x] (P1) S118 - Align Flask error interception and bot handling: return `None` on bot to propagate 500; treat `Werkzeug/*` UA as non-bot; always log to DB on error-email exceptions.

  - [x] (P1) S003 - Redact sensitive data in logs: Ensure emails/logs remove secrets and PII; add unit tests.

  - [x] (P1) S001 - Stabilize error reporting tests: Add unit tests for `init_app` exception interception and backend logging; wire into CI.

  - [x] (P1) S002 - Resilient configuration loading: Validate local fallback for `mail_connection` when server is down; add tests.

  - [x] S071 - Standardize import order and remove unused imports; enable CI lint check.

  - [x] S073 - Add missing type hints and refine return types across public APIs; generate API docs.

  - [x] S083 - Redaction unit tests: Cover PII masking and edge cases across log/email bodies.

  - [x] S114 - High-coverage tests: Added cases for Flask ignore/templates, success-email flow, and utils/encryption.

  - [x] S115 - Coverage script enhancements: per-file breakdown written to badges/coverage_breakdown.txt with stderr capture path.

  - [x] (P1) S101 - Error handler robustness: ensure custom template selection never returns `None`; added consistent fallback responses and regression coverage.

  - [x] S208 - Enforce import sorting and docstring style (via ruff rules/docformatter); add CI lint gate.

  - [x] S203 - Provide sensible default `ignore_url_patterns` (static assets, health checks) with env override and README examples.

  - [x] S217 - Align error emails with actual exceptions: format traceback from the raised exception (not ambient), include exception type/message in email body; add regression test.

  - [x] S207 - Adopt ruff + black in `pyproject.toml` with pre-commit hooks; format codebase consistently.

  - [x] (P1) S220 - Fix duplicate emails under concurrency: make throttling check atomic with a lock; add unit test (`tests/test_throttle_concurrency.py`).

  - [x] (P1) S223 - Flask error propagation: preserve original status codes and avoid 418 conversions. Ignored URLs and non-existent routes no longer send emails but return correct codes (e.g., 404/500). Updated tests to reflect behavior.
