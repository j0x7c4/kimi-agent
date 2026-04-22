#!/bin/bash
set -e

echo "========================================"
echo "  kimi-agent-gateway starting up..."
echo "========================================"

# Validate required environment
if [ -z "$KIMI_WEB_SESSION_TOKEN" ]; then
    echo "WARNING: KIMI_WEB_SESSION_TOKEN is not set."
    echo "         Running without authentication - suitable for local development only."
fi

# Validate LLM configuration
if [ -z "$KIMI_API_KEY" ] && [ -z "$OPENAI_API_KEY" ] && [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "WARNING: No LLM API key configured."
    echo "Set at least one of: KIMI_API_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY"
fi

# Configure session storage
export KIMI_SESSIONS_DIR="/data/sessions"
mkdir -p "$KIMI_SESSIONS_DIR"

# Web UI static files directory
export KIMI_WEB_STATIC_DIR="/app/src/kimi_cli/web/static"

# Set Python path to include source
export PYTHONPATH="/app/src:${PYTHONPATH}"

# Determine listen host/port
HOST="${KIMI_WEB_HOST:-0.0.0.0}"
PORT="${KIMI_WEB_PORT:-5494}"

echo ""
echo "Configuration:"
echo "  Listen:       ${HOST}:${PORT}"
echo "  LLM Provider: ${LLM_PROVIDER:-not set}"
echo "  Model:        ${KIMI_MODEL_NAME:-not set}"
echo "  Sessions Dir: ${KIMI_SESSIONS_DIR}"
echo "  Sandbox Image: ${SANDBOX_IMAGE:-kimi-agent-sandbox:latest}"
echo ""

# Start the web server via uvicorn (factory mode reads env vars directly)
exec uvicorn "kimi_cli.web.app:create_app" \
    --factory \
    --host "$HOST" \
    --port "$PORT" \
    --log-level info \
    --timeout-graceful-shutdown 3
