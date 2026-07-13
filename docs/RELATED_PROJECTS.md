# Related projects

This map records projects with direct source, dependency, template, or runtime
relationships to this repository.

## Confirmed related projects

### claude-code-permissions-hook

- Relationship: Upstream source or fork
- Link: https://github.com/kornysietsma/claude-code-permissions-hook
- Evidence: The import commit copies the Claude hook backend,
  [Cargo.toml](../Cargo.toml) credits Korny Sietsma, and the Codex profile retains
  its TOML rule model.
- Notes: This repository adapts that backend to Codex `PreToolUse` while preserving
  Claude policy compatibility.

### OpenAI Codex

- Relationship: Optional integration target
- Link: https://github.com/openai/codex
- Evidence: [README.md](../README.md) and the hook configuration register this
  binary for Codex `PreToolUse`, and the saved upstream hook reference tracks
  Codex's hook contract.
- Notes: Codex supplies the runtime events and tool-input shapes evaluated here.

### starter-repo-template

- Relationship: Upstream source or fork
- Link: https://github.com/vosslab/starter-repo-template
- Evidence: The repository history records a reset to the Rust base template, and
  the template provides the shared documentation and development conventions.
- Notes: Template inheritance concerns repository maintenance rather than runtime
  permission decisions.

### brush-parser

- Relationship: Direct dependency
- Link: https://crates.io/crates/brush-parser
- Evidence: [Cargo.toml](../Cargo.toml) declares `brush-parser`, and
  [src/decomposer.rs](../src/decomposer.rs) uses it to parse compound shell commands
  before rule evaluation.
- Notes: The parser lets the hook evaluate individual command leaves rather than an
  opaque compound command string.

## Evidence notes

Repository evidence comes from [README.md](../README.md), [Cargo.toml](../Cargo.toml),
source imports, the commit history, the active policy files, and the saved Codex hook
reference. Bounded web discovery verified the upstream repositories, package registry
entry, and Codex runtime source. Similar hook and policy projects without a direct
repository link, dependency, citation, or reciprocal reference were not included.
