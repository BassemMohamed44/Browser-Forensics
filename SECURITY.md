# Security Policy

## Supported Versions

This project is currently maintained as a single evolving line — please
make sure you're on the latest commit/release before reporting an issue.

| Version        | Supported |
|-----------------|:---------:|
| Latest (main)    | ✅ |
| Older releases   | ❌ |

## Reporting a Vulnerability

If you discover a security vulnerability (for example: a way the tool
could leak, corrupt, or expose browsing history/history-database contents
beyond what's intended, or a path/command-injection issue in file
handling), please **do not open a public issue**.

Instead:

1. Use GitHub's **"Report a vulnerability"** option under this repository's
   **Security** tab (Security → Advisories → "Report a vulnerability"), or
2. Contact the maintainers privately via the contact details on their
   GitHub profile.

Please include:

- A description of the vulnerability and its potential impact
- Steps to reproduce (a minimal example is ideal)
- Your OS, Python version, and affected browser(s), if relevant

## What to Expect

- We'll acknowledge your report as soon as possible.
- We'll investigate and, if confirmed, work on a fix and coordinate a
  disclosure timeline with you.
- Credit will be given in the release notes unless you prefer to remain
  anonymous.

## Scope Notes

This tool reads **local** browser history databases and writes exports
**locally** to `output/` — it does not transmit data anywhere over the
network. Reports related to unintended local file exposure (e.g. overly
broad file permissions on exported data) are very much in scope; reports
about the browsers' own history storage are best directed to the
respective browser vendor.
