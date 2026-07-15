# Enterprise Knowledge Platform

This module implements the Phase 12 knowledge foundation for Sentinel Fusion AI.

## Core areas

- Knowledge registry for collections, sources, and document ownership.
- Document processing for upload validation, metadata extraction, and content normalization.
- Chunking for fixed, recursive, semantic, markdown, HTML, code, table, and hybrid strategies.
- Embeddings through a lazy Sentence Transformers adapter with deterministic fallback behavior.
- Qdrant integration with a memory fallback to keep the platform testable in local environments.
- Retrieval and ranking for vector, keyword, metadata, and hybrid search.
- Governance for access policies, document lifecycle, and audit logging.
