from __future__ import annotations

import logging
from typing import Any, Dict, List

import requests

from .config import get_settings

logger = logging.getLogger(__name__)


class LLMServiceError(RuntimeError):
    """Raised when a configured language-model provider cannot return an answer."""


def _evidence_answer(evidence: List[dict], status: str) -> Dict[str, Any]:
    excerpt = evidence[0].get("text", "").strip()
    if len(excerpt) > 260:
        excerpt = excerpt[:257].rsplit(" ", 1)[0] + "..."
    summary = "The indexed evidence states: " + excerpt
    citations = [
        {
            "document": item.get("document"),
            "page_number": item.get("page_number"),
            "text": item.get("text"),
        }
        for item in evidence[:3]
    ]
    return {
        "answer": summary,
        "confidence": "Moderate",
        "citations": citations,
        "sources": citations,
        "provider": "local",
        "llm_status": status,
    }


def generate_grounded_answer(question: str, evidence: List[dict]) -> Dict[str, Any]:
    if not evidence:
        return {
            "answer": "The available documents do not contain enough evidence to answer this question reliably.",
            "confidence": "Insufficient Evidence",
            "citations": [],
            "sources": [],
            "provider": "none",
            "llm_status": "insufficient_evidence",
        }

    settings = get_settings()
    provider = (settings.get("llm_provider") or "local").lower()
    api_key = settings.get("llm_api_key")
    if provider == "local" or not api_key:
        status = "local_provider" if provider == "local" else "api_key_missing"
        return _evidence_answer(evidence, status)
    if provider != "nvidia":
        raise LLMServiceError(f"Unsupported LLM provider '{provider}'. Configure 'nvidia' or 'local'.")

    evidence_text = "\n\n".join(
        f"[S{index}] {item.get('document')} (page {item.get('page_number')}): {item.get('text')}"
        for index, item in enumerate(evidence, start=1)
    )
    prompt = (
        "Answer using only the evidence below. Cite each supporting statement with its [S#] source marker. "
        "If the evidence does not answer the question, say so. Do not invent facts.\n\n"
        f"Question: {question}\n\nEvidence:\n{evidence_text}"
    )
    base_url = str(settings.get("nvidia_base_url", "https://integrate.api.nvidia.com/v1")).rstrip("/")
    try:
        response = requests.post(
            f"{base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.get("llm_model", "nvidia/nemotron-3-super-120b-a12b"),
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
                "max_tokens": 500,
                "chat_template_kwargs": {"enable_thinking": False},
            },
            timeout=settings.get("nvidia_timeout_seconds", 30),
        )
        response.raise_for_status()
        payload = response.json()
        content = payload["choices"][0]["message"]["content"]
        if not isinstance(content, str) or not content.strip():
            raise ValueError("The model returned an empty answer.")
    except (requests.RequestException, ValueError, KeyError, IndexError, TypeError) as exc:
        logger.exception("NVIDIA chat completion failed for model %s", settings.get("llm_model"))
        raise LLMServiceError(
            "The configured NVIDIA model could not answer this question. Check the model, API key, and network connection."
        ) from exc

    citations = [
        {
            "document": item.get("document"),
            "page_number": item.get("page_number"),
            "text": item.get("text"),
        }
        for item in evidence[:3]
    ]
    return {
        "answer": content.strip(),
        "confidence": "Moderate",
        "citations": citations,
        "sources": citations,
        "provider": "nvidia",
        "llm_status": "complete",
    }
