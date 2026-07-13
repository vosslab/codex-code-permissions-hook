# Install

Installation builds the Rust CLI and registers the Codex policy binary as a
lifecycle hook.

## Requirements

- Rust and Cargo, as declared by [Cargo.toml](../Cargo.toml).
- Bash for repository maintenance scripts.
- Codex CLI for the Codex hook registration and `/hooks` trust workflow.
- Python 3.12 only for repository Python checks and fixture runners.

## Build

```bash
cargo build --release
cargo test
```

The resulting executable is
`target/release/codex-code-permissions-hook`.

## Register the Codex hook

Copy the hook block from [config.toml.example](../config.toml.example) into
`~/.codex/config.toml`. The sample runs the binary from this checkout and reads
the policy from `~/.config/codex-code-permissions-hook.toml`.

Project-local hooks require a trusted `.codex/` layer. Open `/hooks` in Codex
CLI after adding or changing the command, inspect the exact definition, and
trust it before expecting it to run.

## Verify install

```bash
./config_test.sh
```

This builds the release binary, runs Rust tests, validates the Codex TOML, and
runs the decision fixtures.

## Troubleshooting

- If Codex skips the hook, open `/hooks` and check whether its current hash still
  needs review.
- If validation reports a missing config, confirm that
  `codex-code-permissions-hook.toml` is in the repository root.
- If the binary path changes, update the absolute command in the Codex hook
  source and review the changed definition again.

## Known gaps

- TODO: verify the final absolute installation paths on each machine that uses
  the shared profiles.
