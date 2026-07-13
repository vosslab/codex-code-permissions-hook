# Configuration guide

## Overview

The root Codex policy uses the same TOML schema and rule ordering as the Claude
hook it was derived from.

- [codex-code-permissions-hook.toml](../codex-code-permissions-hook.toml):
  Codex `Bash`, `apply_patch`, and MCP policy.

## Top-level sections

```toml
[audit]
audit_file = "/tmp/codex-tool-use.json"
audit_level = "all"
passthrough_log_file = "/tmp/codex-passthrough.json"

[limits]
max_chain_length = 5

[git_protection]
protected_branches = ["main", "master"]
protected_refs = ["refs/heads/main", "refs/heads/master"]

[variables]
WORKSPACE_ROOT = "nsh"
```

`audit_level` accepts `off`, `matched`, or `all`. A zero
`max_chain_length` disables the compound-command limit.

## Rules

Rules are repeated `[[deny]]` or `[[allow]]` tables. Deny rules always run
first. A rule needs either an exact `tool` or `tool_regex`.

```toml
[[deny]]
tool = "Bash"
command_regex = "\\bsudo\\b"
reason = "Machine-level changes require explicit review."

[[allow]]
tool = "Bash"
command_regex = "^cargo\\s+(check|test)\\b"
```

Supported matcher fields include:

- `tool` and `tool_regex`.
- `command_regex` and `command_exclude_regex`.
- `file_path_regex` and `file_path_exclude_regex` for Claude file-tool inputs.
- `subagent_type`, `subagent_type_regex`, and exclusions for Claude agent calls.
- `prompt_regex` and `prompt_exclude_regex` for supported Claude agent rules.
- `protected_branch_check` for branch-aware Git rules.
- `reason` for a clear model-visible denial or allow explanation.

Unknown fields are rejected so misspelled rules fail during validation.

## Codex-specific rules

Codex currently exposes `Bash`, `apply_patch`, and MCP calls to `PreToolUse`.
Both Bash and `apply_patch` place their text in `tool_input.command`, so both use
`command_regex`:

```toml
[[deny]]
tool = "apply_patch"
command_regex = "(^|/)\\.(env|secret)([[:space:]]|$)"
reason = "Keep secret-bearing environment files outside automated patches."
```

MCP tools use canonical names such as `mcp__server__tool` and expose their full
argument object in `tool_input`. A tool-only MCP allow can use `tool_regex`:

```toml
[[allow]]
tool_regex = "^mcp__plugin_playwright_playwright__browser_"
```

Codex's sandbox remains the primary filesystem boundary. The policy hook is an
additional deterministic guardrail and does not intercept every execution path.

## Claude compatibility rules

The Claude profile retains `Read`, `Write`, `Edit`, `Glob`, `Grep`, agent, web,
and orchestration tool rules from the source repository. Their input fields are
documented in [TOOL_INPUT_SCHEMAS.md](TOOL_INPUT_SCHEMAS.md).

The shared binary retains path-existence checks for those file tools. Codex tool
names do not enter that path-check branch.

## Variables

`${NAME}` references expand from `[variables]` before regex compilation. Bare
environment references such as `$HOME` expand from the process environment.
Inter-variable references are supported; undefined or circular references fail
validation.

## Matching behavior

1. The exact or regex tool name must match.
2. Exclusion regexes disqualify a rule.
3. Deny matches return immediately.
4. Bash input is decomposed into leaf commands.
5. Every Bash leaf must match an allow rule for the whole call to be allowed.
6. No match returns passthrough with no standard output.

For deny rules, write a positive recovery path in `reason`. Prefer concrete
commands or tools that are actually available on the selected platform.

## Validate changes

```bash
target/release/codex-code-permissions-hook validate \
  --config codex-code-permissions-hook.toml
```

Run [config_test.sh](../config_test.sh) to build, test, and validate the policy.

## See also

- [CODEX_HOOK_USAGE_GUIDE.md](CODEX_HOOK_USAGE_GUIDE.md)
- [CODE_ARCHITECTURE.md](CODE_ARCHITECTURE.md)
- [WORKTREE_POLICY.md](WORKTREE_POLICY.md)
- [TOOL_INPUT_SCHEMAS.md](TOOL_INPUT_SCHEMAS.md)
