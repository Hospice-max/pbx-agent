# Security Policy

## Supported versions

The latest release on the default branch is the supported version.

## Reporting a vulnerability

Do not publish credentials, AMI secrets, private IPs or proof-of-concept access details in a public issue.

Prefer GitHub Security Advisories when enabled for the repository. If that facility is not available, contact the project maintainer privately and provide:

- affected version;
- operating system;
- Asterisk version;
- impact;
- reproduction steps without real credentials.

## Deployment guidance

- Use a dedicated read-only AMI account.
- Keep AMI bound to localhost when the agent runs on the PBX.
- Do not expose port 5038 to the Internet.
- Bind the dashboard to localhost and use a reverse proxy when remote access is required.
- Never commit `/etc/pbx-agent/pbx-agent.conf`.
