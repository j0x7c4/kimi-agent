# 前端 UI 插件系统实现记录

## 概述

为 kimi-cli Web 端实现了一套前端插件系统，支持在 Agent thinking、Subagent 启动、Agent 集群创建等关键时机注入自定义 UI（overlay 动画）。设计目标：轻量、即插即拔、对现有代码最小改动。

## 架构

```
bootstrap.tsx
  └── <PluginSystemProvider>          ← 插件总线 + Portal 宿主
        └── <App>
              └── <ChatWorkspaceContainer>
                    ├── useSessionStream
                    │     └── processEvent → pluginBridgeRef.current(wireEvent)
                    └── usePluginEventEmitter → translateWireEvent
                          └── bus.emit(PluginEvent)

document.body
  └── Portal: PluginPortalHost        ← 独立于 React 树
        ├── ThinkingAnimationOverlay
        ├── SubagentAnimationOverlay
        └── SubagentClusterOverlay
```

### 核心组件

| 文件 | 职责 |
|------|------|
| `plugins/types.ts` | `UIPlugin`、`PluginEvent`、`PluginRegistry` 接口定义 |
| `plugins/PluginSystemProvider.tsx` | `PluginEventBus` 发布订阅 + React Context + Portal overlay 宿主 |
| `plugins/usePluginEventEmitter.ts` | Wire event → 语义 PluginEvent 翻译层 |
| `plugins/registry-store.ts` | localStorage 持久化插件元数据 |
| `plugins/builtins/*.tsx` | 三个内置插件实现 |

### Overlay 模型

- 每个插件 ID 只占一个 slot，新事件原地更新而非堆叠
- 插件 render 返回 `null` 时自动 dismiss
- 支持 `autoDismissMs` 插件级定时消失
- 系统硬上限 10 秒，防止插件泄漏

## 遇到的问题与解决方案

### 1. WebSocket 闭包链导致插件回调不触发

**现象**：`onWireEventForPlugin` 回调已正确传入 `useSessionStream`，但运行时从未被调用。浏览器 Console 无任何插件日志。

**根因**：WebSocket 的 `onmessage` handler 在 `connect()` 时被赋值，此后不再更新。调用链为：

```
connect() 捕获 handleMessage →
  handleMessage 捕获 processEvent →
    processEvent 捕获 onWireEventForPlugin
```

当 `onWireEventForPlugin`（来自 `usePluginEventEmitter` 的 `translateWireEvent`）引用发生变化时，`processEvent` 作为 `useCallback` 会重建，但 WebSocket 的 `onmessage` 仍持有旧的 `handleMessage` 闭包，形成 **stale closure**。

**解决**：使用 `useRef` 桥接，将 `onWireEventForPlugin` 存入 ref，`processEvent` 内部通过 `pluginBridgeRef.current?.()` 调用，绕过闭包链。同时从 `processEvent` 的 deps 数组中移除该回调，避免不必要的重建。

```typescript
// useSessionStream.ts
const pluginBridgeRef = useRef(onWireEventForPlugin);
pluginBridgeRef.current = onWireEventForPlugin;

// processEvent useCallback 内部
pluginBridgeRef.current?.(event, { sessionId, isReplay });
```

### 2. Overlay 事件堆叠导致 UI 不可见

**现象**：thinking 动画从不出现，或出现后无法消失。

**根因**：初始设计中，bus 每收到一个事件就创建一个新的 overlay instance（新 ID）。`thinking:chunk` 每秒触发数十次，堆积了大量 overlay。`thinking:end` 只 dismiss 自己的那一个 overlay，其余全部残留。

**解决**：改为 **one slot per plugin** 模型——每个插件 ID 只维护一个 overlay slot，新事件更新 slot 的 `event` 字段而非创建新 slot。

```typescript
setSlots((prev) => {
  const existing = prev.find((s) => s.pluginId === plugin.id);
  if (existing) {
    return prev.map((s) =>
      s.pluginId === plugin.id ? { ...s, event } : s,
    );
  }
  return [...prev, { pluginId: plugin.id, plugin, event }];
});
```

### 3. Thinking 动画在工具调用阶段不消失

**现象**：Agent 从 thinking 进入工具调用后，thinking 动画仍然显示。

**根因**：`usePluginEventEmitter` 只在收到 **非 think 类型的 ContentPart** 时才发出 `thinking:end`。但 thinking 结束后下一个 wire event 是 `ToolCall`，不是 `ContentPart`，emitter 不识别。

**解决**：将 thinking 结束检测提到 switch 语句之前——任何非 think-ContentPart 的 wire event 到达时，如果有活跃的 thinking 状态，立即发出 `thinking:end`。

```typescript
const isThinkChunk =
  wireEvent.type === "ContentPart" &&
  (wireEvent as ContentPartEvent).payload.type === "think" &&
  !!(wireEvent as ContentPartEvent).payload.think;

if (!isThinkChunk && thinkingRef.current) {
  // emit thinking:end
}
```

### 4. render 阶段调用 setState 导致 React 警告

**现象**：插件 render 返回 `null` 时直接调用 `dismiss()`（内部是 `setSlots`），触发 React "Cannot update during render" 警告。

**解决**：`PluginOverlaySlot` 组件在 render 阶段只标记 `pendingDismissRef`，在后续的 `useEffect` 中执行实际的 dismiss。

### 5. Docker 构建后前端代码未更新

**现象**：`docker compose build && docker compose up -d` 后浏览器仍显示旧页面。

**根因**（之前的 commit 已修复）：`Dockerfile.gateway` 中 `COPY kimi-cli/src/` 在 `COPY --from=web-builder` 之后执行，kimi-cli 子模块中预构建的 `web/static/` 覆盖了刚刚构建的前端产物。

**解决**：调换 COPY 顺序——先复制源码，再用 web-builder 产物覆盖。

```dockerfile
COPY kimi-cli/src/ /app/src/
COPY --from=web-builder /build/dist /app/src/kimi_cli/web/static
```

## 内置插件

| 插件 | 触发事件 | 位置 | 效果 | 时长 |
|------|---------|------|------|------|
| Thinking Animation | `thinking:start/chunk/end` | 右上 | 脉冲胶囊 + 闪烁指示点 | 跟随 thinking 生命周期（上限 10s） |
| Subagent Animation | `subagent:start` | 右上 | 旋转环 + 扫光 + 进度条 + 滑出 | 3 秒 |
| Subagent Cluster | `subagent:cluster` | 右下 | 轨道绘入 + 节点弹入 + 脉冲发光 | 3 秒 |

## 集成改动清单

| 文件 | 改动 |
|------|------|
| `bootstrap.tsx` | 包裹 `<PluginSystemProvider>` |
| `useSessionStream.ts` | 新增 `onWireEventForPlugin` 选项 + `pluginBridgeRef` 旁路广播 |
| `chat-workspace-container.tsx` | 调用 `usePluginEventEmitter`，注册内置插件 |
| `plugins/` 目录（7 个新文件） | 完整插件运行时 |
