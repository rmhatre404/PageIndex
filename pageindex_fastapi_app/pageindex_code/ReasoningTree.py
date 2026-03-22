# PageIndex/pageindex_fastapi_app/pageindex_code/ReasoningTree.py

import json
import time
import sys
from pathlib import Path
from pageindex import PageIndexClient

# Add parent directory to path to import config
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import (
    PAGEINDEX_API_KEY,
    PDF_PATH,
    TREE_JSON_PATH,
    INDEXING_TIMEOUT,
    POLL_INTERVAL,
)

def count_nodes(nodes):
    """Count total nodes in the tree (for feedback)."""
    if not nodes:
        return 0
    return len(nodes) + sum(count_nodes(node.get("nodes", [])) for node in nodes)

def index_document(pdf_path: Path, output_path: Path) -> dict:
    """
    Submit document to PageIndex, poll until ready, save the tree JSON.
    Returns the tree structure (list/dict).
    """
    client = PageIndexClient(api_key=PAGEINDEX_API_KEY)
    print(f"Submitting document: {pdf_path}")
    submit_resp = client.submit_document(str(pdf_path))
    doc_id = submit_resp["doc_id"]
    print(f"Document submitted successfully. doc_id: {doc_id}")

    # Poll until ready
    print("Indexing document. Please wait...")
    elapsed = 0
    while not client.is_retrieval_ready(doc_id):
        if elapsed >= INDEXING_TIMEOUT:
            raise TimeoutError(f"Processing timed out after {INDEXING_TIMEOUT}s")
        time.sleep(POLL_INTERVAL)
        elapsed += POLL_INTERVAL
        print(f"...still analyzing structure ({elapsed}s elapsed)")

    print("Document ready!")
    tree_data = client.get_tree(doc_id, node_summary=True)
    tree_structure = tree_data["result"]

    # Save JSON
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(tree_structure, f, indent=4, ensure_ascii=False)

    # Print summary
    top_level_count = len(tree_structure) if isinstance(tree_structure, list) else 1
    total_nodes = count_nodes(tree_structure) if isinstance(tree_structure, list) else 1
    print(f"Index complete: {top_level_count} top-level node(s), {total_nodes} total nodes saved to {output_path}")
    return tree_structure

if __name__ == "__main__":
    if not PDF_PATH.exists():
        raise FileNotFoundError(f"PDF not found: {PDF_PATH}")
    index_document(PDF_PATH, TREE_JSON_PATH)