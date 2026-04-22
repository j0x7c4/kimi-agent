# kimi-cli + app 服务端 Agent 框架改造方案

## 目标

将 kimi-cli（本地 CLI agent）和 app（浏览器+Jupyter 运行时）合并改造为一个**服务器端 Agent 框架**。用户通过浏览器访问 Web UI 操作 agent，所有代码执行任务必须在**沙箱环境**中运行，禁止直接在宿主机执行。

## 现状分析

- **kimi-cli**：已有 FastAPI Web 服务（端口 5494）和 WebSocket session 机制，但所有 Shell/File/Web 工具直接在宿主机执行，无任何沙箱隔离
- **app**：提供 Jupyter Kernel 管理和浏览器自动化（Chromium），但无 web 接入层
- **kaos**：包抽象了文件系统/进程接口（`LocalKaos`），但未实现远程/沙箱版本

## 总体架构（全容器化）

整个系统**全部运行在 Docker 容器内**，宿主机只需要 Docker Engine，无需安装任何 Python 依赖。

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              宿主机 (Host)                                   │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                     Docker Compose / docker stack                       ││
│  │  ┌─────────────────────────────────────────────────────────────────┐   ││
│  │  │  kimi-gateway 容器                                               │   ││
│  │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │   ││
│  │  │  │ FastAPI     │  │ 静态文件    │  │ Docker SDK (docker-py)  │ │   ││
│  │  │  │ Web API     │  │ (React SPA) │  │ 管理 session 容器       │ │   ││
│  │  │  └─────────────┘  └─────────────┘  └─────────────────────────┘ │   ││
│  │  │         │                                              │        │   ││
│  │  │         │ 挂载 /var/run/docker.sock ───────────────────┘        │   ││
│  │  └─────────┼────────────────────────────────────────────────────────┘   ││
│  │            │                                                             ││
│  │            ▼  WebSocket / HTTP 代理                                      ││
│  │  ┌─────────────────────────────────────────────────────────────────┐    ││
│  │  │              Session Sandbox 容器池（动态创建）                    │    ││
│  │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │    ││
│  │  │  │ session-A   │  │ session-B   │  │ session-N   │             │    ││
│  │  │  │             │  │             │  │             │             │    ││
│  │  │  │ • Worker    │  │ • Worker    │  │ • Worker    │             │    ││
│  │  │  │ • KAOS      │  │ • KAOS      │  │ • KAOS      │             │    ││
│  │  │  │ • Jupyter   │  │ • Jupyter   │  │ • Jupyter   │             │    ││
│  │  │  │   Kernel    │  │   Kernel    │  │   Kernel    │             │    ││
│  │  │  │ • Chromium  │  │ • Chromium  │  │ • Chromium  │             │    ││
│  │  │  └─────────────┘  └─────────────┘  └─────────────┘             │    ││
│  │  └─────────────────────────────────────────────────────────────────┘    ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│           │                                                                 │
│           ▼                                                                 │
│      用户浏览器                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 核心改造点

### 1. 沙箱化 KAOS 层

**当前问题**：`LocalKaos` 直接调用 `asyncio.create_subprocess_exec` 和 `aiofiles`，在宿主机执行命令。

**改造方案**：
- 将 `LocalKaos` 保留为容器内实现（每个沙箱容器里用 `LocalKaos`）
- Gateway 容器不再需要 `Kaos` 实例，它只负责 HTTP/WebSocket 代理和容器生命周期管理
- 每个 session worker 运行在独立 Docker 容器内，容器内使用 `LocalKaos`（此时"local"就是容器内的本地环境）

**关键文件**：
- `kimi-cli/packages/kaos/src/kaos/local.py` —— 无需改动，复用为容器内实现
- `kimi-cli/src/kimi_cli/web/runner/process.py` —— 改造 `SessionProcess` 为容器进程

### 2. Session Worker 容器化

**当前问题**：`SessionProcess` 在宿主机通过 `subprocess.Popen` 启动 Python worker 脚本。

**改造方案**：
- 构建一个 `kimi-agent-sandbox` Docker 镜像，包含：
  - Python 3.12+ 及 kimi-cli 所有依赖
  - `app/` 目录代码（browser_guard, jupyter_kernel, kernel_server）
  - Chromium 浏览器 + Xvfb（虚拟显示）
  - Jupyter kernel（ipykernel）
- 每个 session 对应一个容器实例
- Gateway 通过 Docker API 管理容器生命周期（创建/启动/停止/销毁）
- Worker 进程在容器内监听 Unix Socket 或 TCP，Gateway 通过反向代理连接 WebSocket

**关键改动**：
- 修改 `SessionProcess`：不再 `subprocess.Popen`，改为调用 Docker SDK (`docker-py`)
- 新增 `kimi_cli.web.runner.container` 模块，封装容器操作
- 容器启动命令：`python -m kimi_cli.web.runner.worker --session-id {id}`
- 容器挂载：只将 session 数据目录（Docker volume）挂载到容器内，宿主机其他目录不可见

### 3. 整合 Browser Guard —— 每个容器内置浏览器

**当前问题**：`browser_guard.py` 独立运行，没有与 kimi-cli 的 web 工具集成。

**改造方案**：
- 在 sandbox 镜像中预装 Chromium + Playwright
- 容器启动时自动启动 `BrowserGuard`（通过 `CHROME_INIT_URL` 等环境变量配置）
- `kimi_cli.tools.web`（FetchURL/SearchWeb）改造为通过 CDP 或内部 API 与容器内浏览器通信
- 浏览器运行在容器内的 Xvfb 虚拟显示上，无需真实 X11

**关键文件**：
- `app/browser_guard.py` —— 放入镜像，作为容器内服务
- `kimi-cli/src/kimi_cli/tools/web/fetch.py` —— 改为调用容器内浏览器服务

### 4. 整合 Jupyter Kernel —— Python 代码沙箱执行

**当前问题**：Shell 工具执行 `python script.py` 与执行 `bash cmd` 没有本质区别，都在同一进程空间。

**改造方案**：
- 容器内启动 `kernel_server.py`（FastAPI，端口 8888）
- 新增 `Python` tool 到 kimi-cli 工具集，专门用于执行 Python 代码
- `Python` tool 通过 HTTP 调用容器内的 `kernel_server`
  - `POST /kernel/reset` — 重置环境
  - `POST /kernel/interrupt` — 中断执行
  - `GET /kernel/connection` — 获取连接信息
  - 通过 Jupyter Client 连接 kernel 执行代码
- 所有 Python 代码**必须**通过此通道执行，禁止 Shell tool 直接运行 `python xxx.py`
- 容器内 Kernel 进程与普通 Shell 进程隔离，崩溃不影响主 worker

**关键文件**：
- `app/kernel_server.py` —— 放入镜像，监听 `127.0.0.1:8888`
- `app/jupyter_kernel.py` —— 放入镜像，管理 kernel 生命周期
- `kimi-cli/src/kimi_cli/tools/` —— 新增 `python/__init__.py`

### 5. Shell 工具沙箱化

**当前问题**：Shell tool 直接执行宿主机命令，风险最高。

**改造方案**：
- 容器内执行 → 天然隔离（容器就是沙箱）
- 资源限制：每个容器配置 cgroup 限制
  - CPU: 2 core
  - Memory: 4GB
  - Disk: 10GB overlayfs
  - Network: 可选桥接/禁止外网（根据配置）
- 命令白名单（可选增强）：在 Shell tool 中加入安全检查层，拦截危险命令（`rm -rf /`, `mkfs`, `dd if=/dev/zero of=/dev/sda` 等）
- 禁止特权模式：`--privileged=false`，丢弃 `CAP_SYS_ADMIN` 等能力

### 6. File 工具沙箱化

**当前问题**：File tool 直接读写宿主机文件。

**改造方案**：
- 容器内 `LocalKaos` 只能看到容器内的文件系统
- 需要持久化的 session 数据（context、state、uploads）通过 Docker volume 挂载到容器内
- Gateway 容器的 `/api/sessions/{id}/files` 和 `/api/sessions/{id}/uploads` 仍然可以访问，因为数据在共享 volume 中

### 7. LLM API 环境变量配置

**当前问题**：kimi-cli 依赖本地 OAuth 登录或 `~/.kimi/config.toml` 配置 API Key，不适合服务器端无头部署。

**改造方案**：
- 所有 LLM 配置通过**环境变量**注入 Gateway 容器和 Sandbox 容器
- 遵循 OpenAI SDK 标准命名，同时兼容 kimi 特有变量
- Gateway 在启动时读取环境变量，生成 `Config` 对象传递给 worker

**环境变量清单**：

| 变量名 | 必填 | 说明 | 示例 |
|--------|------|------|------|
| `KIMI_API_KEY` | 是* | Kimi / Moonshot API Key | `sk-xxx` |
| `KIMI_BASE_URL` | 否 | API 基础 URL | `https://api.moonshot.cn/v1` |
| `KIMI_MODEL_NAME` | 否 | 默认模型名称 | `kimi-k2` |
| `OPENAI_API_KEY` | 是* | OpenAI API Key（如使用 OpenAI） | `sk-xxx` |
| `OPENAI_BASE_URL` | 否 | OpenAI 兼容端点 | `https://api.openai.com/v1` |
| `ANTHROPIC_API_KEY` | 是* | Anthropic API Key（如使用 Claude） | `sk-ant-xxx` |
| `LLM_PROVIDER` | 否 | 默认 provider 类型 | `kimi` / `openai` / `anthropic` |
| `LLM_THINKING` | 否 | 是否启用 thinking | `true` / `false` |
| `LLM_TEMPERATURE` | 否 | 采样温度 | `0.7` |

*注：至少配置一个 API Key。*

**实现要点**：
- 改造 `kimi_cli/config.py` 的 `load_config()`，优先从环境变量读取，回退到配置文件
- 改造 `kimi_cli/llm.py` 的 `augment_provider_with_env_vars()`，在服务器模式下跳过 OAuth 流程
- Sandbox 容器通过 `--env` 或 docker-compose 继承 Gateway 的 LLM 环境变量

### 8. Gateway 改造 —— 多 Session 容器编排

**当前问题**：`KimiCLIRunner` 管理宿主机子进程。

**改造方案**：
- Gateway 自身也运行在 Docker 容器内（`kimi-gateway` 服务）
- Gateway 容器挂载宿主机的 `/var/run/docker.sock`，通过 Docker SDK 管理 session 容器
- 新增 `ContainerRunner` 替代/扩展 `KimiCLIRunner`
- 功能：
  - `create(session_id)` → `docker run` 启动容器
  - `start(session_id)` → 启动已存在的容器
  - `stop(session_id)` → `docker stop`
  - `destroy(session_id)` → `docker rm -f`
  - `list()` → 列出运行中的 session 容器
  - `exec(session_id, cmd)` → `docker exec` 执行命令（用于调试）
- 容器命名规范：`kimi-session-{session_id}`
- 容器网络：使用 Docker bridge 网络，每个容器独立 IP
- WebSocket 代理：Gateway 将 `/api/sessions/{id}/stream` WebSocket 连接转发到容器内的 worker socket

**docker-compose.yml 示例**：

```yaml
services:
  gateway:
    build:
      context: .
      dockerfile: Dockerfile.gateway
    ports:
      - "5494:5494"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock  # 管理其他容器
      - session-data:/data/sessions                # session 数据持久化
      - ./app/.agents/skills:/app/.agents/skills:ro # skills 只读挂载
    environment:
      # LLM 配置（至少配置一个）
      - KIMI_API_KEY=${KIMI_API_KEY}
      - KIMI_BASE_URL=${KIMI_BASE_URL:-https://api.moonshot.cn/v1}
      - KIMI_MODEL_NAME=${KIMI_MODEL_NAME:-kimi-k2}
      - OPENAI_API_KEY=${OPENAI_API_KEY:-}
      - OPENAI_BASE_URL=${OPENAI_BASE_URL:-}
      # Web 安全
      - KIMI_WEB_SESSION_TOKEN=${KIMI_WEB_SESSION_TOKEN}
      - KIMI_WEB_ALLOWED_ORIGINS=${KIMI_WEB_ALLOWED_ORIGINS:-*}
      # 容器编排
      - DOCKER_NETWORK=kimi-agent-network
    networks:
      - kimi-agent-network

networks:
  kimi-agent-network:
    driver: bridge

volumes:
  session-data:
```

### 9. 镜像构建 (`Dockerfile`)

```dockerfile
# 基础镜像
FROM python:3.12-slim-bookworm

# 安装系统依赖：Chromium, Xvfb, git, ripgrep 等
RUN apt-get update && apt-get install -y \
    chromium xvfb x11-utils x11-xserver-utils \
    git ripgrep curl wget \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY kimi-cli/pyproject.toml kimi-cli/uv.lock ./
RUN pip install uv && uv pip install --system -r pyproject.toml

# 安装 Playwright 浏览器
RUN playwright install chromium

# 复制 app/ 代码
COPY app/ /app/
COPY kimi-cli/src/ /usr/local/lib/python3.12/site-packages/

# 暴露端口（Worker WebSocket + Kernel Server）
EXPOSE 8080 8888

# 启动脚本
COPY scripts/start-sandbox.sh /start-sandbox.sh
CMD ["/start-sandbox.sh"]
```

`start-sandbox.sh` 逻辑：
1. 启动 Xvfb（虚拟显示）
2. 启动 Jupyter Kernel Server（后台）
3. 启动 Browser Guard（后台）
4. 启动 KimiCLI Worker（前台，监听 WebSocket）

### 10. 安全加固清单

| 层面 | 措施 |
|------|------|
| 容器隔离 | 每个 session 独立容器，overlayfs 隔离 |
| 资源限制 | CPU 2核 / 内存 4GB / 磁盘 10GB / PIDs 1000 |
| 网络隔离 | 默认 bridge 网络，可选禁止外网访问 |
| 特权限制 | `--privileged=false`，精简 capabilities |
| 文件系统 | 只挂载 session volume，宿主机根目录不可见 |
| 内核安全 | AppArmor/SELinux 策略（可选） |
| 超时控制 | 容器存活超时（如 24h 自动销毁） |
| 数据清理 | session 删除时同步销毁容器和 volume |
| 命令过滤 | Shell tool 加入危险命令黑名单 |
| Python 隔离 | 强制通过 Jupyter Kernel 执行，禁止直接 python 命令 |

### 11. Skills 部署与容器内加载

**当前问题**：`app/.agents/skills/` 中有大量 skill 定义，需要确保在 sandbox 容器内能被正确发现。

**Skills 加载机制分析**（基于 `kimi_cli/skill/__init__.py`）：
- `resolve_skills_roots()` 按优先级查找：内置 skills → 用户级 (`~/.agents/skills`) → 项目级 (`{work_dir}/.agents/skills`)
- `discover_skills()` 遍历目录中的子目录，读取每个 `SKILL.md` 文件
- 只要目录在容器内文件系统可见，且 `KaosPath` 能访问，就能正常加载

**改造方案（推荐打包进镜像）**：
- **首选**：将 `app/.agents/skills` **复制进 sandbox 镜像**（`COPY app/.agents/skills /app/.agents/skills`）
  - 优点：无需挂载，每个容器自带 skills，启动更快，无路径问题
  - 适合 skills 不频繁更新的场景
- **备选**：作为只读 volume 挂载到 `work_dir/.agents/skills`
  - 优点：skills 更新无需重建镜像
  - 缺点：需确保挂载路径与容器内 `work_dir` 一致

**容器内加载验证**：
- `LocalKaos` 在容器内正常运行，`iterdir()` 和 `readtext()` 可以读取 skills 文件
- skills 是只读的，无需写权限
- 通过 `Runtime.create()` 中的 `discover_skills_from_roots()` 自动发现

**镜像构建补充**：

```dockerfile
# Dockerfile.sandbox 中增加
COPY app/.agents/skills /app/.agents/skills
ENV SKILLS_DIR=/app/.agents/skills
```

Sandbox 容器启动时，`work_dir` 设为 `/app`，则 `/app/.agents/skills` 会被 `find_project_skills_dirs()` 自动发现。

### 12. 现有 Web UI 复用

- 复用 `kimi-cli/web` 目录下的 React/Vite 前端
- 复用 `kimi-cli/src/kimi_cli/web/api/` 的 FastAPI 路由
- WebSocket 流机制不变，只是后端 worker 从子进程变为容器
- 新增管理页面：展示运行中的 session 容器列表、资源占用、日志

## 文件改动清单

### 新增文件
- `kimi-cli/src/kimi_cli/web/runner/container.py` — ContainerRunner 实现
- `kimi-cli/src/kimi_cli/tools/python/__init__.py` — Python tool（调用 Jupyter Kernel）
- `Dockerfile.gateway` — Gateway 容器镜像（FastAPI + Web UI + Docker SDK）
- `Dockerfile.sandbox` — Sandbox 容器镜像（Worker + Browser + Jupyter）
- `docker-compose.yml` — 编排配置
- `scripts/start-sandbox.sh` — Sandbox 容器启动脚本
- `scripts/build-image.sh` — 镜像构建脚本

### 修改文件
- `kimi-cli/src/kimi_cli/web/runner/process.py` — SessionProcess 容器化改造
- `kimi-cli/src/kimi_cli/web/app.py` — 集成 ContainerRunner
- `kimi-cli/src/kimi_cli/web/api/sessions.py` — WebSocket 代理到容器
- `kimi-cli/src/kimi_cli/tools/shell/__init__.py` — 增加命令安全检查
- `kimi-cli/src/kimi_cli/tools/web/fetch.py` — 改为调用容器内浏览器
- `app/kernel_server.py` — 适配容器内运行（监听 0.0.0.0）
- `app/browser_guard.py` — 适配无头/虚拟显示环境

### 复用不变文件
- `kimi-cli/packages/kaos/src/kaos/local.py` — 作为容器内 KAOS
- `kimi-cli/src/kimi_cli/soul/` — agent 核心逻辑不变
- `kimi-cli/src/kimi_cli/web/store/` — session 存储逻辑不变
- `app/jupyter_kernel.py` — kernel 管理逻辑不变
- `app/utils.py` — 工具函数不变

## 验证方案

1. **构建镜像**：`docker-compose build`
2. **启动系统**：`docker-compose up -d`
3. **访问 Web UI**：浏览器打开 `http://localhost:5494`
4. **创建 Session**：通过 Web UI 或 API 创建新 session
   - 预期：Gateway 自动调用 Docker API 启动 sandbox 容器
5. **执行 Shell**：在 Web UI 中发送 "Run `ls -la`"
   - 预期：命令在容器内执行，返回容器内文件列表（不是宿主机）
6. **执行 Python**：发送 "计算 1+1"
   - 预期：通过 Jupyter Kernel 执行，返回结果
7. **访问网页**：发送 "Fetch https://example.com"
   - 预期：容器内浏览器访问网页，返回内容
8. **资源隔离验证**：在容器内执行 `cat /proc/self/status`，确认 cgroup 限制生效
9. **Session 销毁**：删除 session
   - 预期：对应 Docker 容器被停止并删除
10. **并发测试**：同时创建 10 个 session
    - 预期：10 个独立容器运行，互不干扰
11. **宿主机安全验证**：在 Web UI 中尝试 `cat /etc/passwd`（宿主机敏感文件）
    - 预期：只能看到容器内的 `/etc/passwd`，与宿主机隔离

## 依赖新增

- `docker` (docker-py) — Docker SDK for Python（Gateway 容器内调用 Docker API）
- Docker Compose — 编排 Gateway 和 Session 容器

## 部署方式

```bash
# 1. 克隆代码
git clone <repo>
cd kimi-agent

# 2. 构建镜像
docker-compose build

# 3. 启动服务
docker-compose up -d

# 4. 访问 Web UI
open http://localhost:5494
```

宿主机**仅需安装 Docker + Docker Compose**，无需 Python、Node.js 或其他运行时。
