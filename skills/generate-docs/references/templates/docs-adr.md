# ADR Format

## Template

```md
# ADR-NNN – <Short Decision Title>

> **Date:** YYYY-MM-DD
> **Status:** <!-- Proposed | Accepted | Superseded by ADR-XXX | Obsolete -->
> **Deciders:** <!-- Names or role titles of the people who made this decision -->

## Context

<!-- What is the issue or opportunity that prompted this decision?
     Describe the forces at play: technical constraints, business requirements, team limitations.
     Be objective — do NOT advocate for any solution yet.
     Do NOT include implementation code or detailed technical specs. -->

## Decision

<!-- What was decided? State it clearly in 1–3 sentences.
     Focus on the INTENT and RATIONALE — not the implementation mechanism.
     The codebase itself captures implementation details. -->

## Considered Alternatives

<!-- List the options that were seriously evaluated.
     For each, give a brief description and honest pros/cons.
     Include the rejected options — explain why they were not chosen. -->

| Alternative | Pros         | Cons         |
| ----------- | ------------ | ------------ |
| <Option A>  | <!-- ... --> | <!-- ... --> |
| <Option B>  | <!-- ... --> | <!-- ... --> |

## Consequences

<!-- What are the positive and negative consequences of this decision?
     What becomes easier? What becomes harder or constrained?
     What risks are introduced and how are they mitigated? -->

## Related ADRs

<!-- Optional. Links to other ADRs that this one supersedes, depends on, or relates to. -->

```

That's it. An ADR can be a single paragraph. The value is in recording *that* a decision was made and *why* — not in filling out sections.

## Optional sections

Only include these when they add genuine value. Most ADRs won't need them.

- **Status** frontmatter (`proposed | accepted | deprecated | superseded by ADR-NNNN`) — useful when decisions are revisited
- **Considered Alternatives** — only when the rejected alternatives are worth remembering
- **Consequences** — only when non-obvious downstream effects need to be called out

## Numbering

Scan `docs/adr/` for the highest existing number and increment by one.

## When to offer an ADR

All three of these must be true:

1. **Hard to reverse** — the cost of changing your mind later is meaningful
2. **Surprising without context** — a future reader will look at the code and wonder "why on earth did they do it this way?"
3. **The result of a real trade-off** — there were genuine alternatives and you picked one for specific reasons

If a decision is easy to reverse, skip it — you'll just reverse it. If it's not surprising, nobody will wonder why. If there was no real alternative, there's nothing to record beyond "we did the obvious thing."

### What qualifies

- **Architectural shape.** "We're using a monorepo." "The write model is event-sourced, the read model is projected into Postgres."
- **Integration patterns between contexts.** "Ordering and Billing communicate via domain events, not synchronous HTTP."
- **Technology choices that carry lock-in.** Database, message bus, auth provider, deployment target. Not every library — just the ones that would take a quarter to swap out.
- **Boundary and scope decisions.** "Customer data is owned by the Customer context; other contexts reference it by ID only." The explicit no-s are as valuable as the yes-s.
- **Deliberate deviations from the obvious path.** "We're using manual SQL instead of an ORM because X." Anything where a reasonable reader would assume the opposite. These stop the next engineer from "fixing" something that was deliberate.
- **Constraints not visible in the code.** "We can't use AWS because of compliance requirements." "Response times must be under 200ms because of the partner API contract."
- **Rejected alternatives when the rejection is non-obvious.** If you considered GraphQL and picked REST for subtle reasons, record it — otherwise someone will suggest GraphQL again in six months.
