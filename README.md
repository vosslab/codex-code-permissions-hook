Rust permission hook for Codex that decomposes compound shell commands and decides allow, deny, or passthrough against TOML rules while preserving the established Claude hook workflow and configuration format.

# codex-code-permissions-hook

## Quick start

1. Build the binary: `cargo build --release`. The hook reads JSON on stdin and writes a JSON decision on stdout, ready to wire into Codex `PreToolUse`.
2. Edit the root `codex-code-permissions-hook.toml`, which retains the established Claude policy format.
3. Validate any config edit: `./target/release/codex-code-permissions-hook validate --config codex-code-permissions-hook.toml`.
4. Copy the hook block from [config.toml.example](config.toml.example) into `~/.codex/config.toml`, then review it with `/hooks`.

## Documentation

### Getting started

- [docs/INSTALL.md](docs/INSTALL.md) - build steps, requirements, and Codex hook registration.
- [docs/USAGE.md](docs/USAGE.md) - CLI reference, examples, and I/O formats.
- [docs/CODEX_HOOK_USAGE_GUIDE.md](docs/CODEX_HOOK_USAGE_GUIDE.md) - Codex lifecycle behavior, trust, and known interception limits.

### Reference

- [docs/CONFIGURATION_GUIDE.md](docs/CONFIGURATION_GUIDE.md) - TOML rule syntax and variables.
- [docs/CODE_ARCHITECTURE.md](docs/CODE_ARCHITECTURE.md) - high-level design, modules, and data flow.
- [docs/FILE_STRUCTURE.md](docs/FILE_STRUCTURE.md) - directory map and what belongs where.
- [docs/TOOL_INPUT_SCHEMAS.md](docs/TOOL_INPUT_SCHEMAS.md) - Claude compatibility tool-input schemas.
- [codex-hook-guide.md](codex-hook-guide.md) - saved upstream Codex hook reference.
- [docs/CHANGELOG.md](docs/CHANGELOG.md) - dated record of changes, decisions, and failures.

### Repo standards

- [AGENTS.md](AGENTS.md) - agent workflow guardrails.
- [docs/REPO_STYLE.md](docs/REPO_STYLE.md) - repo-wide conventions.
- [docs/PYTHON_STYLE.md](docs/PYTHON_STYLE.md) - Python style for tooling under `tools/` and `tests/`.
- [docs/PYTEST_STYLE.md](docs/PYTEST_STYLE.md) - pytest test-writing rules and failure triage.
- [docs/MARKDOWN_STYLE.md](docs/MARKDOWN_STYLE.md) - Markdown rules for this repo.

## Testing

Run the established full check sequence with [config_test.sh](config_test.sh). It builds the release binary, runs Rust tests, validates the Codex config, and executes the decision-table regression in [tests/command_decisions.tsv](tests/command_decisions.tsv).

## License

LGPLv3. See [LICENSE.LGPL-3.0.md](LICENSE.LGPL-3.0.md).
