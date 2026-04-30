# 会话记忆归档功能改造

本文记录"Record memory"（会话记忆归档）功能从同步阻塞调用改造为后台任务 + SSE 推送 + 状态点的全过程，包含设计方案、技术路线选择、踩到的坑、解决方案，以及后续待优化项。

---

## 1. 背景

`POST /api/memory/sessions/{id}/archive` 用 LLM 把一个会话压缩为一段摘要写入 `recent.jsonl`，供下一次跨会话记忆注入使用。改造前的痛点：

- LLM 单次往返 5–30 s，**HTTP 请求同步阻塞**，前端 toast 卡死。
- 一次会话的归档状态在前端**不可见**：用户无法在侧栏分辨哪些会话已归档、哪些有新内容尚未归档、哪些归档失败。
- 工作流变化场景（compaction / session_end）由 worker 进程在后台自动归档，**前端看不到**。

---

## 2. 设计方案

### 2.1 后端：202 + 后台任务 + 每用户 SSE

把 archive 端点改成**立即返回 202**，把 LLM 摘要放进 `asyncio.create_task` 在后台跑，结果通过一个**进程内的每用户 pub/sub 通道**经 SSE 推回前端：

```
HTTP POST /sessions/{id}/archive
   │
   ├── 同步段：校验 session、ownership、加载 context.jsonl
   ├── asyncio.create_task(_run_archive_in_background(...))
   └── 返回 202 { session_id, status: "queued" }

后台任务（_run_archive_in_background）
   ├── _summarize_via_llm(history)   ← 5–30 s
   ├── append_summary(recent.jsonl, summary)
   └── _BUS.publish(owner_id, archive.completed | archive.failed)

GET /api/memory/events  (SSE)
   ├── _BUS.subscribe(owner_id) → asyncio.Queue
   ├── 循环 await queue.get()，data: <json>\n\n
   └── 每 15 s 发 ": ping" 心跳
```

### 2.2 前端：5 态状态点 + 菜单门禁

每条会话侧栏行显示一个 6 px 的圆点，5 种状态：

| 状态 | 颜色 | 含义 |
|---|---|---|
| gray | `bg-muted-foreground/40` | 从未归档 |
| **blue, pulsing** | `bg-sky-500 animate-pulse` | 归档进行中（已发出 POST 或收到 202，未收到 SSE 终态事件） |
| green | `bg-emerald-500` | 已归档，且归档后无新对话 |
| yellow | `bg-amber-500` | 已归档，但之后会话又有新活动（`session.lastUpdated > summary.created_at + EPSILON`） |
| red | `bg-red-500` | 上次归档失败（下次成功时清除） |

`EPSILON = 2s`，吸收 `context.jsonl` mtime 与摘要 `created_at` 之间的写入时序漂移。

**菜单门禁**：当点是 blue 或 green 时，"Record memory" 菜单项置灰；点击弹 `<AlertDialog>` 提示原因（避免无效重复归档）。

### 2.3 自动归档（compaction / session_end）的可见性

`recent.jsonl` 同时被三个触发器追加（`SessionSummary.trigger`）：

| trigger | 写入进程 | SSE 实时推送 | 典型颜色 |
|---|---|---|---|
| `manual` | gateway | ✅ 经 `MemoryEventBus` | blue → green |
| `compaction` | worker | ❌ 跨进程 | yellow（压缩后会话仍在继续） |
| `session_end` | worker | ❌ 跨进程 | green（无新一轮） |

worker 与 gateway 是不同进程，**worker 写入的事件无法直接进入 gateway 的内存总线**。两个补偿机制让自动归档在 ≤60 s 内被前端感知：

- 60 s `setInterval` 刷新 `useRecentSummaries`
- `document.visibilitychange` 监听，标签页重新可见时立即刷新

这是有意做成轮询而不是跨进程发布订阅的折中（见"5.4 跨进程推送"）。

---

## 3. 技术路线的选择

### 3.1 推送通道：SSE vs WebSocket vs 轮询

| 方案 | 选用 | 原因 |
|---|---|---|
| **SSE** | ✅ | 单向、纯 HTTP、浏览器自动重连、配 `: ping` 心跳穿透代理；够用 |
| WebSocket | ❌ | 双向能力此处用不到；需要再造一层握手/心跳 |
| 轮询 | ❌ | 5–30 s 等待时频繁打 LLM 状态接口浪费；交互体验差 |

注意：`recent.jsonl` 的 `60 s 轮询`是另一回事——刷新的是已写入文件的摘要列表本身，不是用来等 LLM 完成的。

### 3.2 SSE 鉴权：`?token=` 查询参数兜底

浏览器 `EventSource` API **不能带自定义 header**（无法发 `Authorization: Bearer ...`）。三选一：

| 方案 | 选用 | 原因 |
|---|---|---|
| **`withCredentials: true` + cookie + `?token=` 兜底** | ✅ | 复用 `kimi_session` cookie；Bearer 客户端走查询串 |
| 反向代理改写 cookie | ❌ | 引入运维耦合 |
| 预签短期 token URL | ❌ | 多一次 round-trip，复杂度不值 |

实现镜像 `sessions.py:1156` 的 WebSocket 鉴权：在 `web/user_auth.py` 加 `get_current_user_sse` / `require_current_user_sse`，在普通 cookie / Bearer 检查失败时回落读取 `request.query_params.get("token")`。

### 3.3 进程内 pub/sub：原生 `asyncio.Queue` vs 第三方

```python
class MemoryEventBus:
    _subs: dict[str, list[asyncio.Queue]]   # owner_id → 多 tab 的多个队列
    def subscribe(owner_id) -> Queue: ...
    def unsubscribe(owner_id, q): ...
    def publish(owner_id, event): ...        # 扇出到该用户的所有队列
```

- **多 tab**：同一用户多个标签页各自 subscribe 一个队列，`publish` 扇出。
- **背压**：每队列 `maxsize=64`，满了直接丢最老的（fire-and-forget）。
- **不持久化**：服务器重启时进行中的事件会丢，由前端 90 s 安全超时兜底。

未引入 Redis / arq / asyncpg LISTEN 等：本仓库当前是单进程 gateway 部署形态，过度设计。

### 3.4 "禁用但可点击"的菜单项

shadcn 菜单原生 `disabled` 会**吞掉点击**，但我们要在用户点击时弹对话框解释为什么不能记忆。模式：

```tsx
<button
  aria-disabled={blocked}
  className={blocked ? "cursor-not-allowed opacity-60" : ""}
  onClick={blocked ? () => setRecordMemoryNotice({...}) : actuallyRecord}
>
  Record memory
</button>
```

不用原生 `disabled`，改用 `aria-disabled` + 自定义样式，键盘 Enter/Space 仍可触发（无障碍正确）。

### 3.5 存储格式：JSONL（沿用既有约定）

`recent.jsonl` / `persistent.jsonl` 都是 JSONL：单行一条记录，append 友好，pydantic `model_dump_json()` / `model_validate_json()` 直读直写，损坏行可跳过。本次未改动这一层。

---

## 4. 实现中遇到的坑与解决

### 4.1 SSE 的 EventSource 闭包陷阱

**问题**：`useMemoryEvents(onEvent)` 第一次写法直接用 `onEvent`，浏览器自动重连后回调指向旧闭包。

**解决**：用 `useRef` 存最新 handler，`useEffect` 只在挂载时建一次连接：

```ts
const handlerRef = useRef(onEvent);
handlerRef.current = onEvent;
useEffect(() => {
  const es = new EventSource(url, { withCredentials: true });
  es.onmessage = (ev) => handlerRef.current(JSON.parse(ev.data));
  return () => es.close();
}, []);   // 注意空依赖
```

### 4.2 跨进程归档不可见

**问题**：worker 写 `recent.jsonl` 后，gateway 进程的 `MemoryEventBus` 完全不知情，前端永远是 gray。

**解决**：60 s `setInterval` + `visibilitychange` 双触发刷新 `useRecentSummaries`。这是当前阶段的折中（见 5.4）。

### 4.3 卡住的 in-flight 永远不退

**问题**：服务器在归档中崩溃 / 网络断开，blue 状态点会永远 pulsing。

**解决**：`archiveStartedAtRef` 记录每个 session 的开始时间，每 15 s 扫一次，超过 90 s 仍在 in-flight 的强制退出并标 red（"Timed out waiting for memory recording to complete"）。

### 4.4 SSE 在反向代理后被缓冲

**问题**：nginx 等代理默认会缓冲响应，前端要好几分钟才看到 `data:` 行。

**解决**：响应头双管齐下：

```python
StreamingResponse(
    gen(),
    media_type="text/event-stream",
    headers={"Cache-Control": "no-cache, no-transform",
             "X-Accel-Buffering": "no"},
)
```

并在循环里每 15 s `yield ": ping\n\n"`，既保活又防代理 idle 关闭。

### 4.5 `make build-web` 的产物路径

**问题**：本地模式（`scripts/start.sh --mode=local`）服务的是 `src/kimi_cli/web/static/`，**不是 `web/dist/`**。改完前端只跑 `vite build`，刷新页面看到的还是旧版。

**解决**：必须执行 `cd kimi-cli && make build-web`，该命令在 vite build 之后会把 `web/dist/` 同步到 `src/kimi_cli/web/static/`（构建末尾的 `Synced web UI to ...` 即此步）。

### 4.6 同步阶段的错误必须仍然立即返回

**问题**：把整个 archive 端点扔进 `create_task` 后，不存在的 session_id、非本人会话等问题变成"先返回 202，再后台抛异常"，用户体验混乱。

**解决**：把请求拆成两段：

1. **同步段**：`session` 校验、`_check_session_owner`、`_load_context_messages`，4xx 直接返回。
2. **异步段**：只有 LLM 摘要 + 写文件 + 发布事件这部分进 `create_task`。

后台段用 try/except 兜底，任何异常都转成 `archive.failed` 事件，绝不让 task 抛未捕获异常。

---

## 5. 后续待优化

### 5.1 跨进程事件总线

当前 worker 写的归档要 ≤60 s 才被前端感知。可选升级路径：

- **文件 watcher**：gateway 监听 `recent.jsonl` 的 inotify/FSEvents，写入即转 `MemoryEventBus.publish`。零依赖、单机最简单。
- **Unix domain socket / 命名管道**：worker 写完发一行 owner_id+session_id，gateway 侧守护协程读取并扇出。
- **Redis pub/sub**：多机部署时再考虑。

### 5.2 SSE 服务端持久化

服务器重启 / 用户当前没开 tab 时，`archive.failed` 事件会**永久丢失**（recent.jsonl 不记录失败）。可加一个 `archive_errors` 文件（用户级、可截断），SSE 连接建立时先回放最近 N 条未读失败事件。

### 5.3 取消进行中的归档

当前没有 cancel 通道。可加 `DELETE /sessions/{id}/archive` 配合 `asyncio.Task.cancel()`，前端在 in-flight 状态点上提供"取消"项。

### 5.4 心跳间隔自适应

固定 15 s ping。在闲置 / 高峰可改自适应：用户活跃时拉长（节流），网络抖动时缩短（更快发现断连）。

### 5.5 状态点配置化

5 态颜色目前硬编码在 `sessions.tsx`。后续若主题切换 / 多用户偏好（比如色盲友好配色），抽到 `ARCHIVE_DOT_THEME` 配置。

### 5.6 自动归档触发条件优化

`compaction` 被触发的条件是 `loop_control.compaction_trigger_ratio`，目前是简单的 token 占比阈值。可以进一步：根据上一次 manual archive 与当前 turn 数差值动态决定是否自动归档，避免频繁产生重复语义的 yellow → green 翻转。

### 5.7 失败原因的细分展示

红点 tooltip 现在直接显示原始错误字符串。可加分类：模型不可用 / 上下文为空 / 写文件失败 / 超时，配合更友好的中文提示和 retry 按钮。

### 5.8 跨工作目录的记忆注入过滤

**现状**：`cross_session_memory.py` 把当前用户的 `recent.jsonl` 全量注入新会话，不区分 `work_dir`。本地 CLI（如 `/Users/jie/.openkimo`）和容器（`/app`）共享一份用户级 `recent.jsonl`，于是容器会话的 system prompt 里会出现"我们之前在 /Users/jie/.openkimo 项目里讨论过…"这类与当下 work_dir 无关的提示。

**可选改造**：

- 在 `read_recent_summaries()` 之后按 `s.work_dir == soul.runtime.work_dir`（或宽松匹配 basename）过滤，只注入同目录的摘要。
- 或者保留全量但让 `_render()` 在每条摘要前加 `(work_dir: ...)` 前缀，让 LLM 自己判断相关性。
- 进一步：在 web UI 的 Memory 面板按 work_dir 分组展示，让用户能直观看到本机 / 容器 / 不同项目的记忆。

**为什么不立刻做**：当前还没影响功能（载入不会失败），只是相关性问题；先收集一些实际容器使用场景下的体感再决定过滤策略。

---

## 6. 关键文件索引

| 文件 | 作用 |
|---|---|
| `kimi-cli/src/kimi_cli/web/api/memory.py` | `MemoryEventBus`、`_run_archive_in_background`、`POST /archive` (202)、`GET /events` SSE |
| `kimi-cli/src/kimi_cli/web/user_auth.py` | `get_current_user_sse` / `require_current_user_sse`（`?token=` 兜底） |
| `kimi-cli/src/kimi_cli/memory/recent.py` | `SessionSummary` schema、`append_summary` 文件锁与 trim |
| `kimi-cli/web/src/hooks/useMemory.ts` | `archiveSessionMemory` (Promise<ArchiveAccepted>)、`useMemoryEvents` |
| `kimi-cli/web/src/App.tsx` | in-flight set、errors map、90 s 安全超时、`deriveArchiveState` |
| `kimi-cli/web/src/features/sessions/sessions.tsx` | `MemoryStatusDot`、菜单门禁、`<AlertDialog>` 拦截 |

---

## 7. 验证清单

1. `cd kimi-cli && make build-web`
2. `scripts/start.sh --mode=local --port=5495`
3. DevTools → Network → EventStream 检查 `/api/memory/events`，看到 `: ping`。
4. 点 "Record memory"：blue 脉冲 → ≤30 s → green，toast "Memory saved"。
5. 再发新消息：green → yellow。
6. 多 tab 同账户：A 触发，B 也应 blue → green。
7. 服务端 kill -9 后保持 in-flight：≤90 s 自动转 red。
8. 在 green 上点菜单："Record memory" 灰显，点击弹 "Memory is already up to date…"。
9. 触发 worker 的 compaction：≤60 s 内（或切焦点）自动出现 yellow/green。
