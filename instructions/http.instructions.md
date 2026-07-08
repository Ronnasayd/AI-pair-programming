---
description: REST API design rules — resource-based routes, HTTP verbs over action verbs, kebab-case plural resource names, max 3 nesting levels, JSON payloads, status code table (200/201/422/500). Apply when designing or reviewing HTTP endpoints/routes/controllers. Do NOT use for non-HTTP code style (see code.instructions.md) or OpenAPI doc generation (see openapi.instructions.md).
applyTo: "**/*"
---

# HTTP API Standards

## Follow REST Conventions

Design APIs around resources, not actions. Use HTTP methods to express the operation.

```
✅ GET    /users          → list users
✅ GET    /users/:id      → get a specific user
✅ POST   /users          → create a user
✅ PUT    /users/:id      → replace a user
✅ PATCH  /users/:id      → partial update a user
✅ DELETE /users/:id      → delete a user

❌ POST /getUser
❌ POST /createNewUser
❌ GET  /deleteUser/:id
```

---

## Use kebab-case for Compound Resource Names

```
✅ /user-profiles
✅ /product-categories
✅ /order-items

❌ /userProfiles
❌ /ProductCategories
❌ /order_items
```

---

## Use Plural Resource Names

```
✅ /users
✅ /orders
✅ /product-categories

❌ /user
❌ /order
❌ /product-category
```

---

## Avoid More Than 3 Levels of Nested Resources

Deeply nested URLs are hard to maintain and read. Flatten or rethink the resource design.

```
✅ /users/:userId/orders
✅ /orders/:orderId/items

❌ /users/:userId/orders/:orderId/items/:itemId/reviews
```

If access to deeply nested resources is required, consider a flat endpoint with query parameters:

```
✅ GET /reviews?itemId=123
```

---

## Use JSON for Request and Response Payloads

All request bodies and responses must use `application/json`.

```http
POST /users
Content-Type: application/json

{
  "name": "Jane Doe",
  "email": "jane@example.com"
}
```

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "id": "abc123",
  "name": "Jane Doe",
  "email": "jane@example.com"
}
```

---

## HTTP Status Codes

| Code                        | When to Use                                                                        |
| --------------------------- | ---------------------------------------------------------------------------------- |
| `200 OK`                    | Successful request (GET, PUT, PATCH, DELETE).                                      |
| `201 Created`               | Resource successfully created (POST).                                              |
| `422 Unprocessable Entity`  | Business rule violation or domain validation error (e.g., "email already in use"). |
| `500 Internal Server Error` | Unexpected server error not caused by the client.                                  |

```ts
// ✅ Good — business rule violation returns 422
app.post("/users", async (req, res) => {
  const existing = await userService.findByEmail(req.body.email);
  if (existing) {
    return res.status(422).json({ error: "Email already in use" });
  }
  const user = await userService.create(req.body);
  return res.status(201).json(user);
});

// ✅ Good — unexpected error returns 500
app.use((err, req, res, next) => {
  console.error(err);
  res.status(500).json({ error: "Internal server error" });
});

// ❌ Bad — returning 400 for business rule errors
// ❌ Bad — returning 200 with an error body
```
