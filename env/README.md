# Environment profiles

This directory contains non-secret examples only. No profile is loaded
implicitly. Copy one example outside Git or export the values in your shell,
then run `p4 env check` before any stage.

Profiles express intent, not authority:

- `bootstrap.env.example`: zero-data local development and contract work
- `observed.env.example`: local replay of an explicitly supplied snapshot
- `canary.env.example`: approval-bound bounded collection preparation
- `production.env.example`: production layout; network remains disabled until
  an approval is separately supplied and validated

Relative paths are resolved from the repository root. Never put credentials,
tokens, cookies, signed approvals, or populated absolute paths in Git.
