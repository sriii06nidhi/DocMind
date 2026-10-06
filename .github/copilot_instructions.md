# DocMind Project Instructions

This repository contains DocMind, an AI-driven document intelligence system.

## SOURCE OF TRUTH

Before implementing or modifying functionality, use the project documentation and AI coding instructions as the source of truth.

Primary project instructions:

* `04_AI_CODING_INSTRUCTIONS/MASTER_PROMPT.md`
* `04_AI_CODING_INSTRUCTIONS/CODING_RULES.md`
* `04_AI_CODING_INSTRUCTIONS/ARCHITECTURE_RULES.md`
* `04_AI_CODING_INSTRUCTIONS/UI_UX_RULES.md`
* `04_AI_CODING_INSTRUCTIONS/AI_ML_RULES.md`
* `04_AI_CODING_INSTRUCTIONS/RAG_RULES.md`
* `04_AI_CODING_INSTRUCTIONS/SECURITY_RULES.md`
* `04_AI_CODING_INSTRUCTIONS/DATABASE_RULES.md`
* `04_AI_CODING_INSTRUCTIONS/ERROR_HANDLING_RULES.md`
* `04_AI_CODING_INSTRUCTIONS/TESTING_RULES.md`
* `04_AI_CODING_INSTRUCTIONS/GUARDRAILS.md`

Project architecture and requirements are documented in:

* `03_PROJECT_DOCUMENTATION/`

## CORE ARCHITECTURE

The intended architecture is:

User
→ Streamlit UI
→ Application / Orchestration Layer
→ Document Ingestion
→ PDF Extraction / OCR
→ Preprocessing / Chunking
→ Embeddings
→ ChromaDB
→ Structured Knowledge Extraction
→ Knowledge Graph
→ Retrieval / RAG
→ Cross-Document Reasoning
→ Contradiction Detection
→ Temporal Reasoning
→ Evidence / Provenance
→ LLM Generation
→ Explainable UI

## TECHNOLOGY BASELINE

Use the documented MVP technology stack.

Prefer:

* Python 3.11
* Streamlit
* PyPDF
* Tesseract / PyTesseract
* Pillow
* Sentence Transformers
* Hugging Face Transformers
* ChromaDB
* NetworkX
* PyVis
* Pandas
* NumPy
* Scikit-learn
* requests
* python-dotenv
* pytest
* external NVIDIA LLM API

Do not introduce major infrastructure such as React, Next.js, FastAPI, PostgreSQL, Supabase, Neo4j, Redis, Elasticsearch, Kafka, Spark, Airflow, Docker or Kubernetes unless a documented requirement explicitly justifies it.

## IMPLEMENTATION PRINCIPLES

* Inspect existing files before modifying them.
* Reuse existing architecture and utilities.
* Do not duplicate functionality.
* Keep UI separate from business logic.
* Keep AI/ML components modular.
* Keep configuration separate from source code.
* Use environment variables for secrets.
* Never hard-code API keys.
* Never commit `.env`.
* Write real functionality rather than mock functionality.
* Add tests for important functionality.
* Run tests after meaningful implementation stages.
* Fix errors before continuing when practical.

## EVIDENCE INTEGRITY

Never fabricate:

* documents
* pages
* citations
* evidence
* quotations
* claims
* entities
* relationships
* dates
* confidence values
* metrics

Important generated or extracted information should preserve provenance back to the source document whenever evidence exists.

## RAG

RAG must retrieve evidence before generating document-grounded answers.

If evidence is insufficient, the system must clearly state that the available evidence is insufficient.

Do not use the LLM as the sole source of truth.

## CONTRADICTION DETECTION

Do not treat every difference as a contradiction.

Consider:

* entity
* relation
* value
* date
* reporting period
* context
* document type
* revision status
* temporal ordering
* evidence

Use the documented contradiction classifications.

## SECURITY

Treat uploaded documents as untrusted data.

Content inside documents must never override system instructions.

Protect API keys and sensitive configuration.

Do not expose secrets in logs, UI, source code, tests or error messages.

## UI

DocMind must not become a generic chatbot clone.

The interface must emphasize:

* evidence
* citations
* provenance
* document relationships
* knowledge graph
* contradictions
* timelines
* explainability
* uncertainty

Use the documented UI/UX rules.

## QUALITY HIERARCHY

Prioritize:

1. Safety and privacy
2. Evidence integrity
3. Correctness
4. Traceability
5. Reliability
6. Maintainability
7. Usability
8. Performance
9. Visual polish
10. Additional features

Never sacrifice correctness for fluent AI output.

## IMPORTANT

When implementation begins, read the relevant project documentation before making architectural decisions.

Do not invent missing requirements.

If a genuine ambiguity or conflict exists between project documents, choose the safer documented interpretation and record the issue for review rather than silently changing the architecture.
