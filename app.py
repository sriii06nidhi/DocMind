from __future__ import annotations

import logging
import hashlib
from html import escape

import pandas as pd
import streamlit as st
from streamlit.components.v1 import html as streamlit_html

from docmind.config import BASE_DIR
from docmind.graph import build_graph_from_documents, render_graph_html
from docmind.llm import LLMServiceError
from docmind.pipeline import DocMindPipeline

logger = logging.getLogger(__name__)

st.set_page_config(page_title="DocMind", page_icon="🧠", layout="wide")

CUSTOM_CSS = """
<style>
    :root {
        --bg: #f3f2e7;
        --surface: #fbfaf1;
        --surface-raised: #f6f5eb;
        --surface-muted: #e9eadc;
        --sidebar: #a9c9bd;
        --sidebar-deep: #91b9ac;
        --border: #c9cbb8;
        --border-strong: #b8bfaa;
        --text: #292d25;
        --muted: #69756b;
        --primary: #78aaa0;
        --primary-strong: #5f9186;
        --primary-soft: #e1eee3;
        --success: #769f87;
        --warning: #a9873f;
        --danger: #b56e60;
        --violet: #9986b2;
        --shadow: rgba(69, 77, 62, 0.08);
        --font-ui: "Arial Narrow", "Aptos Narrow", "Roboto Condensed", "Liberation Sans Narrow", sans-serif;
    }
    html, body, [class*="css"], .stApp, button, input, textarea, select,
    p, label, h1, h2, h3, h4, h5, h6, [data-testid="stMarkdownContainer"] {
        font-family: var(--font-ui);
    }
    html, body, [data-testid="stAppViewContainer"] {
        background: var(--bg);
        color: var(--text);
    }
    .stApp {
        background: var(--bg);
        color: var(--text);
    }
    [data-testid="stHeader"] {
        background: rgba(243, 242, 231, 0.94);
    }
    [data-testid="stToolbar"] { color: var(--text); }
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--sidebar) 0%, var(--sidebar-deep) 100%);
        border-right: 1px solid rgba(75, 112, 99, 0.22);
    }
    [data-testid="stSidebar"] > div:first-child {
        background: transparent;
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
        color: #30483e;
    }
    .brand {
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 1.45rem;
        font-weight: 700;
        letter-spacing: 0.02em;
        color: #344c41;
        margin-bottom: 1rem;
        padding: 0.5rem 0.25rem;
    }
    .brand-mark {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 36px;
        height: 36px;
        border-radius: 10px;
        background: var(--primary);
        color: #f8faf3;
        font-weight: 800;
    }
    .section-header {
        margin-top: 1rem;
        margin-bottom: 0.8rem;
        color: var(--text);
        font-weight: 700;
        letter-spacing: 0.02em;
    }
    .metric-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 11px;
        padding: 1rem 1rem 0.85rem;
        min-height: 120px;
        box-shadow: 0 5px 16px var(--shadow);
    }
    .metric-label {
        font-size: 0.74rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--muted);
        margin-bottom: 0.35rem;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: var(--text);
        line-height: 1.1;
    }
    .metric-note {
        margin-top: 0.3rem;
        font-size: 0.78rem;
        color: var(--muted);
    }
    .panel {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1rem 1.1rem;
        margin-top: 1rem;
        box-shadow: 0 5px 16px var(--shadow);
    }
    .doc-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 11px;
        padding: 1rem 1rem 0.8rem;
        margin-bottom: 0.8rem;
    }
    .doc-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 1rem;
        margin-bottom: 0.75rem;
    }
    .doc-name {
        font-weight: 700;
        font-size: 1.05rem;
        color: var(--text);
    }
    .status-pill {
        display: inline-flex;
        align-items: center;
        padding: 0.35rem 0.65rem;
        border-radius: 999px;
        font-size: 0.7rem;
        letter-spacing: 0.05em;
        font-weight: 700;
        text-transform: uppercase;
        border: 1px solid transparent;
    }
    .status-ready { background: #e4efe4; color: #557e67; border-color: #bfd5c1; }
    .status-processing { background: #e4efec; color: var(--primary-strong); border-color: #bfd5ce; }
    .status-warning { background: #f3edda; color: #927538; border-color: #e0d3a8; }
    .status-failed { background: #f3e5e0; color: #9e5e52; border-color: #dfc1b8; }
    .doc-meta {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
        gap: 0.7rem;
        color: var(--muted);
        font-size: 0.8rem;
    }
    .doc-meta strong { color: var(--text); }
    .answer-box {
        background: var(--surface-raised);
        border: 1px solid var(--border-strong);
        border-radius: 12px;
        padding: 1rem;
    }
    .evidence-card {
        border-left: 3px solid var(--primary);
        background: var(--surface);
        border: 1px solid var(--border);
        border-left: 3px solid var(--primary);
        border-radius: 9px;
        padding: 0.8rem 0.9rem;
        margin-top: 0.7rem;
    }
    .small-label {
        color: var(--muted);
        font-size: 0.71rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }
    .empty-state {
        border: 1px dashed var(--border);
        border-radius: 10px;
        padding: 1.2rem;
        color: var(--muted);
        background: rgba(251, 250, 241, 0.58);
    }
    .nav-cta {
        background: rgba(235, 246, 228, 0.75);
        border: 1px solid rgba(82, 128, 109, 0.22);
        border-radius: 10px;
        padding: 0.7rem 0.8rem;
        margin-bottom: 0.75rem;
        color: #3c584b;
    }
    .small-note { color: var(--muted); font-size: 0.8rem; }
    .contrast { color: var(--text); }
    h1, h2, h3, h4, h5, h6, p, li, label, [data-testid="stMarkdownContainer"] {
        color: var(--text);
    }
    h1, h2, h3, h4 {
        letter-spacing: -0.015em;
        font-weight: 650;
    }
    [data-testid="stCaptionContainer"], small {
        color: var(--muted);
    }
    a { color: var(--primary-strong); }
    [data-testid="stRadio"] label,
    [data-testid="stCheckbox"] label {
        color: var(--text);
    }
    input[type="radio"],
    input[type="checkbox"] {
        accent-color: var(--primary-strong);
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        border-radius: 8px;
        padding: 0.25rem 0.4rem;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
        background: rgba(235, 246, 228, 0.78);
        color: #385b4d;
    }
    [data-testid="stRadioOption"][data-selected="true"] > div > div:first-child {
        background-color: var(--primary-strong) !important;
        border-color: var(--primary-strong) !important;
    }
    .stButton > button,
    [data-testid="stDownloadButton"] > button {
        border: 1px solid var(--border-strong);
        border-radius: 8px;
        background: var(--surface-muted);
        color: var(--text);
        transition: background-color 120ms ease, border-color 120ms ease;
    }
    .stButton > button:hover,
    [data-testid="stDownloadButton"] > button:hover {
        border-color: var(--primary-strong);
        background: var(--primary-soft);
        color: #304c41;
    }
    .stButton > button:focus,
    [data-testid="stDownloadButton"] > button:focus {
        box-shadow: 0 0 0 0.15rem rgba(120, 170, 160, 0.28);
    }
    [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea,
    [data-testid="stNumberInput"] input,
    [data-testid="stDateInput"] input,
    [data-testid="stSelectbox"] [role="combobox"],
    [data-testid="stMultiSelect"] [role="combobox"] {
        background: var(--surface);
        color: var(--text);
        border-color: var(--border-strong);
        border-radius: 8px;
    }
    [data-testid="stDataFrame"],
    [data-testid="stTable"] {
        border: 1px solid var(--border);
        border-radius: 9px;
        overflow: hidden;
    }
    [data-testid="stAlert"] {
        border-radius: 9px;
    }
    [data-testid="stExpander"] {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 9px;
    }
    [data-testid="stFileUploader"] section {
        background: rgba(251, 250, 241, 0.68);
        border-color: var(--border-strong);
        border-radius: 10px;
    }
    @media (max-width: 768px) {
        .block-container { padding-left: 0.8rem; padding-right: 0.8rem; }
        .metric-value { font-size: 1.4rem; }
    }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

if "processing_state" not in st.session_state:
    st.session_state.processing_state = []
if "docmind_nav" not in st.session_state:
    st.session_state.docmind_nav = "Dashboard"

if "docmind_pipeline" not in st.session_state:
    st.session_state.docmind_pipeline = DocMindPipeline(BASE_DIR)
pipeline = st.session_state.docmind_pipeline


def status_badge(status: str) -> str:
    normalized = (status or "UNKNOWN").upper().replace(" ", "-")
    classes = {
        "READY": "status-ready",
        "PROCESSING": "status-processing",
        "OCR-PROCESSING": "status-processing",
        "INDEXING": "status-processing",
        "WARNING": "status-warning",
        "FAILED": "status-failed",
    }
    return f"<span class='status-pill {classes.get(normalized, 'status-warning')}'>{_html_text(status or 'Unknown')}</span>"


def _html_text(value: object) -> str:
    return escape(str(value))


def set_navigation(page: str) -> None:
    st.session_state.docmind_nav = page


def current_documents():
    processed_documents = st.session_state.processing_state or pipeline.documents
    pipeline.documents = processed_documents
    return processed_documents


def metric_card(title: str, value: str | int, note: str = ""):
    st.markdown(
        f"""
        <div class='metric-card'>
            <div class='metric-label'>{title}</div>
            <div class='metric-value'>{value}</div>
            <div class='metric-note'>{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


with st.sidebar:
    st.markdown(
        """
        <div class='brand'><span class='brand-mark'>D</span>DocMind</div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<div class='nav-cta'>Evidence-first document intelligence</div>", unsafe_allow_html=True)
    st.radio(
        "Navigation",
        ["Dashboard", "Documents", "Ask DocMind", "Search", "Knowledge Graph", "Compare", "Contradictions", "Timeline"],
        key="docmind_nav",
        label_visibility="collapsed",
    )
    st.sidebar.file_uploader(
        "Upload documents",
        type=["pdf", "png", "jpg", "jpeg", "tiff", "bmp", "txt", "md"],
        accept_multiple_files=True,
        key="doc_uploads",
    )
    st.sidebar.caption("Document evidence and provenance remain visible throughout the analysis workflow.")

processed_uploads = st.session_state.setdefault("processed_uploads", set())
uploaded_files = st.session_state.get("doc_uploads")
if uploaded_files:
    for uploaded_file in uploaded_files:
        upload_fingerprint = (uploaded_file.name, hashlib.sha256(uploaded_file.getvalue()).hexdigest())
        if upload_fingerprint in processed_uploads:
            continue
        try:
            result = pipeline.process_document(uploaded_file, uploaded_file.name)
            existing_index = next(
                (
                    index
                    for index, document in enumerate(st.session_state.processing_state)
                    if document.get("document_id") == result.get("document_id")
                ),
                None,
            )
            if existing_index is None:
                st.session_state.processing_state.append(result)
            else:
                st.session_state.processing_state[existing_index] = result
            processed_uploads.add(upload_fingerprint)
            if result.get("status") == "FAILED":
                st.error(f"Unable to extract text from '{uploaded_file.name}'. No document evidence was indexed.")
            elif result.get("status") == "WARNING":
                details = " ".join(result.get("notes", []))
                st.warning(f"'{uploaded_file.name}' was processed with limitations. {details}")
        except Exception:
            logger.exception("Failed to index uploaded document: %s", uploaded_file.name)
            st.error(f"Unable to process '{uploaded_file.name}'. The document could not be indexed safely.")
            break

pipeline.documents = st.session_state.processing_state
page = st.session_state.docmind_nav

if page == "Dashboard":
    docs = current_documents()
    metrics = pipeline.export_dashboard() if docs else {"documents": 0, "pages": 0, "entities": 0, "claims": 0, "events": 0, "contradictions": 0, "status": "EMPTY"}

    col_a, col_b = st.columns([3, 1])
    with col_a:
        st.markdown("<div class='section-header'>Workspace overview</div>", unsafe_allow_html=True)
        st.markdown("### DocMind workspace")
        st.write("Transform disconnected documents into an evidence-linked knowledge space. Examine the source, the structure, and the reasoning behind every result.")
    with col_b:
        button_col1, button_col2 = st.columns(2)
        with button_col1:
            st.button("Documents", on_click=set_navigation, args=("Documents",))
        with button_col2:
            st.button("Ask DocMind", on_click=set_navigation, args=("Ask DocMind",))

    st.markdown("<div class='section-header'>Key metrics</div>", unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        metric_card("Documents", metrics["documents"], "Indexed records")
    with c2:
        metric_card("Pages", metrics["pages"], "Document pages")
    with c3:
        metric_card("Entities", metrics["entities"], "Extracted entities")
    with c4:
        metric_card("Claims", metrics["claims"], "Structured claims")
    with c5:
        metric_card("Conflicts", metrics["contradictions"], "Potential contradictions")

    col_left, col_right = st.columns([1.5, 1])
    with col_left:
        st.markdown("<div class='section-header'>Recent documents</div>", unsafe_allow_html=True)
        if docs:
            for doc in reversed(docs[-3:]):
                st.markdown(
                    f"""
                    <div class='doc-card'>
                        <div class='doc-row'>
                            <div class='doc-name'>{_html_text(doc.get('name', 'Unnamed document'))}</div>
                            {status_badge(doc.get('status', 'Unknown'))}
                        </div>
                        <div class='doc-meta'>
                            <div><span class='small-label'>Type</span><br><strong>{_html_text(doc.get('file_type', 'unknown'))}</strong></div>
                            <div><span class='small-label'>Pages</span><br><strong>{len(doc.get('pages', []))}</strong></div>
                            <div><span class='small-label'>Claims</span><br><strong>{len(doc.get('claims', []))}</strong></div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.markdown("<div class='empty-state'>No documents have been uploaded yet.</div>", unsafe_allow_html=True)
    with col_right:
        st.markdown("<div class='section-header'>Attention</div>", unsafe_allow_html=True)
        contradictions = pipeline.detect_contradictions()
        if contradictions:
            for contradiction in contradictions[:3]:
                st.markdown(
                    f"""
                    <div class='evidence-card'>
                        <div class='small-label'>Potential conflict</div>
                        <div class='contrast'>{contradiction['classification']}</div>
                        <div class='small-note'>{_html_text(contradiction['reason'])}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.markdown("<div class='empty-state'>No contradictions detected in the current corpus.</div>", unsafe_allow_html=True)

elif page == "Documents":
    st.markdown("<div class='section-header'>Documents</div>", unsafe_allow_html=True)
    docs = current_documents()
    if not docs:
        st.markdown("<div class='empty-state'>No documents uploaded. Use the upload control in the sidebar to begin.</div>", unsafe_allow_html=True)
    else:
        for doc in docs:
            st.markdown(
                f"""
                <div class='doc-card'>
                    <div class='doc-row'>
                        <div class='doc-name'>{_html_text(doc.get('name', 'Unnamed document'))}</div>
                        {status_badge(doc.get('status', 'Unknown'))}
                    </div>
                    <div class='doc-meta'>
                        <div><span class='small-label'>Type</span><br><strong>{_html_text(doc.get('file_type', 'unknown'))}</strong></div>
                        <div><span class='small-label'>Pages</span><br><strong>{len(doc.get('pages', []))}</strong></div>
                        <div><span class='small-label'>Chunks</span><br><strong>{len(doc.get('chunks', []))}</strong></div>
                        <div><span class='small-label'>Entities</span><br><strong>{len(doc.get('entities', []))}</strong></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

elif page == "Ask DocMind":
    st.markdown("<div class='section-header'>Ask DocMind</div>", unsafe_allow_html=True)
    st.write("Ask questions across your documents and inspect the evidence behind every answer.")

    example_questions = [
        "What are the major claims across these documents?",
        "Which documents mention the main subject?",
        "Are there conflicting statements about the contract?",
        "Show the timeline of events.",
    ]
    for q in example_questions:
        if st.button(q, key=f"q_{q[:20]}"):
            st.session_state.ask_query = q

    question = st.text_area("Question", value=st.session_state.get("ask_query", "What do the uploaded documents say about the key findings?"), height=120)
    if st.button("Run evidence-grounded analysis"):
        try:
            answer = pipeline.answer_question(question)
        except LLMServiceError as exc:
            logger.warning("Question answering provider error: %s", exc)
            st.error(str(exc))
        except Exception:
            logger.exception("Question answering failed")
            st.error("Question answering failed unexpectedly. Review the application log for details.")
        else:
            if answer.get("retrieval_warning"):
                st.warning(answer["retrieval_warning"])
            st.markdown("<div class='answer-box'>", unsafe_allow_html=True)
            st.markdown("### Answer")
            st.write(answer.get("answer", "No answer available."))
            st.caption(
                f"Confidence: {answer.get('confidence', 'Unknown')} · "
                f"Provider: {answer.get('provider', 'unknown')} ({answer.get('llm_status', 'unknown')})"
            )
            if answer.get("citations"):
                st.markdown("### Evidence")
                for item in answer["citations"]:
                    st.markdown(
                        f"""
                        <div class='evidence-card'>
                            <div class='small-label'>Source</div>
                            <div class='contrast'>{_html_text(item.get('document', 'Unknown'))}</div>
                            <div class='small-note'>Page {_html_text(item.get('page_number', 'N/A'))}</div>
                            <div>{_html_text(item.get('text', '')[:260])}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.warning("Insufficient evidence in the available documents.")
            st.markdown("</div>", unsafe_allow_html=True)

elif page == "Search":
    st.markdown("<div class='section-header'>Search</div>", unsafe_allow_html=True)
    query = st.text_input("Search across uploaded documents", value="")
    if query:
        try:
            results = pipeline.semantic_search(query, top_k=5)
        except Exception:
            logger.exception("Document search failed")
            st.error("Document search failed. Review the application log for details.")
            results = []
        if pipeline.last_search_warning:
            st.warning(pipeline.last_search_warning)
        if results:
            for hit in results:
                st.markdown(
                    f"""
                    <div class='evidence-card'>
                        <div class='small-label'>Document</div>
                        <div class='contrast'>{_html_text(hit.get('document', 'Unknown'))}</div>
                        <div class='small-note'>Page {hit.get('page_number', 'N/A')} · score {hit.get('score', 0.0)}</div>
                        <div>{_html_text(hit.get('text', '')[:260])}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.markdown("<div class='empty-state'>No search results were found for the current query.</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='empty-state'>Enter a search query to retrieve relevant chunks and evidence.</div>", unsafe_allow_html=True)

elif page == "Knowledge Graph":
    st.markdown("<div class='section-header'>Knowledge graph</div>", unsafe_allow_html=True)
    docs = current_documents()
    if docs:
        graph = build_graph_from_documents(docs)
        html_code = render_graph_html(graph)
        streamlit_html(html_code, height=700, scrolling=True)
    else:
        st.markdown("<div class='empty-state'>Upload documents to render the graph.</div>", unsafe_allow_html=True)

elif page == "Compare":
    st.markdown("<div class='section-header'>Compare</div>", unsafe_allow_html=True)
    docs = current_documents()
    if not docs:
        st.markdown("<div class='empty-state'>No documents available for comparison.</div>", unsafe_allow_html=True)
    else:
        options = [doc["name"] for doc in docs]
        selected = st.multiselect("Select documents", options=options, default=options[:2] if len(options) >= 2 else options)
        if len(selected) >= 2:
            chosen = [doc for doc in docs if doc["name"] in selected]
            rows = []
            for doc in chosen:
                for claim in doc.get("claims", [])[:3]:
                    rows.append({
                        "Document": doc["name"],
                        "Claim": f"{claim.get('subject', '')} {claim.get('relation', '')} {claim.get('obj', '')}",
                        "Evidence": claim.get("evidence", "")[:180],
                    })
            if rows:
                st.dataframe(pd.DataFrame(rows), use_container_width=True)
            else:
                st.markdown("<div class='empty-state'>No extracted claims are available for comparison.</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='empty-state'>Select at least two documents to compare them.</div>", unsafe_allow_html=True)

elif page == "Contradictions":
    st.markdown("<div class='section-header'>Contradictions</div>", unsafe_allow_html=True)
    contradictions = pipeline.detect_contradictions()
    if contradictions:
        for contradiction in contradictions:
            st.markdown(
                f"""
                <div class='panel'>
                    <div class='small-label'>Classification</div>
                    <div class='contrast'>{_html_text(contradiction['classification'])}</div>
                    <div class='small-note'>{_html_text(contradiction['reason'])}</div>
                    <div style='margin-top: 0.8rem; display: grid; grid-template-columns: 1fr 1fr; gap: 0.8rem;'>
                        <div class='evidence-card'>
                            <div class='small-label'>Claim A</div>
                            <div class='contrast'>{_html_text(contradiction['claim_a'].get('subject', 'Unknown'))} {_html_text(contradiction['claim_a'].get('relation', ''))} {_html_text(contradiction['claim_a'].get('obj', ''))}</div>
                            <div class='small-note'>{_html_text(contradiction['claim_a'].get('document_name', 'Unknown'))} · page {_html_text(contradiction['claim_a'].get('page_number', 'N/A'))}</div>
                        </div>
                        <div class='evidence-card'>
                            <div class='small-label'>Claim B</div>
                            <div class='contrast'>{_html_text(contradiction['claim_b'].get('subject', 'Unknown'))} {_html_text(contradiction['claim_b'].get('relation', ''))} {_html_text(contradiction['claim_b'].get('obj', ''))}</div>
                            <div class='small-note'>{_html_text(contradiction['claim_b'].get('document_name', 'Unknown'))} · page {_html_text(contradiction['claim_b'].get('page_number', 'N/A'))}</div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.markdown("<div class='empty-state'>No contradiction candidates are currently available from the indexed documents.</div>", unsafe_allow_html=True)

elif page == "Timeline":
    st.markdown("<div class='section-header'>Timeline</div>", unsafe_allow_html=True)
    timeline = pipeline.extract_timeline()
    if timeline:
        for event in timeline:
            st.markdown(
                f"""
                <div class='evidence-card'>
                    <div class='small-label'>{_html_text(event.get('date', 'Unknown date'))}</div>
                    <div class='contrast'>{_html_text(event.get('title', 'Untitled event'))}</div>
                    <div class='small-note'>{_html_text(event.get('document', 'Unknown document'))} · page {_html_text(event.get('page_number', 'N/A'))}</div>
                    <div>{_html_text(event.get('evidence', '')[:220])}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.markdown("<div class='empty-state'>No timeline events are available.</div>", unsafe_allow_html=True)
