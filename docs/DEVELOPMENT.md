# Development

This guide covers the local workflow for maintaining the Rust hook, its TOML
profiles, and its regression fixtures.

## Local workflow

- Build the release binary with `cargo build --release`.
- Run Rust unit and integration coverage with `cargo test`.
- Validate the active Codex policy with `./config_test.sh`; it builds the
  release binary, runs Rust tests, validates the policy, and replays the command
  decision corpus.
- Run Python repository checks with `source source_me.sh && pytest tests/`.

## Change policy behavior

- Update `codex-code-permissions-hook.toml` for Codex behavior and preserve the
  shared rule layout where it still applies to the inherited backend.
- Run `source source_me.sh && python3 tools/diff_permission_configs.py --check`
  to verify that Claude-to-Codex differences match the reviewed policy patch.
- Add or revise a matching row in [command_decisions.tsv](../tests/command_decisions.tsv)
  for each intentional decision change.
- Run `validate --config <path>` before relying on a changed TOML profile.
- Keep the user-facing rationale in
  [CONFIGURATION_GUIDE.md](CONFIGURATION_GUIDE.md) and
  [CODEX_HOOK_USAGE_GUIDE.md](CODEX_HOOK_USAGE_GUIDE.md) aligned with the
  behavior that agents encounter.

## Release maintenance

- Update the package version and release artifacts with the scripts documented
  in [DEVEL_README.md](../devel/DEVEL_README.md).
- Record intentional changes in [CHANGELOG.md](CHANGELOG.md).
- Keep generated build output under `target/` out of commits.

## See also

- [INSTALL.md](INSTALL.md) for setup and registration.
- [USAGE.md](USAGE.md) for CLI examples.
- [FILE_FORMATS.md](FILE_FORMATS.md) for hook input, output, and TOML shapes.
