# Post-Init Wiring

`init.sh` attempts to auto-wire tRPC providers and routes. If auto-wiring succeeded (output says "Auto-wired"), skip this document entirely.

If auto-wiring failed (output lists "Wiring required"), complete the steps below. Read each file before editing — preserve all existing code.

## 1. Wire TRPCProvider into src/main.tsx

`src/providers/trpc.tsx` exports a `TRPCProvider` component that encapsulates tRPC + React Query setup. Add it inside `<BrowserRouter>`:

```tsx
import { TRPCProvider } from "@/providers/trpc";

// Wrap INSIDE <BrowserRouter>, OUTSIDE everything else:
createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <BrowserRouter>
      <TRPCProvider>
        {/* ...existing providers and <App /> stay here... */}
        <App />
      </TRPCProvider>
    </BrowserRouter>
  </StrictMode>
);
```

## 2. Add Login and NotFound routes to src/App.tsx

Add the backend-provided routes alongside existing routes:

```tsx
import Login from "./pages/Login";
import NotFound from "./pages/NotFound";

// Inside <Routes>, add:
<Route path="/login" element={<Login />} />
<Route path="*" element={<NotFound />} />
```
