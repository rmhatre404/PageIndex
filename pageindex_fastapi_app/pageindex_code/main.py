# PageIndex/pageindex_fastapi_app/pageindex_code/main.py

import logging
from typing import AsyncGenerator
from langchain_core.messages import AIMessageChunk
from pageindex_code.ReasoningRetriever import agent

logger = logging.getLogger(__name__)

def get_answer(query: str) -> str:
    logger.info(f"Processing query: {query}")
    try:
        response = agent.invoke({"messages": [("user", query)]})
        answer = response["messages"][-1].content
        logger.info("Answer generated successfully")
        return answer
    except Exception as e:
        logger.exception("Error during agent invocation")
        raise RuntimeError(f"Failed to get answer: {e}") from e

async def stream_answer(query: str) -> AsyncGenerator[str, None]:
    logger.info(f"Streaming query: {query}")
    try:
        async for chunk in agent.astream({"messages": [("user", query)]}):
            print("DEBUG: chunk keys:", chunk.keys())
            for key, value in chunk.items():
                print(f"DEBUG: key={key}, type={type(value)}")
                # Special handling for the model node
                if key == "model":
                    print(f"DEBUG: model dict contents: {value}")
                    if isinstance(value, dict):
                        # Common pattern: {"messages": [AIMessageChunk, ...]}
                        if "messages" in value:
                            for msg in value["messages"]:
                                if isinstance(msg, AIMessageChunk) and msg.content:
                                    print(f"DEBUG: yielding from model['messages']: {msg.content}")
                                    yield msg.content
                        # Another pattern: the dict itself is an AIMessageChunk
                        elif isinstance(value, AIMessageChunk) and value.content:
                            yield value.content
                else:
                    # Fallback for other keys (if any)
                    if isinstance(value, AIMessageChunk) and value.content:
                        yield value.content
                    elif isinstance(value, list):
                        for msg in value:
                            if isinstance(msg, AIMessageChunk) and msg.content:
                                yield msg.content
    except Exception as e:
        logger.exception("Error during streaming")
        raise