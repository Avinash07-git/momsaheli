#!/usr/bin/env bash
# scripts/start.sh — start all 3 processes: AgentField control plane, FastAPI backend, AgentField agent
# Usage: ./scripts/start.sh
# Ctrl+C kills all three.

set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

AF_BIN="$HOME/.agentfield/bin/af"
NODE_BIN="/tmp/node-v22.15.0-darwin-arm64/bin"

# Add node to path if needed
export PATH="$NODE_BIN:$PATH"

LOG_DIR="/tmp/momsaheli"
mkdir -p "$LOG_DIR"

cleanup() {
    echo ""
    echo "Shutting down all processes..."
    kill "$AF_PID" "$BE_PID" "$AF_AGENT_PID" "$FE_PID" 2>/dev/null || true
    exit 0
}
trap cleanup SIGINT SIGTERM

echo "════════════════════════════════════════════════════════════"
echo "  Mom's Saheli — full stack startup"
echo "════════════════════════════════════════════════════════════"

# 1. AgentField control plane (:8080)
echo "🕹️  Starting AgentField control plane on :8080..."
"$AF_BIN" server --port 8080 > "$LOG_DIR/agentfield.log" 2>&1 &
AF_PID=$!
sleep 2

# 2. FastAPI backend (:8000)
echo "🐍 Starting FastAPI backend on :8000..."
cd "$REPO_ROOT/backend"
source .venv/bin/activate
uvicorn app.main:app --port 8000 > "$LOG_DIR/backend.log" 2>&1 &
BE_PID=$!
sleep 2

# 3. AgentField agent (:8001 → registers with :8080)
echo "🤖 Starting AgentField agent on :8001 (registers with control plane)..."
python -m app.agentfield_agent > "$LOG_DIR/af_agent.log" 2>&1 &
AF_AGENT_PID=$!
sleep 3

# 4. React frontend (:5173)
echo "📦 Starting React frontend on :5173..."
cd "$REPO_ROOT/frontend"
npm run dev > "$LOG_DIR/frontend.log" 2>&1 &
FE_PID=$!
sleep 2

echo ""
echo "════════════════════════════════════════════════════════════"
echo "  ✅ All systems go!"
echo ""
echo "  Frontend:              http://localhost:5173"
echo "  Backend API:           http://localhost:8000"
echo "  AgentField dashboard:  http://localhost:8080"
echo "  AgentField agent:      http://localhost:8001"
echo ""
echo "  Logs: $LOG_DIR/"
echo "  Press Ctrl+C to stop everything."
echo "════════════════════════════════════════════════════════════"

wait
