# Changelog

All notable changes to this project are documented here. The format
follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and
this project adheres to [Semantic Versioning](https://semver.org/).

## [v0.1.0] — 2026-04-30

跨会话记忆系统首次上线，是本次发布的最大亮点。同时优化了本地启动体验和镜像分发链路。

### Highlights

- **跨会话记忆系统**：用户首次拥有持久化的"记忆"层，让 LLM 在不同会话之间保留偏好、项目上下文、调研结论。4 类记忆 (`user` / `feedback` / `project` / `reference`) × 3 种触发 (`manual` / `compaction` / `session_end`)。
- **共享知识库 (Knowledge Base)**：项目级、人工策划的 `.kimi/memory/knowledge/index.md` 自动注入系统提示，详细内容放 `wiki/` 子目录由 LLM 按需 `ReadFile`；管理员可在 Admin 面板里直接编辑索引。
- **会话归档异步化 + SSE 实时推送**：原同步的归档（5–30 s 阻塞）改为后台任务，HTTP 立即返回 202，结果通过 Server-Sent Events 实时推到前端，多 Tab 自动同步。
- **侧栏归档状态点**：会话行新增 5 态颜色点（gray / blue 脉冲 / green / yellow / red），让用户能一眼看到哪些会话已归档、哪些有新内容、哪些归档失败。
- **本地模式启动**：新增 `scripts/start.sh --mode=local`，无 Docker 也能直接在宿主机跑。

### Added

#### 跨会话记忆 (Memory System)

- 新增 `kimi_cli.memory` 模块：`MemoryEntry`、`SessionSummary`、文件锁存储；三层结构：
  - **Session 级**：`SessionState.session_memory`，仅当前会话可见。
  - **Persistent**：`<user_dir>/memory/persistent.jsonl`，跨会话，写入需用户审批。
  - **Recent**：`<user_dir>/memory/recent.jsonl`，归档时自动追加，下次会话注入提示。
- 新增 `Memory` 工具（LLM 可 `add` / `list` / `update` / `delete`）。
- 新增 `CrossSessionMemoryInjectionProvider` / `SessionMemoryInjectionProvider` 把记忆拼进 system prompt。
- Web API：`/api/memory/{knowledge,persistent,recent,sessions/{id}/archive,events}`。

#### 共享知识库 (Knowledge Base)

- 新增 `kimi_cli.memory.knowledge`：从 `<work_dir>/.kimi/memory/knowledge/index.md` 加载索引（32 KiB 上限），缺失或为空时安静返回 `None`。
- 默认 agent 系统提示加入 `{% if KIMI_KNOWLEDGE_BASE %}` 模板段，把索引拼进 system prompt 并明确告知 LLM：详细内容在 `wiki/`，按需 `ReadFile`，不要擅自改动 `.kimi/memory/knowledge/`。
- 新增 Admin API：`GET/PUT /api/admin/knowledge/index`，由 `KIMI_DEFAULT_WORK_DIR`（缺省时为 `~`）解析共享目录。
- 前端新增 `AdminKnowledgePanel`（`web/src/features/admin/admin-knowledge-panel.tsx`）：Textarea 编辑器 + 路径展示 + 脏检查 + 保存提示。

#### 异步归档 + SSE

- `POST /api/memory/sessions/{id}/archive` 改返 `202 Accepted`，LLM 摘要在 `asyncio.create_task` 后台跑。
- 新增 `MemoryEventBus`（per-user pub/sub）+ `GET /api/memory/events` SSE 通道。
- SSE 鉴权支持 `?token=` 查询参数（绕过 EventSource 不能发自定义 header 的限制）。
- 多 Tab 同账户实时同步。

#### 前端

- `<MemoryStatusDot>` 在 list / grouped / archived 三处渲染，附 Tooltip 说明状态。
- "Record memory" 菜单项按状态门禁（绿 / 蓝时禁用并弹 `<AlertDialog>` 解释原因）。
- 新增 hooks：`useMemoryEvents`、`useRecentSummaries`、`usePersistentMemory`、`useKnowledgeBase`。
- 60 s 轮询 + `visibilitychange` 监听：让 worker 进程触发的归档 ≤60 s 内被前端感知。
- 90 s 安全超时：服务端崩溃时 in-flight 状态自动转 red。
- 新增 Memory 管理面板（`web/src/features/memory/`）和 Admin 知识库面板。

#### 启动体验

- `scripts/start.sh`：自动检测 Docker；不可用时切到本地模式（`python -m kimi_cli web`）。
- 支持 `--mode=local|docker`、`--port=`、`--host=` 参数。
- 新增 `docs/LOCAL-MODE.md` 详细启动指南。
- `KIMI_OUTPUT_DIR`、`KIMI_DEFAULT_WORK_DIR` 环境变量支持。
- 默认通过 `ghcr.io/j0x7c4/kimi-agent-{gateway,sandbox}` 分发镜像，普通用户不再需要本地构建。
- 新增 `docs/MEMORY-ARCHIVE-FEATURE.md`：记录本次记忆系统的设计、技术路线、踩坑、待优化项。

### Changed

- `docker-compose.yml`：默认 `pull_policy: if_not_present`，避免本地开发误从 registry 拉取覆盖本地构建。
- `Runtime` 增加 `user_memory_dir` 字段，所有读写记忆的代码统一走这里。
- 默认 agent 系统提示要求"始终把输出落到 `/app/output`"。

### Fixed

- 文件面板：长文件名不再把下载按钮挤出可视区。
- 上传文件：服务端重启后不再重发已上传文件（`_sent_files` 持久化到磁盘）。
- `SubagentAnimation` 与 cluster 动画重叠时正确 dismiss；后台 sequential agent 的 cluster 检测；minion 与 hero bot 的 z-index。
- 多个 biome 前端 lint 错误。

### Known Issues

- **跨工作目录的记忆注入未做过滤**：本地 CLI（如 `~/.openkimo`）和容器（`/app`）共享同一份 `recent.jsonl`，可能在容器会话提示里看到本机 work_dir 的旧调研。详见 `docs/MEMORY-ARCHIVE-FEATURE.md` §5.8。
- **worker 触发的自动归档** 需要 ≤60 s 的轮询窗口或切焦点才会在前端可见（gateway 与 worker 是两个进程，未走 SSE 推送，详见 §5.1）。
- **SSE 失败事件不持久化**：服务器重启 / 用户没开 Tab 时归档失败提示会丢，详见 §5.2。

### Upgrade Notes

从 v0.0.1 升级时：

1. **拉取或重建镜像**：
   ```bash
   docker compose pull          # 用 ghcr.io 上的新版镜像
   # 或者本地构建：
   docker compose build
   docker build -f Dockerfile.sandbox -t ghcr.io/j0x7c4/kimi-agent-sandbox:latest .
   ```
   ⚠️ 若 `.env` 自定义了 `SANDBOX_IMAGE`（比如 `kimi-agent-sandbox:latest` 而非 ghcr 全名），记得给新镜像打对应 tag：
   ```bash
   docker tag ghcr.io/j0x7c4/kimi-agent-sandbox:latest kimi-agent-sandbox:latest
   ```
2. **重启已有 session 容器**：旧容器仍跑旧镜像，删掉重建即可使用新代码。
3. **持久化记忆目录**：`KIMI_SHARE_DIR/users/<owner_id>/memory/{persistent,recent}.jsonl` 自动创建，无需手动迁移。

---

## [v0.0.1]

首个版本：基础容器化 agent runtime。

- Docker Compose 一键部署。
- Web UI 会话管理、Multi-LLM (Kimi / OpenAI / Anthropic) 支持。
- 强制 Docker sandbox 隔离每个 session。
- Jupyter Kernel + 无头 Chromium + Shell 工具集。
- 资源限额（CPU / 内存 / 磁盘 / PID cgroups）。
- 危险命令拦截。

[v0.1.0]: https://github.com/j0x7c4/OpenKimo/releases/tag/v0.1.0
[v0.0.1]: https://github.com/j0x7c4/OpenKimo/releases/tag/v0.0.1
