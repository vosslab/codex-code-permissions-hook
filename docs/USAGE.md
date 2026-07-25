# Usage

Use the CLI to validate a permissions profile or process one lifecycle event
from standard input.

## Quick start

```bash
cargo build --release
target/release/codex-code-permissions-hook validate \
  --config codex-code-permissions-hook.toml
```

Compare the tracked Claude profile with the active Codex profile semantically:

```bash
source source_me.sh && python3 tools/diff_permission_configs.py
```

Use `--check` to fail when the difference no longer matches the reviewed policy
patch in `config/codex_claude_policy_patch.json`.

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

The active Codex profile produces no standard output because deny rules are
disabled and its classifications are allow or passthrough. Both preserve
Codex's normal approval flow.

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
- Standard output: empty for allow and passthrough; enforcing profiles emit JSON
  for deny.
- Audit output: every intercepted call is written as JSON Lines to
  `/tmp/codex-tool-use.json`.

The corpus uses three expected outcomes:

- `allow`: every command leaf matched the allow policy.
- `passthrough`: no complete allow match.
- `deny`: an enforcing test profile returned a denial.
