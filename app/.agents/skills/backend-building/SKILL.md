---
name: backend-building
description: Backend building that grafts tRPC + Drizzle ORM + Hono onto an existing webapp-building frontend. Supports incremental features (db, auth). Use when the user needs a backend, API, database, server, authentication, or wants to add tRPC/Drizzle to their webapp-building project. Requires webapp-building first.
---

# Backend Building

**Stack**: tRPC + Drizzle ORM + Hono + MySQL + OAuth 2.0

A backend-only skill that grafts onto an existing `webapp-building` project. It adds `api/`, `contracts/` directories and optionally `db/` — but **never replaces or modifies** existing frontend files.

**Prerequisite**: An existing project created by `webapp-building`.

## Features

Features can be installed incrementally. Base infrastructure (Hono server, tRPC, contracts) is always installed automatically on first run.

| Feature | What it provides | Dependencies |
|---------|-----------------|--------------|
| `db` | Drizzle ORM + MySQL — adds `db/`, `api/queries/connection.ts`, `drizzle.config.ts` | — |
| `auth` | Kimi OAuth + user management — adds `api/kimi/`, Login page, useAuth, AuthLayout | requires `db` (auto-included) |

Default: `init.sh "App"` with no `--features` → defaults to `auth` (= db + auth), preserving backward compat.

## Workflows

**Frontend-first** (recommended when UI is already built):

1. `webapp-building` init → develop UI pages and components
2. `backend-building` graft (this skill) — auto-wires tRPC providers and routes
3. Verify with `npm run check`, then add tRPC routers, database tables, wire frontend to API

**Full-stack from scratch** (recommended when backend is needed immediately):

1. `webapp-building` init → immediately graft `backend-building`
2. Verify with `npm run check`
3. Develop frontend and backend together

**Incremental features** (add capabilities over time):

1. Start with `--features db` for database only
2. Later add auth: `init.sh "App" --features auth`

## Quick Start

### 1. Initialize Frontend First (webapp-building)

```bash
bash /app/.agents/skills/webapp-building/scripts/init-webapp.sh "My App"
cd /mnt/agents/output/app
```

### 2. Graft Backend

```bash
# Full stack with auth (default, same as before):
bash /app/.agents/skills/backend-building/scripts/init.sh "My App"

# Database only (no auth):
bash /app/.agents/skills/backend-building/scripts/init.sh "My App" --features db

# Add auth later:
bash /app/.agents/skills/backend-building/scripts/init.sh "My App" --features auth

```

**What this does (base, always on first run):**

- Copies `api/`, `contracts/` into the project
- Patches `vite.config.ts` in-place (adds `@contracts` alias, `envDir`, `build.outDir`)
- Adds `tsconfig.server.json` and merges `@contracts/*` path into existing tsconfigs
- Merges `package.json` (adds backend deps and scripts)
- Generates `.env` with portal credentials
- Runs `npm install`

**Additional per feature:**

- **db**: Adds `db/` directory, `drizzle.config.ts`, database connection, `DATABASE_URL` env var, and `db/seed.ts` (scaffold for seeding — run with `npx tsx db/seed.ts`). **Do not overwrite** the generated `api/queries/connection.ts`, `drizzle.config.ts`, or `.env` — they are complete and correct. Only add your tables to `db/schema.ts`
- **auth**: Adds `api/kimi/`, auth router, client patches (Login, useAuth, AuthLayout, TRPCProvider), auto-wires Login/NotFound routes into `App.tsx`

### 3. Verify Auto-Wiring (see below)

### 4. Database Setup (if db or auth feature installed)

```bash
npm run db:push        # sync schema to database (recommended for development)
```

### 5. Development

```bash
npm run dev
```

Start development server with HMR at `http://localhost:3000`

## Post-Init Wiring

On first run, `init.sh` auto-wires `TRPCProvider` into `src/main.tsx`. When `auth` feature is installed, it also adds Login/NotFound routes to `src/App.tsx`. Check the init output:

- **"Auto-wired"** — no action needed, proceed to verification
- **"Wiring required"** — complete the listed steps manually (see [Post-Init Wiring](docs/Post-Init-Wiring.md) for details)

If manual wiring is needed, it typically means:

1. Add `import { TRPCProvider } from "@/providers/trpc"` to `src/main.tsx`
2. Wrap the content inside `<BrowserRouter>` with `<TRPCProvider>`
3. Add Login and NotFound routes to `src/App.tsx`

### Verification

After init (and manual wiring if needed), verify everything works:

1. Run `npm run check` — must pass with zero type errors
2. Run `npm run dev` — server should start at http://localhost:3000
3. If any step fails, read the error and fix before proceeding

## Common Commands

| Command              | Description                                                | Requires |
| -------------------- | ---------------------------------------------------------- | -------- |
| `npm run dev`        | Start development server with HMR at http://localhost:3000 | base |
| `npm run build`      | Build for production (outputs to dist/)                    | base |
| `npm start`          | Start production server                                    | base |
| `npm run check`      | Type-check all TypeScript files                            | base |
| `npm run format`     | Format code with Prettier                                  | base |
| `npm run test`       | Run tests with Vitest                                      | base |
| `npm run db:push`    | Sync schema to DB during development (recommended)         | db |
| `npm run db:generate`| Generate migration SQL for production deployment           | db |
| `npm run db:migrate` | Apply pending migration files to the database              | db |

## Stack Overview

### Backend (added by this skill)

- Hono + tRPC 11.x
- End-to-end type safety
- Public query procedure (base); + authenticated/admin procedures (auth feature)

### Database (db feature)

- Drizzle ORM with MySQL
- Lazy `getDb()` connection, ready to use
- Type-safe queries ([Guide](docs/Database.md))
- Schema migrations

### Authentication (auth feature)

- OAuth 2.0 ([Details](docs/Authentication.md))
- JWT sessions, admin role support

### Frontend (from webapp-building, untouched)

- React 19 + TypeScript + Vite (HMR)
- Tailwind CSS + shadcn/ui components
- Dark/light mode

## Common Mistakes

- **Don't hand-write TypeScript interfaces for DB entities** — use `typeof table.$inferSelect` from `db/schema.ts` to keep types aligned with superjson's Date serialization via tRPC. Hand-written `createdAt: string` will conflict with the actual `Date` objects delivered by superjson
- **Don't write raw SQL** — always use Drizzle's type-safe query API (`getDb().query.*`, `getDb().select()`, `getDb().insert()`)
- **Don't modify `api/lib/` or `api/kimi/`** — these are framework internals (auth, static file serving). Build on top of them, not inside them
- **Don't import `api/` from frontend code** — use `@contracts/` for types/constants that cross the boundary. The only exception is the type import in `src/providers/trpc.tsx`
- **Don't use `api` as the tRPC client name** — it's `trpc` (imported from `@/providers/trpc`)
- **Don't skip Zod validation** on tRPC inputs — always use `.input(z.object({...}))` for mutations and parameterized queries
- **Don't use `serial()` for foreign key columns** — `serial()` creates `bigint unsigned auto_increment`, and MySQL only allows one auto-increment column per table. FK columns must use `bigint("col", { mode: "number", unsigned: true })` to match the PK type
- **Don't use `int()` for foreign keys referencing `serial()` PKs** — `int` is signed 4-byte, `serial()` is `bigint unsigned` 8-byte. MySQL rejects the type mismatch. Use `bigint("col", { mode: "number", unsigned: true })`
- **NEVER drop tables to fix a failed migration** — the database may contain user data. Fix `schema.ts` and run `npm run db:push` to sync. See Troubleshooting below
- **NEVER use `db:push --force`** — it auto-accepts destructive changes (dropping columns/tables) which can destroy user data
- **NEVER modify `.env` values** — `.env` is generated by `init.sh` with valid, working credentials. All values (API keys, OAuth URLs, secrets, database URL) are pre-configured and ready to use. Do not overwrite, regenerate, or placeholder-ify them
- **NEVER overwrite or replace init.sh-generated infrastructure files** — files like `api/queries/connection.ts`, `api/middleware.ts`, `api/lib/`, `drizzle.config.ts`, `src/providers/trpc.tsx`, and `.env` are generated by `init.sh` with correct configuration. Read the init output to see what was created. Build on top of these files (e.g., add routers, schemas), but do not rewrite them
- **Don't change the default port (3000)** — the server runs at `http://localhost:3000`. Do not change this in `vite.config.ts`, `api/boot.ts`, or anywhere else

## AI Agent Instructions

**Required reading before implementing features** — read these docs (under `docs/`) for the features you're working with:
- **db feature**: [Database.md](docs/Database.md) (schema, migrations, connection), [tRPC.md](docs/tRPC.md) (router patterns, procedures, client usage)
- **auth feature**: [Authentication.md](docs/Authentication.md) (OAuth flow, session handling), [tRPC.md](docs/tRPC.md)
- **All features**: [Development-Guide.md](docs/Development-Guide.md) (dev workflow, scripts), [Project-Structure.md](docs/Project-Structure.md) (file layout)

When building features on this stack:

1. **Read existing frontend code** in `src/` to understand the app structure
2. **Design tRPC routers** that match the frontend's data needs
3. **Add DB tables** in `db/schema.ts`, then run `npm run db:push` (requires db feature)
4. **Create new routers** in `api/` and register them in `api/router.ts`
5. **Use type-safe queries** via Drizzle ORM — never raw SQL (requires db feature)
6. **Frontend components** go in `src/` using the existing `@/` alias

**When to use which features:**
- If the user needs a database but no auth, use `--features db`
- If they need user login, use `--features auth` (includes db automatically)
- Default (no `--features` flag) = `auth`, which is backward compatible

### Key Paths

| Path | What to do |
|------|-----------|
| `src/main.tsx` | TRPCProvider auto-wired here (verify after init) |
| `src/App.tsx` | Login/NotFound routes auto-wired here (verify after init, auth feature only) |
| `src/pages/` | Route-level page components (one per route in App.tsx) |
| `src/sections/` | Visual sections within a page (Hero, Footer, etc.) — from webapp-building templates |
| `src/components/` | Create new UI components |
| `api/router.ts` | Register new tRPC routers |
| `api/queries/` | Add query functions for new tables (db feature) |
| `db/schema.ts` | Add new database tables (db feature) |
| `contracts/` | Shared types/constants (frontend + backend) |
| `api/lib/` | Framework internals — don't modify |
| `api/kimi/` | Kimi SDK modules — don't modify (auth feature) |

Full directory tree: [Project Structure](docs/Project-Structure.md)

## Detailed Documentation

- [Project Structure](docs/Project-Structure.md) - Directory layout and where to put things
- [Development Guide](docs/Development-Guide.md) - Component development, API patterns, common workflows
- [Authentication](docs/Authentication.md) - OAuth 2.0 implementation details (optional)
- [Database Guide](docs/Database.md) - Drizzle ORM configuration, schema design, migrations
- [tRPC Best Practices](docs/tRPC.md) - Router patterns and type safety

## Routing (react-router)

This template uses **react-router** v7.

```typescript
// Navigation
import { useNavigate } from "react-router";
const navigate = useNavigate();
navigate("/dashboard");

// Current location
import { useLocation } from "react-router";
const location = useLocation();
console.log(location.pathname);

// Route params
import { useParams } from "react-router";
const { id } = useParams<{ id: string }>();

// Links
import { Link } from "react-router";
<Link to="/about">About</Link>

// Route definitions (in App.tsx)
import { Routes, Route } from "react-router";
<Routes>
  <Route path="/" element={<Home />} />
  <Route path="/users/:id" element={<UserProfile />} />
  <Route path="*" element={<NotFound />} />
</Routes>

// BrowserRouter wraps the app in main.tsx
import { BrowserRouter } from "react-router";
<BrowserRouter>
  <App />
</BrowserRouter>
```

## Troubleshooting

**Port 3000 already in use** — Another process is using the port. Kill it with `lsof -ti:3000 | xargs kill`.

**Database connection refused** — Check `DATABASE_URL` in `.env` is correct and MySQL is running. Run `npm run db:push` before `npm run dev`.

**OAuth callback fails** — The callback URL must be `{origin}/api/oauth/callback`. Verify `VITE_KIMI_AUTH_URL` and `VITE_APP_ID` in `.env` match the portal app config.

**`npm run db:migrate` fails** — NEVER drop tables to recover. MySQL doesn't support transactional DDL, so a failed migration can leave the DB in a partial state. To recover:

1. Fix `schema.ts` (e.g., correct FK types)
2. Run `npm run db:push` — it introspects the actual DB state and syncs it to your corrected schema
3. Delete the broken migration file and its entry in `db/migrations/meta/_journal.json`
4. Run `npm run db:generate` to create a clean baseline migration

**Type errors after adding a new router** — Make sure you registered the router in `api/router.ts` inside `appRouter`. The `AppRouter` type is derived from there and propagates to the frontend automatically.
