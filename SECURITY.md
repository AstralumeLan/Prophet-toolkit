# Security policy

## Supported versions

| Version | Security fixes |
| --- | --- |
| 0.1.x | Supported |
| Earlier releases | Unsupported |

## Reporting a vulnerability

Use [GitHub private vulnerability reporting](https://github.com/AstralumeLan/prophet-toolkit/security/advisories/new).
If the form is unavailable, open a minimal GitHub issue asking to enable private reporting;
do not include exploit details or sensitive data in that issue.

Describe the affected version, minimal fictional reproduction, impact, and suggested fix.
Never attach real birth records, private locations, credentials, caches, draw journals,
or personalized reports. Coordinate disclosure privately until a fix is available.
Maintainers will assess reports and coordinate a patch; there is no guaranteed response SLA.

## Scope

Reports may cover CLI input handling, local file access, subprocess bridges, MCP transport,
dependency setup, unsafe corpus processing, or unintended disclosure of local records.
Prophet runs offline after setup. MCP clients can invoke all exposed CLI commands,
including local record reads and explicit persistence; run clients only with trusted access.
The server provides no network listener or authentication boundary.

Incorrect astrology interpretations or predictions are not security vulnerabilities.
Report reproducible calculation errors using fictional/public charts through the bug form.
Third-party vulnerabilities should also be reported to the relevant upstream project;
keep their licence and disclosure requirements intact.
