<instructions>

You will follow an **iterative process of 3 cycles** (you may shorten it if quality is already high):

### CYCLE 1 – INITIAL DRAFT:

- Generate the initial version of the SRS (**minimum viable complete**).
- Mark uncertainties with the tag **TODO:?** within the body.

### CYCLE 2 – CRITIQUE:

- Generate an **internal section** (not included in the final SRS) performing an audit that evaluates:

  - Coverage of functionalities declared in the PRD
  - Completeness of use case flows
  - Clarity and testability of requirements
  - Traceability (UC/US → FR → NFR)
  - Terminology consistency
  - Gaps (PRD items not mapped)
  - Untreated risks

- **DO NOT display the SRS text here**, only the structured critique.

### CYCLE 3 – REVISION:

- Adjust the SRS by resolving and removing **TODO:?** items.
- Complete missing requirements.
- Ensure each FR references at least one UC or US.
- Optimize language for testability (avoid vague adjectives).

---

### FINAL DELIVERY:

- **Only** the revised final version of the SRS
  (without showing the critique or the raw draft).

---

### Standardization:

- UC-<n>, FR-<module>-<n>, NFR-<category>-<n>, US-<n>
- Matrix: table (US / UC / FR / NFR (if applicable))

---

### INPUTS:

**PRD:**
{{PRD_DOCUMENTO}}

**STRUCTURE:**
{{ESTRUTURA_SRS}}

**Additional Contexts (optional):**
{{CONTEXTOS_ADICIONAIS}}

**Technical Constraints (optional):**
{{RESTRICOES}}

**Stakeholders (optional):**
{{STAKEHOLDERS}}

**Strategic Objectives (optional):**
{{OBJETIVOS}}

---

Now internally execute the **3 cycles** and deliver **only the final revised SRS**.

</instructions>
