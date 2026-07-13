# Usage

Use the CLI to validate a permissions profile or process one lifecycle event
from standard input.

## Quick start

```bash
cargo build --release
target/release/codex-code-permissions-hook validate \
  --config codex-code-permissions-hook.toml
```

## CLI

The executable has two subcommands:

- `validate --config <path>` loads the TOML and compiles every regex.
- `run --config <path>` reads one hook JSON object from standard input and
  writes a decision only when a rule matches.

Show generated help with:

```bash
target/release/codex-code-permissions-hook --help
target/release/codex-code-permissions-hook run --help
```

## Process a Codex event

```bash
printf '%s' '{"session_id":"test","transcript_path":null,"cwd":"/tmp","hook_event_name":"PreToolUse","turn_id":"turn","tool_name":"Bash","tool_use_id":"tool","tool_input":{"command":"git status"},"model":"gpt-5","permission_mode":"default"}' \
  | target/release/codex-code-permissions-hook run \
      --config codex-code-permissions-hook.toml
```

An allow or deny match produces Codex hook JSON. A passthrough result produces
no standard output and preserves Codex's normal approval flow.

## Validate the policy

```bash
./config_test.sh
```

For the larger decision fixture corpus, first build the release binary and then
run the Python tool with the required repository environment:

```bash
cargo build --release
source source_me.sh && python3 tools/run_command_decisions.py
```

## Inputs and outputs

- Input: one `PreToolUse` JSON object on standard input.
- Policy: the TOML path supplied with `--config`.
- Standard output: hook-specific JSON for allow or deny; empty for passthrough.
- Audit output: JSON Lines at the paths configured under `[audit]`.

## Known gaps

- TODO: verify the decision fixture runner's cross-profile expectations after
  every intentional divergence between the Claude and Codex policies.
