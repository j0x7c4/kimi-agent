# 容器化部署问题修复记录

本文档记录在将 kimi-cli 改造为服务器端 Agent 框架（容器化部署）过程中遇到的问题及修复方案。

## 2026-04-22

### 1. Docker CLI 架构映射错误（Gateway 镜像构建失败）

**问题**：在 ARM64 (Mac M系列) 上构建 Gateway 镜像时，下载 Docker 静态二进制文件报错 404。

**根因**：`dpkg --print-architecture` 返回 `arm64`，但 Docker 下载 URL 使用 `aarch64`。

**修复**：在 `Dockerfile.gateway` 中添加架构映射：

```dockerfile
&& DOCKER_ARCH=$(dpkg --print-architecture) \
&& if [ "$DOCKER_ARCH" = "arm64" ]; then DOCKER_ARCH="aarch64"; fi \
&& curl -fsSL "https://download.docker.com/linux/static/stable/${DOCKER_ARCH}/docker-27.3.1.tgz" \
```

---

### 2. Workspace 本地包未安装（`No module named 'kosong'`）

**问题**：容器启动后报错 `ModuleNotFoundError: No module named 'kosong'`。

**根因**：`pyproject.toml` 使用 uv workspace，但 `uv pip install -r pyproject.toml` 不会自动安装本地 workspace 包。

**修复**：在 Dockerfile 中显式安装 workspace 包：

```dockerfile
RUN uv pip install --system --no-deps \
    ./packages/kosong \
    ./packages/kaos
```

---

### 3. 包元数据缺失（`PackageNotFoundError: No package metadata for kimi-cli`）

**问题**：`importlib.metadata.version("kimi-cli")` 报错，因为源码直接复制到 site-packages 但没有 `.dist-info`。

**修复**：在 Dockerfile 中手动注册元数据：

```dockerfile
RUN mkdir -p /usr/local/lib/python3.12/site-packages/kimi_cli-1.37.0.dist-info \
    && printf 'Name: kimi-cli\nVersion: 1.37.0\n' > .../METADATA \
    && touch .../INSTALLER \
    && touch .../RECORD
```

---

### 4. Docker 卷名称不一致（Session 数据隔离）

**问题**：Gateway 容器和 Sandbox 容器使用不同的 Docker 卷，导致 session 数据不共享。

**根因**：`docker-compose` 默认创建 `<project>_session-data`，但 `container.py` 中使用的是 `session-data`。

**修复**：在 `docker-compose.yml` 中显式命名卷：

```yaml
volumes:
  session-data:
    driver: local
    name: session-data
```

---

### 5. 前端静态文件路径错误（`Not Found`）

**问题**：访问 `http://localhost:5494/` 返回 `{"detail":"Not Found"}`。

**根因**：`Dockerfile.gateway` 把前端构建产物放到 `/app/web/dist/`，但 `app.py` 中 `STATIC_DIR` 指向的是 `.../kimi_cli/web/static/`。

**修复**：修改 Dockerfile 中的 COPY 目标路径：

```dockerfile
COPY --from=web-builder /build/dist /app/src/kimi_cli/web/static
```

---

### 6. KIMI_WEB_SESSION_TOKEN 强制检查导致容器重启循环

**问题**：`.env` 中 token 被注释后，容器不断重启（CrashLoop）。

**根因**：`start-gateway.sh` 中 token 缺失时执行 `exit 1`。

**修复**：将强制退出改为 WARNING（适合本地开发）：

```bash
if [ -z "$KIMI_WEB_SESSION_TOKEN" ]; then
    echo "WARNING: KIMI_WEB_SESSION_TOKEN is not set."
    echo "         Running without authentication - suitable for local development only."
fi
```

---

### 7. FetchURL 频繁 404/403（Bot 检测）

**问题**：Agent 使用 FetchURL 抓取网页时频繁遇到 403 Forbidden 或 404 Not Found。

**根因**：
1. User-Agent 过时（Chrome 91）
2. 缺少现代浏览器请求头（`Accept`, `Sec-Fetch-*` 等）
3. 部分网站（Cloudflare 等）需要 JavaScript 渲染
4. 缺少 `brotli` 导致无法解码 `br` 编码的响应

**修复**：
1. **更新 User-Agent** 到 Chrome 120
2. **添加完整浏览器请求头**：`Accept`, `Accept-Language`, `Sec-Fetch-Dest/Mode/Site/User`, `DNT` 等
3. **Playwright 降级**：遇到 HTTP 403 时自动使用 Playwright + Chromium 无头浏览器抓取
4. **安装 brotli**：在 `Dockerfile.sandbox` 中添加 `brotli` pip 包

```python
_BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    # ... 其他 Sec-Fetch 头
}
```

---

## 架构变更摘要

### 新增文件
- `src/kimi_cli/web/runner/container.py` — ContainerRunner 实现
- `Dockerfile.gateway` — Gateway 容器镜像
- `Dockerfile.sandbox` — Sandbox 容器镜像
- `docker-compose.yml` — 编排配置
- `scripts/start-gateway.sh` — Gateway 启动脚本
- `scripts/start-sandbox.sh` — Sandbox 启动脚本

### 修改文件
- `src/kimi_cli/web/runner/__init__.py` — 导出 ContainerRunner
- `src/kimi_cli/web/app.py` — 集成容器模式
- `src/kimi_cli/tools/web/fetch.py` — 增强抓取能力
- `docker-compose.yml` — 显式卷命名
