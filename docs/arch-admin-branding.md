# 技术架构设计：管理后台品牌定制功能

| 字段     | 值                                 |
| -------- | ---------------------------------- |
| 文档版本 | 1.0                               |
| 日期     | 2026-04-26                        |
| 状态     | Draft                             |
| 关联 PRD | `docs/prd-admin-branding-customization.md` |

---

## 一、概述

本文档描述"管理后台品牌/主题定制"功能的详细技术架构，涵盖数据库 Schema、后端 API、前端组件及其交互流程。设计遵循现有代码库的模式和约定，最大限度减少对已有架构的侵入。

---

## 二、数据库 Schema

### 2.1 表设计

在现有 `users.db`（SQLite）中新增 `branding` 表，采用 **Key-Value 单表** 结构，与 PRD 中的数据库设计保持一致：

```sql
CREATE TABLE IF NOT EXISTS branding (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
```

每个品牌配置项对应一行记录：

| key          | value 格式                                           | 说明              |
| ------------ | ---------------------------------------------------- | ----------------- |
| `brand_name` | 纯文本，最多 30 字符                                 | 品牌名称          |
| `version`    | 纯文本，最多 20 字符                                 | 自定义版本号      |
| `page_title` | 纯文本，最多 60 字符                                 | 浏览器标签页标题  |
| `logo_url`   | URL 字符串                                           | Logo 点击跳转链接 |
| `logo`       | Data URL (`data:image/png;base64,...`)                | Logo 图片         |
| `favicon`    | Data URL (`data:image/png;base64,...`)                | Favicon 图片      |

### 2.2 迁移方案

在 `database.py` 的 `init_db()` 函数中追加 `CREATE TABLE IF NOT EXISTS` 语句，与现有 `users` 和 `user_sessions` 表的创建方式一致。无需独立的迁移脚本。

```python
# database.py — 新增常量
_CREATE_BRANDING_TABLE = """
CREATE TABLE IF NOT EXISTS branding (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""

# init_db() 中追加：
def init_db() -> None:
    with get_db() as conn:
        conn.execute(_CREATE_USERS_TABLE)
        conn.execute(_CREATE_USER_SESSIONS_TABLE)
        conn.execute(_CREATE_BRANDING_TABLE)       # <-- 新增
        conn.commit()
        # ... 现有默认 admin 创建逻辑不变
```

### 2.3 设计决策

- **为什么用 KV 表而不是单行多列表？** PRD 明确要求 KV 结构；KV 表在新增配置项时无需 ALTER TABLE，扩展性好。
- **为什么将图片存为 Data URL 而不是拆分 base64 + mime？** Data URL 是自描述格式，前端可直接用于 `<img src>`，减少后端拼装逻辑。后端校验时从 Data URL 中解析 MIME 和 base64 payload 即可。

---

## 三、后端 API 设计

### 3.1 文件结构

```
kimi-cli/src/kimi_cli/web/
  api/
    __init__.py          # 新增 branding_router 导出
    admin.py             # 不改动
    branding.py          # 新增：品牌 API 路由（公开 + 管理员）
  db/
    database.py          # 改动：init_db() 中新增 branding 表创建
    crud.py              # 改动：新增 branding CRUD 函数
```

### 3.2 Pydantic 模型

```python
# branding.py 中定义

from pydantic import BaseModel, field_validator
from typing import Optional
import re

# --- 合法的 Data URL MIME 类型 ---
_LOGO_MIME_PATTERN = re.compile(
    r"^data:image/(png|svg\+xml|jpeg);base64,[A-Za-z0-9+/\n]+=*$",
    re.DOTALL,
)
_FAVICON_MIME_PATTERN = re.compile(
    r"^data:image/(x-icon|png|svg\+xml);base64,[A-Za-z0-9+/\n]+=*$",
    re.DOTALL,
)

class BrandingResponse(BaseModel):
    """公开 API 和管理 API 通用的响应模型。"""
    brand_name: Optional[str] = None
    version: Optional[str] = None
    page_title: Optional[str] = None
    logo_url: Optional[str] = None
    logo: Optional[str] = None       # Data URL 或 None
    favicon: Optional[str] = None    # Data URL 或 None


class UpdateBrandingRequest(BaseModel):
    """PUT /api/admin/branding 的请求体。
    每个字段可选；传 null 表示清除该配置项。
    """
    brand_name: Optional[str] = None
    version: Optional[str] = None
    page_title: Optional[str] = None
    logo_url: Optional[str] = None
    logo: Optional[str] = None
    favicon: Optional[str] = None

    @field_validator("brand_name")
    @classmethod
    def validate_brand_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v) > 30:
            raise ValueError("brand_name must be <= 30 characters")
        return v

    @field_validator("version")
    @classmethod
    def validate_version(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v) > 20:
            raise ValueError("version must be <= 20 characters")
        return v

    @field_validator("page_title")
    @classmethod
    def validate_page_title(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v) > 60:
            raise ValueError("page_title must be <= 60 characters")
        return v

    @field_validator("logo_url")
    @classmethod
    def validate_logo_url(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.startswith(("http://", "https://")):
            raise ValueError("logo_url must start with http:// or https://")
        return v

    @field_validator("logo")
    @classmethod
    def validate_logo(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not _LOGO_MIME_PATTERN.match(v):
                raise ValueError("logo must be a valid Data URL (PNG/SVG/JPEG)")
            # 校验解码后大小 <= 512 KB
            _check_data_url_size(v, max_kb=512, field="logo")
        return v

    @field_validator("favicon")
    @classmethod
    def validate_favicon(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not _FAVICON_MIME_PATTERN.match(v):
                raise ValueError("favicon must be a valid Data URL (ICO/PNG/SVG)")
            _check_data_url_size(v, max_kb=256, field="favicon")
        return v


def _check_data_url_size(data_url: str, *, max_kb: int, field: str) -> None:
    """从 Data URL 中提取 base64 部分，解码后检查字节大小。"""
    import base64
    try:
        b64_part = data_url.split(",", 1)[1]
        raw = base64.b64decode(b64_part)
        if len(raw) > max_kb * 1024:
            raise ValueError(
                f"{field} decoded size exceeds {max_kb} KB"
            )
    except (IndexError, Exception) as e:
        if "exceeds" in str(e):
            raise
        raise ValueError(f"{field} contains invalid base64 data") from e
```

### 3.3 CRUD 函数

在 `crud.py` 中新增以下函数：

```python
# ---------------------------------------------------------------------------
# Branding CRUD
# ---------------------------------------------------------------------------

# 所有合法的 branding key
BRANDING_KEYS = {"brand_name", "version", "page_title", "logo_url", "logo", "favicon"}


def get_branding(db: sqlite3.Connection) -> dict[str, str | None]:
    """返回所有品牌配置，未设置的 key 对应值为 None。"""
    rows = db.execute("SELECT key, value FROM branding").fetchall()
    result: dict[str, str | None] = {k: None for k in BRANDING_KEYS}
    for row in rows:
        k = row["key"]
        if k in BRANDING_KEYS:
            result[k] = row["value"]
    return result


def upsert_branding(db: sqlite3.Connection, settings: dict[str, str | None]) -> None:
    """批量更新品牌配置。value 为 None 的 key 将被删除（恢复默认）。"""
    for key, value in settings.items():
        if key not in BRANDING_KEYS:
            continue
        if value is None or value == "":
            db.execute("DELETE FROM branding WHERE key = ?", (key,))
        else:
            db.execute(
                "INSERT INTO branding (key, value) VALUES (?, ?) "
                "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                (key, value),
            )
    db.commit()


def delete_all_branding(db: sqlite3.Connection) -> None:
    """清除所有品牌配置，恢复默认。"""
    db.execute("DELETE FROM branding")
    db.commit()
```

### 3.4 API 端点

新建文件 `api/branding.py`，包含两个 Router：一个公开、一个管理员专用。

```python
"""Branding API endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from kimi_cli.web.db.crud import (
    get_branding,
    upsert_branding,
    delete_all_branding,
)
from kimi_cli.web.db.database import get_db
from kimi_cli.web.user_auth import require_admin

# --- 公开路由（无需 admin 认证，但需基础认证/无认证取决于 AuthMiddleware） ---
public_router = APIRouter(prefix="/api/branding", tags=["branding"])

# --- 管理员路由 ---
admin_router = APIRouter(prefix="/api/admin/branding", tags=["admin-branding"])


@public_router.get("", summary="Get current branding settings")
async def get_public_branding() -> BrandingResponse:
    """返回当前生效的品牌配置。未设置的字段为 null。

    此端点不需要管理员权限，登录页等场景均可调用。
    """
    with get_db() as db:
        data = get_branding(db)
    return BrandingResponse(**data)


@admin_router.get("", summary="Get branding settings (admin)")
async def get_admin_branding(
    admin: dict[str, Any] = Depends(require_admin),
) -> BrandingResponse:
    """管理后台表单回显用。响应格式与公开接口一致。"""
    with get_db() as db:
        data = get_branding(db)
    return BrandingResponse(**data)


@admin_router.put("", summary="Update branding settings (admin)")
async def update_branding(
    body: UpdateBrandingRequest,
    admin: dict[str, Any] = Depends(require_admin),
) -> BrandingResponse:
    """更新品牌配置。仅包含需要更新的字段；传 null 表示清除。"""
    settings = body.model_dump()  # 包含所有字段，None 表示清除
    with get_db() as db:
        upsert_branding(db, settings)
        data = get_branding(db)
    return BrandingResponse(**data)


@admin_router.delete("", summary="Reset branding to defaults (admin)", status_code=204)
async def reset_branding(
    admin: dict[str, Any] = Depends(require_admin),
) -> None:
    """清除所有自定义品牌配置，恢复默认值。"""
    with get_db() as db:
        delete_all_branding(db)
```

### 3.5 路由注册

修改 `api/__init__.py`：

```python
# api/__init__.py 新增
from kimi_cli.web.api import branding as branding_module

branding_public_router = branding_module.public_router
branding_admin_router = branding_module.admin_router
```

修改 `app.py` 的 `create_app()`：

```python
from kimi_cli.web.api import (
    # ... 现有导入 ...
    branding_public_router,
    branding_admin_router,
)

# 在 application.include_router(admin_router) 后追加：
application.include_router(branding_public_router)
application.include_router(branding_admin_router)
```

### 3.6 公开端点的认证豁免

`GET /api/branding` 需要在登录页（未认证状态）也能访问。当前 `AuthMiddleware` 对 `/api/auth/` 路径有豁免逻辑，需要将 `/api/branding` 加入豁免白名单。具体做法：在 `AuthMiddleware` 的路径检查中新增：

```python
# auth.py 中的公开路径列表
PUBLIC_PATHS = ["/api/auth/", "/api/branding"]
```

仅 `GET /api/branding` 是公开的；`/api/admin/branding` 路径不在白名单中，走正常认证 + `require_admin` 保护。

---

## 四、前端架构

### 4.1 文件结构

```
kimi-cli/web/src/
  lib/api/apis/
    BrandingApi.ts           # 新增：品牌 API 客户端
  hooks/
    useBranding.ts           # 新增：品牌数据 React Hook + Context
  features/admin/
    admin-branding-panel.tsx  # 新增：管理后台 Branding 标签页
    admin-page.tsx            # 改动：新增 Branding tab
  components/
    kimi-cli-brand.tsx        # 改动：从 Context 读取品牌数据
  App.tsx                     # 改动：包裹 BrandingProvider
```

### 4.2 API 客户端 — `BrandingApi.ts`

遵循 `AdminApi.ts` 的手写模式（非代码生成），使用 `fetch` + `getAuthHeader` + `getApiBaseUrl`：

```typescript
// BrandingApi.ts

import { getAuthHeader } from "../../auth";
import { getApiBaseUrl } from "../../../hooks/utils";

export interface BrandingConfig {
  brand_name: string | null;
  version: string | null;
  page_title: string | null;
  logo_url: string | null;
  logo: string | null;      // Data URL
  favicon: string | null;   // Data URL
}

function apiUrl(path: string): string {
  return `${getApiBaseUrl()}${path}`;
}

async function handleResponse<T>(resp: Response): Promise<T> {
  if (!resp.ok) {
    let message = `Request failed (${resp.status})`;
    try {
      const data = await resp.json();
      if (typeof data.detail === "string") message = data.detail;
    } catch { /* ignore */ }
    throw new Error(message);
  }
  return resp.json() as Promise<T>;
}

/** 公开接口 — 获取当前品牌配置（无需 admin） */
export async function getBranding(): Promise<BrandingConfig> {
  const resp = await fetch(apiUrl("/api/branding"), {
    method: "GET",
    headers: { ...getAuthHeader() },
    credentials: "include",
  });
  return handleResponse<BrandingConfig>(resp);
}

/** 管理接口 — 获取品牌配置（admin only） */
export async function getAdminBranding(): Promise<BrandingConfig> {
  const resp = await fetch(apiUrl("/api/admin/branding"), {
    method: "GET",
    headers: { ...getAuthHeader() },
    credentials: "include",
  });
  return handleResponse<BrandingConfig>(resp);
}

/** 管理接口 — 更新品牌配置 */
export async function updateBranding(
  data: Partial<BrandingConfig>,
): Promise<BrandingConfig> {
  const resp = await fetch(apiUrl("/api/admin/branding"), {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      ...getAuthHeader(),
    },
    credentials: "include",
    body: JSON.stringify(data),
  });
  return handleResponse<BrandingConfig>(resp);
}

/** 管理接口 — 重置品牌配置 */
export async function resetBranding(): Promise<void> {
  const resp = await fetch(apiUrl("/api/admin/branding"), {
    method: "DELETE",
    headers: { ...getAuthHeader() },
    credentials: "include",
  });
  if (!resp.ok) {
    let message = `Reset failed (${resp.status})`;
    try {
      const data = await resp.json();
      if (typeof data.detail === "string") message = data.detail;
    } catch { /* ignore */ }
    throw new Error(message);
  }
}
```

### 4.3 品牌状态 Hook — `useBranding.ts`

遵循 `useGlobalConfig.ts` 的模式，额外提供 React Context 以便任意子组件消费：

```typescript
// useBranding.ts

import {
  createContext,
  useContext,
  useCallback,
  useEffect,
  useRef,
  useState,
  type ReactNode,
} from "react";
import { getBranding, type BrandingConfig } from "@/lib/api/apis/BrandingApi";

// --- 默认值常量 ---
export const BRANDING_DEFAULTS = {
  brand_name: "Kimi Code",
  version: null,               // 回退到 kimiCliVersion
  page_title: "Kimi Code Web UI",
  logo_url: "https://www.kimi.com/code",
  logo: "/logo.png",           // 默认静态文件
  favicon: "/logo.png",
} as const;

// --- Context ---
export type BrandingState = {
  config: BrandingConfig | null;
  isLoading: boolean;
  refresh: () => Promise<void>;
};

const BrandingContext = createContext<BrandingState>({
  config: null,
  isLoading: true,
  refresh: async () => {},
});

export function useBranding(): BrandingState {
  return useContext(BrandingContext);
}

// --- Provider ---
export function BrandingProvider({ children }: { children: ReactNode }) {
  const [config, setConfig] = useState<BrandingConfig | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const isInitializedRef = useRef(false);

  const refresh = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await getBranding();
      setConfig(data);
    } catch (err) {
      console.error("[useBranding] Failed to load branding:", err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // 初始加载
  useEffect(() => {
    if (isInitializedRef.current) return;
    isInitializedRef.current = true;
    refresh();
  }, [refresh]);

  // 监听自定义事件：管理员保存后广播刷新
  useEffect(() => {
    const handler = () => { refresh(); };
    window.addEventListener("kimi:branding-update", handler);
    return () => window.removeEventListener("kimi:branding-update", handler);
  }, [refresh]);

  // 动态更新 document.title
  useEffect(() => {
    if (!config) return;
    document.title = config.page_title ?? BRANDING_DEFAULTS.page_title;
  }, [config]);

  // 动态更新 favicon
  useEffect(() => {
    if (!config) return;
    const faviconUrl = config.favicon ?? BRANDING_DEFAULTS.favicon;
    let link = document.querySelector(
      'link[rel="icon"]',
    ) as HTMLLinkElement | null;
    if (!link) {
      link = document.createElement("link");
      link.rel = "icon";
      document.head.appendChild(link);
    }
    link.href = faviconUrl;
  }, [config]);

  return (
    <BrandingContext.Provider value={{ config, isLoading, refresh }}>
      {children}
    </BrandingContext.Provider>
  );
}
```

### 4.4 KimiCliBrand 组件改造

将硬编码值替换为从 `BrandingContext` 读取，保持向下兼容：

```typescript
// kimi-cli-brand.tsx — 改造后

import { kimiCliVersion } from "@/lib/version";
import { cn } from "@/lib/utils";
import { useBranding, BRANDING_DEFAULTS } from "@/hooks/useBranding";

type KimiCliBrandProps = {
  className?: string;
  size?: "sm" | "md";
  showVersion?: boolean;
};

export function KimiCliBrand({
  className,
  size = "md",
  showVersion = true,
}: KimiCliBrandProps) {
  const { config } = useBranding();

  const brandName = config?.brand_name ?? BRANDING_DEFAULTS.brand_name;
  const logoSrc = config?.logo ?? BRANDING_DEFAULTS.logo;
  const logoUrl = config?.logo_url ?? BRANDING_DEFAULTS.logo_url;
  const versionText = config?.version || kimiCliVersion; // 空字符串也回退

  const textSizeClass = size === "sm" ? "text-base" : "text-lg";
  const versionPadding = size === "sm" ? "text-xs" : "text-sm";
  const logoSize = size === "sm" ? "size-6" : "size-7";
  const logoPx = size === "sm" ? 24 : 28;

  return (
    <div className={cn("flex items-center gap-2", className)}>
      <a
        href={logoUrl}
        target="_blank"
        rel="noopener noreferrer"
        className="flex items-center gap-2 hover:opacity-80 transition-opacity"
      >
        <img
          src={logoSrc}
          alt={brandName}
          width={logoPx}
          height={logoPx}
          className={logoSize}
        />
        <span className={cn(textSizeClass, "font-semibold text-foreground")}>
          {brandName}
        </span>
      </a>
      {showVersion && (
        <span className={cn("text-muted-foreground font-medium", versionPadding)}>
          v{versionText}
        </span>
      )}
    </div>
  );
}
```

### 4.5 App.tsx 改造

在应用根部包裹 `BrandingProvider`：

```typescript
// App.tsx — 关键改动

import { BrandingProvider } from "./hooks/useBranding";

// 在 return 最外层包裹：
// 登录页场景（未认证）也需要品牌信息，因此 Provider 放在认证判断之前
function App() {
  // ... 现有逻辑 ...

  return (
    <BrandingProvider>
      {/* 现有全部 JSX 不变 */}
    </BrandingProvider>
  );
}
```

同时，`App.tsx` 中侧栏收起状态下的 Logo 硬编码（`<img src="/logo.png">`）也需改为从 Context 读取：

```typescript
// App.tsx 侧栏收起状态的 Logo
const { config } = useBranding();
const collapsedLogoSrc = config?.logo ?? "/logo.png";
const collapsedLogoUrl = config?.logo_url ?? "https://www.kimi.com/code";

// JSX 中：
<a href={collapsedLogoUrl} target="_blank" rel="noopener noreferrer" ...>
  <img src={collapsedLogoSrc} alt="Logo" width={24} height={24} className="size-6" />
</a>
```

### 4.6 Admin Page 改造 — 新增 Branding Tab

在 `admin-page.tsx` 中：

```typescript
// admin-page.tsx 关键改动

import { Palette } from "lucide-react";
import { AdminBrandingPanel } from "./admin-branding-panel";

type AdminTab = "users" | "plugins" | "branding";  // 新增 "branding"

// Tab 导航区域新增按钮：
<button
  type="button"
  onClick={() => setActiveTab("branding")}
  className={[
    "inline-flex items-center gap-2 rounded-md px-3 py-1.5 text-sm font-medium transition-colors",
    activeTab === "branding"
      ? "bg-background text-foreground shadow-sm"
      : "text-muted-foreground hover:text-foreground",
  ].join(" ")}
>
  <Palette className="size-3.5" />
  Branding
</button>

// Tab 内容区域新增：
{activeTab === "branding" && <AdminBrandingPanel />}
```

### 4.7 AdminBrandingPanel 组件

`admin-branding-panel.tsx` 是 Branding 标签页的核心 UI，包含：

- **实时预览卡片**：模拟侧栏品牌区域，随表单输入实时更新
- **Logo / Favicon 上传区域**：文件选择 -> FileReader 转 Data URL -> 预览
- **文本输入区域**：brand_name、version、page_title、logo_url
- **操作栏**：Save Changes / Reset to Defaults

组件内部状态管理：

```typescript
// admin-branding-panel.tsx — 核心状态结构

type FormState = {
  brand_name: string;
  version: string;
  page_title: string;
  logo_url: string;
  logo: string | null;       // Data URL 或 null
  favicon: string | null;    // Data URL 或 null
};

// 加载流程：
// 1. mount -> getAdminBranding() -> 填充表单
// 2. 编辑 -> 本地 FormState 更新 + 实时预览
// 3. Save -> updateBranding(formState) -> toast.success
//         -> window.dispatchEvent(new Event("kimi:branding-update"))
// 4. Reset -> 二次确认 -> resetBranding() -> 清空表单 -> 广播事件
```

Logo/Favicon 上传处理逻辑：

```typescript
function handleFileUpload(
  file: File,
  options: { maxSizeKB: number; accept: string[] },
  onResult: (dataUrl: string) => void,
) {
  // 1. 校验 MIME 类型
  if (!options.accept.includes(file.type)) {
    toast.error(`Unsupported format: ${file.type}`);
    return;
  }
  // 2. 校验文件大小
  if (file.size > options.maxSizeKB * 1024) {
    toast.error(`File too large (max ${options.maxSizeKB} KB)`);
    return;
  }
  // 3. FileReader 转 Data URL
  const reader = new FileReader();
  reader.onload = () => {
    onResult(reader.result as string);
  };
  reader.readAsDataURL(file);
}
```

---

## 五、组件交互图

### 5.1 应用启动时的品牌数据加载

```
+------------------+     GET /api/branding      +------------------+
|                  | --------------------------> |                  |
|   BrandingProvider|                            |   FastAPI        |
|   (React Context) | <------------------------ |   branding.py    |
|                  |     { brand_name, ... }     |                  |
+--------+---------+                            +--------+---------+
         |                                               |
         |  BrandingContext                               |  SELECT * FROM branding
         v                                               v
+------------------+                            +------------------+
| KimiCliBrand     |                            |  SQLite          |
| App.tsx (title)  |                            |  users.db        |
| App.tsx (favicon)|                            |  branding table  |
| LoginPage        |                            +------------------+
+------------------+
```

### 5.2 管理员保存品牌配置的数据流

```
+---------------------+   PUT /api/admin/branding   +------------------+
| AdminBrandingPanel  | --------------------------> | FastAPI          |
| (Admin Tab)         |   { brand_name, logo, ... } | branding.py      |
|                     | <-------------------------- | (require_admin)  |
|                     |   200 { updated config }     |                  |
+----------+----------+                             +--------+---------+
           |                                                 |
           | 1. toast.success()                              | UPSERT branding
           | 2. dispatch("kimi:branding-update")             v
           |                                        +------------------+
           v                                        | SQLite           |
+---------------------+                            | users.db         |
| BrandingProvider    |                            +------------------+
| (listens to event)  |
| -> refetch GET      |
| -> update Context   |
+----------+----------+
           |
           | Context 更新
           v
+---------------------+
| KimiCliBrand        |  <- 立即显示新 Logo/名称
| document.title      |  <- 立即更新标题
| <link rel="icon">   |  <- 立即更新 Favicon
+---------------------+
```

### 5.3 跨标签页同步

```
  Tab A (Admin)                    Tab B (User)
  +----------------+               +----------------+
  | Save branding  |               |                |
  |    |           |               |                |
  |    v           |               |                |
  | dispatch event |               |                |
  | "kimi:branding |               |                |
  |  -update"      |               |                |
  +-------+--------+               +--------+-------+
          |                                 |
          |  (同一窗口内的事件)               |
          |  如需跨标签页同步，可用           |
          |  BroadcastChannel API:           |
          |                                 |
          +---- BroadcastChannel ---------->+
                "kimi:branding-update"      |
                                            v
                                   BrandingProvider
                                   -> refetch -> 更新 UI
```

**注意：** `window.dispatchEvent` 仅在同一浏览器标签页内有效。若需跨标签页即时同步，`BrandingProvider` 中应额外使用 `BroadcastChannel` API：

```typescript
// useBranding.ts — 跨标签页同步
useEffect(() => {
  const channel = new BroadcastChannel("kimi:branding");
  channel.onmessage = () => { refresh(); };
  return () => channel.close();
}, [refresh]);

// 管理员保存后广播：
const channel = new BroadcastChannel("kimi:branding");
channel.postMessage("updated");
channel.close();
```

---

## 六、Logo 上传完整流程

```
  管理员操作                     前端处理                      后端处理
  ──────────                    ─────────                     ─────────
  1. 点击 Upload            ->  <input type="file"
     或拖拽文件                   accept="image/png,
                                 image/svg+xml,image/jpeg">

  2. 选择文件               ->  FileReader.readAsDataURL()
                                -> 校验 MIME + 大小 (<= 512KB)
                                -> 更新 formState.logo
                                -> 预览区立即显示

  3. 点击 Save Changes      ->  PUT /api/admin/branding
                                body: { logo: "data:image/png;
                                base64,iVBOR...", ... }
                                                              -> Pydantic 校验
                                                                 MIME + base64 + 大小
                                                              -> UPSERT INTO branding
                                                              -> 返回 200 + 完整配置

  4. 保存成功               ->  dispatch("kimi:branding-update")
                                + BroadcastChannel

  5. BrandingProvider       ->  GET /api/branding
     收到事件并 refetch         -> Context 更新

  6. KimiCliBrand           ->  <img src={config.logo}> 更新
     读取新 Context              （Data URL 直接渲染，无需额外请求）
```

**关于 Logo 的 src 策略：**

- 当自定义 Logo 存在时，`<img src>` 直接使用 Data URL（`data:image/png;base64,...`），无需额外的二进制端点。
- 当未设置自定义 Logo 时，回退到 `/logo.png` 静态文件。
- 这种方式避免了额外的二进制图片端点，简化了实现。Data URL 在 512KB 限制下对页面加载影响可忽略。

---

## 七、安全考量

| 项目               | 措施                                                                 |
| ------------------ | -------------------------------------------------------------------- |
| 写入权限           | `PUT` / `DELETE` 端点使用 `Depends(require_admin)` 保护              |
| 图片注入           | 后端 Pydantic 校验强制 MIME 类型白名单 + base64 合法性检查           |
| XSS — logo_url     | 校验必须以 `http://` 或 `https://` 开头，前端 `<a>` 使用 `rel="noopener noreferrer"` |
| 大小限制           | Logo <= 512KB, Favicon <= 256KB（base64 解码后字节数）               |
| 公开端点安全       | `GET /api/branding` 仅返回只读配置数据，不含敏感信息                 |

---

## 八、影响范围与兼容性

### 8.1 改动文件清单

| 文件                                      | 改动类型 | 说明                                |
| ----------------------------------------- | -------- | ----------------------------------- |
| `web/db/database.py`                      | 修改     | `init_db()` 新增 branding 表创建    |
| `web/db/crud.py`                          | 修改     | 新增 3 个 branding CRUD 函数        |
| `web/api/branding.py`                     | **新增** | 公开 + 管理员 API 端点              |
| `web/api/__init__.py`                     | 修改     | 导出新路由                          |
| `web/app.py`                              | 修改     | 注册新路由                          |
| `web/auth.py`                             | 修改     | 公开路径白名单新增 `/api/branding`  |
| `web/src/lib/api/apis/BrandingApi.ts`     | **新增** | 前端 API 客户端                     |
| `web/src/hooks/useBranding.ts`            | **新增** | React Hook + Context + Provider     |
| `web/src/features/admin/admin-branding-panel.tsx` | **新增** | 管理后台 Branding 表单 UI    |
| `web/src/features/admin/admin-page.tsx`   | 修改     | 新增 Branding tab                   |
| `web/src/components/kimi-cli-brand.tsx`   | 修改     | 从 Context 读取品牌数据             |
| `web/src/App.tsx`                         | 修改     | 包裹 BrandingProvider + 侧栏 Logo   |

### 8.2 向后兼容

- **数据库**：`CREATE TABLE IF NOT EXISTS`，不影响已有表。branding 表为空时，所有 API 返回 `null`，前端使用硬编码默认值，行为与改造前完全一致。
- **API**：新增端点，不修改已有端点的签名或行为。
- **前端**：`KimiCliBrand` 在 `BrandingContext` 值为 `null` 时回退到原有硬编码值，不影响无 Provider 的测试场景。
- **容器镜像**：无需额外依赖或构建步骤。

---

## 九、测试策略

| 层级     | 测试内容                                                                            |
| -------- | ----------------------------------------------------------------------------------- |
| 单元测试 | Pydantic 模型校验：非法 MIME、超长字段、超大 base64、非法 URL                       |
| 单元测试 | CRUD 函数：upsert 幂等性、delete_all 清空、get_branding 空表返回全 None              |
| API 测试 | `GET /api/branding` 无认证可访问；`PUT /api/admin/branding` 非 admin 返回 403       |
| API 测试 | `PUT` 校验失败返回 400 + 具体字段错误信息                                           |
| API 测试 | `DELETE /api/admin/branding` 后 `GET` 返回全 null                                   |
| E2E 测试 | 管理员上传 Logo -> 保存 -> 普通用户侧栏看到新 Logo                                  |
| E2E 测试 | 重置到默认 -> 所有品牌元素恢复                                                       |
| E2E 测试 | 容器重启后品牌配置仍然保留                                                           |
