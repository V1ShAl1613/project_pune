# COPILOT_INSTRUCTIONS.md

# GitHub Copilot Repository Instructions

## Project Name

Sentinel Fusion AI

AI-Driven Correlation of Cybersecurity Telemetry & Transactional Behaviour

---

# Purpose

You are the primary AI software engineer responsible for building an enterprise-grade banking cybersecurity platform.

Every code generation, refactoring, documentation update, architecture suggestion, and implementation must strictly follow this document together with:

- PROJECT_RULES.md
- SYSTEM_ARCHITECTURE.md
- CODING_STANDARDS.md
- SECURITY_GUIDELINES.md
- AI_MODEL_REQUIREMENTS.md
- HACKATHON_COMPLIANCE_CHECKLIST.md

These documents are considered mandatory engineering specifications.

Never violate them.

---

# Primary Objective

Build a production-ready AI-powered Cyber Fusion Platform that:

- Correlates banking transactions
- Correlates cybersecurity telemetry
- Detects fraud
- Detects cyber attacks
- Detects insider threats
- Detects quantum security risks
- Produces explainable AI decisions
- Supports SOC analysts
- Is deployment ready
- Maximizes the Bank of Maharashtra Hackathon evaluation criteria

This is NOT a prototype.

This is NOT a CRUD application.

This is NOT a chatbot.

This is an enterprise banking security platform.

---

# General Development Rules

Always prioritize:

1. Security
2. Correctness
3. Maintainability
4. Scalability
5. Modularity
6. Readability
7. Performance
8. Explainability

Never optimize for writing less code.

Optimize for writing better software.

---

# Repository Context

Always understand the complete repository before generating code.

Before creating new code:

- Inspect existing architecture
- Reuse existing components
- Reuse interfaces
- Reuse models
- Avoid duplication

Never generate isolated code.

Everything must integrate into the current architecture.

---

# Architecture Rules

Follow:

- Clean Architecture
- Domain Driven Design
- SOLID Principles
- Repository Pattern
- Dependency Injection
- Event Driven Architecture
- Modular Services

Never place business logic inside:

- UI
- Controllers
- API Routes
- Database Models

Business logic belongs inside services.

---

# Coding Style

Generate code that is:

Readable

Consistent

Well documented

Reusable

Strongly typed

Modular

Testable

Never generate:

Large monolithic files

Deeply nested logic

Duplicated implementations

Unused functions

Unused imports

Magic numbers

Hardcoded secrets

---

# Language Rules

Frontend

- TypeScript only
- Strict Mode enabled
- Functional Components
- React Hooks
- No class components

Backend

- Python
- Async FastAPI
- Type hints everywhere
- Pydantic models
- Dependency Injection

Database

- SQLAlchemy
- Alembic
- Neo4j Driver

---

# Naming Conventions

Variables

camelCase

Functions

camelCase

Classes

PascalCase

Interfaces

PascalCase

Enums

PascalCase

Files

kebab-case

Folders

lowercase

Constants

UPPER_CASE

Database Tables

snake_case

Columns

snake_case

---

# File Size Rules

Functions

Maximum 60 lines

Classes

Maximum 300 lines

Files

Maximum 500 lines

If exceeded:

Refactor automatically.

---

# Comments

Write meaningful comments.

Explain:

Why

Not

What

Avoid unnecessary comments.

Public methods must contain documentation.

Complex algorithms require explanation.

---

# Error Handling

Every operation must include:

Input validation

Exception handling

Meaningful error messages

Logging

Recovery where appropriate

Never swallow exceptions.

Never ignore failures.

---

# Logging Rules

Use structured logging.

Every log must include:

Timestamp

Correlation ID

Request ID

Service Name

Severity

Never log:

Passwords

Tokens

Secrets

Personally Identifiable Information

Bank Account Numbers

OTP

Private Keys

---

# Security Rules

Security takes priority over convenience.

Always implement:

JWT Authentication

RBAC

Least Privilege

Secure Cookies

HTTPS Ready

Input Validation

Output Encoding

Rate Limiting

CSRF Protection

CORS

Prompt Injection Protection

Secrets Management

Immutable Audit Logs

Secure Headers

Dependency Validation

Never:

Disable authentication

Bypass authorization

Hardcode credentials

Store secrets in source code

Use insecure cryptography

---

# AI Rules

Every AI output must include:

Prediction

Confidence Score

Evidence

Reasoning

Business Impact

MITRE Mapping

Recommended Action

Every AI prediction must be explainable.

Never generate black-box predictions.

---

# Quantum Rules

Support:

Quantum Risk Score

Harvest Now Decrypt Later detection

Cryptographic Inventory

Post Quantum Migration Recommendation

Quantum Readiness Assessment

Never ignore quantum risk indicators.

---

# Graph Rules

Every incident shall be represented as a graph.

Graph Nodes

Users

Devices

Transactions

Endpoints

Threats

Alerts

Firewall Events

VPN Events

Threat Intelligence

Graph Relationships

Communicates With

Logged Into

Triggered

Executed

Transferred

Correlated With

Never flatten graph relationships.

---

# API Rules

RESTful

Versioned

OpenAPI

Consistent responses

Validation

Pagination

Filtering

Sorting

Authentication

Authorization

Every endpoint must include documentation.

---

# Database Rules

Normalize relational data.

Use Neo4j for relationships.

Never duplicate data.

Never write raw SQL unless necessary.

Use migrations.

---

# Frontend Rules

Use:

Next.js

Tailwind

shadcn/ui

React Query

Framer Motion where appropriate

Responsive Design

Dark Mode

Accessibility

Never:

Inline CSS

Duplicate Components

Large Pages

Business Logic inside UI

---

# Dashboard Rules

The dashboard must include:

Executive Dashboard

SOC Dashboard

Risk Score

Timeline

Graph Visualization

Incident Details

MITRE Mapping

AI Explanation

Recommendations

Filters

Search

Analytics

---

# Testing Rules

Every feature requires:

Unit Tests

Integration Tests

API Tests

Security Tests

Edge Case Tests

No feature is complete without tests.

---

# Documentation Rules

Every module requires:

README

Architecture

API Documentation

Sequence Diagram

Flow Diagram

Configuration Guide

Deployment Guide

Never leave undocumented modules.

---

# Performance Rules

API

Target <300ms

Dashboard

Target <2 seconds

Graph Queries

Target <500ms

AI Inference

Target <2 seconds

Optimize queries before optimizing code.

---

# Maintainability Rules

Keep modules independent.

Avoid circular dependencies.

Favor composition over inheritance.

Extract reusable services.

Never tightly couple modules.

---

# Git Rules

Generate:

Meaningful commits

Meaningful pull request descriptions

Semantic Versioning

Feature branches

Never modify unrelated files.

---

# Phase Completion Rules

Before declaring any phase complete, verify:

✅ Project builds successfully

✅ No compilation errors

✅ No TypeScript errors

✅ No Python linting errors

✅ Tests passing

✅ Documentation updated

✅ APIs documented

✅ Logging implemented

✅ Security implemented

✅ AI validation completed

✅ Architecture unchanged

If any item fails:

Stop.

Produce a report listing:

- Failed Item
- Cause
- Suggested Fix

Do not proceed.

---

# Phase Completion Output

When every requirement has passed, output exactly:

=================================================

✅ Phase Completed Successfully

Project Status

✔ Architecture Verified

✔ Security Verified

✔ Tests Passed

✔ Documentation Updated

✔ AI Validation Passed

✔ Performance Verified

✔ Ready For Next Phase

=================================================

---

# Final Completion Rules

Before declaring the project complete, verify:

Business Potential

Security

Innovation

User Experience

Scalability

Maintainability

Deployment

Documentation

Testing

AI Validation

Quantum Module

Threat Intelligence

Graph Intelligence

SOC Dashboard

Executive Dashboard

API Documentation

Docker

Database

Authentication

Authorization

Risk Engine

Correlation Engine

Explainable AI

MITRE Mapping

Quantum Monitoring

Threat Detection

Fraud Detection

Event Correlation

Incident Timeline

If any requirement is missing:

Return a detailed remediation report.

Do not declare completion.

---

# Final Success Output

When every requirement passes:

=============================================================

🎉 SENTINEL FUSION AI

Enterprise Cyber Fusion Platform

STATUS

✔ Production Ready

✔ Security Verified

✔ AI Verified

✔ Documentation Complete

✔ Tests Passed

✔ Deployment Ready

✔ Bank of Maharashtra Evaluation Criteria Satisfied

Business Potential ✔

Security ✔

Innovation ✔

User Experience ✔

Scalability ✔

Maintainability ✔

Repository is submission ready.

=============================================================
