# OpenKIMO

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue?logo=docker)](https://www.docker.com/)

A containerized server-side agent framework built on top of [kimi-cli](https://github.com/j0x7c4/kimi-cli). Users operate the agent through a web browser, while all code execution tasks run inside sandboxed Docker containers — nothing executes on the host machine.

## How It Works

1. **User opens the Web UI** in a browser and creates a new session.
2. **The gateway container** (`kimi-gateway`) receives the request and spawns a dedicated Docker container for that session via the Docker socket.
3. **The session sandbox** starts the agent worker, Jupyter kernel, and headless Chromium browser inside the container.
4. **All user prompts** flow through the gateway's WebSocket proxy into the sandbox container.
5. **Tool execution** (Shell, Python, Browser) happens entirely inside the sandbox — the host machine is never touched.
6. **Results** stream back through the WebSocket to the browser in real time.
7. **When the session ends**, the gateway stops and removes the sandbox container automatically.

The host machine only needs Docker Engine installed. No Python, Node.js, or other build tools are required on the host.

## Architecture

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────────┐
│   Browser   │────▶│  kimi-gateway    │────▶│  Session Sandbox    │
│  (Web UI)   │◀────│  (FastAPI + WS)  │◀────│  (Docker per sess)  │
└─────────────┘     └──────────────────┘     └─────────────────────┘
                             │
                             ▼
                     ┌───────────────┐
                     │ Docker Engine │
                     │  (Host only)  │
                     └───────────────┘
```

- **kimi-gateway** — FastAPI web server, WebSocket session proxy, container orchestration
- **Session Sandbox** — One Docker container per session. Runs the agent worker, Jupyter kernel, and headless Chromium browser
- **Host** — Only needs Docker Engine. No Python, Node.js, or other runtimes required

## Features

- **Full Containerization** — Every session runs in its own isolated Docker container
- **Sandboxed Execution** — Shell, Python, and browser tasks execute inside containers, never on the host
- **Web UI** — React-based SPA for managing sessions, chatting with the agent, and reviewing outputs
- **Multi-LLM Support** — Kimi (Moonshot), OpenAI, and Anthropic (Claude) via environment variables
- **Browser Automation** — Headless Chromium with Playwright for web scraping and interaction
- **Jupyter Kernel** — Python code execution via isolated IPython kernel
- **Resource Limits** — Per-container CPU, memory, disk, and PID limits via cgroup

## Quick Start

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

### 1. Clone & Configure

```bash
git clone --recurse-submodules git@github.com:j0x7c4/OpenKimo.git
cd openkimo

cp .env.example .env
# Edit .env and set at least one LLM API key
```

### 2. Build Images

#### Build both images at once (recommended)

```bash
docker-compose build
```

#### Build individually

**Gateway image** (FastAPI server + React frontend):
```bash
docker build -f Dockerfile.gateway -t kimi-agent-gateway:latest .
```

**Sandbox image** (agent worker + Jupyter + Chromium):
```bash
docker build -f Dockerfile.sandbox -t kimi-agent-sandbox:latest .
```

#### Rebuild after code changes

If you modify `kimi-cli/` source or frontend code:
```bash
docker-compose up -d --build
```

### 3. Start the Stack

```bash
docker-compose up -d
```

### 3. Access Web UI

Open http://localhost:5494 in your browser.

#### Default Admin Account

| Field | Value |
|-------|-------|
| Username | `admin` |
| Password | `admin123` |

> **Important:** Change the default password immediately after first login via the admin panel at `/admin`.

If Bearer token authentication is also enabled, append your token to the URL:
```
http://localhost:5494/?token=<your-token>
```

## Configuration

All configuration is done via environment variables in `.env`:

| Variable | Required | Description |
|----------|----------|-------------|
| `KIMI_API_KEY` | Yes* | Kimi / Moonshot API key |
| `OPENAI_API_KEY` | Yes* | OpenAI API key |
| `ANTHROPIC_API_KEY` | Yes* | Anthropic API key |
| `LLM_PROVIDER` | No | Default provider (`kimi` / `openai` / `anthropic`) |
| `KIMI_WEB_SESSION_TOKEN` | No | Bearer token for web UI auth |
| `KIMI_WEB_PORT` | No | Web server port (default: 5494) |
| `SANDBOX_CPU_LIMIT` | No | Per-session CPU limit (default: 2) |
| `SANDBOX_MEMORY_LIMIT` | No | Per-session memory limit (default: 4g) |

\* At least one API key is required.

See [`.env.example`](.env.example) for the full list.

## Project Structure

```
.
├── kimi-cli/              # CLI agent source (FastAPI web, agent loop, tools)
│   ├── src/kimi_cli/
│   └── web/               # React frontend
├── app/                   # Browser automation + Jupyter runtime
│   ├── browser_guard.py
│   ├── jupyter_kernel.py
│   └── kernel_server.py
├── Dockerfile.gateway     # Gateway container image
├── Dockerfile.sandbox     # Session sandbox container image
├── docker-compose.yml     # Docker Compose orchestration
├── scripts/
│   ├── start-gateway.sh
│   └── start-sandbox.sh
└── docs/                  # Documentation & fix records
```

## Security

- Each session runs in a dedicated container with `--privileged=false`
- Resource limits: CPU, memory, disk, and PID cgroup restrictions
- Host filesystem is not mounted into sandboxes (only shared session volume)
- No privilege escalation or host network access by default
- Dangerous shell commands can be blocked via `BLOCK_DANGEROUS_COMMANDS`

## License

This project is licensed under the Apache License 2.0 — see the [LICENSE](LICENSE) file for details.
