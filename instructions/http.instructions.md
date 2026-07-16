---
description: REST API design rules — resource-based routes, HTTP verbs over action verbs, kebab-case plural resource names, max 3 nesting levels, JSON payloads, status code table (200/201/422/500). Apply when designing or reviewing HTTP endpoints/routes/controllers. Do NOT use for non-HTTP code style (see code.instructions.md) or OpenAPI doc generation (see openapi.instructions.md).
applyTo: "**/*.md"
---

# HTTP API Standards

## Quick rules

| Rule                                                       | ✅ Good                  | ❌ Bad                                                 |
| ---------------------------------------------------------- | ------------------------ | ------------------------------------------------------ |
| Resources, not actions — HTTP verb expresses the operation | `POST /users`            | `POST /createNewUser`                                  |
| kebab-case for compound resource names                     | `/product-categories`    | `/productCategories`, `/product_categories`            |
| Plural resource names                                      | `/users`, `/orders`      | `/user`, `/order`                                      |
| Max 3 levels of nested resources                           | `/orders/:orderId/items` | `/users/:userId/orders/:orderId/items/:itemId/reviews` |

## REST verbs

```
GET    /users          → list users
GET    /users/:id      → get a specific user
POST   /users          → create a user
PUT    /users/:id      → replace a user
PATCH  /users/:id      → partial update a user
DELETE /users/:id      → delete a user
```

## Deep nesting → flatten with query params

```
✅ GET /reviews?itemId=123
❌ GET /users/:userId/orders/:orderId/items/:itemId/reviews
```

## JSON only for request/response payloads

```http
POST /users
Content-Type: application/json

{ "name": "Jane Doe", "email": "jane@example.com" }
```

## HTTP Status Codes

| Code                        | When to Use                                                                        |
| --------------------------- | ---------------------------------------------------------------------------------- |
| `200 OK`                    | Successful request (GET, PUT, PATCH, DELETE).                                      |
| `201 Created`               | Resource successfully created (POST).                                              |
| `422 Unprocessable Entity`  | Business rule violation or domain validation error (e.g., "email already in use"). |
| `500 Internal Server Error` | Unexpected server error not caused by the client.                                  |

```ts
// ✅ business rule violation → 422
if (existing) return res.status(422).json({ error: "Email already in use" });

// ✅ unexpected error → 500 (global handler)
app.use((err, req, res, next) =>
  res.status(500).json({ error: "Internal server error" })
);

// ❌ do not return 400 for business rule errors
// ❌ do not return 200 with an error body
```
