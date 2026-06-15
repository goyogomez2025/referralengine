#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"
source .venv/bin/activate 2>/dev/null || source venv/bin/activate 2>/dev/null
echo "Starting Referral Engine..."
open http://localhost:8501 2>/dev/null &
streamlit run app/ui/dashboard.py --server.port 8501 --browser.gatherUsageStats false
