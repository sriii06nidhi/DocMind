from __future__ import annotations

from html import escape
from typing import Iterable

import networkx as nx
from pyvis.network import Network


def build_graph_from_documents(documents: Iterable[dict]) -> nx.DiGraph:
    graph = nx.DiGraph()
    for document in documents:
        doc_id = str(document.get("document_id"))
        graph.add_node(doc_id, kind="document", label=escape(str(document.get("name", "Document"))))

        page_ids = {}
        for page in document.get("pages", []):
            page_id = f"{doc_id}-page-{page['page_number']}"
            page_ids[page["page_number"]] = page_id
            graph.add_node(page_id, kind="page", label=f"Page {page['page_number']}")
            graph.add_edge(doc_id, page_id, relation="contains")

        for chunk in document.get("chunks", []):
            chunk_id = chunk["chunk_id"]
            page_id = page_ids.get(chunk["page_number"])
            graph.add_node(
                chunk_id,
                kind="chunk",
                label=f"Chunk {chunk.get('chunk_index', '?')}",
                title=chunk.get("text", ""),
                page_number=chunk["page_number"],
                document_id=doc_id,
            )
            if page_id:
                graph.add_edge(page_id, chunk_id, relation="contains_chunk")

        for entity in document.get("entities", []):
            entity_id = f"{doc_id}-entity-{entity['entity_type']}-{entity['name'].lower()}"
            graph.add_node(
                entity_id,
                kind="entity",
                label=escape(str(entity["name"])),
                entity_type=entity["entity_type"],
            )
            graph.add_edge(doc_id, entity_id, relation="mentions")
            graph.add_edge(entity_id, doc_id, relation="appears_in")
            page_id = page_ids.get(entity.get("page_number"))
            if page_id:
                graph.add_edge(page_id, entity_id, relation="mentions")

        for claim in document.get("claims", []):
            claim_id = claim["claim_id"]
            graph.add_node(
                claim_id,
                kind="claim",
                label=escape(f"{claim['subject']} {claim['relation']} {claim['obj']}"),
            )
            page_id = page_ids.get(claim.get("page_number"))
            graph.add_edge(page_id or doc_id, claim_id, relation="contains_claim")

        for event in document.get("events", []):
            event_id = event["event_id"]
            graph.add_node(event_id, kind="event", label=escape(str(event["title"])), date=event["date"])
            page_id = page_ids.get(event.get("page_number"))
            graph.add_edge(page_id or doc_id, event_id, relation="records_event")

    return graph


def render_graph_html(graph: nx.DiGraph) -> str:
    net = Network(height="650px", width="100%", directed=True, bgcolor="#26332e", font_color="#f3f2e7")
    net.set_options(
        """
        {
          "edges": {
            "color": {"color": "#a5b9aa", "highlight": "#78aaa0"},
            "font": {"color": "#e4e8dc", "size": 12}
          }
        }
        """
    )
    for node_id, attrs in graph.nodes(data=True):
        label = attrs.get("label", str(node_id))
        kind = attrs.get("kind", "node")
        color = {
            "document": "#82b3a4",
            "page": "#d6c58c",
            "entity": "#9fc7ad",
            "claim": "#c9b4d8",
            "event": "#d8a393",
            "chunk": "#d9b883",
        }.get(kind, "#b9c7b9")
        net.add_node(str(node_id), label=escape(str(label)), color=color, title=escape(str(attrs)))
    for source, target, attrs in graph.edges(data=True):
        net.add_edge(str(source), str(target), label=attrs.get("relation", "related"), arrows="to")
    return net.generate_html()
