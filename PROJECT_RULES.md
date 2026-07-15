# PROJECT_RULES.md

# Sentinel Fusion AI
## AI-Driven Correlation of Cybersecurity Telemetry & Transactional Behaviour

Version: 1.0

---

# 1. Project Vision

Sentinel Fusion AI is an enterprise-grade cybersecurity intelligence platform designed for the banking ecosystem.

The platform correlates:

- Banking Transactions
- Cybersecurity Telemetry
- Identity Signals
- Threat Intelligence
- Device Telemetry
- Quantum Risk Indicators

to generate explainable, high-confidence security decisions in real time.

This project is being developed for the Bank of Maharashtra Hackathon.

The solution must satisfy every evaluation criterion while remaining production-ready, scalable, secure, modular, and maintainable.

This is NOT a demo dashboard.

This is NOT a simple fraud detection system.

This repository represents a production-ready cyber fusion platform.

---

# 2. Primary Objectives

The application shall:

✓ Correlate cybersecurity telemetry

✓ Correlate banking transactions

✓ Detect cyber threats

✓ Detect fraud

✓ Reduce false positives

✓ Generate explainable AI decisions

✓ Support SOC analysts

✓ Detect quantum security risks

✓ Recommend incident response actions

✓ Scale across banking infrastructure

---

# 3. Development Philosophy

Every implementation must follow these principles:

Production First

Security by Design

Privacy by Design

AI with Explainability

Cloud Native

Modular Architecture

Enterprise Coding Standards

Zero Trust

Maintainability

Scalability

Observability

No shortcuts.

No placeholder implementations.

No fake business logic.

No mock AI where production logic can reasonably be implemented.

---

# 4. Hackathon Success Criteria

The project must maximize the following evaluation criteria.

Business Potential
40%

Security
30%

Innovation
15%

User Experience
5%

Scalability
5%

Maintainability
5%

Every pull request and every generated component shall improve at least one evaluation criterion.

---

# 5. Mandatory Functional Requirements

The system must support:

Transaction ingestion

Cyber telemetry ingestion

Identity event ingestion

Threat intelligence ingestion

Device telemetry

Graph correlation

Dynamic risk scoring

Fraud detection

Cyber anomaly detection

Explainable AI

MITRE ATT&CK mapping

Quantum Risk Monitoring

SOC Dashboard

Incident Investigation

Timeline Reconstruction

AI Recommendations

Audit Logging

Role Based Access Control

Authentication

Authorization

Reporting

Search

Filtering

Notifications

Export

Analytics

---

# 6. Mandatory Non Functional Requirements

High Availability

Horizontal Scalability

Fault Tolerance

Low Latency

Extensible Architecture

Observability

Monitoring

Security

Accessibility

Maintainability

Containerization

API Documentation

Automated Testing

CI/CD Ready

Cloud Ready

---

# 7. Project Architecture Principles

The architecture shall follow:

Clean Architecture

Domain Driven Design

Event Driven Design

SOLID Principles

Repository Pattern

Dependency Injection

Layered Architecture

Hexagonal Architecture where applicable.

Business logic must never depend on UI.

Database logic must never leak into frontend.

AI modules must remain isolated.

---

# 8. Repository Structure

Root

frontend/

backend/

services/

agents/

models/

datasets/

graph/

telemetry/

transactions/

quantum/

correlation/

connectors/

security/

auth/

analytics/

shared/

deployment/

docs/

scripts/

tests/

.github/

docker/

Every directory must contain a README describing its responsibility.

---

# 9. Technology Stack

Frontend

Next.js

React

TypeScript

Tailwind CSS

shadcn/ui

Backend

FastAPI

Python

PostgreSQL

Redis

Neo4j

Kafka Ready

AI

PyTorch

Scikit-learn

XGBoost

Transformers

LLM Integration

Infrastructure

Docker

Docker Compose

Kubernetes Ready

GitHub Actions

---

# 10. Coding Principles

Readable over clever.

Reusable over duplicated.

Typed over dynamic.

Documented over assumed.

Secure over convenient.

Every class shall have a single responsibility.

Every function shall be small.

No function should exceed approximately 60 lines unless justified.

Avoid global mutable state.

---

# 11. AI Development Rules

Every AI decision must be explainable.

Every prediction must include

confidence score

supporting evidence

reasoning

related events

recommended actions

No black-box AI output.

Explainability is mandatory.

---

# 12. Security Rules

Security is mandatory.

Implement

JWT

RBAC

Secure Cookies

HTTPS

Encryption

Secrets Management

Rate Limiting

Input Validation

Output Encoding

Audit Logs

Immutable Logs

Secure Headers

Prompt Injection Protection

Least Privilege

Zero Trust

No sensitive information may be logged.

---

# 13. Quantum Security Rules

The platform must include

Quantum Risk Monitoring

Harvest Now Decrypt Later awareness

Cryptographic inventory

Migration recommendations

PQC readiness indicators

Quantum Risk Score

---

# 14. Graph Intelligence Rules

All incidents must be represented as graph relationships.

Example

User

↓

Device

↓

VPN

↓

Firewall

↓

Transaction

↓

Threat Feed

↓

Incident

Graph relationships must be queryable.

---

# 15. Explainable AI Rules

Every alert must answer

Why?

How?

Evidence?

Confidence?

Business Impact?

Recommended Action?

MITRE Technique?

Without explanations the alert is considered incomplete.

---

# 16. Dashboard Rules

The dashboard shall include

Executive Dashboard

SOC Dashboard

Incident Timeline

Graph View

Risk Score

Attack Chain

MITRE Mapping

AI Explanation

Recommendations

Search

Filters

Dark Mode

Responsive UI

---

# 17. Logging Rules

Structured Logging

JSON Logs

Correlation IDs

Trace IDs

Request IDs

No sensitive data

Log Levels

INFO

WARN

ERROR

SECURITY

AUDIT

---

# 18. Documentation Rules

Every module requires

README

Architecture Diagram

API Documentation

Flow Diagram

Sequence Diagram

Configuration Guide

Deployment Guide

---

# 19. Testing Rules

Every module shall include

Unit Tests

Integration Tests

API Tests

Security Tests

Performance Tests

Edge Case Tests

Regression Tests

---

# 20. Code Review Rules

Generated code shall be reviewed for

Correctness

Security

Performance

Maintainability

Readability

Reusability

Scalability

No unused code.

No dead code.

No duplicated logic.

---

# 21. Performance Goals

Dashboard

<2 seconds

API

<300ms average

AI Inference

<2 seconds

Graph Queries

<500ms

Risk Calculation

Real Time

---

# 22. Accessibility

Keyboard Navigation

ARIA Labels

Responsive Design

WCAG Compliance where practical

Readable typography

Accessible color contrast

---

# 23. Git Rules

Feature branches

Meaningful commits

Semantic commit messages

No direct commits to main.

Every phase should end with a tagged release.

---

# 24. Completion Gates

A feature is complete only if

✓ Code Compiles

✓ Tests Pass

✓ Security Checks Pass

✓ Documentation Updated

✓ APIs Documented

✓ UI Integrated

✓ Logging Added

✓ Error Handling Added

✓ Monitoring Added

✓ Performance Acceptable

✓ No Critical Bugs

---

# 25. Copilot Rules

GitHub Copilot shall

Never remove existing functionality.

Never simplify architecture.

Never replace enterprise patterns with shortcuts.

Never introduce insecure code.

Never generate placeholder implementations unless explicitly requested.

Always preserve modular architecture.

Always follow PROJECT_RULES.md before generating code.

---

# 26. Phase Completion Rule

At the end of every development phase, verify:

Architecture Integrity

Security Compliance

Documentation

Testing

Business Requirements

Evaluation Criteria

If every check passes, output exactly:

-------------------------------------------------

✅ Phase X Completed

All acceptance criteria passed.

Architecture validated.

Security validated.

Documentation updated.

Ready for Phase X+1.

-------------------------------------------------

If any requirement fails, stop implementation and produce:

❌ Phase Validation Failed

Include:

Failed Requirement

Reason

Suggested Fix

Do not continue until every issue is resolved.

---

# 27. Final Completion Rule

The project is considered complete only when

✓ Every phase passes

✓ Every module implemented

✓ Every test passes

✓ Security review passes

✓ AI validation passes

✓ Documentation complete

✓ Deployment works

✓ Docker works

✓ APIs documented

✓ Architecture complete

✓ Hackathon evaluation criteria satisfied

The final output shall be

====================================================

🎉 Sentinel Fusion AI

Submission Ready

Business Potential ✔

Security ✔

Innovation ✔

User Experience ✔

Scalability ✔

Maintainability ✔

All project rules satisfied.

Ready for Bank of Maharashtra Hackathon Submission.

====================================================