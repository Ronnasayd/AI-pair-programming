# Backend Test Templates

Reference templates for `test-typescript-node-backend.instructions.md`. Copy and adapt.

## File Organization

```
src/modules/<feature>/
├── tests/                          # For service/business logic tests
│   ├── <feature>.service.test.ts
│   ├── <feature>.controller.test.ts
│   ├── <feature>.mappers.test.ts
│   └── utils.test.ts
└── __tests__/                      # For isolated unit tests (utilities)
    └── <feature>-utils.test.ts
```

## Controller — Integration with Supertest

```typescript
import request from "supertest";
import app from "@/src/app";
import { PATHS } from "@/src/common/paths";
import prisma from "@/src/lib/prisma";
import { UserService } from "../user/user.service";
import { AuthService } from "../auth/auth.service";

describe("Team Controller - Integração com DB real", () => {
  let adminAccessToken: string;

  beforeEach(async () => {
    await prisma.team.deleteMany();
    await prisma.refreshToken.deleteMany();
    await prisma.user.deleteMany();

    const adminUser = await UserService.create({
      username: "admin@example.com",
      password: "password123",
      name: "Admin User"
    });

    const tokenResult = await AuthService.login({
      username: adminUser.username,
      password: "password123"
    });
    adminAccessToken = tokenResult.accessToken;
  });

  it("deve criar um time com sucesso", async () => {
    const res = await request(app)
      .post(PATHS.TEAMS.CREATE.path)
      .set("Authorization", `Bearer ${adminAccessToken}`)
      .send({ name: "Tech Team" });

    expect(res.statusCode).toBe(201);
    expect(res.body).toHaveProperty("id");
    expect(res.body.name).toBe("Tech Team");
  });
});
```

## Controller — Request/Response Mock Pattern (when integration isn't feasible)

```typescript
import { Request, Response } from "express";
import { jest } from "@jest/globals";

describe("ResourceController", () => {
  let req: Partial<Request>;
  let res: Partial<Response>;
  let json: jest.Mock;
  let status: jest.Mock;

  beforeEach(() => {
    jest.clearAllMocks();
    json = jest.fn();
    status = jest.fn().mockReturnValue({ json });
    req = {
      body: {},
      params: {},
      query: {},
      user: { userId: "test-user-id" } as any
    };
    res = { json: json as any, status: status as any };
  });

  it("deve criar um recurso", async () => {
    req.body = { name: "Test Resource" };
    await ResourceController.create(req as Request, res as Response);
    expect(status).toHaveBeenCalledWith(201);
    expect(json).toHaveBeenCalledWith(
      expect.objectContaining({ name: "Test Resource" })
    );
  });
});
```

## Service — Integration with SQLite

```typescript
describe("ResourceService - Integração com SQLite", () => {
  let userId: string;

  beforeEach(async () => {
    await prisma.resource.deleteMany();
    await prisma.user.deleteMany();
    const user = await prisma.user.create({
      data: { username: "testuser", password: "password123", name: "Test User" }
    });
    userId = user.id;
  });

  it("deve criar um recurso com sucesso", async () => {
    const data: CreateResourceRequestDTO = { ... };
    externalApiClientMock.createResource.mockResolvedValue(100); // mock only external services
    const result = await ResourceService.create(data, externalApiClientMock as any);

    expect(result).toBeDefined();
    expect(result.name).toBe(data.name);
    const found = await prisma.resource.findUnique({ where: { id: result.id } });
    expect(found).not.toBeNull();
  });
});
```

## Mock Management

```typescript
// Centralized mock file: src/lib/external-api.client.mock.ts
export const externalApiClientMock = {
  createResource: jest.fn(),
  updateResource: jest.fn(),
  deleteResource: jest.fn()
};

// In test file
beforeEach(() => {
  jest.clearAllMocks();
  externalApiClientMock.createResource.mockResolvedValue(100);
});
```

```typescript
// Logger — mock to reduce console noise
jest.mock("@/src/utils/logger");
beforeEach(() => {
  jest.spyOn(logger, "info").mockImplementation();
  jest.spyOn(logger, "warn").mockImplementation();
  jest.spyOn(logger, "error").mockImplementation();
});
afterEach(() => jest.restoreAllMocks());
```

```typescript
// File system — mock when necessary
jest.mock("fs");
import fs from "fs";
beforeEach(() => {
  (fs.readFileSync as jest.Mock).mockReturnValue("mock CSV content");
  (fs.existsSync as jest.Mock).mockReturnValue(true);
});
```

## Error Testing

```typescript
it("deve retornar erro ao criar usuário duplicado", async () => {
  await UserService.create({
    username: "duplicado@teste.com",
    password: "123456",
    name: "João"
  });
  await expect(
    UserService.create({
      username: "duplicado@teste.com",
      password: "123456",
      name: "João"
    })
  ).rejects.toThrow(APIError);
});

it("deve retornar erro 404 quando recurso não existe", async () => {
  await expect(ResourceService.findById("non-existent-id")).rejects.toThrow(
    new APIError("Recurso não encontrado", 404)
  );
});
```

## Helper Functions

```typescript
/**
 * Generates test dates dynamically so tests don't break when hardcoded dates expire.
 */
function generateTestDateSequence(
  startDaysFromNow: number,
  intervalDays: number,
  count: number
): Date[] {
  const baseDate = new Date();
  baseDate.setDate(baseDate.getDate() + startDaysFromNow);
  baseDate.setHours(10, 0, 0, 0);
  return Array.from({ length: count }, (_, i) => {
    const date = new Date(baseDate);
    date.setDate(date.getDate() + i * intervalDays);
    return date;
  });
}

/**
 * Creates a test user with admin privileges.
 * @param overrides - Optional fields to override default user data
 * @returns User object with generated access token
 */
async function createAdminUser(overrides = {}) {
  const user = await UserService.create({
    username: "admin@test.com",
    password: "password123",
    name: "Admin",
    ...overrides
  });
  const role = await RoleService.create({ name: "SYSTEM_ADMIN" });
  await AccessControlService.create({
    user_id: user.id,
    role_id: role.id,
    team_id: null
  });
  return user;
}
```

## CSV / Bulk Import

```typescript
describe("Resource CSV Import", () => {
  beforeEach(async () => {
    await prisma.importJobLine.deleteMany();
    await prisma.importJob.deleteMany();
    await prisma.resource.deleteMany();
    jest.clearAllMocks();
  });

  it("deve importar recursos via CSV com sucesso", async () => {
    const mockCSVContent = `Name,Description,Type,StartDate,Duration\nResource 1,Desc 1,user,2026-02-10T10:00:00,60`;
    (fs.readFileSync as jest.Mock).mockReturnValue(mockCSVContent);

    const result = await ResourceService.importFromCSV({
      filePath: "test.csv",
      userId
    });

    expect(result.importedCount).toBe(1);
    expect(result.errors).toHaveLength(0);
    const resources = await prisma.resource.findMany();
    expect(resources).toHaveLength(1);
  });
});
```

## Auth / Protected Routes

```typescript
describe("Protected Routes", () => {
  it("deve retornar 401 sem token", async () => {
    const res = await request(app).get(PATHS.TEAMS.LIST.path);
    expect(res.statusCode).toBe(401);
  });

  it("deve retornar 403 sem permissão", async () => {
    const normalUser = await UserService.create({
      username: "normal@example.com",
      password: "password123",
      name: "Normal User"
    });
    const tokenResult = await AuthService.login({
      username: normalUser.username,
      password: "password123"
    });
    const res = await request(app)
      .post(PATHS.TEAMS.CREATE.path)
      .set("Authorization", `Bearer ${tokenResult.accessToken}`)
      .send({ name: "New Team" });
    expect(res.statusCode).toBe(403);
  });
});
```

## Running Tests

```bash
yarn test:prepare                                   # generates schema.test.prisma
yarn test                                            # run all
yarn test:watch                                      # watch mode
yarn test src/modules/user/user.service.test.ts       # single file
yarn test --coverage                                  # with coverage
```
