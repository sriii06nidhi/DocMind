"""DocMind package."""

from .config import get_settings
from .pipeline import DocMindPipeline

__all__ = ["DocMindPipeline", "get_settings"]
