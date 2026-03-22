# PageIndex/pageindex_fastapi_app/main.py

from fastapi import FastAPI, status, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import logging
import json
from pageindex_code.main import get_answer, stream_answer
from config import STREAMING_MARKER_START, STREAMING_MARKER_END

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.get("/", status_code=status.HTTP_200_OK)
async def root():
    return {"status": status.HTTP_200_OK, "message": "Hello World!"}

# AI question-answering endpoints:

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str
    error: str = None

# Non‑streaming endpoint
@app.post("/ask", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    try:
        answer = get_answer(request.query)
        return QueryResponse(answer=answer)
    except Exception as e:
        logger.exception("Request failed")
        raise HTTPException(status_code=500, detail=str(e))

# Streaming endpoint with JSON lines
@app.post("/ask/stream")
async def ask_question_stream(request: QueryRequest):
    async def event_generator():
        try:
            # 1. Start marker (from config)
            yield json.dumps({"stream": STREAMING_MARKER_START}) + "\n"

            # 2. Stream tokens
            async for token in stream_answer(request.query):
                # Each token is a string (may contain markdown/markup)
                yield json.dumps({"stream": token}) + "\n"

            # 3. End marker (from config)
            yield json.dumps({"stream": STREAMING_MARKER_END}) + "\n"

        except Exception as e:
            # Optionally send an error as a stream line
            yield json.dumps({"stream": f"ERROR: {str(e)}"}) + "\n"

    return StreamingResponse(
        event_generator(),
        media_type="application/x-ndjson"   # or "application/json-lines"
    )