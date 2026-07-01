#!/bin/bash
echo "🚀 Starting AI Bipad Sahayak..."
cd /home/user/bipad-sahayak/backend
python3 -m venv venv 2>/dev/null || true
source venv/bin/activate
pip install -r requirements.txt -q
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
cd /home/user/bipad-sahayak/frontend-web
npm install -q 2>/dev/null || true
npm run dev
