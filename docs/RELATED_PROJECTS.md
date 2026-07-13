# Related projects

This map identifies the upstream template and platform documentation that
directly inform this repository's maintenance and integration work.

## Direct relationships

- [starter-repo-template](https://github.com/vosslab/starter-repo-template) is
  the repository template identified by this project's GitHub metadata. Its
  shared development and documentation conventions inform this checkout.
- [Codex hooks documentation](https://learn.chatgpt.com/docs/hooks) is the
  platform reference for lifecycle-hook registration, event handling, and
  trusted hook definitions.
- [codex-code-permissions-hook](https://github.com/vosslab/codex-code-permissions-hook)
  is the public repository for this source tree and its release history.

## Related local references

- [CODEX_HOOK_USAGE_GUIDE.md](CODEX_HOOK_USAGE_GUIDE.md) translates the platform
  contract into this hook's installation and audit workflow.
- [CONFIGURATION_GUIDE.md](CONFIGURATION_GUIDE.md) documents this repository's
  TOML policy schema and rule-authoring conventions.

## Scope boundary

- This repository is a Codex permission-hook implementation, not a replacement
  for Codex itself or a general-purpose policy language.
- The inherited Claude-compatible portions of the policy remain implementation
  compatibility details; use the Codex guides for active integration behavior.
