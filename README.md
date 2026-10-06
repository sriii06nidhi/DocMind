# DocMind

DocMind is an evidence-first document intelligence application built with Python and Streamlit. It supports document upload, PDF extraction, OCR fallback, text chunking, semantic retrieval with ChromaDB, knowledge graph exploration, contradiction checks, timeline extraction, and grounded question answering.

## Features

- PDF and image document ingestion
- Text extraction with PyMuPDF and OCR fallback with Tesseract
- Sentence-transformer embeddings and semantic search
- Evidence-grounded Q&A through NVIDIA NIM, with a clearly identified local fallback when no API key is configured
- Entity, claim, event, and contradiction extraction
- NetworkX/PyVis knowledge graph
- Timeline and document comparison summaries
- Security-conscious configuration using environment variables

## Setup

1. Create a virtual environment and install dependencies.
2. Copy `.env.example` to `.env` and populate the required settings. For compatibility, an existing `.env.txt` is also loaded when a variable is not already defined by the environment or `.env`.
3. Run the app:

```bash
streamlit run app.py
```

## Environment variables

- `LLM_PROVIDER`: `nvidia` (default) or `local`
- `NVIDIA_API_KEY` or `LLM_API_KEY`: NVIDIA API key; keep it only in the ignored `.env` file or environment
- `LLM_MODEL`: model name for generation; if unset, `PRIMARY_MODEL`, then `FALLBACK_MODEL`, is used
- `NVIDIA_TIMEOUT_SECONDS`: request timeout in seconds (defaults to 30; values below 30 are raised to 30 for slower hosted models)
- `EMBEDDING_MODEL`: sentence-transformer model path/name
- `TESSERACT_PATH`: optional OCR binary path
- `CHROMA_PATH`: path for persistent Chroma storage
- `NVIDIA_BASE_URL`: base URL for NVIDIA APIs

The default model is `nvidia/nemotron-3-super-120b-a12b`. Copy `.env.example` to `.env` and add a valid NVIDIA API key locally. Do not use a committed example file for credentials.

## Notes

- Do not commit secrets to Git.
- The system requires evidence before answering document-specific questions.
- If no LLM API key is configured, the app uses a marked evidence-based local fallback rather than silently claiming the NVIDIA model answered.
- Configured NVIDIA API errors are reported to the user and are not silently disguised as successful model answers.
