
# Running PageIndex FastAPI App

## Start Development Server

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### Parameters
- `main:app` - Uvicorn application instance
- `--reload` - Auto-reload on code changes
- `--host 127.0.0.1` - Localhost only
- `--port 8000` - Port number

The server will be available at `http://127.0.0.1:8000`
## Prerequisites

Ensure you have Python 3.8+ installed and all dependencies from `requirements.txt`:

```bash
pip install -r requirements.txt
```

## Running the Application

1. Navigate to the project directory
2. Execute the uvicorn command above
3. The FastAPI interactive docs will be available at `http://127.0.0.1:8000/docs`
4. Swagger UI can be accessed at `http://127.0.0.1:8000/redoc`

## Stopping the Server

Press `Ctrl+C` in your terminal to stop the development server.
