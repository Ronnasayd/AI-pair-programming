# PRD Template – 13 Sections

Use this template to generate consistent PRDs. Fill each section using answers from the 5-battery question framework.

---

## Section 1: Executive Summary

**Purpose:** One-paragraph overview. Who reads this: executives, investors, partners.

**Template:**

[PROJECT_NAME] is a [product type] for [target users]. It solves [key problem] by [how]. Revenue model: [business model]. MVP scope: [1 sentence]. Timeline: [weeks/months].

---

## Section 2: Product Vision & Goals

**Purpose:** Strategic direction. Why does this product exist?

**Template:**

### Vision

[1-sentence statement describing the ideal future state]

### Goals

- **Goal 1:** [What success looks like in metric X]
- **Goal 2:** [What success looks like in metric Y]
- **Goal 3:** [Strategic goal, not tactical]

---

## Section 3: Target Users & Use Cases

**Purpose:** Who is this for? What do they do with it?

**Template:**

### Primary Users

1. **Persona 1:** [Job title/role]. Pain point: [what hurts]. Needs: [top 3 needs].
2. **Persona 2:** [Different user type if applicable].

### Secondary Users

[Optional: admin, partner, etc.]

### Use Cases

- **Use Case 1:** [Actor] → [action] → [outcome]
- **Use Case 2:** [Actor] → [action] → [outcome]

---

## Section 4: MVP Feature Scope (v1.0)

**Purpose:** What ships in v1? What doesn't?

**Template:**

### Core Features (Must Have)

#### 4.1 [Feature Area 1]

- **[Feature 1a]:** [1-2 sentence description]
- **[Feature 1b]:** [1-2 sentence description]

#### 4.2 [Feature Area 2]

- **[Feature 2a]:** [description]

### Integrations & Infrastructure

#### 4.3 [Integration Category]

- **[API/service]:** [Details on what, how, why]

### Out of Scope for MVP (v1.0)

- [Feature X] — defer to v1.1
- [Feature Y] — defer to v2
- [Nice-to-have Z] — future

---

## Section 5: Technical Architecture

**Purpose:** High-level system design.

**Template:**

### Architecture Overview

[ASCII diagram or prose description]

```
┌─────────────────┐
│   Frontend      │
├─────────────────┤
│   Business Logic│
├─────────────────┤
│   Backend / APIs│
└─────────────────┘
```

### Layers & Components

- **Layer 1 (UI/Frontend):** [What, why, technologies]
- **Layer 2 (Business Logic):** [Key services, algorithms]
- **Layer 3 (Data/Backend):** [Storage, APIs, external services]

---

## Section 6: Tech Stack Decisions

**Purpose:** What tools, languages, frameworks?

**Template:**

| Layer    | Technology           | Rationale    |
| -------- | -------------------- | ------------ |
| Frontend | [React/Vue/etc]      | [Why chosen] |
| Backend  | [Node/Python/Go]     | [Why chosen] |
| Database | [PostgreSQL/MongoDB] | [Why chosen] |
| Hosting  | [AWS/GCP/Azure]      | [Why chosen] |

### Decision Trees (for TBDs)

**Decision: [Question]**

```
If [condition A]:
  → Choose [Option 1]
Else if [condition B]:
  → Choose [Option 2]
Else:
  → TBD by [date/team]
```

---

## Section 7: Data Model

**Purpose:** What data exists? How is it stored?

**Template:**

### Core Entities

```
User
├── id: UUID
├── email: string (unique)
├── name: string
└── created_at: timestamp

Content
├── id: string
├── title: string
├── owner_id: UUID (foreign key)
└── metadata: JSON
```

### Storage Strategy

- **User data:** [PostgreSQL / Cloud Firestore]
- **Sessions:** [Redis / in-memory]
- **Files:** [S3 / Cloud Storage]
- **Offline cache:** [SQLite / IndexedDB]

---

## Section 8: User Flows

**Purpose:** Step-by-step "happy path" + edge cases.

**Template:**

### Flow 1: [Main User Action]

1. User [action]
2. System [checks/validates]
3. System [executes]
4. User [sees result]

Error case: If [X] fails, show [message].

### Flow 2: [Secondary Action]

[Same structure]

---

## Section 9: Success Metrics (KPIs)

**Purpose:** How do we know if this is working?

**Template:**

### Adoption

- **Target:** [X installs/signups in month Y]
- **Retention (D7):** [percentage]
- **Retention (D30):** [percentage]

### Engagement

- **Average session length:** [minutes]
- **Feature usage:** [% of users who use feature X]
- **Repeat usage:** [% returning within 7 days]

### Monetization

- **ARPU (if applicable):** [$X per user]
- **Ad impressions:** [X per session]
- **Conversion rate (if paid):** [% converting to paid]

### Quality

- **Crash rate:** [< X%]
- **Latency:** [< X ms]
- **Availability:** [SLA: 99.X%]

---

## Section 10: Timeline & Phased Rollout

**Purpose:** When do things ship? In what order?

**Template:**

### Phase 1 (MVP) | Weeks 1–12

- **Weeks 1–3:** [Feature set A]
- **Weeks 4–6:** [Feature set B]
- **Weeks 7–9:** [Feature set C]
- **Weeks 10–12:** [Testing, bug fixes, launch]

Deliverable: [What ships at end of phase 1]

### Phase 2 | Weeks 13–20

[Same structure]

### Phase 3+ | Future

[Same structure]

---

## Section 11: Dependencies & Risks

**Purpose:** What could go wrong? What do we depend on?

**Template:**

### Critical Dependencies

- **Dependency 1:** [What it is]. Risk: [What if it breaks]. Mitigation: [How we handle it]
- **Dependency 2:** [...]

### Risk Register

| Risk     | Impact       | Probability  | Mitigation            |
| -------- | ------------ | ------------ | --------------------- |
| [Risk 1] | High/Med/Low | High/Med/Low | [What we do about it] |
| [Risk 2] | [Impact]     | [Prob]       | [Mitigation]          |

---

## Section 12: Constraints & Assumptions

**Purpose:** Boundaries and things we're taking for granted.

**Template:**

### Constraints

- **Timeline:** MVP in [N] weeks (hard constraint)
- **Budget:** [$ or team size]
- **Regulation:** [GDPR / HIPAA / none]

### Assumptions

- Assumption 1: [We assume X is true]. Impact if wrong: [Y].
- Assumption 2: [...]

---

## Section 13: Out of Scope & Appendix

**Purpose:** Explicitly what's NOT in this PRD.

**Template:**

### Out of Scope (v1.0)

- [Feature A] — defer to v1.1
- [Feature B] — defer to v2
- [Feature C] — never (antithetical to product)

### Glossary

- **Term 1:** Definition
- **Term 2:** Definition

### References

- [Link to design system, if exists]
- [Link to market research, if exists]
- [Link to competitive analysis, if exists]

### Appendix: API Reference (if applicable)

```
GET /api/users/:id
  → Returns user object
  → Auth: Bearer token

POST /api/users
  → Creates user
  → Body: { email, name }
```

---

**Template complete. Adapt sections as needed for your project type.**
