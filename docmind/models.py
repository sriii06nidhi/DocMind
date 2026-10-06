from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class PageRecord:
    document_id: str
    page_number: int
    text: str
    extraction_method: str
    status: str = "READY"


@dataclass
class ChunkRecord:
    chunk_id: str
    document_id: str
    document_name: str
    page_number: int
    text: str
    source_type: str = "text"
    chunk_index: int = 0


@dataclass
class EntityRecord:
    name: str
    entity_type: str
    document_id: str
    document_name: str
    page_number: int
    evidence: str


@dataclass
class ClaimRecord:
    claim_id: str
    subject: str
    relation: str
    obj: str
    document_id: str
    document_name: str
    page_number: int
    evidence: str
    confidence: str = "Medium"


@dataclass
class EventRecord:
    event_id: str
    title: str
    date: str
    document_id: str
    document_name: str
    page_number: int
    evidence: str


@dataclass
class ContradictionRecord:
    claim_a: Dict[str, Any]
    claim_b: Dict[str, Any]
    classification: str
    reason: str
    confidence: str = "Medium"


@dataclass
class DocumentRecord:
    document_id: str
    name: str
    file_path: str
    file_type: str
    size_bytes: int
    upload_ts: str
    status: str
    pages: List[PageRecord] = field(default_factory=list)
    chunks: List[ChunkRecord] = field(default_factory=list)
    entities: List[EntityRecord] = field(default_factory=list)
    claims: List[ClaimRecord] = field(default_factory=list)
    events: List[EventRecord] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "document_id": self.document_id,
            "name": self.name,
            "file_path": self.file_path,
            "file_type": self.file_type,
            "size_bytes": self.size_bytes,
            "upload_ts": self.upload_ts,
            "status": self.status,
            "pages": [
                {
                    "document_id": p.document_id,
                    "page_number": p.page_number,
                    "text": p.text,
                    "extraction_method": p.extraction_method,
                    "status": p.status,
                }
                for p in self.pages
            ],
            "chunks": [
                {
                    "chunk_id": c.chunk_id,
                    "document_id": c.document_id,
                    "document_name": c.document_name,
                    "page_number": c.page_number,
                    "text": c.text,
                    "source_type": c.source_type,
                    "chunk_index": c.chunk_index,
                }
                for c in self.chunks
            ],
            "entities": [
                {
                    "name": e.name,
                    "entity_type": e.entity_type,
                    "document_id": e.document_id,
                    "document_name": e.document_name,
                    "page_number": e.page_number,
                    "evidence": e.evidence,
                }
                for e in self.entities
            ],
            "claims": [
                {
                    "claim_id": c.claim_id,
                    "subject": c.subject,
                    "relation": c.relation,
                    "obj": c.obj,
                    "document_id": c.document_id,
                    "document_name": c.document_name,
                    "page_number": c.page_number,
                    "evidence": c.evidence,
                    "confidence": c.confidence,
                }
                for c in self.claims
            ],
            "events": [
                {
                    "event_id": e.event_id,
                    "title": e.title,
                    "date": e.date,
                    "document_id": e.document_id,
                    "document_name": e.document_name,
                    "page_number": e.page_number,
                    "evidence": e.evidence,
                }
                for e in self.events
            ],
            "notes": self.notes,
        }
