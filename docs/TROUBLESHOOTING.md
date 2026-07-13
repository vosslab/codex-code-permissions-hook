# Troubleshooting

Use this guide when the hook does not load, a policy edit does not take effect,
or a command decision differs from expectation.

## Hook does not run

- Open `/hooks` in Codex and verify that the current hook definition is trusted.
- Confirm that the configured command names the release binary from this
  checkout and the intended TOML profile.
- Rebuild with `cargo build --release` after changing Rust code.

## Configuration validation fails

- Run `target/release/codex-code-permissions-hook validate --config <path>` to
  identify the invalid TOML or regex before invoking the hook.
- Confirm that the requested configuration path exists and that its variables
  resolve to valid regular expressions.
- Compare the changed rule with [CONFIGURATION_GUIDE.md](CONFIGURATION_GUIDE.md)
  rather than copying a command pattern without its exclusions.

## Decision differs from expectation

- Add a focused row to [command_decisions.tsv](../tests/command_decisions.tsv)
  and replay it with `./config_test.sh`.
- Remember that deny rules run before allow rules and compound Bash input is
  processed as leaf commands.
- A passthrough result deliberately writes no standard output; inspect the
  configured audit files when an unmatched command needs investigation.

## Python checks fail

- Run Python tools through `source source_me.sh && python3` so they use the
  repository's required Python 3.12 environment.
- Re-run the narrow failing test first, then run `source source_me.sh && pytest tests/`.

## See also

- [INSTALL.md](INSTALL.md) for registration requirements.
- [USAGE.md](USAGE.md) for input and output examples.
- [DEVELOPMENT.md](DEVELOPMENT.md) for the full local workflow.
