# Development Guide

> **Contents**: [Adding a Feature End-to-End](#adding-a-feature-end-to-end) · [Component Development](#component-development) · [API Development](#api-development) · [Database Best Practices](#database-best-practices) · [Runtime Behaviors](#runtime-behaviors) · [Common Patterns](#common-patterns) · [Testing](#testing)

## Adding a Feature End-to-End

Example: adding a "notes" feature with CRUD. This shows the full flow from database to UI.

### Step 1: Schema (`db/schema.ts`)

```typescript
export const notes = mysqlTable("notes", {
  id: serial("id").primaryKey(),
  title: varchar("title", { length: 255 }).notNull(),
  content: text("content"),
  userId: bigint("userId", { mode: "number", unsigned: true }).notNull(),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
});

export type Note = typeof notes.$inferSelect;
```

Then run `npm run db:push`.

### Step 2: Query Functions (`api/queries/notes.ts`)

```typescript
import { getDb } from "./connection";
import { notes } from "@db/schema";
import { eq } from "drizzle-orm";

export async function findNotesByUser(userId: number) {
  return getDb().select().from(notes).where(eq(notes.userId, userId));
}

export async function createNote(data: { title: string; content?: string; userId: number }) {
  await getDb().insert(notes).values(data);
}
```

### Step 3: Router (`api/noteRouter.ts`)

```typescript
import { z } from "zod";
import { createRouter, authedQuery } from "./middleware";
import { findNotesByUser, createNote } from "./queries/notes";

export const noteRouter = createRouter({
  list: authedQuery.query(({ ctx }) =>
    findNotesByUser(ctx.user.id),
  ),
  create: authedQuery
    .input(z.object({ title: z.string().min(1), content: z.string().optional() }))
    .mutation(({ ctx, input }) =>
      createNote({ ...input, userId: ctx.user.id }),
    ),
});
```

### Step 4: Register (`api/router.ts`)

```typescript
import { noteRouter } from "./noteRouter";

export const appRouter = createRouter({
  // ...existing routes
  note: noteRouter,
});
```

### Step 5: Frontend (`src/pages/Notes.tsx`)

```tsx
import { trpc } from "@/providers/trpc";
import { Button } from "@/components/ui/button";

export default function Notes() {
  const { data: notes, isLoading } = trpc.note.list.useQuery();
  const utils = trpc.useUtils();
  const create = trpc.note.create.useMutation({
    onSuccess: () => utils.note.list.invalidate(),
  });

  if (isLoading) return <div>Loading...</div>;

  return (
    <div>
      <Button onClick={() => create.mutate({ title: "New note" })}>Add</Button>
      {notes?.map((n) => <div key={n.id}>{n.title}</div>)}
    </div>
  );
}
```

### Step 6: Route (`src/App.tsx`)

```tsx
import Notes from "./pages/Notes";

// Inside <Routes>:
<Route path="/notes" element={<Notes />} />
```

---

## Component Development

Before creating custom components, check the existing shadcn/ui components in `src/components/ui/`. It contains 53+ ready-to-use components.

### Customizing Components

1. **Modify** components in `src/components/ui/`
2. **Use ThemeContext** for dark/light mode support

### Creating New Pages

Create new route-level page components in `src/pages/` and add corresponding routes in `src/App.tsx`. Visual sections within a page (e.g., Hero, Features) go in `src/sections/` and are composed inside the page component.

## API Development

### tRPC Procedure Types

From `api/middleware.ts`:

- `createRouter` - Create tRPC routers

  ```typescript
  export const myRouter = createRouter({
    getData: publicQuery.query(() => "data"),
  });
  ```

- `publicQuery` - Public endpoints (no auth required)

  ```typescript
  getPublic: publicQuery.query(() => ({ message: "Public data" }));
  ```

- `authedQuery` - Authenticated endpoints (requires login)
  ```typescript
  getSecrets: authedQuery.query(({ ctx }) => {
    return { userId: ctx.user.id };
  });
  ```

- `adminQuery` - Admin-only endpoints (requires `role: "admin"`)
  ```typescript
  manageUsers: adminQuery.query(({ ctx }) => {
    return getAllUsers();
  });
  ```

### Adding New Routers

1. Create router file: `api/featureRouter.ts`
2. Define procedures using `createRouter`, `publicQuery`, or `authedQuery` from `api/middleware.ts`
3. Add to aggregation in `api/router.ts`

## Database Best Practices

See [Database Guide](Database.md) for comprehensive database documentation.

### Quick Reference

**NEVER write raw SQL** - always use Drizzle's type-safe query API:

```typescript
// Bad - Raw SQL (loses type safety)
const users = await getDb().execute("SELECT * FROM users");

// Good - Type-safe query
const users = await getDb().query.users.findMany();
```

**Key principles**:

- Use `getDb().query.table` for type-safe queries
- Leverage TypeScript inference with `typeof table.$inferSelect`
- Create migrations with `npm run db:push`

## Runtime Behaviors

### Database Connection

- **Lazy initialization**: `getDb()` creates the connection on first call — import from `api/queries/connection.ts`
- **Connection pooling**: Handled by `mysql2` driver
- **Transaction support**: Use `getDb().transaction()` for atomic operations

### Environment Variables

- **Configuration location**: `api/lib/env.ts`
- **Frontend variables**: Prefix with `VITE_` (e.g., `VITE_APP_ID`)
- **Reference**: See `.env.example` for all available variables

### Hot Reload Development

- **HMR**: Vite Hot Module Replacement enabled in dev mode
- **tRPC**: Full type safety and auto-refetch on HMR
- **Database**: Changes to schema require restart for migrations

## Common Patterns

### Frontend Data Fetching with tRPC

```typescript
import { trpc } from "@/providers/trpc";

function UserProfile() {
  const { data: user, isLoading } = trpc.auth.me.useQuery();

  if (isLoading) return <div>Loading...</div>;
  if (!user) return <div>Not authenticated</div>;

  return <div>Welcome, {user.name}</div>;
}
```

### Backend Authenticated Procedures

```typescript
import { createRouter, authedQuery } from "./middleware";

export const userRouter = createRouter({
  getProfile: authedQuery.query(({ ctx }) => {
    return ctx.user;
  }),

  updateProfile: authedQuery
    .input(z.object({ name: z.string() }))
    .mutation(({ ctx, input }) => {
      return updateUser(ctx.user.id, input);
    }),
});
```

### Error Handling

```typescript
import { Errors } from "@contracts/errors";

export const myProcedure = publicQuery.query(async () => {
  try {
    const data = await fetchData();
    return data;
  } catch (error) {
    throw Errors.internal("Failed to fetch data");
  }
});
```

## Testing

Run `npm run test` to execute the test suite with Vitest.

Focus testing on:

- Business logic in procedures
- Frontend component interactions
- Database query results
- Authentication edge cases (if using auth)
