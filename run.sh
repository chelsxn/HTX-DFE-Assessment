#!/bin/bash
# Use chmod +x run.sh to make it executable

# Activate virtual environment if needed
# source venv/bin/activate

# Run FastAPI on localhost:8000
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
