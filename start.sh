#!/bin/bash

echo "🚀 Starting Backend (FastAPI) in the background..."
cd backend
uvicorn app:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

sleep 3 # Wait 3 seconds for the backend to boot up

echo "🖥️ Starting Frontend (Streamlit)..."
cd frontend
streamlit run app.py

# When you press Ctrl+C to stop Streamlit, this will also kill the backend
echo "🛑 Stopping Backend..."
kill $BACKEND_PID