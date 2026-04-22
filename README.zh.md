# Kimi Agent

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue?logo=docker)](https://www.docker.com/)

基于 [kimi-cli](https://github.com/j0x7c4/kimi-cli) 构建的容器化服务端 Agent 框架。用户通过浏览器操作 Agent，所有代码执行任务均在沙箱化的 Docker 容器内运行，**禁止直接在宿主机执行**。

## 工作原理

1. **用户在浏览器中打开 Web UI**，创建一个新的 Session。
2. **Gateway 容器** (`kimi-gateway`) 收到请求后，通过挂载的 Docker Socket 为该 Session 启动一个专用的 Docker 容器。
3. **Session 沙箱容器** 内启动 Agent Worker、Jupyter Kernel 和无头 Chromium 浏览器。
4. **所有用户消息** 通过 Gateway 的 WebSocket 代理转发到沙箱容器内的 Worker。
5. **工具执行**（Shell、Python、浏览器访问）完全在沙箱容器内进行，宿主机不受影响。
6. **执行结果** 实时通过 WebSocket 流返回浏览器。
7. **Session 结束**时，Gateway 自动停止并销毁对应的沙箱容器。

宿主机仅需安装 Docker Engine，无需 Python、Node.js 或其他任何运行时。

## 架构

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

- **kimi-gateway** — FastAPI Web 服务器、WebSocket Session 代理、容器编排
- **Session Sandbox** — 每个 Session 一个独立的 Docker 容器，运行 Agent Worker、Jupyter Kernel、无头 Chromium 浏览器
- **宿主机 (Host)** — 只需 Docker Engine，无需 Python、Node.js 等运行时

## 功能特性

- **全容器化** — 每个 Session 运行在独立的 Docker 容器内
- **沙箱执行** — Shell、Python、浏览器任务均在容器内执行，永不触及宿主机
- **Web UI** — 基于 React 的单页应用，支持 Session 管理、Agent 对话、结果查看
- **多 LLM 支持** — 通过环境变量配置 Kimi（Moonshot）、OpenAI、Anthropic (Claude)
- **浏览器自动化** — 集成无头 Chromium + Playwright，支持网页抓取和交互
- **Jupyter Kernel** — 通过隔离的 IPython Kernel 执行 Python 代码
- **资源限制** — 通过 cgroup 限制每个容器的 CPU、内存、磁盘和 PID

## 快速开始

### 前置要求

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

### 1. 克隆与配置

```bash
git clone --recurse-submodules git@github.com:j0x7c4/kimi-agent.git
cd kimi-agent

cp .env.example .env
# 编辑 .env，至少配置一个 LLM API Key
```

### 2. 构建镜像

#### 同时构建两个镜像（推荐）

```bash
docker-compose build
```

#### 分别构建

**Gateway 镜像**（FastAPI 服务器 + React 前端）：
```bash
docker build -f Dockerfile.gateway -t kimi-agent-gateway:latest .
```

**Sandbox 镜像**（Agent Worker + Jupyter + Chromium）：
```bash
docker build -f Dockerfile.sandbox -t kimi-agent-sandbox:latest .
```

#### 修改代码后重新构建

如果修改了 `kimi-cli/` 源码或前端代码：
```bash
docker-compose up -d --build
```

### 3. 启动服务

```bash
docker-compose up -d
```

### 4. 访问 Web UI

浏览器打开 http://localhost:5494

如果启用了认证，请在 URL 中附加 token：
```
http://localhost:5494/?token=<你的token>
```

## 配置说明

所有配置通过 `.env` 文件中的环境变量完成：

| 变量 | 必填 | 说明 |
|------|------|------|
| `KIMI_API_KEY` | 是* | Kimi / Moonshot API Key |
| `OPENAI_API_KEY` | 是* | OpenAI API Key |
| `ANTHROPIC_API_KEY` | 是* | Anthropic API Key |
| `LLM_PROVIDER` | 否 | 默认 LLM 提供商 (`kimi` / `openai` / `anthropic`) |
| `KIMI_WEB_SESSION_TOKEN` | 否 | Web UI 访问认证 Token |
| `KIMI_WEB_PORT` | 否 | Web 服务端口 (默认: 5494) |
| `SANDBOX_CPU_LIMIT` | 否 | 每个 Session 的 CPU 限制 (默认: 2) |
| `SANDBOX_MEMORY_LIMIT` | 否 | 每个 Session 的内存限制 (默认: 4g) |

\* 至少配置一个 API Key。

完整配置列表请参见 [`.env.example`](.env.example)。

## 项目结构

```
.
├── kimi-cli/              # CLI Agent 源码 (FastAPI Web、Agent 循环、工具集)
│   ├── src/kimi_cli/
│   └── web/               # React 前端
├── app/                   # 浏览器自动化 + Jupyter 运行时
│   ├── browser_guard.py
│   ├── jupyter_kernel.py
│   └── kernel_server.py
├── Dockerfile.gateway     # Gateway 容器镜像
├── Dockerfile.sandbox     # Session 沙箱容器镜像
├── docker-compose.yml     # Docker Compose 编排配置
├── scripts/
│   ├── start-gateway.sh   # Gateway 启动脚本
│   └── start-sandbox.sh   # Sandbox 启动脚本
└── docs/                  # 文档与修复记录
```

## 安全说明

- 每个 Session 在独立容器中运行，使用 `--privileged=false`
- 资源限制：CPU、内存、磁盘和 PID 的 cgroup 限制
- 宿主机文件系统不挂载到沙箱容器（仅共享 Session 数据卷）
- 默认禁止特权提升和宿主机网络访问
- 可通过 `BLOCK_DANGEROUS_COMMANDS=true` 拦截危险 Shell 命令

## 许可证

本项目基于 Apache License 2.0 开源，详见 [LICENSE](LICENSE) 文件。
