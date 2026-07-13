# Code architecture

## Overview

This repository builds one Rust policy engine that can process `PreToolUse`
events from Codex and Claude Code. The two root TOML policies share one schema
but use tool-specific rule sets. A stable symlink selects which policy a hook
invocation uses.

## Major components

- [main.rs](../src/main.rs) defines the `run` and `validate` CLI commands.
- [hook_io.rs](../src/hook_io.rs) parses lifecycle JSON from standard input
  and serializes hook decisions. It accepts Codex's nullable
  `transcript_path` and ignores forward-compatible input fields.
- [config.rs](../src/config.rs) loads TOML, expands environment and reusable
  regex variables, and compiles allow and deny rules.
- [decomposer.rs](../src/decomposer.rs) parses compound Bash input into leaf
  commands so each operation receives a separate policy decision.
- [matcher.rs](../src/matcher.rs) matches tool names and input fields. Bash
  and Codex `apply_patch` calls both expose `tool_input.command`.
- [path_check.rs](../src/path_check.rs) preserves path-existence checks for
  Claude file tools. Codex Bash, `apply_patch`, and MCP calls skip those checks.
- [auditing.rs](../src/auditing.rs) writes bounded JSON Lines audit records
  with file locking.

## Policy profiles

- [codex-code-permissions-hook.toml](../codex-code-permissions-hook.toml)
  contains Codex Bash, `apply_patch`, and MCP rules.
- [config.toml.example](../config.toml.example) demonstrates Codex registration
  against the root Codex policy.

## Data flow

1. Codex or Claude Code launches the binary with `run --config <path>`.
2. The binary reads one `PreToolUse` JSON object from standard input.
3. The selected TOML profile is loaded and compiled.
4. Bash commands are decomposed; deny rules run before allow rules.
5. A deny or allow match produces hook-specific JSON. No match produces no
   standard output and leaves the platform's normal permission flow intact.
6. The configured audit files receive the bounded event record.

## Testing and verification

- `cargo test` runs unit, integration, and protected-branch tests.
- [config_test.sh](../config_test.sh) builds the release binary and validates
  both root policies.
- [command_decisions.tsv](../tests/command_decisions.tsv) is the larger
  behavior fixture corpus used by
  [run_command_decisions.py](../tools/run_command_decisions.py).
- Python repository checks run with `source source_me.sh && pytest tests/`.

## Extension points

- Add new rule fields and validation in [config.rs](../src/config.rs).
- Add tool-input matching behavior in [matcher.rs](../src/matcher.rs).
- Add shell parsing behavior in [decomposer.rs](../src/decomposer.rs).
- Add platform protocol fields in [hook_io.rs](../src/hook_io.rs).
- Add policy behavior fixtures under `tests`.

## Known gaps

- TODO: verify Codex hook behavior against a live `/hooks`-trusted installation
  after the current binary and active config paths are finalized.
