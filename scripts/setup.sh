#!/usr/bin/env bash
# scripts/setup.sh — one-command setup for a fresh laptop.
# Usage: ./scripts/setup.sh
#
# Idempotent: safe to re-run. Won't overwrite an existing .env.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "════════════════════════════════════════════════════════════"
echo "  Mom's Saheli — fresh-laptop setup"
echo "════════════════════════════════════════════════════════════"

# --- 1. .env ---
if [[ -f .env ]]; then
  echo "✅ .env already exists — leaving it alone"
else
  cp .env.example .env
  echo "📝 Created .env from template."
  echo "   👉 Edit .env and paste at minimum:"
  echo "      GEMINI_API_KEY=...   (get one: https://aistudio.google.com/apikey)"
  echo "      TAVILY_API_KEY=...   (get one: https://tavily.com)"
  echo "   Without these the swarm runs on cached fixtures only."
fi
echo ""

# --- 2. uv check ---
if ! command -v uv &>/dev/null; then
  echo "❌ 'uv' is not installed. Install with:"
  echo "   brew install uv     (mac)"
  echo "   curl -LsSf https://astral.sh/uv/install.sh | sh   (linux)"
  exit 1
fi

# --- 3. Backend ---
echo "🐍 Setting up Python backend..."
cd "$REPO_ROOT/backend"
if [[ ! -d .venv ]]; then
  uv venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate

# Decide which index to use (Walmart network vs. public)
INDEX_FLAGS=""
if curl -s --max-time 2 https://pypi.ci.artifacts.walmart.com >/dev/null 2>&1; then
  echo "   (Walmart network detected — using internal index)"
  INDEX_FLAGS="--index-url https://pypi.ci.artifacts.walmart.com/artifactory/api/pypi/external-pypi/simple --allow-insecure-host pypi.ci.artifacts.walmart.com"
fi

# shellcheck disable=SC2086
uv pip install -e . $INDEX_FLAGS

echo "✅ Backend deps installed"
echo ""

# --- 4. Frontend ---
echo "📦 Setting up React frontend..."
cd "$REPO_ROOT/frontend"
if ! command -v npm &>/dev/null; then
  echo "❌ 'npm' is not installed. Install Node.js first:"
  echo "   brew install node"
  exit 1
fi
npm install --silent
echo "✅ Frontend deps installed"
echo ""

# --- 5. Done ---
cat <<'EOF'
════════════════════════════════════════════════════════════
  ✅ Setup complete!

  To run:

    # Terminal 1 — backend
    cd backend
    source .venv/bin/activate
    uvicorn app.main:app --port 8000

    # Terminal 2 — frontend
    cd frontend
    npm run dev

  Then open http://localhost:5173 and click "Run Jenny".

  🤖 If you're an AI agent, read AGENTS.md for full context.
════════════════════════════════════════════════════════════
EOF
