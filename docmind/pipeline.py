from __future__ import annotations

import hashlib
import io
import logging
import os
import re
import uuid
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Iterable, List

import numpy as np
import pymupdf as fitz
import pytesseract
from PIL import Image
from sentence_transformers import SentenceTransformer

try:
    import chromadb
except Exception:  # pragma: no cover
    chromadb = None

from .config import BASE_DIR, get_settings

logger = logging.getLogger(__name__)


def normalize_text(text: str) -> str:
    if not text:
        return ""
    cleaned = text.replace("\r\n", "\n").replace("\r", "\n").replace("\u00a0", " ")
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    cleaned = re.sub(r"[ \t]{2,}", " ", cleaned)
    return cleaned.strip()


class DocMindPipeline:
    def __init__(self, root_dir: str | Path | None = None):
        self.root_dir = Path(root_dir) if root_dir else Path(BASE_DIR)
        self.data_dir = self.root_dir / "data"
        self.upload_dir = self.data_dir / "uploads"
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.settings = get_settings()
        if not os.getenv("CHROMA_PATH") and self.root_dir.resolve() != BASE_DIR.resolve():
            self.settings["chroma_path"] = str(self.data_dir / "chroma")
        self.documents: List[dict] = []
        self.chroma_error: str | None = None
        self.last_search_warning: str | None = None
        tesseract_path = self.settings.get("tesseract_path")
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        self.embedding_model = self._init_embedding_model()
        self.collection = self._init_chroma()

    def _init_embedding_model(self):
        model_name = self.settings.get("embedding_model", "sentence-transformers/all-MiniLM-L6-v2")
        try:
            return SentenceTransformer(model_name)
        except Exception:
            logger.exception("Unable to load embedding model %s", model_name)
            return None

    def _init_chroma(self):
        if chromadb is None:
            self.chroma_error = "The chromadb package is not installed."
            logger.error(self.chroma_error)
            return None
        try:
            client = chromadb.PersistentClient(path=self.settings.get("chroma_path", str(self.data_dir / "chroma")))
            return client.get_or_create_collection(name="docmind_chunks")
        except Exception as exc:  # pragma: no cover
            self.chroma_error = str(exc)
            logger.exception("Unable to initialize ChromaDB")
            return None

    def _stable_document_id(self, file_path: Path, filename: str, file_bytes: bytes | None = None) -> str:
        if file_bytes is None and file_path.exists():
            file_bytes = file_path.read_bytes()
        payload = bytearray()
        if file_bytes:
            payload.extend(file_bytes)
        payload.extend(b"\0")
        payload.extend((filename or file_path.name).encode("utf-8"))
        return hashlib.sha256(bytes(payload)).hexdigest()

    def _validate_chunk_batch(self, ids: List[str], texts: List[str], embeddings: List[List[float]], metadata: List[dict], document_name: str) -> None:
        if not (len(ids) == len(texts) == len(embeddings) == len(metadata)):
            logger.error(
                "Chunk batch length mismatch for %s: ids=%s texts=%s embeddings=%s metadata=%s",
                document_name,
                len(ids),
                len(texts),
                len(embeddings),
                len(metadata),
            )
            raise ValueError(
                f"Chunk batch validation failed for '{document_name}': "
                f"ids={len(ids)}, texts={len(texts)}, embeddings={len(embeddings)}, metadata={len(metadata)}"
            )
        seen: set[str] = set()
        duplicates: set[str] = set()
        for item in ids:
            if item in seen:
                duplicates.add(item)
            seen.add(item)
        if duplicates:
            duplicate_sample = sorted(duplicates)[:10]
            logger.error("Duplicate chunk IDs in batch for %s: %s", document_name, duplicate_sample)
            raise ValueError(f"Duplicate chunk IDs detected for '{document_name}': {duplicate_sample}")

    def _replace_document_vectors(self, document_id: str, ids: List[str], texts: List[str], embeddings: List[List[float]], metadata: List[dict]) -> None:
        if self.collection is None:
            return
        try:
            existing = self.collection.get(where={"document_id": document_id})
            existing_ids = set(existing.get("ids", []))
            new_ids = set(ids)
            if ids:
                self.collection.upsert(ids=ids, embeddings=embeddings, documents=texts, metadatas=metadata)
            stale_ids = list(existing_ids - new_ids)
            if stale_ids:
                self.collection.delete(ids=stale_ids)
        except Exception:
            logger.exception("ChromaDB indexing failed for document_id=%s", document_id)
            raise

    def process_document(self, uploaded_file: str | Any, document_name: str | None = None) -> dict:
        if hasattr(uploaded_file, "read"):
            filename = document_name or getattr(uploaded_file, "name", "upload")
            if hasattr(uploaded_file, "getvalue"):
                file_bytes = uploaded_file.getvalue()
            else:
                if hasattr(uploaded_file, "seek"):
                    uploaded_file.seek(0)
                file_bytes = uploaded_file.read()
                if hasattr(uploaded_file, "seek"):
                    uploaded_file.seek(0)
            file_path = self.upload_dir / f"{uuid.uuid4()}_{filename}"
            file_path.write_bytes(file_bytes)
        else:
            file_path = Path(uploaded_file)
            filename = document_name or file_path.name
            file_bytes = file_path.read_bytes() if file_path.exists() else b""

        doc_id = self._stable_document_id(file_path, filename, file_bytes)
        file_type = file_path.suffix.lower().lstrip('.') or "unknown"
        file_size = file_path.stat().st_size if file_path.exists() else 0
        record = {
            "document_id": doc_id,
            "name": filename,
            "file_path": str(file_path),
            "file_type": file_type,
            "size_bytes": file_size,
            "upload_ts": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
            "status": "PROCESSING",
            "pages": [],
            "chunks": [],
            "entities": [],
            "claims": [],
            "events": [],
            "notes": [],
        }

        pages = self._extract_pages(file_path)
        if not pages:
            record["status"] = "FAILED"
            record["notes"].append("No text could be extracted from the provided file.")
            self._replace_existing_document(record)
            return record

        record["pages"] = pages

        all_chunks = []
        chunk_cursor = 0
        for page in pages:
            page_number = page["page_number"]
            chunk_list = self._chunk_text(
                page["text"],
                doc_id,
                filename,
                page_number,
                chunk_cursor,
                page.get("extraction_method", "TEXT"),
            )
            chunk_cursor += len(chunk_list)
            all_chunks.extend(chunk_list)
            record["chunks"].extend(chunk_list)
            record["entities"].extend(self._extract_entities(page["text"], doc_id, filename, page_number))
            record["claims"].extend(self._extract_claims(page["text"], doc_id, filename, page_number))
            record["events"].extend(self._extract_events(page["text"], doc_id, filename, page_number))

        record["status"] = "READY" if all_chunks else "WARNING"
        record["notes"].append(f"Extracted {len(pages)} pages and {len(all_chunks)} chunks.")
        empty_pages = [page["page_number"] for page in pages if not page.get("text", "").strip()]
        if empty_pages:
            record["notes"].append(f"No text was extracted from page(s): {', '.join(map(str, empty_pages))}.")

        if self.collection is not None:
            texts = [chunk["text"] for chunk in all_chunks]
            embeddings = self._embed_texts(texts) if texts else []
            ids = [chunk["chunk_id"] for chunk in all_chunks]
            metadata = [
                {
                    "document_id": chunk["document_id"],
                    "document_name": chunk["document_name"],
                    "page_number": chunk["page_number"],
                    "chunk_index": chunk.get("chunk_index"),
                    "chunk_id": chunk["chunk_id"],
                    "source_type": chunk.get("source_type", "text"),
                }
                for chunk in all_chunks
            ]
            self._validate_chunk_batch(ids, texts, embeddings, metadata, filename)
            self._replace_document_vectors(doc_id, ids, texts, embeddings, metadata)
        elif self.chroma_error:
            logger.error("Document %s processed without ChromaDB: %s", filename, self.chroma_error)
            record["status"] = "WARNING"
            record["notes"].append("ChromaDB is unavailable; semantic vector search is disabled.")

        self._replace_existing_document(record)
        return record

    def _replace_existing_document(self, record: dict) -> None:
        existing_index = None
        for index, document in enumerate(self.documents):
            if document.get("document_id") == record.get("document_id"):
                existing_index = index
                break
        if existing_index is not None:
            self.documents[existing_index] = record
        else:
            self.documents.append(record)

    def _extract_pages(self, file_path: Path) -> List[dict]:
        suffix = file_path.suffix.lower()
        if suffix == ".pdf":
            return self._extract_pdf_pages(file_path)
        if suffix in {".png", ".jpg", ".jpeg", ".tiff", ".bmp"}:
            return self._extract_image_pages(file_path)
        if suffix in {".txt", ".md", ".csv", ".json"}:
            text = normalize_text(file_path.read_text(encoding="utf-8", errors="replace"))
            return [{"page_number": 1, "text": text, "extraction_method": "TEXT_FILE"}]
        return []

    def _extract_pdf_pages(self, file_path: Path) -> List[dict]:
        pages: List[dict] = []
        try:
            with fitz.open(file_path) as pdf:
                for page_number, page in enumerate(pdf, start=1):
                    page_text = normalize_text(page.get_text("text"))
                    method = "PDF_TEXT"
                    if not page_text:
                        try:
                            pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                            image = Image.open(io.BytesIO(pixmap.tobytes("png")))
                            page_text = normalize_text(pytesseract.image_to_string(image, config="--psm 6"))
                            method = "OCR"
                        except Exception:
                            logger.exception("OCR failed for %s page %s", file_path.name, page_number)
                            method = "OCR_FAILED"
                    pages.append({"page_number": page_number, "text": page_text, "extraction_method": method})
        except Exception:
            logger.exception("Unable to extract PDF %s", file_path.name)
            return []
        return pages

    def _extract_image_pages(self, file_path: Path) -> List[dict]:
        try:
            image = Image.open(file_path)
            text = normalize_text(pytesseract.image_to_string(image, config="--psm 6"))
            return [{"page_number": 1, "text": text, "extraction_method": "OCR"}]
        except Exception:
            logger.exception("Unable to extract OCR text from image %s", file_path.name)
            return []

    def _chunk_text(
        self,
        text: str,
        document_id: str,
        document_name: str,
        page_number: int,
        chunk_offset: int = 0,
        source_type: str = "TEXT",
    ) -> List[dict]:
        if not text:
            return []
        sentences = re.split(r"(?<=[.!?])\s+|\n+", text)
        chunks: List[dict] = []
        current = []
        current_length = 0
        next_chunk_index = chunk_offset + 1
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            if current_length + len(sentence) > 350 and current:
                chunk_text = " ".join(current)
                chunk_id = f"{document_id}-chunk-{next_chunk_index}"
                chunks.append({
                    "chunk_id": chunk_id,
                    "chunk_index": next_chunk_index,
                    "document_id": document_id,
                    "document_name": document_name,
                    "page_number": page_number,
                    "text": normalize_text(chunk_text),
                    "source_type": source_type,
                })
                next_chunk_index += 1
                current = [sentence]
                current_length = len(sentence)
            else:
                current.append(sentence)
                current_length += len(sentence)
        if current:
            chunk_text = " ".join(current)
            chunk_id = f"{document_id}-chunk-{next_chunk_index}"
            chunks.append({
                "chunk_id": chunk_id,
                "chunk_index": next_chunk_index,
                "document_id": document_id,
                "document_name": document_name,
                "page_number": page_number,
                "text": normalize_text(chunk_text),
                "source_type": source_type,
            })
        return chunks

    def _extract_entities(self, text: str, document_id: str, document_name: str, page_number: int) -> List[dict]:
        entities = []
        seen = set()
        for match in re.finditer(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3}\b", text):
            value = match.group(0)
            if value.lower() in {"the", "this", "that", "these", "those"}:
                continue
            if value not in seen:
                seen.add(value)
                entities.append({
                    "name": value,
                    "entity_type": "Organization" if value.lower() in {"company", "team", "department"} else "Person",
                    "document_id": document_id,
                    "document_name": document_name,
                    "page_number": page_number,
                    "evidence": value,
                })
        for match in re.finditer(r"\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}|[A-Z][a-z]+ \d{1,2}, \d{4})\b", text):
            value = match.group(0)
            if value not in seen:
                seen.add(value)
                entities.append({
                    "name": value,
                    "entity_type": "Date",
                    "document_id": document_id,
                    "document_name": document_name,
                    "page_number": page_number,
                    "evidence": value,
                })
        for match in re.finditer(r"\b\d+(?:\.\d+)?%?\b", text):
            value = match.group(0)
            if value not in seen:
                seen.add(value)
                entities.append({
                    "name": value,
                    "entity_type": "Value",
                    "document_id": document_id,
                    "document_name": document_name,
                    "page_number": page_number,
                    "evidence": value,
                })
        return entities

    def _extract_claims(self, text: str, document_id: str, document_name: str, page_number: int) -> List[dict]:
        claims: List[dict] = []
        sentences = re.split(r"(?<=[.!?])\s+|\n+", text)
        for index, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if not sentence:
                continue
            match = re.search(r"(?P<subject>[A-Za-z][A-Za-z0-9 &/-]+?)\s+(?:is|was|are|were|has|have|reported|shows|states|indicates|increased|decreased|reached)\s+(?P<object>[^.]+)", sentence, flags=re.IGNORECASE)
            if match:
                subject = match.group("subject").strip()
                relation = "reported" if "reported" in sentence.lower() else "states"
                obj = match.group("object").strip()
                claims.append({
                    "claim_id": f"{document_id}-claim-{page_number}-{index}",
                    "subject": subject,
                    "relation": relation,
                    "obj": obj,
                    "document_id": document_id,
                    "document_name": document_name,
                    "page_number": page_number,
                    "evidence": sentence,
                    "confidence": "Medium",
                })
        return claims

    def _extract_events(self, text: str, document_id: str, document_name: str, page_number: int) -> List[dict]:
        events = []
        sentences = re.split(r"(?<=[.!?])\s+|\n+", text)
        for index, sentence in enumerate(sentences):
            date_match = re.search(r"\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}|[A-Z][a-z]+ \d{1,2}, \d{4})\b", sentence)
            if date_match:
                events.append({
                    "event_id": f"{document_id}-event-{page_number}-{index}",
                    "title": sentence[:80],
                    "date": date_match.group(0),
                    "document_id": document_id,
                    "document_name": document_name,
                    "page_number": page_number,
                    "evidence": sentence,
                })
        return events

    def _embed_texts(self, texts: Iterable[str]) -> List[List[float]]:
        texts = list(texts)
        if not texts:
            return []
        if self.embedding_model is None:
            raise RuntimeError("The configured embedding model is unavailable; refusing to index zero-vector embeddings.")
        embeddings = np.asarray(self.embedding_model.encode(texts, convert_to_numpy=True))
        if embeddings.ndim != 2 or embeddings.shape[0] != len(texts) or not np.isfinite(embeddings).all():
            raise ValueError(
                f"Embedding output is invalid: expected {len(texts)} finite vectors, received shape {embeddings.shape}."
            )
        return embeddings.tolist()

    def semantic_search(self, query: str, top_k: int = 5) -> List[dict]:
        self.last_search_warning = None
        if not query.strip() or top_k <= 0:
            return []
        searchable_documents = [
            document for document in self.documents
            if document.get("status") in {"READY", "WARNING"} and document.get("chunks")
        ]
        if not searchable_documents:
            return []
        document_ids = [document["document_id"] for document in searchable_documents]
        if self.collection is not None and self.embedding_model is not None:
            try:
                query_vector = np.asarray(
                    self.embedding_model.encode([query], convert_to_numpy=True)
                )[0].tolist()
                results = self.collection.query(
                    query_embeddings=[query_vector],
                    n_results=top_k,
                    where={"document_id": {"$in": document_ids}},
                )
                hits = []
                for idx, document in enumerate(results.get("documents", [[]])[0]):
                    metadata = results.get("metadatas", [[]])[0][idx]
                    hits.append({
                        "text": document,
                        "document": metadata.get("document_name"),
                        "page_number": metadata.get("page_number"),
                        "document_id": metadata.get("document_id"),
                        "chunk_id": metadata.get("chunk_id"),
                        "score": float(results.get("distances", [[0.0]])[0][idx]) if results.get("distances") else 0.0,
                    })
                if hits:
                    return hits
                self.last_search_warning = "No vector matches were found; lexical matching was used."
            except Exception:
                logger.exception("ChromaDB semantic search failed; using local lexical retrieval")
                self.last_search_warning = "Vector search failed; lexical matching was used."
        else:
            self.last_search_warning = "Vector search is unavailable; lexical matching was used."

        query_terms = {
            term for term in re.findall(r"[a-z0-9]+", query.lower())
            if len(term) > 2 and term not in {"the", "and", "for", "what", "which", "who", "does", "did", "are", "was", "were", "about", "from", "with"}
        }
        ranked_hits = []
        for document in searchable_documents:
            for chunk in document.get("chunks", []):
                text = chunk["text"]
                terms = set(re.findall(r"[a-z0-9]+", text.lower()))
                overlap = len(query_terms & terms)
                if overlap:
                    ranked_hits.append((overlap, {
                        "text": chunk["text"],
                        "document": document["name"],
                        "page_number": chunk["page_number"],
                        "document_id": document["document_id"],
                        "chunk_id": chunk["chunk_id"],
                        "score": overlap / max(len(query_terms), 1),
                    }))
        ranked_hits.sort(key=lambda item: item[0], reverse=True)
        return [hit for _, hit in ranked_hits[:top_k]]

    def answer_question(self, question: str) -> dict:
        evidence = self.semantic_search(question, top_k=5)
        if not evidence:
            return {
                "answer": "The available documents do not contain enough evidence to answer this question reliably.",
                "confidence": "Insufficient Evidence",
                "citations": [],
                "sources": [],
            }
        from .llm import generate_grounded_answer

        local_evidence = [
            {
                "document": item["document"],
                "page_number": item.get("page_number", 1),
                "text": item["text"],
            }
            for item in evidence
        ]
        answer = generate_grounded_answer(question, local_evidence)
        answer["sources"] = answer.get("sources", [])
        answer["citations"] = answer.get("citations", [])
        answer["retrieval_warning"] = self.last_search_warning
        return answer

    def detect_contradictions(self) -> List[dict]:
        contradictions: List[dict] = []
        claims = []
        for document in self.documents:
            for claim in document.get("claims", []):
                claims.append({**claim, "document_name": document["name"]})

        for idx, left in enumerate(claims):
            for right in claims[idx + 1:]:
                if (
                    left["subject"].strip().casefold() != right["subject"].strip().casefold()
                    or left["relation"].strip().casefold() != right["relation"].strip().casefold()
                ):
                    continue
                left_obj = left["obj"].lower()
                right_obj = right["obj"].lower()
                if left_obj == right_obj:
                    continue
                classification = "POTENTIAL_CONTRADICTION"
                reason = "The same subject is described with different values or relationships."
                negation_pattern = r"\b(?:not|no|false|never)\b"
                left_negated = bool(re.search(negation_pattern, left_obj))
                right_negated = bool(re.search(negation_pattern, right_obj))
                left_without_negation = re.sub(negation_pattern, "", left_obj).strip()
                right_without_negation = re.sub(negation_pattern, "", right_obj).strip()
                if left_negated != right_negated and left_without_negation == right_without_negation:
                    classification = "EXPLICIT_CONTRADICTION"
                    reason = "The statements directly disagree on the same claim."
                contradictions.append({
                    "claim_a": left,
                    "claim_b": right,
                    "classification": classification,
                    "reason": reason,
                    "confidence": "Medium",
                })
        return contradictions

    def extract_timeline(self) -> List[dict]:
        timeline = []
        for document in self.documents:
            for event in document.get("events", []):
                timeline.append({
                    "document": document["name"],
                    "page_number": event["page_number"],
                    "date": event["date"],
                    "title": event["title"],
                    "evidence": event["evidence"],
                })
        def sort_key(item: dict) -> tuple[bool, date]:
            value = item["date"]
            for date_format in ("%Y", "%m/%d/%Y", "%m-%d-%Y", "%m/%d/%y", "%m-%d-%y", "%B %d, %Y", "%b %d, %Y"):
                try:
                    parsed = datetime.strptime(value, date_format).date()
                    return False, parsed
                except ValueError:
                    continue
            return True, date.max

        return sorted(timeline, key=sort_key)

    def export_dashboard(self) -> dict:
        documents = self.documents
        total_pages = sum(len(doc.get("pages", [])) for doc in documents)
        total_entities = sum(len(doc.get("entities", [])) for doc in documents)
        total_claims = sum(len(doc.get("claims", [])) for doc in documents)
        total_events = sum(len(doc.get("events", [])) for doc in documents)
        return {
            "documents": len(documents),
            "pages": total_pages,
            "entities": total_entities,
            "claims": total_claims,
            "events": total_events,
            "contradictions": len(self.detect_contradictions()),
            "status": "READY" if documents else "EMPTY",
        }
