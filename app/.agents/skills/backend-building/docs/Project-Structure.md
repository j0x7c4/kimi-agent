# Project Structure

> **Contents**: [Directory Layout](#directory-layout) · [Key Directories Explained](#key-directories-explained) · [Development Workflow](#development-workflow)

## Directory Layout

> Entries marked *(auth)* are only present when the `auth` feature is installed.

```
project-root/
├── src/                       # Frontend code (from webapp-building + backend patches)
│   ├── hooks/                # Reusable React hooks
│   │   └── useAuth.ts       # (auth)
│   ├── components/           # Reusable UI components
│   │   ├── ui/              # 53+ shadcn/ui components
│   │   ├── AuthLayout.tsx   # (auth)
│   │   └── AuthLayoutSkeleton.tsx  # (auth)
│   ├── pages/                # Route-level page components (one per route in App.tsx)
│   │   ├── Login.tsx         # (auth) Added by init.sh
│   │   ├── NotFound.tsx      # Added by init.sh (cp -n, won't overwrite)
│   │   └── Home.tsx          # Created by agent from existing App.tsx content
│   ├── sections/             # Visual sections within a page (from webapp-building templates)
│   ├── providers/            # React context providers
│   │   └── trpc.tsx         # tRPC React client + TRPCProvider
│   ├── const.ts              # Frontend constants
│   ├── index.css             # Tailwind CSS entry
│   └── main.tsx              # React app entry
├── index.html                # HTML entry (from webapp-building)
├── api/                      # Backend code (added by backend building)
│   ├── lib/                 # Framework utilities
│   │   ├── env.ts           # Environment config
│   │   ├── vite.ts          # Vite middleware setup
│   │   ├── cookies.ts       # Session cookie config
│   │   └── http.ts          # HTTP client utility
│   ├── kimi/                # Kimi SDK modules (auth)
│   │   ├── auth.ts          # OAuth flow + request authentication
│   │   ├── session.ts       # JWT sign/verify
│   │   ├── platform.ts      # Kimi Open Platform API
│   │   └── types.ts         # Kimi-specific types
│   ├── queries/             # Database query functions
│   │   ├── connection.ts    # Lazy drizzle instance
│   │   └── users.ts         # User query functions
│   ├── boot.ts              # Hono entry, Vite/static, OAuth callback
│   ├── router.ts            # tRPC router aggregation
│   ├── middleware.ts         # tRPC init + procedure definitions
│   └── context.ts           # Authentication context for tRPC
├── db/                       # Database schema and migrations
│   ├── schema.ts            # Table definitions
│   ├── relations.ts         # Table relations
│   ├── seed.ts              # Seed script scaffold (run with `npx tsx db/seed.ts`)
│   └── migrations/
├── contracts/                # Shared between frontend and server
│   ├── errors.ts            # Error types
│   ├── constants.ts         # Shared constants (auth)
│   └── types.ts             # Shared types
├── vite.config.ts           # Vite configuration (patched by init script)
├── tsconfig.json            # Root TypeScript config (project references)
├── tsconfig.app.json        # Frontend TypeScript config (from webapp-building)
├── tsconfig.node.json       # Node/Vite TypeScript config (from webapp-building)
├── tsconfig.server.json     # Server TypeScript config (added by backend building)
├── drizzle.config.ts        # Drizzle ORM configuration
└── vitest.config.ts         # Test configuration
```

## Key Directories Explained

### `src/`

**pages/** - Route-level page components, one per route in `App.tsx`. `Login.tsx` and `NotFound.tsx` are copied by `init.sh`; `Home.tsx` is created by the agent (extracted from existing `App.tsx` content during post-init wiring).

**sections/** - Visual building blocks within a page (e.g., Hero, Footer, Services). Present when a webapp-building styled template is used. Sections are composed inside page components — don't add routes for them.

**components/** - Reusable UI components organized by:
- `ui/` - shadcn/ui component library (53+ components)
- `AuthLayout.tsx` - Authenticated layout with sidebar navigation

**hooks/** - Reusable React hooks including `useAuth.ts`.

**providers/** - React context providers including `trpc.tsx`.

### `api/`

**lib/** - Framework utilities — don't modify unless you understand the architecture:
- `env.ts` - Environment variable loading
- `vite.ts` - Vite middleware setup
- `cookies.ts` - Session cookie configuration
- `http.ts` - HTTP client utility

**kimi/** - Kimi SDK modules — don't modify:
- `auth.ts` - OAuth implementation + request authentication
- `session.ts` - JWT sign/verify functions
- `platform.ts` - Kimi Open Platform API client

**queries/** - Database query functions. Add new files here for new features.

**router.ts** - Where you add new API endpoints. Import routers and aggregate them here.

**middleware.ts** - tRPC setup and procedure definitions (`publicQuery`, `authedQuery`, `adminQuery`).

### `db/`

**schema.ts** - Database table definitions. Modify this file, then run `npm run db:push` to sync.

**migrations/** - Auto-generated migration files. Don't edit manually.

### `contracts/`

TypeScript types and constants that need to be shared between frontend and backend for end-to-end type safety.

## Development Workflow

### Adding a New Page

1. Create `src/pages/MyPage.tsx`
2. Add route in `src/App.tsx`

### Adding a New API Endpoint

1. Create new router file (e.g., `api/featureRouter.ts`)
2. Define procedures using `createRouter`, `publicQuery`, or `authedQuery` from `api/middleware.ts`
3. Import and add to `api/router.ts`
4. Use on frontend with full type safety

### Adding a Database Table

1. Add table definition to `db/schema.ts`
2. Add query functions in `api/queries/`
3. Run `npm run db:push`
4. Import from `@db/schema` in API code (not `@/db/schema` — `@/` resolves to `src/`, frontend only)

### Import Conventions

| Alias | Target | Used by |
|-------|--------|---------|
| `@/` | `src/` | Frontend code |
| `@contracts/` | `contracts/` | Both frontend and API code |
| `@db/` | `db/` | API code only |

- **Within `api/`**: use relative imports (`./lib/env`, `../queries/connection`)
- **From `api/` to `db/`**: use `@db/schema` (not relative paths or `@/db/`)
- **From `api/` to `contracts/`**: use `@contracts/errors`
- **`@/` is frontend-only** — it resolves to `src/`, not the project root

### Customizing UI Components

1. Modify components directly in `src/components/ui/`
2. Use ThemeContext for dark/light mode support
