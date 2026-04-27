# tRPC Best Practices

> **Contents**: [Modularize Routers](#1-modularize-routers-by-feature) · [Context](#2-context) · [Procedure Types](#3-procedure-types) · [Input Validation](#4-input-validation-with-zod) · [Client-Side Usage](#5-client-side-usage) · [Superjson](#6-superjson-serialization) · [Testing with curl](#7-testing-endpoints-with-curl)

Guide for building tRPC APIs in this stack. All examples use the actual project paths and exports.

## 1. Modularize Routers by Feature

Create separate router files per feature, then register them in `api/router.ts`.

```typescript
// api/todoRouter.ts
import { z } from "zod";
import { createRouter, authedQuery } from "./middleware";
import { findTodosByUser, createTodo } from "./queries/todos";

export const todoRouter = createRouter({
  list: authedQuery.query(({ ctx }) =>
    findTodosByUser(ctx.user.id),
  ),
  create: authedQuery
    .input(z.object({ title: z.string().min(1) }))
    .mutation(({ ctx, input }) =>
      createTodo({ title: input.title, userId: ctx.user.id }),
    ),
});

// api/router.ts — register it
import { todoRouter } from "./todoRouter";

export const appRouter = createRouter({
  // ... existing routes
  todo: todoRouter,
});
```

## 2. Context

Context is defined in `api/context.ts` and provides `req`, `res`, and `user` (populated from JWT if authenticated).

```typescript
// Already set up — you get this in every procedure:
type TrpcContext = {
  req: Request;
  resHeaders: Headers;
  user?: User; // undefined if not authenticated
};
```

You don't need to modify context. Just use `ctx.user` in authenticated procedures — it's guaranteed non-null.

## 3. Procedure Types

Defined in `api/middleware.ts`:

| Export | Auth | Use case |
|--------|:----:|----------|
| `publicQuery` | No | Public endpoints (ping, public data) |
| `authedQuery` | Yes | User endpoints (requires `auth` feature) |
| `adminQuery` | Yes + admin | Admin endpoints (requires `auth` feature) |

> **db-only mode**: Only `publicQuery` and `createRouter` are exported from `api/middleware.ts`. Use `publicQuery` for all endpoints.

```typescript
import { createRouter, publicQuery, authedQuery, adminQuery } from "./middleware";

export const myRouter = createRouter({
  public: publicQuery.query(() => ({ status: "ok" })),
  profile: authedQuery.query(({ ctx }) => ctx.user),
  users: adminQuery.query(() => getDb().query.users.findMany()),
});
```

## 4. Input Validation with Zod

Always validate inputs. Zod schemas provide both runtime validation and TypeScript types.

```typescript
import { z } from "zod";

export const postRouter = createRouter({
  create: authedQuery
    .input(
      z.object({
        title: z.string().min(3, "Title must be at least 3 characters"),
        content: z.string().optional(),
      }),
    )
    .mutation(async ({ ctx, input }) => {
      await createPost({
        title: input.title,
        content: input.content,
        authorId: ctx.user.id,
      });
    }),
});
```

## 5. Client-Side Usage

The tRPC React client is at `src/providers/trpc.tsx` and exported as `trpc`.

```typescript
// src/components/PostForm.tsx
import { trpc } from "@/providers/trpc";

function PostForm() {
  const utils = trpc.useUtils();
  const createPost = trpc.post.create.useMutation({
    onSuccess: () => {
      // Invalidate queries to refetch
      utils.post.list.invalidate();
    },
  });

  const handleSubmit = (data: { title: string; content?: string }) => {
    createPost.mutate(data);
  };

  return (/* ... */);
}
```

## 6. Superjson Serialization

Already configured — `Date`, `Map`, `Set` are serialized automatically between client and server. No action needed.

**Important**: Timestamp columns (e.g., `timestamp("createdAt")`) return `Date` objects from Drizzle, and superjson preserves them as `Date` instances on the client. Do not hand-write TypeScript interfaces with `createdAt: string` — use schema-inferred types instead:

```typescript
// ✅ Correct — types stay in sync with the database schema
import { posts } from "@db/schema";
type Post = typeof posts.$inferSelect; // createdAt is Date

// ❌ Wrong — will cause type errors with tRPC responses
interface Post {
  createdAt: string; // superjson delivers Date, not string
}
```

See [Database Guide — Schema Design](Database.md#basic-table-example) for the `$inferSelect` pattern.

## 7. Testing Endpoints with curl

tRPC uses superjson encoding. Query procedures use GET with URL-encoded `input`:

```bash
# Query (GET) — no input
curl http://localhost:3000/api/trpc/post.list

# Query (GET) — with input (superjson-encoded)
# For simple types like numbers/strings, wrap in {"json": value}
curl 'http://localhost:3000/api/trpc/post.byId?input={"json":1}'

# Mutation (POST) — with input
curl -X POST http://localhost:3000/api/trpc/post.create \
  -H 'Content-Type: application/json' \
  -d '{"json":{"title":"Test","content":"Hello"}}'
```

> **Note**: The tRPC React client handles superjson encoding automatically. Manual curl is only needed for debugging.
