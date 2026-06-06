---
description: Checklist and rules for creating `*.openapi.ts` files with @asteasolutions/zod-to-openapi.
applyTo: "**/*.openapi.ts"
---

# Checklist for Creating a `*.openapi.ts`

## 1. Read the controller before writing anything

Check real `res.json(...)` shape in each handler. Biggest bug: 200 response uses request schema, but controller returns different shape.

```
controller.ts → what does res.json() send on success?
```

## 2. Trace all possible errors by layer

For each endpoint, trace layers in this order:

| Layer                          | What to check                                                 |
| ------------------------------ | ------------------------------------------------------------- |
| Middleware (before controller) | Which `AppError` it throws? (ex: 401 in KeycloakMiddleware)   |
| Body validation                | Zod `.parse()` without try/catch -> 400                       |
| Use case                       | All `throw new AppError(...)` or `throw new DomainError(...)` |
| Repository / infra             | Any uncaught error -> **500** via global error handler        |

## 3. Confirm the error shape in the global error handler

In `app.ts`:

```ts
res.status((err as AppError).statusCode ?? 500).json({ error: err.message });
```

All errors return `{ error: string }`. One `ErrorResponseSchema` covers all error status codes.

## 4. Create schemas that don't exist, reuse those that do

- **Reuse**: schemas already in `presentation/validators/<module>.schema.ts` with `.openapi()`
- **Create**: only when shape not exist yet (ex: `RefreshTokenResponseSchema`, `ErrorResponseSchema`)
- **Never redefine** schema that already has `.openapi()` elsewhere

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

Include only status codes endpoint really produces. Example: do not add 403 if no RBAC middleware.

## 7. Golden rule for 500

**Every endpoint documents 500.** Global error handler catches any error without `statusCode` and returns 500. DB failure, network issue, external service issue: all end here.

## 8. Import order

Project ESLint rule: `@modules/` before `@src/`, no blank line between them in same group.
