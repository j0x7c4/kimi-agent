# Authentication System

> **Contents**: [Overview](#overview) · [Architecture](#architecture) · [Configuration](#configuration) · [API Reference](#api-reference) · [Admin Role](#admin-role)

The template includes a complete OAuth 2.0 authentication system that can be
used for user management.

## Overview

**This is optional** - skip this if your app doesn't need user authentication.

**When to use**: User login, protected routes, or user-specific data.

**When to skip**: For public-facing apps, landing pages, or internal tools
without user management.

## Architecture

### Backend Implementation

The backend handles OAuth flow, JWT session management, and database operations.

**Core files**:

- `api/kimi/auth.ts` - OAuth flow and request authentication
- `api/kimi/session.ts` - JWT sign/verify functions
- `api/kimi/platform.ts` - Kimi Open Platform API
- `api/context.ts` - Authentication context for tRPC
- `api/queries/users.ts` - User query functions

**Key features**:

- Complete OAuth 2.0 flow with authorization code exchange
- JWT-based session management (1-year expiry)
- Automatic user provisioning (upsert on first login)
- Secure cookie handling (httpOnly, secure, sameSite)
- Protected tRPC procedures via `authedQuery` middleware

### Frontend Implementation

The frontend provides hooks and UI components for authentication.

**Core files**:

- `src/hooks/useAuth.ts` - Authentication React hook
- `src/components/AuthLayout.tsx` - Authenticated layout with sidebar and auth UI
- `src/pages/Login.tsx` - OAuth login page (see full source below)
- `src/const.ts` - LOGIN_PATH constant

#### Login Page (`src/pages/Login.tsx`)

**IMPORTANT**: This file is already provided by `init.sh`. Do NOT create your own login page — use the existing one as-is:

```typescript
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

function getOAuthUrl() {
  const kimiAuthUrl = import.meta.env.VITE_KIMI_AUTH_URL;
  const appID = import.meta.env.VITE_APP_ID;
  const redirectUri = `${window.location.origin}/api/oauth/callback`;
  const state = btoa(redirectUri);

  const url = new URL(`${kimiAuthUrl}/api/oauth/authorize`);
  url.searchParams.set("client_id", appID);
  url.searchParams.set("redirect_uri", redirectUri);
  url.searchParams.set("response_type", "code");
  url.searchParams.set("scope", "profile");
  url.searchParams.set("state", state);

  return url.toString();
}

export default function Login() {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <Card className="w-full max-w-sm">
        <CardHeader className="text-center">
          <CardTitle>Welcome</CardTitle>
        </CardHeader>
        <CardContent>
          <Button
            className="w-full"
            size="lg"
            onClick={() => {
              window.location.href = getOAuthUrl();
            }}
          >
            Sign in with Kimi
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
```

This page constructs the OAuth URL from environment variables and redirects the user. The route `/login` should point to this component in `App.tsx`. Do not modify the OAuth URL construction logic or create a custom login page.

**Key features**:

- `useAuth()` hook for state management
- Automatic redirect for unauthenticated users
- Loading states and error handling
- Logout functionality
- Type-safe integration with tRPC

## Configuration

### Environment Variables

Required environment variables for OAuth and JWT: Already provided in `.env`,
you MUST not modify.

```bash
VITE_APP_ID
VITE_KIMI_AUTH_URL
KIMI_AUTH_URL
APP_SECRET
```

### Database Schema

Located in `db/schema.ts`:

```typescript
export const users = mysqlTable("users", {
  id: serial("id").primaryKey(),
  unionId: varchar("unionId", { length: 255 }).notNull().unique(),
  name: varchar("name", { length: 255 }),
  email: varchar("email", { length: 320 }),
  avatar: text("avatar"),
  role: mysqlEnum("role", ["user", "admin"]).default("user").notNull(),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().notNull(),
  lastSignInAt: timestamp("lastSignInAt").defaultNow().notNull(),
});
```

## API Reference

### Authentication Endpoints

- `GET /api/oauth/callback` - OAuth callback handler
- `auth.me` - Get current user (authenticated)
- `auth.logout` - Logout user (authenticated)

### Using in Your Code

#### Frontend

Use the `useAuth()` hook:

```typescript
import { useAuth } from "@/hooks/useAuth";

function MyComponent() {
  const { user, isAuthenticated, isLoading, logout } = useAuth();

  if (isLoading) return <div>Loading...</div>;
  if (!isAuthenticated) return <div>Please log in</div>;

  return <div>Welcome, {user.name}!</div>;
}
```

Use `AuthLayout` for automatic auth UI:

```typescript
<AuthLayout>
  <YourPageContent />
</AuthLayout>;
```

Automatic redirect:

```typescript
import { LOGIN_PATH } from "@/const";

const { user, isLoading } = useAuth({
  redirectOnUnauthenticated: true,
  redirectPath: LOGIN_PATH,
});
```

#### Backend

Protect tRPC procedures:

```typescript
import { createRouter, authedQuery } from "./middleware";

export const myRouter = createRouter({
  getSecrets: authedQuery.query(({ ctx }) => {
    return { secrets: `User ${ctx.user.id} secrets` };
  }),
});
```

Access user in context:

```typescript
authedQuery.query(({ ctx }) => {
  const userId = ctx.user.id; // User is authenticated here
  return getUserData(userId);
});
```

## Admin Role

The template supports admin/normal user distinction via the `role` column on the users table.

### How admin is assigned

The **app creator** (the person who created the app via the portal) is automatically assigned the `admin` role on first login. This is controlled by the `OWNER_UNION_ID` environment variable, which is set automatically by `init.sh` during project setup.

- `OWNER_UNION_ID` is extracted from the portal's `creator_user_id` response
- When a user logs in and their `unionId` matches `OWNER_UNION_ID`, they get `role: "admin"`
- All other users get `role: "user"` (the default)

### Procedure types

Three procedure levels are available in `api/middleware.ts`:

| Procedure | Auth required | Admin required | Use case |
|-----------|:---:|:---:|----------|
| `publicQuery` | No | No | Public endpoints (ping, public data) |
| `authedQuery` | Yes | No | User-specific endpoints (profile, user data) |
| `adminQuery` | Yes | Yes | Admin-only endpoints (user management, settings) |

```typescript
import { createRouter, authedQuery, adminQuery } from "./middleware";

export const adminRouter = createRouter({
  listUsers: adminQuery.query(({ ctx }) => {
    // Only accessible by admin users
    return getAllUsers();
  }),
});
```
