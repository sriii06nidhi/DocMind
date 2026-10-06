# DocMind - Schema Design

## 1. Document Information

**Project Name:** DocMind

**Project Title:** An AI-Driven Framework for Intelligent Document Understanding and Cross-Document Knowledge Discovery

**Document:** Schema Design

**Purpose:** Define the logical data structures, entities, relationships, metadata, provenance information, vector records, knowledge graph structures, and processing states required by the DocMind system.

---

# 2. Schema Design Overview

DocMind does not depend on a single traditional relational database.

The system uses a hybrid data architecture consisting of:

1. Document/File Storage
2. Structured Metadata
3. Vector Storage
4. Knowledge Graph Storage
5. Provenance and Evidence Records
6. Processing and Evaluation Records

The schema is designed around the principle:

**Every important piece of extracted knowledge must remain traceable to its original document, page, chunk, and evidence whenever possible.**

The logical data model must remain independent from any specific database implementation.

---

# 3. Data Architecture

The DocMind data architecture can be represented as:

```text
                    DOCUMENT
                       │
                       ▼
                  PAGE / CONTENT
                       │
                       ▼
                     CHUNK
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
       EMBEDDING     ENTITY       CLAIM
          │            │            │
          │            │            ▼
          │            │          EVIDENCE
          │            │            │
          │            ▼            │
          │        RELATIONSHIP     │
          │            │            │
          │            ▼            │
          │          EVENT          │
          │            │            │
          └────────────┼────────────┘
                       ▼
                KNOWLEDGE GRAPH
                       │
                       ▼
              REASONING / ANALYSIS
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
   CONTRADICTION    TIMELINE     ANSWER
          │            │            │
          └────────────┼────────────┘
                       ▼
                  PROVENANCE