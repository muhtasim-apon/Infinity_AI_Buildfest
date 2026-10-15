# Security tests

Automated: `test_*.py` (one file per threat in `docs/security/threat-model.md`). Red-team: `red_team_cases.md`.
Scanners: Bandit (`bandit -r services/api/app -ll`), pip-audit, npm audit, gitleaks, and OWASP ZAP baseline
against **staging only**:
`docker run -t ghcr.io/zaproxy/zaproxy:stable zap-baseline.py -t https://<staging-web>.onrender.com -r zap.html`
Never scan systems we do not own (Congress §20.11).
