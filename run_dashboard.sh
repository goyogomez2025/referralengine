#!/bin/bash
cd "/Users/goyogomez/Desktop/Yirra Care Agents"
source .venv/bin/activate
streamlit run app/ui/dashboard.py --server.port 8501 --server.headless false
