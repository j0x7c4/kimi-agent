# Database Guide

> **Contents**: [Overview](#overview) · [Configuration](#configuration) · [Schema Design](#schema-design) · [Migrations](#migrations) · [Best Practices](#best-practices) · [Common Patterns](#common-patterns) · [Advanced Usage](#advanced-usage) · [Troubleshooting](#troubleshooting)

Type-safe database operations using Drizzle ORM with MySQL.

## Overview

**Database**: Drizzle ORM with MySQL (via `mysql2` driver).

**Key features**:

- **Lazy connection**: `getDb()` initializes the connection on first call
- **Type-safe queries**: No raw SQL, full TypeScript inference
- **Migration workflow**: Schema-driven migrations

## Configuration

### Database Connection (`drizzle.config.ts`)

```typescript
import "dotenv/config";
import { defineConfig } from "drizzle-kit";

export default defineConfig({
  dialect: "mysql",
  schema: "./db/schema.ts",
  out: "./db/migrations",
  dbCredentials: {
    url: process.env.DATABASE_URL!,
  },
});
```

### Environment Variable

```bash
DATABASE_URL=mysql://user:pass@host:port/dbname
```

## Schema Design

### Basic Table Example

```typescript
import { mysqlTable, serial, varchar, text, timestamp } from "drizzle-orm/mysql-core";

export const users = mysqlTable("users", {
  id: serial("id").primaryKey(),
  unionId: varchar("unionId", { length: 255 }).notNull().unique(),
  name: varchar("name", { length: 255 }),
  email: varchar("email", { length: 320 }),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
});

export type User = typeof users.$inferSelect;
export type InsertUser = typeof users.$inferInsert;
```

> **Tip**: Always use `$inferSelect` / `$inferInsert` instead of hand-writing interfaces. These inferred types stay in sync with superjson serialization — e.g., timestamp columns will correctly be typed as `Date`, not `string`. See [tRPC — Superjson Serialization](tRPC.md#6-superjson-serialization).

### Type-Safe Queries

```typescript
import { getDb } from "../api/queries/connection";
import { users } from "@db/schema";
import { eq } from "drizzle-orm";

const db = getDb();

// Relational query (requires schema passed to drizzle())
const allUsers = await db.query.users.findMany();

// Select with filter
const activeUsers = await db
  .select()
  .from(users)
  .where(eq(users.email, "user@example.com"));

// Select one
const user = await db.query.users.findFirst({
  where: eq(users.id, userId),
});

// Type-safe joins via relations
const usersWithPosts = await db.query.users.findMany({
  with: {
    posts: true,
  },
});
```

### Insert/Update/Delete

```typescript
// Insert (MySQL does not support .returning() — use .$returningId() for the PK,
// or re-query after insert to get the full row)
const [{ id }] = await db.insert(users).values({
  unionId: "abc123",
  name: "John Doe",
  email: "john@example.com",
}).$returningId();
const newUser = await db.query.users.findFirst({ where: eq(users.id, id) });

// Update
await db.update(users).set({ name: "Jane Doe" }).where(eq(users.id, userId));

// Delete
await db.delete(users).where(eq(users.id, userId));

// Upsert (insert or update on duplicate key)
await db
  .insert(users)
  .values({
    unionId: "abc123",
    name: "John Doe",
  })
  .onDuplicateKeyUpdate({
    set: { name: "John Doe", lastSignInAt: new Date() },
  });
```

## Migrations

Three separate commands, each doing one thing:

| Command | What it does | Touches DB? | Creates files? |
|---------|-------------|:-----------:|:--------------:|
| `npm run db:generate` | Diffs `schema.ts` against previous migrations → produces `.sql` file | No | Yes |
| `npm run db:migrate` | Applies unapplied migration files to the database | Yes | No |
| `npm run db:push` | Syncs schema directly to DB (no migration files) | Yes | No |

### Development: use `db:push`

During development, use `npm run db:push` to iterate on schema design. It introspects the live database, diffs against your `schema.ts`, and applies only what's needed — no migration files, no journal issues.

```bash
# 1. Edit db/schema.ts
# 2. Push changes directly
npm run db:push
# 3. Repeat until schema is right
```

`npm run db:push` handles "table already exists" naturally because it knows what's already in the DB. It won't create duplicates or fail on partial state.

### Production: use `db:generate` + `db:migrate`

When the schema is stable and ready to deploy, generate a migration file for version control and auditability:

```bash
npm run db:generate    # creates .sql file — review it
npm run db:migrate     # applies it to the database
```

### Recovery: when `db:migrate` fails

**NEVER drop tables to recover** — the database may contain user data.

MySQL does not support transactional DDL — a migration with multiple statements can partially succeed (e.g., table A created, table B fails). There is no automatic rollback.

Recovery steps:

1. Fix `schema.ts` (e.g., correct FK types)
2. Run `npm run db:push` to sync the database to the corrected schema
3. Delete the broken migration `.sql` file **and** its entry in `db/migrations/meta/_journal.json`
4. Run `npm run db:generate` to produce a clean migration that matches the now-correct DB state
5. The generated migration should be empty or minimal — commit it as the baseline

## Best Practices

### Do

- Use Drizzle's query API (never raw SQL)
- Leverage TypeScript inference with `typeof table.$inferSelect`
- Use transactions for multiple operations
- Create indexes for frequently queried columns

```typescript
const db = getDb();

// Type-safe query
const result = await db.query.users.findFirst({
  where: eq(users.id, id),
});

// With transaction
await db.transaction(async (tx) => {
  await tx.insert(users).values(newUser);
  await tx.insert(profiles).values({ userId: newUser.id, bio });
});
```

### Don't

```typescript
// Bad - Raw SQL (loses type safety)
const result = await db.execute("SELECT * FROM users WHERE id = ?", [id]);

// Bad - No null check
const user = await db.query.users.findFirst({ where: eq(users.id, id) });
return user.email; // Could be undefined!
```

## Common Patterns

### Standalone Query Functions

`api/queries/` contains standalone query functions. Follow this pattern for new features:

```typescript
// api/queries/todos.ts
import { getDb } from "./connection";
import { todos } from "@db/schema";
import { eq } from "drizzle-orm";

export async function findTodosByUser(userId: number) {
  return getDb().query.todos.findMany({
    where: eq(todos.userId, userId),
  });
}

export async function createTodo(data: { title: string; userId: number }) {
  await getDb().insert(todos).values(data);
}
```

Use these from routers: `import { findTodosByUser } from "./queries/todos";`

## Advanced Usage

### Relations

Define relations in `db/relations.ts`:

```typescript
import { relations } from "drizzle-orm";
import { users, posts } from "./schema";

export const usersRelations = relations(users, ({ many }) => ({
  posts: many(posts),
}));

export const postsRelations = relations(posts, ({ one }) => ({
  author: one(users, { fields: [posts.authorId], references: [users.id] }),
}));
```

### Indexes

```typescript
import { mysqlTable, serial, varchar, index } from "drizzle-orm/mysql-core";

export const users = mysqlTable(
  "users",
  {
    id: serial("id").primaryKey(),
    email: varchar("email", { length: 320 }).notNull().unique(),
  },
  (table) => ({
    emailIdx: index("email_idx").on(table.email),
  }),
);
```

## TiDB Compatibility

TiDB does not support `LATERAL JOIN` ([docs](https://docs.pingcap.com/tidb/stable/mysql-compatibility/), [tracking issue](https://github.com/pingcap/tidb/issues/40328)). Drizzle's relational query builder (`db.query.*` with `with: { ... }`) generates LATERAL JOINs in `mode: "default"`.

**Fix**: Use `mode: "planetscale"` when creating the Drizzle instance. This mode avoids LATERAL JOINs by using subqueries instead, and all relational queries work normally:

```typescript
// api/queries/connection.ts
export function getDb() {
  if (!instance) {
    instance = drizzle(env.databaseUrl, {
      mode: "planetscale",  // ← avoids LATERAL JOINs, works with TiDB
      schema: { ...schema, ...relations },
    });
  }
  return instance;
}
```

With `mode: "planetscale"`, relational queries work as expected:

```typescript
// Works on TiDB with mode: "planetscale"
const postsWithAuthors = await getDb().query.posts.findMany({
  with: { author: true },
});
```

If you cannot use `mode: "planetscale"` for some reason, the fallback is to avoid relational queries and use separate `getDb().select()` calls:

```typescript
// Also works — manual approach
const db = getDb();
const posts = await db.select().from(schema.posts)
  .orderBy(desc(schema.posts.createdAt));

const postsWithAuthors = await Promise.all(
  posts.map(async (post) => {
    const [author] = await db.select().from(schema.users)
      .where(eq(schema.users.id, post.authorId))
      .limit(1);
    return { ...post, author };
  })
);
```

### Other TiDB Notes

`serial()` maps to `bigint unsigned auto_increment` in MySQL. Foreign key columns referencing a `serial()` PK must match this type exactly — use `bigint` with `unsigned: true`:

```typescript
// Wrong — serial() adds auto_increment (only one per table)
postId: serial("postId").notNull(),

// Wrong — int is signed 4-byte, can't reference bigint unsigned
postId: int("postId").notNull(),

// Correct — matches serial()'s bigint unsigned type
postId: bigint("postId", { mode: "number", unsigned: true }).notNull(),
```

Full one-to-many example:

```typescript
import { mysqlTable, serial, bigint, varchar, text, timestamp } from "drizzle-orm/mysql-core";

export const users = mysqlTable("users", {
  id: serial("id").primaryKey(),  // bigint unsigned auto_increment
  name: varchar("name", { length: 255 }),
});

export const posts = mysqlTable("posts", {
  id: serial("id").primaryKey(),
  authorId: bigint("authorId", { mode: "number", unsigned: true }).notNull(),
  title: varchar("title", { length: 255 }).notNull(),
  content: text("content"),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
});
```

### SSL Configuration

TiDB Cloud requires SSL. The `DATABASE_URL` must include `?ssl={"rejectUnauthorized":true}`. The mysql2 driver does **not** accept `?ssl=true` (it requires an object, not a boolean).

```bash
# Correct — JSON object (portal generates this)
DATABASE_URL=mysql://user:pass@host:4000/db?ssl={"rejectUnauthorized":true}

# Wrong — mysql2 rejects boolean ssl
DATABASE_URL=mysql://user:pass@host:4000/db?ssl=true
```

## Troubleshooting

```bash
# Connection refused
Error: connect ECONNREFUSED
→ Check DATABASE_URL is correct and MySQL is running

# Table already exists
Error: table already exists
→ Drop table manually, then re-run migration

# SSL profile error
Error: SSL profile must be an object, instead it's a boolean
→ Use ?ssl={"rejectUnauthorized":true} instead of ?ssl=true

# LATERAL JOIN error (TiDB)
Error: ER_PARSE_ERROR ... LATERAL ...
→ Set mode: "planetscale" in drizzle() config.
  See "TiDB Compatibility" section above.
```

## Learn More

- [Drizzle ORM Docs](https://orm.drizzle.team)
- [Drizzle Kit Migrations](https://orm.drizzle.team/docs/migrations)
