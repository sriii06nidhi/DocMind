from __future__ import annotations

import os
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]


def _read_env_file(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}

    values: dict[str, str] = {}
    colon_labels = {
        "api key": "NVIDIA_API_KEY",
        "nvidia api key": "NVIDIA_API_KEY",
        "llm api key": "LLM_API_KEY",
        "primary model": "PRIMARY_MODEL",
        "fallback model": "FALLBACK_MODEL",
        "chat fallback model": "CHAT_FALLBACK_MODEL",
        "safety model": "SAFETY_MODEL",
        "nvidia base url": "NVIDIA_BASE_URL",
        "nvidia timeout seconds": "NVIDIA_TIMEOUT_SECONDS",
    }
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        assignment = re.match(r"^(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$", stripped)
        if assignment:
            key, value = assignment.groups()
        elif ":" in stripped:
            label, value = stripped.split(":", 1)
            normalized_label = re.sub(r"[^a-z0-9]+", " ", label.strip().lower()).strip()
            key = colon_labels.get(normalized_label)
            if key is None:
                continue
        else:
            continue

        parsed_value = value.strip()
        if parsed_value.startswith(("'", '"')):
            quote = parsed_value[0]
            if len(parsed_value) >= 2 and parsed_value.endswith(quote):
                parsed_value = parsed_value[1:-1]
        else:
            parsed_value = re.split(r"\s+#", parsed_value, maxsplit=1)[0].rstrip()
        values[key] = parsed_value
    return values


_FILE_SETTINGS: dict[str, str] = {}
for _env_path in (BASE_DIR / ".env.txt", BASE_DIR / ".env"):
    _FILE_SETTINGS.update(_read_env_file(_env_path))


def get_setting(name: str, default: str | None = None) -> str | None:
    value = os.getenv(name)
    if value is not None:
        return value.strip()
    return _FILE_SETTINGS.get(name, default)


def get_settings() -> dict:
    chroma_path = Path(get_setting("CHROMA_PATH") or (BASE_DIR / "data" / "chroma")).expanduser()
    if not chroma_path.is_absolute():
        chroma_path = BASE_DIR / chroma_path
    timeout_value = get_setting("NVIDIA_TIMEOUT_SECONDS", "30")
    try:
        nvidia_timeout_seconds = max(30, int(timeout_value or "30"))
    except ValueError:
        nvidia_timeout_seconds = 30
    return {
        "llm_provider": get_setting("LLM_PROVIDER", "nvidia").lower(),
        "llm_api_key": get_setting("LLM_API_KEY") or get_setting("NVIDIA_API_KEY"),
        "llm_model": (
            get_setting("LLM_MODEL")
            or get_setting("PRIMARY_MODEL")
            or get_setting("CHAT_FALLBACK_MODEL")
            or get_setting("FALLBACK_MODEL")
            or "nvidia/nemotron-3-super-120b-a12b"
        ),
        "nvidia_timeout_seconds": nvidia_timeout_seconds,
        "embedding_model": get_setting("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"),
        "tesseract_path": get_setting("TESSERACT_PATH"),
        "chroma_path": str(chroma_path),
        "nvidia_base_url": get_setting("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1"),
        "base_dir": str(BASE_DIR),
    }
