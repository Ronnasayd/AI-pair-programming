---
name: prd-get-implicit-requirements
description: 'Extract implicit requirements from product requirement documents (PRDs), identify coverage gaps across 14 universal categories, and generate clarification questions for stakeholders. Use when user says "analyze PRD for gaps", "extract implicit requirements", "find missing requirements", "what''s not defined in our spec", "identify PRD holes", or "get clarification questions from PRD". Systematically covers: interface states, error handling, navigation, data persistence, network behavior, security, performance, platform behavior, content fallbacks, localization, accessibility, legal compliance, deployment, and observability. Do NOT use for creating PRDs (use tlc-spec-driven), technical design documents, architectural decisions, or test planning.'
---

### Phase 1 — Structured Reading

1. Read the entire PRD without taking notes
2. Identify: **product type**, **target platforms**, **external integrations**, **MVP scope**
3. List domains explicitly covered
4. Note what is explicitly out of scope

> Exit criterion: be able to describe the product in 2 sentences and list its main flows.

---

### Phase 2 — Gap Analysis by Universal Category

For each category, ask: _"Does the PRD define behavior for this scenario?"_

#### 2.1 Interface States

- What should be displayed while data is loading?
- What should be displayed when a list/result is empty?
- What should be displayed when an operation fails?
- Is there a skeleton screen, spinner, or placeholder?

#### 2.2 Error Handling

- What happens when each external integration fails?
- Is there automatic retry? With what policy (exponential backoff, retry limit)?
- Are errors shown to the user or handled silently?
- Is there a fallback when a service is unavailable?

#### 2.3 Navigation and Flow

- What happens when the user presses "back" on each screen?
- Is screen state preserved when navigating away and returning?
- Is deep linking / direct URL access supported?
- What happens if the user reaches a non-existent route?

#### 2.4 Data and Persistence

- What is the cache TTL for each data type?
- How are schema migrations handled during version upgrades?
- What is the maximum allowed local storage size?
- What happens when storage is full?

#### 2.5 Network and Connectivity

- Offline behavior: block, degrade gracefully, or operate from cache?
- Timeouts by request type?
- HTTP vs HTTPS — which is allowed and where?
- What happens if the connection drops during a critical operation?

#### 2.6 Security

- Sensitive data: where and how is it stored?
- Does the session expire? What happens if it expires during active use?
- What can be captured (screenshots, clipboard, logs)?
- Input validation: where does it occur (client, server, both)?

#### 2.7 Performance

- Volume limits: how many items can a list contain before pagination/virtualization is required?
- Heavy assets (images, videos): how should they be cached and what is the maximum size?
- Long-running operations: is progress feedback provided?
- What is the acceptable timeout per operation before displaying an error?

#### 2.8 Platform Behavior

- Which system permissions are required?
- How does the product behave when moving to background/foreground?
- Screen orientation: locked or free?
- Do system notifications interfere? How should they be handled?

#### 2.9 Missing or Invalid Content

- Image/asset fails to load: what fallback is used?
- Optional data missing: hide the field or show a placeholder?
- Content expired or removed at the source: what should be displayed?

#### 2.10 Localization and Internationalization

- Date, time, currency, and number formats: follow device locale or fixed format?
- Support for RTL languages (Arabic, Hebrew)?
- Are pluralizable strings handled correctly?
- User-generated content: expected encoding?

#### 2.11 Accessibility

- Are screen readers supported?
- Minimum touch target / interactive element size?
- Is minimum color contrast defined?
- Is keyboard or remote control navigation required?

#### 2.12 Legal and Compliance

- Does data collection require explicit consent (GDPR, LGPD, CCPA)?
- Is the privacy policy accessible within the product?
- Are terms of use shown before critical actions?
- Is age classification required for distribution?

#### 2.13 Deployment and Distribution

- Delivery format (bundle, package, container, binary)?
- Maximum artifact size?
- Is code obfuscation or protection required?
- Update process: manual, automatic, OTA?

#### 2.14 Observability

- Which error events are logged?
- Do logs contain PII? How is it handled?
- Is crash reporting enabled by default?
- Are performance metrics collected?

---

**Output of this phase:** Raw list of gaps by category, with severity:

- **Critical** — blocks development, distribution, or poses legal risk
- **Important** — impacts architecture or core UX
- **Nice-to-have** — refinement detail

---

### Phase 3 — Triage Before Asking

Before bringing a gap to the user, apply this filter:

| Condition                                 | Action                                   |
| ----------------------------------------- | ---------------------------------------- |
| Clear platform convention exists          | Document the default, do not ask         |
| Decision affects architecture             | Ask before any implementation            |
| Decision blocks deployment/store approval | Highest priority in round 1              |
| Decision is purely visual/cosmetic        | Use best practice; ask only if uncertain |
| Explicitly out of MVP scope               | Record as deferred, do not ask           |

---

### Phase 4 — User Elicitation

Group questions into **thematic rounds** of 3–4 questions each:

- **Round 1:** Critical issues (security, legal, architecture blockers)
- **Round 2:** Core UX and main flows
- **Round 3:** Details (formats, fallbacks, edge-case behaviors)

Each question should include:

- One-line context (why it matters)
- 2–4 options with consequences described, not just names
- Recommended option marked when a best practice exists

---

### Phase 5 — Document Decisions in the PRD

Entry format:

```markdown
#### [ID] Title

- **Decision:** what was decided
- **Behavior:** exact behavior expected from the system
- **Rationale:** reason for the choice
- **Deferred:** what was excluded and to which version/phase
```

Where to insert:

- PRDs with an Appendix → implicit decisions section (e.g., `Appendix C`)
- Simple PRDs → `## Implicit Requirements` section before the Glossary
- Number sequentially for traceability

---

### Phase 6 — Completion Checklist

- [ ] Every critical gap has a documented decision
- [ ] No decision contradicts the PRD's explicit scope
- [ ] Deferred decisions have a target version
- [ ] PRD revision date has been updated
- [ ] Development team has been notified of additions

---

### Pocket Heuristics

> If the PRD defines **what** but does not define **what happens when it fails** → gap.

> If the PRD defines a **feature** but does not define **empty state + error state + loading state** → 3 gaps.

> If the product runs on a **specific platform** and the PRD does not mention native platform behaviors → integration gaps.

> If the product **collects data** and the PRD does not mention consent → legal gap.
