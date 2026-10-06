# DocMind - System Architecture

## 1. Document Information

**Project Name:** DocMind

**Project Title:** An AI-Driven Framework for Intelligent Document Understanding and Cross-Document Knowledge Discovery

**Document:** System Architecture

**Purpose:** Define the complete technical architecture, component responsibilities, data flow, processing pipelines, and architectural principles of the DocMind system.

---

# 2. Architecture Overview

DocMind is designed as a layered AI-driven document intelligence system that transforms a collection of unstructured and semi-structured documents into an evidence-linked, semantically searchable, structured knowledge space.

The architecture follows the principle:

**Retrieve → Structure → Connect → Compare → Reason → Verify → Explain**

The system combines:

- Document processing
- OCR
- Natural Language Processing
- Semantic embeddings
- Vector retrieval
- Retrieval-Augmented Generation (RAG)
- Knowledge graphs
- Entity and claim extraction
- Cross-document reasoning
- Contradiction analysis
- Temporal reasoning
- Evidence and provenance tracking
- Explainable answer generation

The system must not be implemented as a simple PDF chatbot. The LLM must not be responsible for all reasoning. Retrieval, structured representations, graph relationships, evidence verification, and deterministic processing should perform as much of the reasoning as possible before information is passed to the LLM for explanation and response generation.

---

# 3. High-Level Architecture

The DocMind architecture consists of the following major layers:

1. Presentation Layer
2. Application and Orchestration Layer
3. Document Ingestion Layer
4. Document Processing and OCR Layer
5. Semantic and Structured Processing Layer
6. Knowledge Storage Layer
7. Retrieval and Intelligence Layer
8. Cross-Document Reasoning Layer
9. Evidence and Provenance Layer
10. LLM Generation Layer
11. Evaluation and Monitoring Layer

High-level flow:

User
↓
Presentation Layer
↓
Application Orchestrator
↓
Document Processing / Query Processing
↓
Semantic and Structured Representation
↓
Vector Store + Knowledge Graph + Provenance
↓
Retrieval and Reasoning
↓
Evidence Verification
↓
LLM Generation
↓
Explainable Output

---

# 4. Architectural Diagram

```text
                         ┌─────────────────────┐
                         │        USER         │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │  PRESENTATION LAYER │
                         │      Streamlit      │
                         │                     │
                         │ Upload │ Chat │     │
                         │ Search │ Compare    │
                         │ Timeline │ Graph    │
                         │ Evidence │ Reports  │
                         └──────────┬──────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │ APPLICATION / ORCHESTRATION   │
                    │             LAYER             │
                    │                               │
                    │ Query Router                  │
                    │ Pipeline Controller           │
                    │ Request Validation            │
                    │ Session Management             │
                    │ Error Handling                 │
                    └───────────────┬───────────────┘
                                    │
                  ┌─────────────────┴─────────────────┐
                  │                                   │
                  ▼                                   ▼
        ┌───────────────────┐              ┌───────────────────┐
        │ DOCUMENT PIPELINE │              │  QUERY PIPELINE   │
        └─────────┬─────────┘              └─────────┬─────────┘
                  │                                  │
                  ▼                                  ▼
        ┌───────────────────┐              ┌───────────────────┐
        │ EXTRACTION / OCR  │              │ QUERY UNDERSTAND. │
        │                   │              │                   │
        │ PyPDF             │              │ Intent             │
        │ Tesseract         │              │ Entities           │
        │ Page Detection    │              │ Query Expansion    │
        └─────────┬─────────┘              └─────────┬─────────┘
                  │                                  │
                  ▼                                  │
        ┌─────────────────────────────────────────────┐
        │     SEMANTIC & STRUCTURED PROCESSING       │
        │                                             │
        │ Chunking                                    │
        │ Metadata Extraction                         │
        │ Entity Extraction                           │
        │ Claim Extraction                            │
        │ Relationship Extraction                     │
        │ Date/Event Extraction                       │
        └─────────────────────┬───────────────────────┘
                              │
             ┌────────────────┼─────────────────┐
             │                │                 │
             ▼                ▼                 ▼
      ┌────────────┐  ┌───────────────┐  ┌───────────────┐
      │  VECTOR    │  │ KNOWLEDGE     │  │ PROVENANCE    │
      │  STORE     │  │ GRAPH         │  │ STORE         │
      │            │  │               │  │               │
      │ ChromaDB   │  │ NetworkX      │  │ Documents     │
      │ Embeddings │  │ Entities      │  │ Pages         │
      │ Chunks     │  │ Claims        │  │ Chunks        │
      │ Metadata   │  │ Relations     │  │ Evidence      │
      └─────┬──────┘  │ Events        │  │ Confidence    │
            │         └───────┬───────┘  └───────┬───────┘
            │                 │                  │
            └─────────────────┼──────────────────┘
                              │
                              ▼
                   ┌────────────────────────┐
                   │ RETRIEVAL & INTELLIGENCE│
                   │         LAYER           │
                   │                         │
                   │ Semantic Retrieval      │
                   │ Hybrid Retrieval        │
                   │ Reranking               │
                   │ Graph Retrieval          │
                   │ RAG                     │
                   └────────────┬────────────┘
                                │
                                ▼
                   ┌────────────────────────┐
                   │ CROSS-DOCUMENT         │
                   │ REASONING              │
                   │                        │
                   │ Claim Comparison       │
                   │ Entity Resolution      │
                   │ Relationship Analysis  │
                   │ Information Changes     │
                   └────────────┬───────────┘
                                │
                    ┌───────────┴────────────┐
                    │                        │
                    ▼                        ▼
          ┌──────────────────┐     ┌──────────────────┐
          │ CONTRADICTION    │     │ TEMPORAL         │
          │ ENGINE           │     │ REASONING        │
          │                  │     │                  │
          │ Agreement        │     │ Date Extraction  │
          │ Potential        │     │ Event Ordering   │
          │ Explicit         │     │ Timeline         │
          │ Superseded       │     │ Temporal Conflict│
          │ Insufficient     │     │ Detection        │
          └────────┬─────────┘     └────────┬─────────┘
                   │                        │
                   └────────────┬───────────┘
                                │
                                ▼
                    ┌────────────────────────┐
                    │ EVIDENCE & PROVENANCE  │
                    │         ENGINE          │
                    │                         │
                    │ Evidence Collection     │
                    │ Source Verification     │
                    │ Page Mapping            │
                    │ Chunk Mapping           │
                    │ Confidence              │
                    │ Citation Generation     │
                    └────────────┬───────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │    LLM GENERATION      │
                    │                        │
                    │ Context Assembly       │
                    │ Evidence-Constrained   │
                    │ Answer Generation      │
                    │ Uncertainty Handling   │
                    └────────────┬───────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │  EXPLAINABLE OUTPUT    │
                    │                        │
                    │ Answer                 │
                    │ Sources                │
                    │ Evidence               │
                    │ Confidence             │
                    │ Graph                  │
                    │ Timeline               │
                    │ Contradictions         │
                    └────────────────────────┘