#!/usr/bin/env bash
# scripts/start.sh — boot the full Mom's Saheli stack with a single command.
#
# Starts (in order):
#   1. AgentField control plane on :8080   (skipped if `af` not installed)
#   2. FastAPI backend           on :8000
#   3. AgentField agent          on :8001  (skipped if AGENTFIELD_API_KEY empty
#                                          OR control plane not reachable —
#                                          the agent module itself preflights)
#   4. React frontend            on :5173
#
# Ctrl+C kills all running processes cleanly. Logs go to /tmp/momsaheli/.
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="/tmp/momsaheli"
mkdir -p "$LOG_DIR"

# ── locate `af` (AgentField CLI) ────────────────────────────────────────
AF_BIN="${AF_BIN:-}"
if [[ -z "$AF_BIN" ]]; then
  if [[ -x "$HOME/.agentfield/bin/af" ]]; then
    AF_BIN="$HOME/.agentfield/bin/af"
  elif command -v af >/dev/null 2>&1; then
    AF_BIN="$(command -v af)"
  fi
fi

# ── locate node/npm (avoid hardcoded /tmp paths) ────────────────────────
if ! command -v npm >/dev/null 2>&1; then
  for cand in /tmp/node-v*/bin /usr/local/bin /opt/homebrew/bin "$HOME/.nvm/versions/node/*/bin"; do
    for d in $cand; do
      if [[ -x "$d/npm" ]]; then export PATH="$d:$PATH"; break 2; fi
    done
  done
fi
if ! command -v npm >/dev/null 2>&1; then
  echo "❌ npm not found on PATH. Install Node 22+ or set PATH manually." >&2
  exit 1
fi

# ── PIDs ────────────────────────────────────────────────────────────────
AF_PID=""; BE_PID=""; AF_AGENT_PID=""; FE_PID=""

cleanup() {
  echo ""
  echo "🛑 Shutting down…"
  for pid in "$AF_PID" "$BE_PID" "$AF_AGENT_PID" "$FE_PID"; do
    [[ -n "$pid" ]] && kill "$pid" 2>/dev/null || true
  done
  exit 0
}
trap cleanup SIGINT SIGTERM

echo "════════════════════════════════════════════════════════════"
echo "  Mom's Saheli — full stack startup"
echo "════════════════════════════════════════════════════════════"

# ── 1. AgentField control plane (:8080) ─────────────────────────────────
if [[ -n "$AF_BIN" && -x "$AF_BIN" ]]; then
  echo "🕹️  Starting AgentField control plane on :8080…"
  "$AF_BIN" server --port 8080 > "$LOG_DIR/agentfield.log" 2>&1 &
  AF_PID=$!
  sleep 2
else
  echo "⚠️  AgentField CLI (af) not found — skipping control plane."
  echo "    Install: curl -fsSL https://agentfield.ai/install.sh | sh"
fi

# ── 2. FastAPI backend (:8000) ──────────────────────────────────────────
echo "🐍 Starting FastAPI backend on :8000…"
cd "$REPO_ROOT/backend"
# shellcheck source=/dev/null
source .venv/bin/activate
uvicorn app.main:app --port 8000 > "$LOG_DIR/backend.log" 2>&1 &
BE_PID=$!
sleep 2

# ── 3. AgentField agent (:8001 → registers with :8080) ──────────────────
# The agent module itself preflights (API key + control plane reachability).
# If either is missing it exits 0 silently — we just won't have AF_AGENT_PID.
echo "🤖 Starting AgentField agent on :8001 (preflight will skip if not configured)…"
python -m app.agentfield_agent > "$LOG_DIR/af_agent.log" 2>&1 &
AF_AGENT_PID=$!
sleep 2
# Detect whether it self-skipped
if ! kill -0 "$AF_AGENT_PID" 2>/dev/null; then
  AF_AGENT_PID=""
  echo "    (AgentField agent skipped — see $LOG_DIR/af_agent.log for why)"
fi

# ── 4. React frontend (:5173) ───────────────────────────────────────────
echo "📦 Starting React frontend on :5173…"
cd "$REPO_ROOT/frontend"
npm run dev > "$LOG_DIR/frontend.log" 2>&1 &
FE_PID=$!
sleep 3

echo ""
echo "════════════════════════════════════════════════════════════"
echo "  ✅ All systems go!"
echo ""
echo "  Frontend:              http://localhost:5173"
echo "  Backend API:           http://localhost:8000"
[[ -n "$AF_PID"       ]] && echo "  AgentField dashboard:  http://localhost:8080/ui/"
[[ -n "$AF_AGENT_PID" ]] && echo "  AgentField agent:      http://localhost:8001"
echo ""
echo "  Logs: $LOG_DIR/"
echo "  Press Ctrl+C to stop everything."
echo "════════════════════════════════════════════════════════════"

# Open browser (macOS only — silent on other OSes)
if command -v open >/dev/null 2>&1; then
  (sleep 1 && open http://localhost:5173) &
fi

wait
