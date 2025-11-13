#!/usr/bin/env bash
set -euo pipefail


# Path to SSH key
KEY_PATH="${KEY_PATH:-$HOME/.ssh/hkn-portal.pem}"

# Python executable to use when creating the venv
PY_BIN="${PY_BIN:-python3}"

# Virtual environment directory name
VENV_DIR="${VENV_DIR:-venv}"

# Frontend directory 
FRONTEND_DIR="${FRONTEND_DIR:-frontend}"

# Backend manage.py location 
MANAGE_PY_PATH="${MANAGE_PY_PATH:-manage.py}"

# Frontend dev command and Backend dev command
FRONTEND_DEV_CMD="${FRONTEND_DEV_CMD:-npm run dev}"
BACKEND_DEV_CMD="${BACKEND_DEV_CMD:-$PY_BIN ${MANAGE_PY_PATH} runserver}"


log() { printf "\033[1;34m[INFO]\033[0m %s\n" "$*"; }
warn() { printf "\033[1;33m[WARN]\033[0m %s\n" "$*"; }
err() { printf "\033[1;31m[ERR ]\033[0m %s\n" "$*" 1>&2; }
die() { err "$*"; exit 1; }

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "Required command '$1' not found in PATH"
}


need_cmd git
need_cmd "$PY_BIN"
need_cmd pip3 || true
need_cmd npm

[ -f "$KEY_PATH" ] || die "SSH key not found at $KEY_PATH. Update KEY_PATH or create the key."

[ -f "requirements.txt" ] || die "requirements.txt not found in repo root."
[ -d "$FRONTEND_DIR" ] || die "Frontend directory '$FRONTEND_DIR' not found."
[ -f "$MANAGE_PY_PATH" ] || die "Could not find backend entrypoint at '$MANAGE_PY_PATH'."


log "Pulling latest changes..."
git pull --ff-only || die "git pull failed."


if [ -d "$VENV_DIR" ]; then
  log "Removing existing virtual environment '$VENV_DIR'..."
  rm -rf "$VENV_DIR"
fi

log "Creating virtual environment '$VENV_DIR'..."
"$PY_BIN" -m venv "$VENV_DIR" || die "Failed to create virtualenv."

source "$VENV_DIR/bin/activate"
trap 'deactivate || true' EXIT

log "Upgrading pip..."
python -m pip install --upgrade pip wheel setuptools || die "pip upgrade failed."

log "Installing Python requirements..."
python -m pip install -r requirements.txt || die "pip install -r requirements.txt failed."


pushd "$FRONTEND_DIR" >/dev/null

if [ -d "node_modules" ]; then
  log "Found existing node_modules. Running clean install via 'npm ci'..."
  npm ci || die "npm ci failed."
else
  if [ -f "package-lock.json" ]; then
    log "No node_modules but package-lock.json found. Running 'npm ci'..."
    npm ci || die "npm ci failed."
  else
    log "No lockfile found. Running 'npm install'..."
    npm install || die "npm install failed."
  fi
fi

log "Pruning extraneous packages (npm prune)..."
npm prune || warn "npm prune issued a warning."

USE_TMUX=0
if command -v tmux >/dev/null 2>&1; then
  USE_TMUX=1
fi

popd >/dev/null


if [ "$USE_TMUX" -eq 1 ]; then
  SESSION_NAME="hkn_portal_dev"

  if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
    warn "tmux session '$SESSION_NAME' already exists; killing it."
    tmux kill-session -t "$SESSION_NAME"
  fi

  log "Starting dev servers in tmux session '$SESSION_NAME'..."
  tmux new-session -d -s "$SESSION_NAME" "cd \"$(pwd)/$FRONTEND_DIR\" && $FRONTEND_DEV_CMD"
  tmux split-window -h -t "$SESSION_NAME" "cd \"$(pwd)\" && source \"$VENV_DIR/bin/activate\" && $BACKEND_DEV_CMD"
  tmux select-layout -t "$SESSION_NAME" even-horizontal

  log "Attach with: tmux attach -t $SESSION_NAME"
  log "Detach with: Ctrl-b then d"
else
  log "tmux not found. Starting frontend and backend in background..."

  ( cd "$FRONTEND_DIR" && $FRONTEND_DEV_CMD ) > frontend.dev.log 2>&1 &
  FRONTEND_PID=$!
  log "Frontend started (PID $FRONTEND_PID). Logs: $(pwd)/$FRONTEND_DIR/frontend.dev.log"

  log "Starting Django dev server..."
  $BACKEND_DEV_CMD
fi

log "Done."