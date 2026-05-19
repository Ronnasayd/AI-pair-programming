# API Endpoints

> **Audience:** Frontend developers, API integrators, external consumers

## Overview

<!-- What API style is used? (REST, GraphQL, gRPC, WebSocket, etc.)
     What is the base URL structure for each environment (local, staging, production)?
     What authentication mechanism is required?
     2–4 sentences — no internal implementation references. -->

## Authentication

<!-- How do consumers authenticate?
     Describe the mechanism (e.g., Bearer token, API key, OAuth2 flow) and
     where credentials are obtained.
     Show only the request header shape — do NOT reference internal auth code. -->

```http
Authorization: Bearer <token>
```

## Resource Groups

<!-- Organise endpoints by resource or domain area. One subsection per group.
     Each group should represent a cohesive set of operations on a single concept.
     Do NOT describe internal controllers, services, or middleware. -->

### <Resource Group Name>

<!-- Brief description of what this group of endpoints covers and who uses them. -->

| Method | Path            | Description                          | Auth Required |
| ------ | --------------- | ------------------------------------ | :-----------: |
| GET    | `/resource`     | List resources with optional filters |      ✅       |
| GET    | `/resource/:id` | Get a single resource by ID          |      ✅       |
| POST   | `/resource`     | Create a new resource                |      ✅       |
| PUT    | `/resource/:id` | Replace a resource                   |      ✅       |
| PATCH  | `/resource/:id` | Partially update a resource          |      ✅       |
| DELETE | `/resource/:id` | Remove a resource                    |      ✅       |

#### Request / Response Shape

<!-- Show representative example payloads using realistic values.
     Use JSON comments (`//`) to explain field meanings.
     Do NOT reference internal DTOs, validators, serializers, or ORM models. -->

**Request body (POST/PUT/PATCH):**

```json
{
  "field": "example value"
}
```

**Success response:**

```json
{
  "id": "abc-123",
  "field": "example value"
}
```

---

<!-- Repeat the ### Resource Group pattern for every resource group in the API. -->

## Common Query Parameters

<!-- Parameters that apply across multiple endpoints (pagination, filtering, sorting). -->

| Parameter | Type    | Description             | Default |
| --------- | ------- | ----------------------- | ------- |
| `page`    | integer | Page number (1-indexed) | `1`     |
| `limit`   | integer | Results per page        | `20`    |

## Error Codes

<!-- Standard error responses returned by the API.
     Describe the MEANING of each code — not how the error is generated internally. -->

| Status | Code/Key        | Meaning                             | When It Occurs                              |
| ------ | --------------- | ----------------------------------- | ------------------------------------------- |
| 400    | `INVALID_INPUT` | Request body failed validation      | Missing required fields or wrong types      |
| 401    | `UNAUTHORIZED`  | Missing or invalid credentials      | No token, expired token                     |
| 403    | `FORBIDDEN`     | Authenticated but not authorised    | Insufficient permissions for the resource   |
| 404    | `NOT_FOUND`     | Resource does not exist             | ID not found or deleted                     |
| 409    | `CONFLICT`      | State conflict                      | Duplicate creation, concurrent modification |
| 422    | `UNPROCESSABLE` | Input valid but cannot be processed | Business rule violation                     |
| 429    | `RATE_LIMITED`  | Too many requests                   | Exceeded request quota                      |
| 500    | `SERVER_ERROR`  | Unexpected internal error           | Unhandled exception (check server logs)     |

## Rate Limits and Quotas

<!-- Optional — include only if rate limiting is enforced.
     State limits in user-facing terms (requests per minute, per token, per plan). -->
