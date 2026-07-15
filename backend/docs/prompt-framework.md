# Prompt Framework

The prompt framework provides the enterprise prompt registry, template management, version lifecycle, validation, governance, execution, analytics, and security controls used by Sentinel Fusion AI.

## Key capabilities

- Prompt registry with categories, ownership, labels, tags, and archive state.
- Prompt templates for system, developer, user, context, instruction, JSON, Markdown, XML, YAML, and dynamic prompts.
- Version lifecycle with draft, published, archived, rollback, clone, and restore flows.
- Prompt validation for placeholder integrity, required variables, duplicate or unused variables, maximum length, and content-specific syntax.
- Prompt security for injection detection, sanitization, forbidden keyword enforcement, and secret masking.
- Prompt execution with prompt rendering, variable injection, context injection, streaming support, structured responses, audit logging, and analytics capture.

## Operational model

- Redis caches prompt catalogs, validation results, execution summaries, and analytics snapshots.
- PostgreSQL persists prompts, templates, versions, variables, policies, approvals, audits, executions, and analytics.
- Ollama provides the local inference runtime for prompt execution.
