#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# ============================================================
# Argument parsing
# ============================================================

MODE="${MODE:-}"
PORT=""
HOST=""

print_help() {
    cat <<EOF
Usage: $0 [OPTIONS]

Unified startup script for kimi-agent (Docker or local mode).

Options:
  --mode=docker|local   Force a specific mode (overrides MODE env var)
  --port=PORT           Web server port (local mode only, overrides KIMI_WEB_PORT)
  --host=HOST           Web server bind host (local mode only, overrides KIMI_WEB_HOST)
  -h, --help            Show this help message

Mode detection order:
  1. --mode flag
  2. MODE environment variable
  3. Auto-detect: use Docker if available, otherwise local

Examples:
  $0                          # auto-detect
  $0 --mode=local             # force local mode
  $0 --mode=local --port=8080 # local mode on port 8080
  MODE=local $0               # same as --mode=local
  $0 --mode=docker            # force docker-compose up
EOF
}

for arg in "$@"; do
    case "$arg" in
        --mode=*)   MODE="${arg#--mode=}" ;;
        --port=*)   PORT="${arg#--port=}" ;;
        --host=*)   HOST="${arg#--host=}" ;;
        -h|--help)  print_help; exit 0 ;;
        *)          echo "Unknown option: $arg"; print_help; exit 1 ;;
    esac
done

# ============================================================
# Load .env
# ============================================================

load_env() {
    local env_file="$PROJECT_DIR/.env"
    if [ -f "$env_file" ]; then
        echo "Loading $env_file"
        set -o allexport
        # shellcheck disable=SC1090
        source "$env_file"
        set +o allexport
    fi
}

# ============================================================
# Mode detection
# ============================================================

detect_mode() {
    if [ -n "$MODE" ]; then
        return
    fi
    if command -v docker &>/dev/null && docker info &>/dev/null 2>&1; then
        MODE="docker"
    else
        MODE="local"
    fi
}

# ============================================================
# Docker mode
# ============================================================

start_docker() {
    echo "========================================"
    echo "  kimi-agent starting (Docker mode)..."
    echo "========================================"

    if ! command -v docker &>/dev/null; then
        echo "ERROR: docker command not found. Install Docker or use --mode=local."
        exit 1
    fi

    if ! docker info &>/dev/null 2>&1; then
        echo "ERROR: Docker daemon is not running."
        exit 1
    fi

    # Prefer 'docker compose' (v2) over 'docker-compose' (v1)
    if docker compose version &>/dev/null 2>&1; then
        COMPOSE_CMD="docker compose"
    elif command -v docker-compose &>/dev/null; then
        COMPOSE_CMD="docker-compose"
    else
        echo "ERROR: Neither 'docker compose' nor 'docker-compose' found."
        exit 1
    fi

    cd "$PROJECT_DIR"
    echo "Running: $COMPOSE_CMD up"
    echo ""
    exec $COMPOSE_CMD up
}

# ============================================================
# Local mode
# ============================================================

start_local() {
    echo "========================================"
    echo "  kimi-agent starting (local mode)..."
    echo "========================================"

    # Validate Python
    if ! command -v python3 &>/dev/null && ! command -v python &>/dev/null; then
        echo "ERROR: Python not found. Install Python 3.10+ and kimi-cli dependencies."
        exit 1
    fi
    PYTHON="${PYTHON:-$(command -v python3 || command -v python)}"

    # Validate kimi_cli is importable; add repo src to PYTHONPATH if needed
    if ! "$PYTHON" -c "import kimi_cli" &>/dev/null 2>&1; then
        KIMI_SRC="$PROJECT_DIR/kimi-cli/src"
        if [ -d "$KIMI_SRC" ] && PYTHONPATH="$KIMI_SRC:${PYTHONPATH}" "$PYTHON" -c "import kimi_cli" &>/dev/null 2>&1; then
            export PYTHONPATH="$KIMI_SRC:${PYTHONPATH}"
            echo "Using kimi_cli from $KIMI_SRC"
        else
            echo "ERROR: kimi_cli package not found."
            echo "       Run: pip install -e $PROJECT_DIR/kimi-cli"
            exit 1
        fi
    fi

    # Validate LLM API key
    if [ -z "$KIMI_API_KEY" ] && [ -z "$OPENAI_API_KEY" ] && [ -z "$ANTHROPIC_API_KEY" ]; then
        echo "WARNING: No LLM API key configured."
        echo "         Set at least one of: KIMI_API_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY"
    fi

    # Local mode: no Docker containers for sessions
    export KIMI_USE_CONTAINERS=false
    export ENABLE_BROWSER=false
    export ENABLE_JUPYTER=false

    # Default work directory for new sessions
    export KIMI_DEFAULT_WORK_DIR="${KIMI_DEFAULT_WORK_DIR:-$HOME/.openkimo}"

    # Session data directory — also used for users.db (KIMI_SHARE_DIR)
    SESSIONS_DIR="${KIMI_SESSION_DATA_DIR:-$PROJECT_DIR/data/sessions}"
    mkdir -p "$SESSIONS_DIR"
    export KIMI_SESSIONS_DIR="$SESSIONS_DIR"
    export KIMI_SHARE_DIR="$SESSIONS_DIR"

    # Static files (from repo if not overridden)
    if [ -z "$KIMI_WEB_STATIC_DIR" ]; then
        STATIC_DIR="$PROJECT_DIR/kimi-cli/src/kimi_cli/web/static"
        if [ -d "$STATIC_DIR" ]; then
            export KIMI_WEB_STATIC_DIR="$STATIC_DIR"
        fi
    fi

    # Resolve host and port (CLI flag > env var > default)
    LISTEN_PORT="${PORT:-${KIMI_WEB_PORT:-5494}}"
    LISTEN_HOST="${HOST:-${KIMI_WEB_HOST:-0.0.0.0}}"

    echo ""
    echo "Configuration:"
    echo "  Listen:       ${LISTEN_HOST}:${LISTEN_PORT}"
    echo "  LLM Provider: ${LLM_PROVIDER:-not set}"
    echo "  Model:        ${KIMI_MODEL_NAME:-not set}"
    echo "  Sessions Dir: ${KIMI_SESSIONS_DIR}"
    echo "  Default Work: ${KIMI_DEFAULT_WORK_DIR}"
    echo "  Browser:      disabled"
    echo "  Jupyter:      disabled"
    echo ""

    exec "$PYTHON" -m uvicorn "kimi_cli.web.app:create_app" \
        --factory \
        --host "$LISTEN_HOST" \
        --port "$LISTEN_PORT" \
        --log-level info \
        --timeout-graceful-shutdown 3
}

# ============================================================
# Main
# ============================================================

load_env
detect_mode

case "$MODE" in
    docker) start_docker ;;
    local)  start_local ;;
    *)
        echo "ERROR: Unknown mode '$MODE'. Use 'docker' or 'local'."
        exit 1
        ;;
esac
