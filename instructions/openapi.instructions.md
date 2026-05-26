---
description: Checklist and rules for creating `*.openapi.ts` files with @asteasolutions/zod-to-openapi.
applyTo: "**/*.openapi.ts"
---

# Checklist for Creating a `*.openapi.ts`

## 1. Read the controller before writing anything

Verify the real shape of `res.json(...)` in each handler. The most critical bug is exactly this: the 200 response may accidentally use a request schema while the controller returns a different shape.

```
controller.ts → what does res.json() send on success?
```

## 2. Trace all possible errors by layer

For each endpoint, go through the layers in this order:

| Layer                          | What to check                                                     |
| ------------------------------ | ----------------------------------------------------------------- |
| Middleware (before controller) | Which `AppError` does it throw? (e.g.: 401 in KeycloakMiddleware) |
| Body validation                | Zod `.parse()` without try/catch → 400                            |
| Use case                       | All `throw new AppError(...)` or `throw new DomainError(...)`     |
| Repository / infra             | Any uncaught error → **500** via global error handler             |

## 3. Confirm the error shape in the global error handler

In `app.ts`:

```ts
res.status((err as AppError).statusCode ?? 500).json({ error: err.message });
```

All errors return `{ error: string }`. A single `ErrorResponseSchema` covers all error status codes.

## 4. Create schemas that don't exist, reuse those that do

- **Reuse**: schemas already defined in `presentation/validators/<module>.schema.ts` with `.openapi()`
- **Create**: only when the shape doesn't exist yet (e.g.: `RefreshTokenResponseSchema`, `ErrorResponseSchema`)
- **Never redefine** a schema that already has `.openapi()` elsewhere

## 5. Register the security scheme before paths that use it

```ts
// ALWAYS before any registerPath with security
registry.registerComponent("securitySchemes", "bearerAuth", { ... });
```

## 6. Complete `registerPath` structure

```ts
registry.registerPath({
  method: "post" | "get" | "put" | "delete" | "patch",
  path: "/module/endpoint",
  tags: ["ModuleName"],
  security: [{ bearerAuth: [] }], // only if authenticated
  request: {
    // only if there is a body
    body: {
      content: { "application/json": { schema: RequestSchema } }
    }
  },
  responses: {
    200: {
      description: "...",
      content: { "application/json": { schema: ResponseSchema } }
    },
    400: {
      description: "Invalid body",
      content: { "application/json": { schema: ErrorResponseSchema } }
    },
    401: {
      description: "Unauthenticated",
      content: { "application/json": { schema: ErrorResponseSchema } }
    },
    403: {
      description: "Forbidden",
      content: { "application/json": { schema: ErrorResponseSchema } }
    },
    404: {
      description: "Resource not found",
      content: { "application/json": { schema: ErrorResponseSchema } }
    },
    422: {
      description: "Domain rule violated",
      content: { "application/json": { schema: ErrorResponseSchema } }
    },
    500: {
      description: "Unexpected internal error",
      content: { "application/json": { schema: ErrorResponseSchema } }
    }
  }
});
```

Only include the status codes that the endpoint actually produces — don't add 403 if there is no RBAC middleware, for example.

## 7. Golden rule for 500

**Every endpoint documents 500.** The global error handler catches any error without a `statusCode` and returns 500. Database failures, network issues, external services — all end up here.

## 8. Import order

Project ESLint: `@modules/` before `@src/`, no blank line between them within the same group.
