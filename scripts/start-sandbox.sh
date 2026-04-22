#!/bin/bash
set -e

echo "========================================"
echo "  kimi-agent-sandbox starting up..."
echo "========================================"

# -----------------------------------------------------------
# 1. 启动虚拟显示 (Xvfb)
# -----------------------------------------------------------
if [ "$ENABLE_BROWSER" != "false" ]; then
    echo "[1/4] Starting Xvfb virtual display..."
    export DISPLAY=:99
    Xvfb :99 -screen 0 1920x1080x24 -ac +extension GLX +render -noreset &
    sleep 1
    echo "      Xvfb started on DISPLAY=:99"
fi

# -----------------------------------------------------------
# 2. 启动 Jupyter Kernel Server
# -----------------------------------------------------------
if [ "$ENABLE_JUPYTER" != "false" ]; then
    echo "[2/4] Starting Jupyter Kernel Server..."
    python /app/kernel_server.py \
        --host 0.0.0.0 \
        --port "${JUPYTER_KERNEL_PORT:-8888}" \
        --log-level info &
    KERNEL_PID=$!
    echo "      Kernel Server PID: $KERNEL_PID"
fi

# -----------------------------------------------------------
# 3. 启动 Browser Guard (后台)
# -----------------------------------------------------------
if [ "$ENABLE_BROWSER" != "false" ]; then
    echo "[3/4] Starting Browser Guard..."
    python /app/browser_guard.py --wait-display --timeout 30 || true
    # BrowserGuard 在 monitor 模式下持续运行
    python /app/browser_guard.py --monitor &
    BROWSER_PID=$!
    echo "      Browser Guard PID: $BROWSER_PID"
fi

# -----------------------------------------------------------
# 4. 启动 KimiCLI Worker (前台)
# -----------------------------------------------------------
echo "[4/4] Starting KimiCLI Worker..."
echo "      Session ID: ${KIMI_SESSION_ID:-unknown}"
echo "      Work Dir: ${KIMI_WORK_DIR:-/app}"
echo ""

# 等待必要的服务就绪
sleep 2

# 启动 Worker (监听 WebSocket，由 Gateway 反向代理)
exec python -m kimi_cli.web.runner.worker \
    --session-id "${KIMI_SESSION_ID:-default}" \
    --host 0.0.0.0 \
    --port "${WORKER_PORT:-8080}"
