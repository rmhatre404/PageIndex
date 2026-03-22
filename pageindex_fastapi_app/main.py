# PageIndex/pageindex_fastapi_app/main.py

from fastapi import FastAPI, status

app = FastAPI()

@app.get("/", status_code=status.HTTP_200_OK)
async def root():
    return {"status": status.HTTP_200_OK, "message": "Hello World!"}
