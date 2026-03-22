# PageIndex/pageindex_fastapi_app/pageindex_code/ReasoningRetriever.py

import json
import sys
from pathlib import Path
from typing import Dict, List
from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

# Add parent directory to path to import config
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import (
    MODEL_NAME,
    OPENAI_API_KEY,
    TEMPERATURE,
    TREE_JSON_PATH,
)

# Set OpenAI API key for LangChain
import os
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# -----------------------------------------------------------------------------
# 1. Load the tree JSON and build helper structures
# -----------------------------------------------------------------------------
if not TREE_JSON_PATH.exists():
    raise FileNotFoundError(f"Tree file not found: {TREE_JSON_PATH}\nRun ReasoningTree.py first.")

with open(TREE_JSON_PATH, "r", encoding="utf-8") as f:
    tree_data = json.load(f)

# The tree may be under "result" key or directly the list
if isinstance(tree_data, dict) and "result" in tree_data:
    root_nodes = tree_data["result"]
else:
    root_nodes = tree_data if isinstance(tree_data, list) else [tree_data]

# -----------------------------------------------------------------------------
# 2. Build node map and stripped tree
# -----------------------------------------------------------------------------
node_map: Dict[str, Dict] = {}

def flatten_nodes(nodes: List[Dict]) -> None:
    for node in nodes:
        node_id = node.get("node_id")
        if node_id:
            node_map[node_id] = node
        if "nodes" in node and node["nodes"]:
            flatten_nodes(node["nodes"])

flatten_nodes(root_nodes)

def strip_text(node: Dict) -> Dict:
    """Remove the full 'text' field to save tokens."""
    stripped = {k: v for k, v in node.items() if k != "text"}
    if "nodes" in stripped and stripped["nodes"]:
        stripped["nodes"] = [strip_text(child) for child in stripped["nodes"]]
    return stripped

reasoning_tree = [strip_text(node) for node in root_nodes]

# -----------------------------------------------------------------------------
# 3. Shared LLM instances
# -----------------------------------------------------------------------------
# One for reasoning node selection (temperature=0 for deterministic)
_reasoning_llm = ChatOpenAI(model=MODEL_NAME, temperature=0)
# Main agent's LLM (with streaming and reasoning_effort)
_main_llm = ChatOpenAI(
    model=MODEL_NAME,
    temperature=TEMPERATURE,
    streaming=True,
)

# -----------------------------------------------------------------------------
# 4. Retrieval tool using LLM reasoning
# -----------------------------------------------------------------------------
def reasoning_node_selection(query: str) -> List[str]:
    """
    Step 1: Use the LLM to choose relevant node IDs by inspecting the stripped tree.
    """
    prompt = f"""You are an expert document analyst. Given a user question and a document tree,
your task is to select which nodes most likely contain the answer.

Question: {query}

Document tree (titles, summaries, page numbers – no full text):
{json.dumps(reasoning_tree, indent=2)}

Reply in JSON format exactly:
{{
  "thinking": "step-by-step reasoning",
  "node_list": ["node_id_1", "node_id_2", ...]
}}
"""
    response = _reasoning_llm.invoke([HumanMessage(content=prompt)])
    try:
        result = json.loads(response.content)
        return result.get("node_list", [])
    except json.JSONDecodeError:
        return []

def extract_content(node_ids: List[str]) -> str:
    """Step 2: Fetch full text for the selected nodes."""
    sections = []
    for nid in node_ids:
        node = node_map.get(nid)
        if node and node.get("text"):
            title = node.get("title", "Untitled")
            page = node.get("page_index", "unknown")
            sections.append(f"--- Node {nid} (Page {page}) : {title} ---\n{node['text']}")
    return "\n\n".join(sections)

@tool
def search_document_structure(query: str) -> str:
    """
    Navigates the document tree using hierarchical reasoning.
    Returns the most relevant sections' full text for the given query.
    """
    node_ids = reasoning_node_selection(query)
    if not node_ids:
        return "No relevant sections found."
    context = extract_content(node_ids)
    if not context:
        return "Selected nodes contained no text."
    return context

# -----------------------------------------------------------------------------
# 5. Build the LangChain agent
# -----------------------------------------------------------------------------
system_prompt = """You are a specialized document analyst. 
Use the search_document_structure tool to locate data within the document. 
When you receive the retrieved context, answer the user's question based solely on that information. 
Always cite the exact Node ID and Page Number in your final answer, if available.
If the tool returns nothing, say that the information is not found.
"""

agent = create_agent(
    model=_main_llm,
    tools=[search_document_structure],
    system_prompt=system_prompt,
    middleware=[SummarizationMiddleware(model=MODEL_NAME)],
)
