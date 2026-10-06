from __future__ import annotations

import io
from pathlib import Path

import fitz
import pytest
import requests

from docmind.config import get_settings
from docmind.graph import build_graph_from_documents
from docmind.llm import LLMServiceError, generate_grounded_answer
from docmind.pipeline import DocMindPipeline


def _build_pdf(tmp_path: Path, name: str, pages: list[str]) -> Path:
    pdf = fitz.open()
    for text in pages:
        page = pdf.new_page()
        page.insert_text((72, 72), text)
    path = tmp_path / name
    pdf.save(path)
    pdf.close()
    return path


def test_settings_include_expected_keys():
    settings = get_settings()
    assert "llm_model" in settings
    assert "embedding_model" in settings
    assert "chroma_path" in settings


def test_default_nvidia_model_is_configured_without_an_api_key(monkeypatch):
    for variable in (
        "LLM_PROVIDER", "LLM_API_KEY", "NVIDIA_API_KEY", "LLM_MODEL",
        "PRIMARY_MODEL", "FALLBACK_MODEL", "CHAT_FALLBACK_MODEL",
    ):
        monkeypatch.delenv(variable, raising=False)
    monkeypatch.setattr("docmind.config._FILE_SETTINGS", {})

    settings = get_settings()

    assert settings["llm_provider"] == "nvidia"
    assert settings["llm_model"] == "nvidia/nemotron-3-super-120b-a12b"
    assert settings["llm_api_key"] is None


def test_colon_formatted_env_file_loads_nvidia_key_and_primary_model(tmp_path):
    from docmind.config import _read_env_file

    env_file = tmp_path / ".env"
    env_file.write_text(
        "NVIDIA API KEY\n"
        "API_KEY: test-secret-value\n"
        "Primary Model: nvidia/test-model\n"
        "NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1\n",
        encoding="utf-8",
    )

    settings = _read_env_file(env_file)

    assert settings["NVIDIA_API_KEY"] == "test-secret-value"
    assert settings["PRIMARY_MODEL"] == "nvidia/test-model"
    assert settings["NVIDIA_BASE_URL"] == "https://integrate.api.nvidia.com/v1"


def test_nvidia_model_and_timeout_environment_aliases(monkeypatch):
    monkeypatch.delenv("LLM_MODEL", raising=False)
    monkeypatch.setenv("PRIMARY_MODEL", "nvidia/nemotron-primary")
    monkeypatch.setenv("NVIDIA_TIMEOUT_SECONDS", "9")

    settings = get_settings()

    assert settings["llm_model"] == "nvidia/nemotron-primary"
    assert settings["nvidia_timeout_seconds"] == 30


def test_configured_nvidia_without_key_reports_local_fallback(monkeypatch):
    monkeypatch.setattr("docmind.llm.get_settings", lambda: {
        "llm_provider": "nvidia",
        "llm_api_key": None,
    })

    answer = generate_grounded_answer(
        "Question?",
        [{"document": "source.pdf", "page_number": 1, "text": "Evidence from the document."}],
    )

    assert answer["provider"] == "local"
    assert answer["llm_status"] == "api_key_missing"
    assert "Evidence from the document." in answer["answer"]


def test_pipeline_extracts_text_and_answer(tmp_path):
    pipeline = DocMindPipeline(root_dir=tmp_path)
    source = tmp_path / "sample.txt"
    source.write_text(
        "Alpha reported 12% growth in 2024. Beta reported 15% growth in 2024. The company expanded operations.",
        encoding="utf-8",
    )

    result = pipeline.process_document(source, source.name)
    assert result["status"] == "READY"
    assert len(result["chunks"]) >= 1
    assert result["entities"]

    answer = pipeline.answer_question("What did Alpha report in 2024?")
    assert "answer" in answer
    assert "citations" in answer or "sources" in answer


def test_pipeline_reprocessing_same_document_is_idempotent(tmp_path):
    pipeline = DocMindPipeline(root_dir=tmp_path)
    source = tmp_path / "repeatable.txt"
    source.write_text(
        "Alpha reported 12% growth in 2024. Beta reported 15% growth in 2024. The company expanded operations.",
        encoding="utf-8",
    )

    first = pipeline.process_document(source, source.name)
    second = pipeline.process_document(source, source.name)

    assert first["document_id"] == second["document_id"]
    assert sum(1 for doc in pipeline.documents if doc["document_id"] == first["document_id"]) == 1
    if pipeline.collection is not None:
        indexed = pipeline.collection.get(where={"document_id": first["document_id"]})
        assert len(indexed["ids"]) == len(first["chunks"])
    assert len(first["chunks"]) == len(second["chunks"])


def test_pipeline_chunk_ids_are_unique_and_metadata_is_preserved(tmp_path):
    pipeline = DocMindPipeline(root_dir=tmp_path)
    pdf_path = _build_pdf(
        tmp_path,
        "multi_page.pdf",
        [
            "Alpha reported 12% growth in 2024. Beta reported 15% growth in 2024.",
            "The company expanded operations in Europe. The contract was renewed in 2025.",
        ],
    )

    result = pipeline.process_document(pdf_path, pdf_path.name)
    chunk_ids = [chunk["chunk_id"] for chunk in result["chunks"]]
    assert len(chunk_ids) == len(set(chunk_ids))
    assert all(chunk["document_id"] == result["document_id"] for chunk in result["chunks"])
    assert all(chunk["document_name"] == pdf_path.name for chunk in result["chunks"])
    assert {chunk["page_number"] for chunk in result["chunks"]} <= {1, 2}

    if pipeline.collection is not None:
        indexed = pipeline.collection.get(where={"document_id": result["document_id"]})
        assert len(indexed["ids"]) == len(result["chunks"])
        for metadata in indexed["metadatas"]:
            assert metadata["document_id"] == result["document_id"]
            assert metadata["document_name"] == pdf_path.name
            assert metadata["chunk_id"] in chunk_ids
            chunk = next(item for item in result["chunks"] if item["chunk_id"] == metadata["chunk_id"])
            assert metadata["page_number"] == chunk["page_number"]
            assert metadata["chunk_index"] == chunk["chunk_index"]
            assert metadata["source_type"] == "PDF_TEXT"


def test_pipeline_handles_streamlit_style_repeated_uploads(tmp_path):
    pipeline = DocMindPipeline(root_dir=tmp_path)
    pdf_path = _build_pdf(
        tmp_path,
        "rerun.pdf",
        [
            "Alpha reported a delay in Q1. Beta reported no delay in Q1.",
            "The audit concluded in March 2025.",
        ],
    )

    first = pipeline.process_document(pdf_path, pdf_path.name)
    second = pipeline.process_document(pdf_path, pdf_path.name)

    assert first["document_id"] == second["document_id"]
    assert first["status"] == "READY"
    assert second["status"] == "READY"
    if pipeline.collection is not None:
        stored = pipeline.collection.get(where={"document_id": first["document_id"]})
        assert len(stored["ids"]) == len(first["chunks"])


def test_uploaded_file_stream_can_be_processed_repeatedly(tmp_path):
    pipeline = DocMindPipeline(root_dir=tmp_path)
    content = b"Alpha reported 12% growth in 2024."
    uploaded = io.BytesIO(content)
    uploaded.name = "browser_upload.txt"

    first = pipeline.process_document(uploaded, uploaded.name)
    second = pipeline.process_document(uploaded, uploaded.name)

    assert first["document_id"] == second["document_id"]
    assert len(pipeline.documents) == 1
    if pipeline.collection is not None:
        stored = pipeline.collection.get(where={"document_id": first["document_id"]})
        assert len(stored["ids"]) == len(first["chunks"]) == 1


def test_ocr_extraction_keeps_page_and_source_provenance(tmp_path, monkeypatch):
    pipeline = DocMindPipeline(root_dir=tmp_path)
    source = tmp_path / "scanned.pdf"
    _build_pdf(tmp_path, source.name, [""])

    def fake_ocr(image, config):
        assert image is not None
        assert config == "--psm 6"
        return "Scanned page evidence."

    monkeypatch.setattr("docmind.pipeline.pytesseract.image_to_string", fake_ocr)

    result = pipeline.process_document(source, source.name)

    assert result["status"] == "READY"
    assert result["pages"][0]["page_number"] == 1
    assert result["pages"][0]["extraction_method"] == "OCR"
    assert result["chunks"][0]["source_type"] == "OCR"
    if pipeline.collection is not None:
        stored = pipeline.collection.get(where={"document_id": result["document_id"]})
        assert stored["metadatas"][0]["page_number"] == 1
        assert stored["metadatas"][0]["source_type"] == "OCR"


def test_search_is_scoped_to_current_document_ids(tmp_path):
    pipeline = DocMindPipeline(root_dir=tmp_path)
    source = tmp_path / "scoped.txt"
    source.write_text("Alpha document evidence about growth.", encoding="utf-8")
    result = pipeline.process_document(source, source.name)

    class FakeEmbeddingModel:
        def encode(self, texts, **kwargs):
            assert kwargs.get("convert_to_numpy") is True
            return [[0.1, 0.2, 0.3] for _ in texts]

    class FakeCollection:
        def __init__(self):
            self.where = None

        def query(self, **kwargs):
            self.where = kwargs.get("where")
            return {
                "documents": [["Alpha document evidence about growth."]],
                "metadatas": [[{
                    "document_id": result["document_id"],
                    "document_name": source.name,
                    "page_number": 1,
                    "chunk_id": result["chunks"][0]["chunk_id"],
                }]],
                "distances": [[0.1]],
            }

    collection = FakeCollection()
    pipeline.collection = collection
    pipeline.embedding_model = FakeEmbeddingModel()

    hits = pipeline.semantic_search("growth evidence")

    assert hits[0]["document_id"] == result["document_id"]
    assert collection.where == {"document_id": {"$in": [result["document_id"]]}}


def test_timeline_uses_chronological_date_sort(tmp_path):
    pipeline = DocMindPipeline(root_dir=tmp_path)
    pipeline.documents = [{
        "name": "dates.txt",
        "events": [
            {"page_number": 1, "date": "2025", "title": "Later", "evidence": "Later event."},
            {"page_number": 1, "date": "March 2, 2024", "title": "Earlier", "evidence": "Earlier event."},
        ],
    }]

    assert [event["title"] for event in pipeline.extract_timeline()] == ["Earlier", "Later"]


def test_empty_document_has_no_searchable_or_fabricated_answer(tmp_path):
    pipeline = DocMindPipeline(root_dir=tmp_path)
    source = tmp_path / "empty.txt"
    source.write_text("", encoding="utf-8")

    result = pipeline.process_document(source, source.name)

    assert result["status"] == "WARNING"
    assert result["chunks"] == []
    assert pipeline.semantic_search("anything") == []
    answer = pipeline.answer_question("What does it say?")
    assert answer["confidence"] == "Insufficient Evidence"
    assert answer["citations"] == []


def test_batch_validation_rejects_duplicate_ids_and_logs_diagnostics(tmp_path, caplog):
    pipeline = DocMindPipeline(root_dir=tmp_path)

    with pytest.raises(ValueError, match="Duplicate chunk IDs"):
        pipeline._validate_chunk_batch(
            ["same-id", "same-id"],
            ["first", "second"],
            [[0.1], [0.2]],
            [{}, {}],
            "duplicate.pdf",
        )

    assert "Duplicate chunk IDs in batch for duplicate.pdf" in caplog.text


def test_contradiction_negation_requires_a_matching_claim(tmp_path):
    pipeline = DocMindPipeline(root_dir=tmp_path)
    pipeline.documents = [{
        "name": "claims.txt",
        "claims": [
            {"subject": "Alpha", "relation": "reported", "obj": "notable growth"},
            {"subject": "Alpha", "relation": "reported", "obj": "strong growth"},
            {"subject": "Beta", "relation": "reported", "obj": "no delays"},
            {"subject": "Beta", "relation": "reported", "obj": "delays"},
        ],
    }]

    contradictions = pipeline.detect_contradictions()

    assert len(contradictions) == 2
    assert all(item["classification"] == "POTENTIAL_CONTRADICTION" for item in contradictions if item["claim_a"]["subject"] == "Alpha")
    beta = next(item for item in contradictions if item["claim_a"]["subject"] == "Beta")
    assert beta["classification"] == "EXPLICIT_CONTRADICTION"


def test_knowledge_graph_links_document_page_and_chunk():
    document = {
        "document_id": "doc-1",
        "name": "evidence.pdf",
        "pages": [{"page_number": 1}],
        "chunks": [{
            "chunk_id": "doc-1-chunk-1",
            "chunk_index": 1,
            "page_number": 1,
            "text": "Alpha reported growth.",
        }],
        "entities": [],
        "claims": [],
        "events": [],
    }

    graph = build_graph_from_documents([document])

    assert graph.has_edge("doc-1", "doc-1-page-1")
    assert graph.has_edge("doc-1-page-1", "doc-1-chunk-1")


def test_nvidia_request_uses_configured_bearer_token_and_model(monkeypatch):
    token = "unit-test-token"
    evidence = [{"document": "source.pdf", "page_number": 2, "text": "Alpha reported 12% growth."}]
    monkeypatch.setattr("docmind.llm.get_settings", lambda: {
        "llm_provider": "nvidia",
        "llm_api_key": token,
        "llm_model": "nvidia/nemotron-3-super-120b-a12b",
        "nvidia_base_url": "https://example.invalid/v1/",
    })
    captured = {}

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"choices": [{"message": {"content": "Alpha reported 12% growth. [S1]"}}]}

    def fake_post(url, **kwargs):
        captured["url"] = url
        captured.update(kwargs)
        return FakeResponse()

    monkeypatch.setattr("docmind.llm.requests.post", fake_post)

    answer = generate_grounded_answer("What did Alpha report?", evidence)

    assert captured["url"] == "https://example.invalid/v1/chat/completions"
    assert captured["headers"]["Authorization"] == f"Bearer {token}"
    assert captured["json"]["model"] == "nvidia/nemotron-3-super-120b-a12b"
    assert captured["json"]["chat_template_kwargs"] == {"enable_thinking": False}
    assert captured["timeout"] == 30
    assert answer["provider"] == "nvidia"
    assert answer["citations"][0]["page_number"] == 2


def test_pdf_to_chroma_retrieval_and_nvidia_answer_flow(tmp_path, monkeypatch):
    pdf_path = _build_pdf(
        tmp_path,
        "end_to_end.pdf",
        ["Project Orion reported 42% completion on January 15, 2025."],
    )
    pipeline = DocMindPipeline(root_dir=tmp_path)
    monkeypatch.setattr("docmind.llm.get_settings", lambda: {
        "llm_provider": "nvidia",
        "llm_api_key": "unit-test-token",
        "llm_model": "nvidia/nemotron-3-super-120b-a12b",
        "nvidia_base_url": "https://example.invalid/v1",
    })

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"choices": [{"message": {"content": "Project Orion was 42% complete. [S1]"}}]}

    def fake_post(url, **kwargs):
        assert url.endswith("/chat/completions")
        assert kwargs["headers"]["Authorization"] == "Bearer unit-test-token"
        return FakeResponse()

    monkeypatch.setattr("docmind.llm.requests.post", fake_post)

    document = pipeline.process_document(pdf_path, pdf_path.name)
    answer = pipeline.answer_question("What completion did Project Orion report?")

    assert document["status"] == "READY"
    assert document["chunks"]
    assert answer["provider"] == "nvidia"
    assert answer["citations"]
    assert answer["citations"][0]["document"] == pdf_path.name
    assert answer["citations"][0]["page_number"] == 1
    assert answer["citations"][0]["text"] in document["chunks"][0]["text"]


def test_nvidia_api_failure_is_not_silently_reported_as_success(monkeypatch):
    monkeypatch.setattr("docmind.llm.get_settings", lambda: {
        "llm_provider": "nvidia",
        "llm_api_key": "unit-test-token",
        "llm_model": "nvidia/nemotron-3-super-120b-a12b",
        "nvidia_base_url": "https://example.invalid/v1",
    })

    def failing_post(url, **kwargs):
        assert url.endswith("/chat/completions")
        assert kwargs["headers"]["Authorization"] == "Bearer unit-test-token"
        raise requests.ConnectionError("network unavailable")

    monkeypatch.setattr("docmind.llm.requests.post", failing_post)

    with pytest.raises(LLMServiceError, match="configured NVIDIA model could not answer"):
        generate_grounded_answer(
            "Question?",
            [{"document": "source.pdf", "page_number": 1, "text": "Evidence."}],
        )
