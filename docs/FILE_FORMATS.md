# File formats

The hook accepts one JSON lifecycle event, reads TOML policy profiles, emits
optional JSON decisions, and writes JSON Lines audit records.

## Hook input JSON

- Standard input contains one `PreToolUse` object with session, tool, working
  directory, and `tool_input` fields.
- `tool_input` is a JSON object. Bash and Codex `apply_patch` rules read its
  `command` field.
- Codex input permits a null `transcript_path`; forward-compatible fields are
  accepted and ignored.
- [USAGE.md](USAGE.md) provides a complete minimal input example.

## Policy TOML

- A profile contains configuration, variables, audit settings, protected-branch
  settings, and ordered allow and deny rule arrays.
- Rules select a tool or tool regex and may match command, file-path, prompt,
  or subagent fields with regular expressions.
- [CONFIGURATION_GUIDE.md](CONFIGURATION_GUIDE.md) is the authoring reference;
  `codex-code-permissions-hook.toml` is the active Codex example.

## Hook output JSON

- A deny match emits Codex hook JSON containing the decision and its reason.
- Allow and passthrough decisions emit no standard output, preserving Codex's
  normal permission flow. Codex accepts a `PreToolUse` allow response only when
  it includes an `updatedInput` rewrite, which this hook does not perform.

## Audit JSON Lines

- Audit files contain one JSON object per line.
- Records retain the event context, decision, and reason when the configured
  audit level requires them.
- Long string fields are bounded before logging to keep audit records manageable.
