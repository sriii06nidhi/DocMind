# DocMind: UI/UX RULES

## 1. Purpose

This document defines the user interface and user experience rules for the DocMind application.

The UI must reflect the actual intelligence architecture of DocMind:

```text
Upload
 ↓
Understand
 ↓
Search
 ↓
Connect
 ↓
Compare
 ↓
Reason
 ↓
Verify
 ↓
Explain
```

DocMind must not look or behave like a generic PDF chatbot.

The interface should communicate that the system can:

* Understand multiple documents
* Search across documents
* Extract entities and claims
* Explore relationships
* Compare information
* Detect potential contradictions
* Build timelines
* Show supporting evidence
* Explain how an answer was produced

The UI must prioritize:

```text
Clarity
Evidence
Traceability
Consistency
Usability
Trust
```

---

# 2. Core UX Philosophy

The central UX principle is:

> **Show the answer, but make the evidence behind the answer easy to inspect.**

Users should never have to trust an AI-generated answer blindly.

The interface should allow the user to move from:

```text
Answer
 ↓
Reasoning
 ↓
Evidence
 ↓
Source
 ↓
Original document
```

The application should therefore expose evidence progressively instead of overwhelming the user with technical implementation details.

---

# 3. Product Identity

DocMind should visually communicate:

```text
Professional
Intelligent
Analytical
Evidence-driven
Modern
Reliable
Research-oriented
```

Avoid making the application look like:

```text
A generic AI chatbot
A social media application
A gaming interface
A flashy AI demo
A simple PDF viewer
```

The interface should feel closer to an **intelligent research and document analysis workspace**.

---

# 4. Design Principles

## 4.1 Evidence First

Whenever the system produces a document-derived conclusion, the user should be able to identify its source.

For example:

```text
Answer

The contract was terminated in March 2025.

Sources
Contract_Final.pdf · Page 12
```

The source should be clickable or expandable.

---

## 4.2 Progressive Disclosure

Do not display every internal detail immediately.

Use layers:

```text
Level 1:
Answer

Level 2:
Key evidence

Level 3:
Source details

Level 4:
Detailed reasoning / comparison

Level 5:
Raw document
```

This keeps the interface understandable while still providing deep transparency.

---

## 4.3 User Control

The user should always understand:

* What documents are loaded
* What the system is analyzing
* What query is being processed
* Whether the answer is based on sufficient evidence
* Which sources support the answer

Avoid hidden processing wherever possible.

---

## 4.4 Minimal Cognitive Load

The application may contain sophisticated AI/ML functionality, but the user should not need to understand:

* embeddings
* vector databases
* transformers
* graph algorithms
* chunking
* retrieval pipelines

unless they explicitly open a technical information section.

Technical complexity should remain behind the interface.

---

# 5. Overall Application Layout

Use a consistent application shell.

Recommended structure:

```text
┌────────────────────────────────────────────────────────────┐
│ DOCMIND                                      Status / Help │
├───────────────┬────────────────────────────────────────────┤
│               │                                            │
│ Dashboard     │                                            │
│ Documents     │              Main Workspace               │
│ Search        │                                            │
│ Knowledge     │                                            │
│ Graph         │                                            │
│ Contradictions│                                            │
│ Timeline      │                                            │
│ Compare       │                                            │
│ Settings      │                                            │
│               │                                            │
└───────────────┴────────────────────────────────────────────┘
```

Use a persistent navigation area so users can easily switch between major analytical views.

---

# 6. Navigation Structure

The primary navigation should contain:

```text
Dashboard
Documents
Ask DocMind
Knowledge Graph
Compare
Contradictions
Timeline
Evaluation / System
Settings
```

The exact visibility of advanced sections may depend on the maturity of the application.

---

# 7. Dashboard

## Purpose

The dashboard provides a high-level overview of the current document workspace.

It should answer:

> "What is currently inside DocMind and what can I do with it?"

## Recommended components

```text
Documents
Total documents
Pages processed
Entities discovered
Claims extracted
Potential contradictions
Timeline events
```

Example:

```text
DOCUMENTS        12

PAGES            247

ENTITIES         684

CLAIMS           1,342

CONFLICTS        17

EVENTS           93
```

These statistics should be informative rather than decorative.

---

# 8. Document Library

The document library should provide a clear overview of uploaded documents.

Each document card or row should show:

```text
Filename
Document type
Page count
Processing status
Upload date
Processing warnings
```

Example:

```text
┌────────────────────────────────────────────┐
│ Contract_2025.pdf                          │
│ 24 pages                                    │
│ Processed ✓                                 │
│ 12 entities · 36 claims                     │
└────────────────────────────────────────────┘
```

---

# 9. Document Processing States

The UI must clearly communicate processing state.

Use states such as:

```text
UPLOADING
PROCESSING
OCR PROCESSING
EXTRACTING
INDEXING
READY
WARNING
FAILED
```

Never leave the user wondering whether the application is still processing a document.

Example:

```text
Contract.pdf

✓ Uploaded
✓ Text extracted
✓ OCR checked
✓ Chunks created
● Building knowledge representation
○ Ready
```

---

# 10. Upload Experience

The upload interface should be simple.

Recommended:

```text
┌──────────────────────────────────────────────┐
│                                              │
│       Drag & Drop documents here             │
│                                              │
│       or                                     │
│                                              │
│       [ Browse Files ]                       │
│                                              │
│       Supported: PDF                         │
│                                              │
└──────────────────────────────────────────────┘
```

Do not immediately expose technical settings such as:

```text
chunk size
embedding dimensions
vector distance
OCR engine
```

These should remain advanced configuration options.

---

# 11. Upload Validation

Before processing, clearly communicate problems such as:

```text
Unsupported file
Corrupted PDF
Empty document
OCR required
Duplicate document
File too large
```

Use human-readable messages.

Bad:

```text
PDFParserException: XRef table invalid
```

Better:

```text
This PDF could not be processed because its internal structure appears to be corrupted.
Please try another copy of the file.
```

Technical error details may be available under:

```text
Show technical details
```

---

# 12. Ask DocMind Interface

The main query interface should be the central interaction point.

Recommended:

```text
┌─────────────────────────────────────────────────────────┐
│ Ask DocMind                                             │
│                                                         │
│ What changed between the 2024 and 2025 reports?        │
│                                                         │
│ [ Ask ]                                                 │
└─────────────────────────────────────────────────────────┘
```

The input should support natural language.

Users should not need special commands.

---

# 13. Query Suggestions

When no query exists, provide useful example questions.

Examples:

```text
What are the main findings across these reports?

Which documents mention Company X?

What changed between the two contracts?

Are there conflicting revenue figures?

Show the timeline of the project.

How is Person A connected to Company B?
```

Suggestions should demonstrate the system's capabilities.

---

# 14. Query Classification

The UI may internally classify queries as:

```text
Document QA
Cross-document analysis
Comparison
Contradiction analysis
Timeline query
Entity query
Graph query
Global corpus analysis
```

This classification should normally remain invisible to users.

If displayed, present it in a simple form such as:

```text
Analysis type: Cross-document comparison
```

Do not expose internal routing terminology.

---

# 15. Answer Presentation

Answers should have a clear hierarchy.

Recommended:

```text
Answer
────────────

The company's reported revenue increased from
$3.9M in 2024 to $4.6M in 2025.

Evidence
────────────

1. Annual_Report_2024.pdf · Page 18
2. Annual_Report_2025.pdf · Page 21

Confidence
────────────

High
```

Avoid presenting a large block of unstructured text.

---

# 16. Evidence Panel

Every document-grounded answer should have an evidence section.

Recommended structure:

```text
Evidence

┌─────────────────────────────────────────────┐
│ Annual_Report_2025.pdf                      │
│ Page 21                                     │
│                                             │
│ "..."                                       │
│                                             │
│ [Open document]                             │
└─────────────────────────────────────────────┘
```

The evidence should be visually distinct from AI-generated interpretation.

---

# 17. Distinguish Facts From AI Interpretation

The UI should visually differentiate:

```text
Source fact
AI interpretation
Detected relationship
Potential contradiction
System uncertainty
```

For example:

```text
SOURCE FACT
Revenue was reported as $3.9M.

SYSTEM ANALYSIS
This differs from the $4.2M value reported in another
document for the same reporting period.

STATUS
Potential contradiction
```

This prevents users from confusing generated reasoning with original document content.

---

# 18. Citation Rules

Citations should contain:

```text
Document name
Page number
Relevant evidence
```

Example:

```text
[1] Financial_Report.pdf — Page 14
```

Clicking or expanding the citation should reveal the supporting passage.

Never display:

```text
Source: Unknown
Page: 0
```

if the system does not actually know the source.

Never invent citation information.

---

# 19. Confidence Indicators

Confidence should be displayed carefully.

Recommended categories:

```text
High confidence
Moderate confidence
Low confidence
Insufficient evidence
```

Avoid presenting arbitrary numerical confidence such as:

```text
97.83%
```

unless the underlying model and calibration justify that number.

Confidence should communicate uncertainty, not create false precision.

---

# 20. Insufficient Evidence UX

If the evidence is insufficient, the UI should clearly say so.

Example:

```text
Insufficient evidence

The available documents do not provide enough information
to answer this question reliably.

Related evidence:
• Document A — Page 4
• Document C — Page 11
```

Never force the LLM to produce an answer merely because the user asked a question.

---

# 21. Cross-Document Comparison UI

Comparison should use a structured layout.

Recommended:

```text
                 Document A       Document B
------------------------------------------------
Revenue          $4.2M             $3.9M
Employees        124               131
Contract status  Active            Terminated
Date             2024              2025
```

Below each row, allow the user to inspect evidence.

This is preferable to presenting a long AI-generated comparison paragraph.

---

# 22. Contradiction Dashboard

Contradictions should have a dedicated view.

Recommended:

```text
Contradictions

17 potential conflicts detected

┌─────────────────────────────────────────────┐
│ Revenue                                      │
│                                             │
│ Report A: $4.2M                             │
│ Report B: $3.9M                             │
│                                             │
│ Classification: Potential contradiction    │
│ Confidence: Moderate                        │
│                                             │
│ [Compare Evidence]                          │
└─────────────────────────────────────────────┘
```

---

# 23. Contradiction Severity

Use understandable classifications:

```text
Agreement
Potential contradiction
Explicit contradiction
Superseded information
Insufficient context
```

Do not use alarming visual language for every difference.

A difference is not automatically a contradiction.

---

# 24. Contradiction Explanation

When the user opens a contradiction, display:

```text
Claim A
Source
Page
Evidence

vs.

Claim B
Source
Page
Evidence

Why they may conflict

Temporal context

Classification

Confidence
```

Example:

```text
Why this was flagged:

Both documents report revenue for FY2024,
but they provide different values.

Possible explanation:
The second document may represent an audited revision.
```

The interface should distinguish detected conflict from possible explanation.

---

# 25. Timeline UI

The timeline should present events chronologically.

Example:

```text
2024
 │
 ├── June
 │   Contract signed
 │
 ├── September
 │   Contract modified
 │
2025
 │
 ├── January
 │   Contract extended
 │
 └── March
     Contract terminated
```

Each event should be expandable.

Expanded event:

```text
March 2025

Contract terminated

Source:
Contract_Final.pdf

Page:
12

Evidence:
[relevant passage]
```

---

# 26. Timeline Conflict Visualization

Potential temporal conflicts should be shown separately from normal events.

Example:

```text
⚠ Potential temporal conflict

Document A:
Contract ended — March 2025

Document B:
Contract active — April 2025

[Compare Evidence]
```

The system must not automatically declare which source is correct.

---

# 27. Knowledge Graph UI

The graph should help users understand relationships rather than simply display a visually impressive network.

Nodes may represent:

```text
Person
Organization
Document
Claim
Event
Location
Product
```

Edges may represent:

```text
works_for
owns
acquired
signed
mentions
related_to
contradicts
```

---

# 28. Graph Interaction

The graph should support:

```text
Zoom
Pan
Node selection
Relationship inspection
Filtering
Search
Reset view
```

Selecting a node should show:

```text
Entity
Type
Related entities
Supporting documents
Claims
Evidence
```

---

# 29. Avoid Graph Overload

Do not display the entire knowledge graph by default if it contains hundreds or thousands of nodes.

Instead:

```text
User selects entity
        ↓
Show local neighborhood
        ↓
Expand if required
```

This reduces visual clutter.

---

# 30. Entity-Centric Exploration

Example:

```text
Company A

Relationships
────────────────────
Acquired → Company B
Works with → Person C
Mentioned in → Report 2025
Related project → Project X

Sources
────────────────────
Report_A.pdf
Contract_B.pdf
Project_Report.pdf
```

This creates a useful research workflow.

---

# 31. Search Interface

Search should support both:

```text
Semantic search
Exact search
```

The user should be able to search naturally.

Example:

```text
Search:
employee termination
```

Results should show:

```text
Document
Page
Relevant passage
Relevance
```

---

# 32. Search Result Design

Recommended:

```text
Search Results — 12 matches

1. HR_Report.pdf
   Page 8

   "...employee termination..."

2. Contract.pdf
   Page 14

   "...termination clause..."
```

Avoid showing only filenames without contextual evidence.

---

# 33. Document Viewer

When users inspect a source, provide:

```text
Document
Page navigation
Relevant highlighted passage
Source metadata
```

If technically practical, the application should open the exact page associated with evidence.

The evidence should be visually highlighted where possible.

---

# 34. Loading States

AI processing can take time.

Never show a blank screen.

Use meaningful progress indicators:

```text
Processing document...

✓ Reading document
✓ Extracting text
✓ Checking OCR
● Generating embeddings
○ Extracting claims
○ Building knowledge graph
```

For queries:

```text
Searching documents...
Analyzing relevant claims...
Checking for conflicting evidence...
Preparing answer...
```

Do not pretend that a stage completed if it did not.

---

# 35. Empty States

Every major screen should have a useful empty state.

Example:

```text
No documents yet.

Upload your first PDF to begin building
your DocMind knowledge space.

[Upload Document]
```

For contradictions:

```text
No contradictions detected.

This does not necessarily mean that all documents
are perfectly consistent. It means no conflicts were
identified by the current analysis.
```

This wording avoids making an unsupported claim.

---

# 36. Error States

Errors should be actionable.

Bad:

```text
Error 500
```

Better:

```text
The AI service could not process this request.

Possible causes:
• Temporary service issue
• Invalid configuration
• Network problem

[Try Again]
```

If retrying is possible, provide a retry action.

---

# 37. Visual Design

The visual language should be:

```text
Clean
Professional
Minimal
Structured
Readable
Data-oriented
```

Use visual hierarchy rather than excessive decoration.

Prioritize:

```text
Typography
Spacing
Cards
Borders
Panels
Icons
Status indicators
```

Avoid excessive gradients, animations, shadows, and decorative elements.

---

# 38. Color Usage

Color should communicate meaning rather than decoration.

Use consistent semantic meanings:

```text
Success / Agreement
Warning / Potential conflict
Error / Processing failure
Information / Evidence
Neutral / Metadata
```

Do not rely on color alone.

For example:

```text
⚠ Potential contradiction
```

should remain understandable even without color.

---

# 39. Typography

Typography must prioritize readability.

Recommended hierarchy:

```text
Application title
Page title
Section heading
Card heading
Body text
Metadata
Evidence text
```

Evidence text should be easy to read because users may need to compare it carefully.

Avoid very small text for citations or evidence.

---

# 40. Responsive Layout

The application should remain usable on different screen sizes.

The primary target is desktop because document analysis benefits from larger screens.

However:

```text
Desktop → Full analytical workspace
Tablet  → Reduced panels
Mobile  → Simplified reading and search
```

Do not attempt to fit every graph and comparison panel onto a small screen simultaneously.

---

# 41. Accessibility

The UI should follow basic accessibility principles.

Requirements:

```text
Readable text
Sufficient contrast
Keyboard-friendly controls
Clear labels
Non-color-only status indicators
Meaningful error messages
Consistent navigation
```

Buttons should clearly describe their actions.

Prefer:

```text
Compare Evidence
```

over:

```text
Click Here
```

---

# 42. User Workflow

The primary user journey should be:

```text
1. Open DocMind
       ↓
2. Upload documents
       ↓
3. Wait for processing
       ↓
4. View document workspace
       ↓
5. Ask a question or select an analysis
       ↓
6. Review answer
       ↓
7. Inspect evidence
       ↓
8. Explore relationships / contradictions / timeline
       ↓
9. Verify against source document
```

The UI should make this journey obvious.

---

# 43. Advanced Analysis Workflow

For a complex question:

```text
User Query
    ↓
Retrieve relevant documents
    ↓
Retrieve relevant claims
    ↓
Identify entities
    ↓
Compare information
    ↓
Check temporal context
    ↓
Check contradictions
    ↓
Verify evidence
    ↓
Generate explanation
```

The user should not have to manually execute every step.

DocMind should orchestrate the process automatically.

---

# 44. Do Not Expose Internal Architecture Unnecessarily

Avoid exposing terms such as:

```text
Embedding vector
Cosine similarity
Chunk ID
Vector distance
Retriever pipeline
NLI logits
Graph traversal algorithm
```

unless the user opens an advanced technical/debugging view.

Instead show:

```text
Relevant evidence
Related information
Potential conflict
Supporting source
Confidence
```

---

# 45. Advanced Technical View

Because DocMind is an academic/engineering project, an optional technical view can be included.

It may show:

```text
Processing pipeline
Retrieved chunks
Model information
Embedding model
Retrieval score
Graph relationships
Processing time
System logs
```

This should be separated from the normal user workflow.

Recommended label:

```text
Advanced / Technical Details
```

---

# 46. Trust and Transparency Rules

The UI must never create false certainty.

Avoid:

```text
This is definitely correct.
```

Prefer:

```text
High-confidence answer supported by 3 sources.
```

Avoid:

```text
The documents are contradictory.
```

when the model has only detected a potential conflict.

Prefer:

```text
Potential contradiction detected between two claims.
```

---

# 47. Privacy UX

Users should be informed that their documents are being processed.

The application should clearly communicate:

```text
Documents currently loaded
Processing status
Data handling where applicable
External API usage where applicable
```

Do not expose document contents in system logs or debug panels by default.

---

# 48. API / LLM Failure UX

If the external LLM is unavailable, the application should fail gracefully.

Example:

```text
AI generation is currently unavailable.

Your documents are still available for:
• Search
• Document browsing
• Previously indexed information

[Retry]
```

Do not make the entire UI appear broken when one external service fails.

---

# 49. Performance UX

The interface should provide immediate feedback for long-running operations.

For example:

```text
Processing 8 documents

██████████████░░░░░░ 72%

6 of 8 documents completed
```

For large operations, show:

```text
Current document
Current stage
Overall progress
Estimated state
```

Do not display fabricated completion percentages if actual progress is unavailable.

---

# 50. State Preservation

The application should preserve useful session state where possible.

For example, after navigating away and returning, preserve:

```text
Selected documents
Current query
Selected entity
Graph filters
Comparison selection
Timeline filters
```

Avoid unexpectedly resetting the user's analysis.

---

# 51. Consistency Rules

The same concept must have the same name throughout the application.

For example, do not use:

```text
Document
File
PDF
Source
```

interchangeably when they represent different concepts.

Use:

```text
Document
```

for the uploaded document.

Use:

```text
Source
```

for the evidence origin.

Use:

```text
Evidence
```

for the supporting passage.

Use:

```text
Claim
```

for extracted factual statements.

---

# 52. UI Terminology

Preferred terminology:

```text
Document
Evidence
Claim
Entity
Relationship
Source
Confidence
Potential contradiction
Timeline
Knowledge graph
Search
Analysis
```

Avoid overly technical terminology in the primary UI.

---

# 53. Explainability Pattern

Every major analytical result should follow:

```text
RESULT
 ↓
WHY
 ↓
EVIDENCE
 ↓
SOURCE
```

Example:

```text
RESULT
Company A acquired Company B.

WHY
Two documents explicitly describe the acquisition.

EVIDENCE
Report_A.pdf — Page 7
Contract_B.pdf — Page 3

SOURCE
[Open evidence]
```

This should become a consistent UI pattern across the application.

---

# 54. AI Response Guardrails in UI

The interface must support the following AI behaviors:

### If evidence exists:

```text
Answer + evidence + source
```

### If evidence is conflicting:

```text
Answer + conflict + both sources
```

### If evidence is incomplete:

```text
Partial finding + uncertainty
```

### If evidence is absent:

```text
Insufficient evidence
```

The UI should make these states visually distinguishable.

---

# 55. Comparison UX

When comparing two documents, users should be able to select:

```text
Document A
Document B
```

Optionally:

```text
Document C
Document D
```

The comparison interface should organize differences into categories:

```text
Facts
Claims
Entities
Dates
Values
Relationships
Status
```

---

# 56. Filtering

Where datasets become large, provide filters.

Examples:

```text
Document
Date
Entity
Claim type
Confidence
Conflict type
Event type
```

Filters should be optional and easy to reset.

Provide:

```text
Clear filters
```

rather than forcing users to manually remove every selection.

---

# 57. Search + Analysis Integration

Search results should allow users to move directly into analysis.

Example:

```text
Search result

Company X

[View Evidence]
[Compare Sources]
[Explore Graph]
[View Timeline]
```

This creates a connected analytical workflow rather than isolated screens.

---

# 58. Dashboard-to-Analysis Integration

Dashboard metrics should be interactive where practical.

Example:

```text
17 Potential Contradictions
        ↓
Click
        ↓
Contradiction Dashboard
```

Similarly:

```text
93 Timeline Events
        ↓
Timeline
```

This makes the dashboard functional rather than decorative.

---

# 59. Graph-to-Evidence Integration

Selecting a graph relationship should reveal its supporting evidence.

Example:

```text
Person A
    │
    └── works_for → Company B
                       ↓
                   Evidence
                       ↓
                HR_Report.pdf
                    Page 4
```

This is essential for making the knowledge graph trustworthy.

---

# 60. Contradiction-to-Document Integration

Selecting a contradiction should allow the user to open both original sources.

```text
Claim A
[Open Document A]

Claim B
[Open Document B]
```

The user should be able to independently verify the conflict.

---

# 61. Timeline-to-Document Integration

Every timeline event should provide:

```text
Event
Date
Source
Page
Evidence
```

This prevents the timeline from becoming an unexplained AI-generated visualization.

---

# 62. Avoid Over-Engineering the UI

The initial version should not attempt to implement every possible visualization.

Priority should be:

```text
1. Document upload
2. Document library
3. Search / Ask DocMind
4. Evidence-backed answers
5. Comparison
6. Contradiction dashboard
7. Timeline
8. Knowledge graph
```

Advanced visualization can be introduced after the core workflow is stable.

---

# 63. Streamlit-Specific UX Rules

Since Streamlit is the selected application framework:

* Keep the interface modular.
* Avoid excessive nested expanders.
* Avoid putting the entire application into one extremely long page.
* Use clear navigation.
* Use session state carefully.
* Use caching for expensive reusable operations.
* Keep long-running processing visible.
* Avoid unnecessary reruns.
* Separate UI logic from processing logic.
* Do not place core AI/ML logic directly inside UI components.
* Maintain a clean separation between presentation and backend modules.

---

# 64. UI Architecture Rule

The UI must not contain core business logic.

Use:

```text
UI
 ↓
Application / Service Layer
 ↓
AI / ML Modules
 ↓
Storage
```

Do not implement:

```text
UI
 ↓
Direct database manipulation
 ↓
Direct model calls
 ↓
Direct graph construction
```

This keeps the application maintainable.

---

# 65. Component Reusability

Reusable components should be created for repeated patterns.

Examples:

```text
DocumentCard
EvidenceCard
SourceCitation
ConfidenceBadge
StatusIndicator
ClaimCard
ContradictionCard
TimelineEvent
EntityCard
GraphPanel
ProcessingProgress
ErrorMessage
```

The same component should behave consistently wherever it appears.

---

# 66. Mobile and Desktop Priorities

Desktop is the primary interface.

Optimize the desktop experience for:

```text
Document comparison
Evidence inspection
Knowledge graph exploration
Timeline analysis
Large search results
```

Mobile should prioritize:

```text
Reading
Searching
Basic document inspection
```

Complex graph and comparison experiences may be simplified on mobile.

---

# 67. UX Quality Criteria

The UI will be considered successful if a new user can:

```text
1. Upload a document without instructions.

2. Understand whether processing is complete.

3. Ask a natural-language question.

4. Understand the generated answer.

5. Identify the evidence supporting the answer.

6. Open the source document/page.

7. Compare information across documents.

8. Understand why a contradiction was detected.

9. Explore relationships between entities.

10. Understand a timeline without technical knowledge.
```

---

# 68. Anti-Patterns

The AI coding agent must NOT create:

```text
❌ Generic ChatGPT clone UI
❌ Chat-only interface
❌ Excessive animations
❌ Decorative dashboards with meaningless statistics
❌ Huge graph containing every entity by default
❌ Unsupported confidence percentages
❌ Fake citations
❌ Fake progress bars
❌ Unexplained AI conclusions
❌ Technical terminology everywhere
❌ Hidden processing failures
❌ Unreadable dense tables
❌ Excessive popups
❌ Unnecessary authentication systems
❌ Unnecessary frontend frameworks
```

---

# 69. Recommended Primary Screens

The application should ultimately provide these major screens:

```text
1. Dashboard
2. Documents
3. Ask DocMind
4. Search Results
5. Document Viewer
6. Knowledge Graph
7. Compare Documents
8. Contradictions
9. Timeline
10. Settings
11. Optional Technical / Evaluation View
```

---

# 70. Final UX Principle

The entire DocMind experience should follow:

```text
UNDERSTAND
     ↓
DISCOVER
     ↓
CONNECT
     ↓
COMPARE
     ↓
REASON
     ↓
VERIFY
     ↓
EXPLAIN
```

The user should never feel that DocMind is simply producing an AI answer.

The interface should make it clear that DocMind:

```text
Reads documents
      ↓
Finds information
      ↓
Structures knowledge
      ↓
Connects related information
      ↓
Compares sources
      ↓
Identifies possible conflicts
      ↓
Tracks information through time
      ↓
Verifies results against evidence
      ↓
Explains the result
```

The ultimate UX goal is:

> **Make complex document intelligence feel simple without hiding the evidence that makes the intelligence trustworthy.**

Every UI decision should support this principle.
