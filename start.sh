#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

cd frontend
npm install
npm run build
cd ..

cd backend
python3 -m venv .venv 2>/dev/null || true
source .venv/bin/activate
pip install -q -r requirements.txt
python main.py
