# Universal Rules Integration (kuro-rules)

Integrate new technical standards, security protocols, and pedagogical mandates into the master `kuro-rules` repository and sync them with the `Alarmify` project.

## User Review Required

> [!IMPORTANT]
> This update adds several high-level technical requirements (CodeQL, SonarQube, Fuzzing, Locust, Stryker) that may require significant infrastructure setup if not already present.

- **Fuzzing (AFL)**: Added as a mandatory testing step for critical paths.
- **Mutation Testing (Stryker)**: Added to ensure test quality.
- **Policy as Code**: Integrated into the security section.
- **Reversibility Principle**: New architectural mandate to ensure designs can be unwound or pivoted.

## Proposed Changes

### [kuro-rules]

Summary: Update master rule files to include the new user-specified standards.

#### [MODIFY] [.cursorrules](file:///home/kuro/Documents/kuro-rules/.cursorrules)
- Update "Technical Standards" with Profile/Complexity and Reversibility mandates.
- Update "Testing" section (or add it) with Fuzzing, Locust, and Stryker.
- Update "Pedagogical Protocol" with "Understandable Comments".

#### [MODIFY] [AI_GUIDELINES.md](file:///home/kuro/Documents/kuro-rules/AI_GUIDELINES.md)
- Add "CI/CD & Analysis" section (CodeQL, SonarQube, Codacy).
- Add "Advanced Testing" section (AFL, Locust, Stryker).
- Enhance "Security Hardening" with `security.md`, security policies, and "Policy as Code".
- Enhance "Architectural Principles" with "Reversibility Principle" and complexity indexing.

---

### [Alarmify]

Summary: Sync the updated rules to the local project.

#### [MODIFY] [.cursorrules](file:///home/kuro/Documents/Alarmify/.cursorrules)
- Sync with kuro-rules.

#### [MODIFY] [AI_GUIDELINES.md](file:///home/kuro/Documents/Alarmify/AI_GUIDELINES.md)
- Sync with kuro-rules.

## Verification Plan

### Automated Tests
- Static analysis check (linting) on the updated rule files for markdown consistency.
- Verify sync success by comparing checksums or manual diffing.

### Manual Verification
- Verify that the new rules are visible and clearly categorized in both `kuro-rules` and `Alarmify`.
- Confirm "Policy as Code" and "Reversibility Principle" are correctly defined in the text.
