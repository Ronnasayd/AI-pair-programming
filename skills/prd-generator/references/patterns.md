# Project Type Patterns

Quick reference: How to adapt PRD generation for different project categories.

---

## Pattern 1: SaaS (Software as a Service)

**Examples:** Project management, CRM, analytics platform, collaboration tools

### Battery 1 Emphasis (Strategy)

- **Scope:** Typically core + management (because SaaS needs feature richness to justify subscription)
- **Users:** Multi-persona (admin, end-user, sometimes power user)
- **Timeline:** 6–12 weeks typical (not urgent, quality matters)

### Battery 2 Emphasis (Architecture)

- **State:** Often greenfield or existing codebase reuse
- **Platforms:** Web-first (responsive) + mobile (iOS/Android) phase 2
- **Monetization:** Subscription (pricing tiers, per-user, per-feature) OR freemium

### Battery 3 Emphasis (Features)

- **Features:** Core + management (search, favorites, settings, bulk actions, etc.)
- **Auth:** OAuth (GitHub, Google, Apple) OR custom SSO
- **Offline:** Cache read (no persistent offline; sync when online)

### Battery 4 Emphasis (Operations)

- **Controls:** User roles/permissions, org settings, API keys
- **Ads:** None (paid-only) OR freemium includes ads
- **Analytics:** Detailed (feature adoption, engagement funnels, cohort analysis)

### Battery 5 Emphasis (Dependencies)

- **Backend:** Complete (user management, billing/subscription, webhooks, integrations)
- **Constraints:** Stripe/payment integration, GDPR compliance, data export, SSO providers

### PRD Sections to Expand

- Section 9 (KPIs): ARPU, churn rate, CAC, LTV, NPS
- Section 10 (Timeline): Include "billing system", "onboarding", "first integration"
- Section 11 (Risks): Competitor moves, payment processor outages, user churn

### Tech Stack Typical

| Layer    | Example                              |
| -------- | ------------------------------------ |
| Frontend | React, Vue, Next.js                  |
| Backend  | Node.js, Python (Django/FastAPI), Go |
| Database | PostgreSQL (primary), Redis (cache)  |
| Auth     | Auth0, Firebase Auth, or custom JWT  |
| Payment  | Stripe, Paddle                       |
| Hosting  | AWS/GCP/Azure (VPC, managed DB)      |

---

## Pattern 2: Mobile App (Native, Cross-Platform, or Web-Based)

**Examples:** Fitness tracker, social app, IPTV player, photo editor, games

### Battery 1 Emphasis (Strategy)

- **Scope:** Core + management typical (app engagement needs features)
- **Users:** Single or dual persona (but often consumer-focused)
- **Timeline:** 3–6 months typical (mobile platform rules complex, testing extensive)

### Battery 2 Emphasis (Architecture)

- **State:** Often greenfield (new app) or wrapping existing backend
- **Platforms:** iOS + Android (simultaneous or phased), or web-responsive
- **Monetization:** Ad-supported, in-app purchase, subscription, or free

### Battery 3 Emphasis (Features)

- **Features:** Core + management (favorites, search, history, sharing, settings)
- **Auth:** Phone number (SMS), OAuth (Apple/Google), email
- **Offline:** Often full offline (full sync when online) — mobile users expect this

### Battery 4 Emphasis (Operations)

- **Controls:** Parental controls, privacy settings, content filtering, data export
- **Ads:** If present: pre-roll, banner, or rewarded video
- **Analytics:** Detailed (session tracking, crash reporting, feature usage, funnel analysis)

### Battery 5 Emphasis (Dependencies)

- **Backend:** Minimal (API for sync, auth, analytics) or complete (social, messaging, etc.)
- **Constraints:** Platform guidelines (App Store review, Google Play), device fragmentation, location services

### PRD Sections to Expand

- Section 5–6 (Architecture): Platform-specific UI/UX considerations
- Section 9 (KPIs): Downloads, DAU/MAU, retention, session length, crash rate
- Section 10 (Timeline): Include "platform certification", "app store submission", "beta testing"

### Tech Stack Typical

| Layer     | Example                                              |
| --------- | ---------------------------------------------------- |
| Frontend  | React Native, Flutter, Swift (iOS), Kotlin (Android) |
| Backend   | Node.js, Python, Go (stateless APIs)                 |
| Database  | Firebase Firestore, AWS DynamoDB, or PostgreSQL      |
| Auth      | Firebase Auth, Auth0, or OAuth providers             |
| Analytics | Firebase Analytics, Mixpanel, AppsFlyer              |
| Hosting   | Firebase, AWS Lambda, Heroku                         |

---

## Pattern 3: Backend / API / Microservice

**Examples:** Payment gateway, notification service, data pipeline, queue system, authentication service

### Battery 1 Emphasis (Strategy)

- **Scope:** Core only (backend rarely has "management" in MVP; focus on reliability)
- **Users:** Developer/engineers (internal) or third-party API consumers
- **Timeline:** 4–8 weeks typical (but with extensive testing)

### Battery 2 Emphasis (Architecture)

- **State:** Often wraps existing data or services
- **Platforms:** REST API, GraphQL, WebSockets (not "web" vs "mobile", but protocol)
- **Monetization:** Free (internal) OR per-transaction, per-request, or subscription (if public)

### Battery 3 Emphasis (Features)

- **Features:** Core only (CRUD, webhooks, batch operations, rate limiting)
- **Auth:** API keys, OAuth tokens, mTLS (mutual TLS)
- **Offline:** N/A (backend is always online); focus on retry logic, idempotency

### Battery 4 Emphasis (Operations)

- **Controls:** Rate limiting, IP whitelist, request validation, versioning
- **Ads:** N/A
- **Analytics:** Detailed (request volume, latency, error rates, throughput)

### Battery 5 Emphasis (Dependencies)

- **Backend:** Complete (database, message queue, logging, monitoring)
- **Constraints:** SLA (99.9%+), zero-downtime deployment, backwards compatibility, security (encryption, audit logs)

### PRD Sections to Expand

- Section 5–6 (Architecture): API contract, error codes, rate limiting strategy
- Section 9 (KPIs): Uptime, latency (p50, p99), error rate, throughput, cost per request
- Section 10 (Timeline): Include "API documentation", "SDK generation", "integration testing"

### Tech Stack Typical

| Layer     | Example                            |
| --------- | ---------------------------------- |
| Language  | Node.js, Python, Go, Java, Rust    |
| Framework | Express, FastAPI, Gin, Spring Boot |
| Database  | PostgreSQL, MongoDB, Cassandra     |
| Queue     | RabbitMQ, Kafka, AWS SQS           |
| Logging   | ELK Stack, Datadog, CloudWatch     |
| Hosting   | Kubernetes, AWS ECS, Heroku        |

---

## Pattern 4: Desktop / CLI Tool

**Examples:** Dev tool, IDE extension, automation CLI, system utility

### Battery 1 Emphasis (Strategy)

- **Scope:** Core + management (power users expect customization)
- **Users:** Developers/power users (single persona usually)
- **Timeline:** 4–12 weeks (depends on complexity; IDEs extensive, simple CLI minimal)

### Battery 2 Emphasis (Architecture)

- **State:** Often greenfield or wraps CLI tools
- **Platforms:** macOS, Linux, Windows (all three or subset)
- **Monetization:** Free (open source), paid license, or freemium

### Battery 3 Emphasis (Features)

- **Features:** Core + management (profiles, plugins, telemetry, themes)
- **Auth:** GitHub OAuth, local keys, or none
- **Offline:** Full offline (desktop works without internet typically)

### Battery 4 Emphasis (Operations)

- **Controls:** Telemetry opt-out, config location, profile management
- **Ads:** None typically
- **Analytics:** Detailed (command usage, feature adoption, error tracking)

### Battery 5 Emphasis (Dependencies)

- **Backend:** Minimal (cloud sync optional, telemetry, update checks)
- **Constraints:** Package managers (Homebrew, npm, Chocolatey), auto-updates, cross-platform consistency

### PRD Sections to Expand

- Section 5–6 (Architecture): CLI vs GUI, plugin system
- Section 9 (KPIs): Downloads, daily active users, feature adoption, GitHub stars
- Section 10 (Timeline): Include "package manager registration", "auto-update testing"

### Tech Stack Typical

| Layer        | Example                                    |
| ------------ | ------------------------------------------ |
| Frontend     | Electron (desktop), Ink (TUI)              |
| Backend      | Node.js, Python, Rust                      |
| Database     | SQLite (local) or none                     |
| Distribution | npm, Homebrew, Chocolatey, GitHub Releases |
| Hosting      | GitHub, S3 (for updates)                   |

---

## Pattern 5: Web App (Browser-Based)

**Examples:** Dashboard, web editor, productivity tool, data visualizer

### Battery 1 Emphasis (Strategy)

- **Scope:** Core + management (web users expect interactivity)
- **Users:** Often multi-persona (admin + end-user)
- **Timeline:** 6–12 weeks (web is flexible; iteration fast)

### Battery 2 Emphasis (Architecture)

- **State:** Greenfield or existing system integration
- **Platforms:** Web (responsive), PWA (offline capable), or web-only
- **Monetization:** Subscription, ads, freemium, or free

### Battery 3 Emphasis (Features)

- **Features:** Core + management (search, filters, favorites, notifications, exports)
- **Auth:** OAuth, SAML (enterprise), or custom
- **Offline:** Optional (PWA cache, or online-only)

### Battery 4 Emphasis (Operations)

- **Controls:** User roles, permissions, audit logs, data export
- **Ads:** If present: contextual or unobtrusive
- **Analytics:** Detailed (heatmaps, session recording, funnel analysis)

### Battery 5 Emphasis (Dependencies)

- **Backend:** Usually complete (user management, data persistence, real-time sync)
- **Constraints:** GDPR, WCAG accessibility, browser compatibility, SEO (if public-facing)

### PRD Sections to Expand

- Section 5–6 (Architecture): Frontend framework, state management, API design
- Section 9 (KPIs): Page load time, bounce rate, user session length, conversion
- Section 10 (Timeline): Include "accessibility audit", "SEO optimization", "PWA setup"

### Tech Stack Typical

| Layer      | Example                                           |
| ---------- | ------------------------------------------------- |
| Frontend   | React, Vue, Angular, Svelte                       |
| Backend    | Node.js, Python, Go, Java                         |
| Database   | PostgreSQL, MongoDB                               |
| Hosting    | Vercel, Netlify (frontend) + Heroku/AWS (backend) |
| Monitoring | Sentry, DataDog, New Relic                        |

---

## Cross-Cutting Considerations

### Regulatory / Compliance

If any of these apply, add Battery 5.5 (Compliance):

- **GDPR:** EU user data, right to deletion, data exports
- **HIPAA:** Healthcare data, audit logs, encryption
- **PCI-DSS:** Payment processing, card data handling
- **SOC2:** Security, access controls, incident response
- **CCPA:** California user privacy, opt-out mechanisms

PRD Section to add: **Section 12.1 — Compliance & Legal** detailing requirements.

### Enterprise / B2B

If selling to enterprises (not consumers):

- Add Battery 2 detail: **Multi-tenant** support? **White-label** capability?
- Battery 4: Add SSO (SAML, OIDC), role-based access control (RBAC), audit trails
- Section 9 (KPIs): Contract value, enterprise NPS, onboarding time, support tickets
- Section 10 (Timeline): Add "enterprise security review", "compliance certification"

### Open Source

If open-sourcing:

- Section 13: Add governance (how decisions made), contribution guidelines, license (MIT, Apache 2.0, GPL, etc.)
- Section 11 (Risks): Community burnout, security vulnerabilities in dependencies
- Section 9 (KPIs): GitHub stars, contributors, issue response time

---

## Decision Matrix: Which Pattern Fits?

| Project Type            | Primary Pattern  | Backup Patterns |
| ----------------------- | ---------------- | --------------- |
| Slack-like app          | SaaS + Mobile    | Web App         |
| Shopify integration     | Backend/API      | SaaS            |
| Figma alternative       | Web App          | Desktop         |
| npm package             | Backend/API      | CLI Tool        |
| Notion competitor       | SaaS             | Web App         |
| GitHub Actions workflow | CLI Tool         | Backend/API     |
| Spotify clone           | Mobile + Backend | Web App         |
| AWS cost analyzer       | Web App          | CLI Tool        |
| Stripe competitor       | Backend/API      | SaaS            |
| Obsidian plugin         | Desktop/CLI      | Web App         |

---

**End of Patterns. Use above as quick reference when filling PRD sections.**
