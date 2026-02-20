# Security Policy — Alarmify (Charmed)

## Policy as Code & Governance
This project follows the **Policy as Code** principle. Security compliance and governance are automated where possible.

## 🔒 Security Hardening — Mandatory Standards
1.  **Secrets Management**: Never log, print, or commit API keys, tokens, or secrets. Use environment variables defined in `.env` (git-ignored).
2.  **Input Validation**: Always validate and sanitize user input to prevent injection attacks.
3.  **Path Traversal**: Protect against path traversal; no unauthorized file access.
4.  **Static Analysis**: CI/CD must include **CodeQL**, **SonarQube**, and **Codacy** for deep analysis.
5.  **Security Scanning**: Run `bandit` and `safety` before every commit/PR.

## 🧪 Advanced Security Testing
- **Fuzzing (AFL)**: Perform fuzz testing on critical parser or data-handling paths.
- **Load Testing (Locust.io)**: Conduct load tests to verify performance stability.
- **Mutation Testing (Stryker)**: Verify test suite efficacy by injecting faults.

## Reporting a Vulnerability
If you discover a security vulnerability within this project, please open a GitHub Issue or contact the maintainer directly.
