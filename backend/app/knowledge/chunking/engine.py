from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from typing import Any

from app.core.settings import AppSettings


@dataclass(slots=True)
class ChunkData:
    content: str
    chunk_type: str
    chunk_index: int
    token_count: int
    character_count: int
    overlap_start: int | None = None
    overlap_end: int | None = None
    section_title: str | None = None
    page_number: int | None = None
    metadata: dict[str, Any] | None = None


@dataclass(slots=True)
class ChunkingEngine:
    """Chunk text into configurable knowledge segments."""

    settings: AppSettings

    def chunk(self, content: str, *, strategy: str = "hybrid", chunk_size: int | None = None, chunk_overlap: int | None = None, metadata: dict[str, Any] | None = None) -> list[ChunkData]:
        strategy = strategy.lower()
        chunk_size = chunk_size or self.settings.knowledge_max_chunk_size
        chunk_overlap = chunk_overlap if chunk_overlap is not None else self.settings.knowledge_default_chunk_overlap
        metadata = metadata or {}

        if strategy == "markdown":
            return self._chunk_markdown(content, chunk_size, chunk_overlap, metadata)
        if strategy == "html":
            return self._chunk_html(content, chunk_size, chunk_overlap, metadata)
        if strategy == "code":
            return self._chunk_code(content, chunk_size, chunk_overlap, metadata)
        if strategy == "table":
            return self._chunk_table(content, chunk_size, chunk_overlap, metadata)
        if strategy == "recursive":
            return self._chunk_recursive(content, chunk_size, chunk_overlap, metadata)
        if strategy == "semantic":
            return self._chunk_semantic(content, chunk_size, chunk_overlap, metadata)
        if strategy == "hybrid":
            return self._chunk_hybrid(content, chunk_size, chunk_overlap, metadata)
        return self._chunk_fixed(content, chunk_size, chunk_overlap, metadata)

    def estimate_tokens(self, content: str) -> int:
        return max(1, (len(content) + 3) // 4)

    def chunk_hash(self, content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def _chunk_fixed(self, content: str, chunk_size: int, chunk_overlap: int, metadata: dict[str, Any]) -> list[ChunkData]:
        segments: list[ChunkData] = []
        start = 0
        index = 0
        while start < len(content):
            end = min(len(content), start + chunk_size)
            chunk_content = content[start:end].strip()
            if chunk_content:
                segments.append(self._build_chunk(chunk_content, "fixed", index, start, end, metadata))
                index += 1
            if end >= len(content):
                break
            start = max(end - chunk_overlap, start + 1)
        return segments

    def _chunk_recursive(self, content: str, chunk_size: int, chunk_overlap: int, metadata: dict[str, Any]) -> list[ChunkData]:
        paragraphs = [paragraph.strip() for paragraph in re.split(r"\n{2,}", content) if paragraph.strip()]
        chunks: list[ChunkData] = []
        index = 0
        for paragraph in paragraphs:
            if len(paragraph) <= chunk_size:
                chunks.append(self._build_chunk(paragraph, "recursive", index, None, None, metadata))
                index += 1
            else:
                for nested in self._chunk_fixed(paragraph, chunk_size, chunk_overlap, metadata):
                    nested.chunk_index = index
                    chunks.append(nested)
                    index += 1
        return chunks

    def _chunk_semantic(self, content: str, chunk_size: int, chunk_overlap: int, metadata: dict[str, Any]) -> list[ChunkData]:
        sentences = re.split(r"(?<=[.!?])\s+", content)
        return self._chunk_grouped(sentences, chunk_size, chunk_overlap, "semantic", metadata)

    def _chunk_markdown(self, content: str, chunk_size: int, chunk_overlap: int, metadata: dict[str, Any]) -> list[ChunkData]:
        sections = re.split(r"(?m)^(?=#{1,6}\s)", content)
        return self._chunk_grouped([section for section in sections if section.strip()], chunk_size, chunk_overlap, "markdown", metadata)

    def _chunk_html(self, content: str, chunk_size: int, chunk_overlap: int, metadata: dict[str, Any]) -> list[ChunkData]:
        sections = re.split(r"<section[^>]*>|</section>", content, flags=re.IGNORECASE)
        return self._chunk_grouped([section for section in sections if section.strip()], chunk_size, chunk_overlap, "html", metadata)

    def _chunk_code(self, content: str, chunk_size: int, chunk_overlap: int, metadata: dict[str, Any]) -> list[ChunkData]:
        blocks = re.split(r"(?m)^\s*def\s+|^\s*class\s+", content)
        return self._chunk_grouped([block for block in blocks if block.strip()], chunk_size, chunk_overlap, "code", metadata)

    def _chunk_table(self, content: str, chunk_size: int, chunk_overlap: int, metadata: dict[str, Any]) -> list[ChunkData]:
        rows = [row for row in content.splitlines() if row.strip()]
        return self._chunk_grouped(rows, chunk_size, chunk_overlap, "table", metadata)

    def _chunk_hybrid(self, content: str, chunk_size: int, chunk_overlap: int, metadata: dict[str, Any]) -> list[ChunkData]:
        paragraphs = [paragraph.strip() for paragraph in re.split(r"\n{2,}", content) if paragraph.strip()]
        chunks: list[ChunkData] = []
        index = 0
        for paragraph in paragraphs:
            if len(paragraph) <= chunk_size:
                chunks.append(self._build_chunk(paragraph, "hybrid", index, None, None, metadata))
                index += 1
            else:
                sentence_chunks = self._chunk_semantic(paragraph, chunk_size, chunk_overlap, metadata)
                for nested in sentence_chunks:
                    nested.chunk_index = index
                    nested.chunk_type = "hybrid"
                    chunks.append(nested)
                    index += 1
        return chunks

    def _chunk_grouped(self, units: list[str], chunk_size: int, chunk_overlap: int, chunk_type: str, metadata: dict[str, Any]) -> list[ChunkData]:
        chunks: list[ChunkData] = []
        current = ""
        index = 0
        for unit in units:
            candidate = f"{current}\n{unit}".strip() if current else unit.strip()
            if len(candidate) <= chunk_size:
                current = candidate
                continue
            if current:
                chunks.append(self._build_chunk(current, chunk_type, index, None, None, metadata))
                index += 1
            current = unit.strip()
            while len(current) > chunk_size:
                segment = current[:chunk_size].strip()
                chunks.append(self._build_chunk(segment, chunk_type, index, None, None, metadata))
                index += 1
                current = current[max(1, chunk_size - chunk_overlap):]
        if current:
            chunks.append(self._build_chunk(current, chunk_type, index, None, None, metadata))
        return chunks

    def _build_chunk(self, content: str, chunk_type: str, chunk_index: int, start: int | None, end: int | None, metadata: dict[str, Any]) -> ChunkData:
        return ChunkData(
            content=content,
            chunk_type=chunk_type,
            chunk_index=chunk_index,
            token_count=self.estimate_tokens(content),
            character_count=len(content),
            overlap_start=start,
            overlap_end=end,
            section_title=metadata.get("section_title") if isinstance(metadata, dict) else None,
            page_number=metadata.get("page_number") if isinstance(metadata, dict) else None,
            metadata=metadata,
        )
