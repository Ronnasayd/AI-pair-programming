# GENERAL RECOMMENDATIONS

1. Clearly differentiate:

   - **User Story**: format “As a [actor], I want [goal] so that [benefit].”
   - **Use Case**: detailed flows (main + alternative flows).

2. **Functional Requirements**:

   - Start with an infinitive verb: “The system shall…”
   - Avoid ambiguity: replace terms like “fast” with measurable metrics (e.g., “< 2s to…”).

3. **Non-Functional Requirements** (example categories):

   - Performance, Scalability, Security, Observability, Availability, Usability, Compliance, Maintainability.

4. **Proposed Architecture**:

   - Components (e.g., Web Frontend, Backend API, Auth Service, DB, Cache, Gateway)
   - Style (REST, Event-Driven, Hexagonal, etc.)
   - External integrators (payments, notifications, etc.)

5. **APIs and Data**:

   - Only include if the PRD implies clear endpoints. Otherwise, justify their absence.

6. **Risks**:

   - Technological uncertainty, external dependencies, aggressive timelines, future scalability, compliance.

7. **Rejected Alternatives**:

   - Briefly describe and justify (e.g., “GraphQL rejected due to initial simplicity”).

8. **Traceability Matrix**:

   - Each FR must map to at least one UC or US.

9. **Ambiguities**:

   - List open questions for stakeholders.
