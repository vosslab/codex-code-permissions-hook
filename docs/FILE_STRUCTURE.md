# File structure

## Top-level layout

```text
codex-code-permissions-hook/
+- src/                              Rust policy engine
+- tests/                            Rust and Python tests plus fixtures
+- tools/                            Standalone diagnostic runners
+- devel/                            Build, release, and maintenance scripts
+- docs/                             Project documentation and changelog
+- Cargo.toml                        Rust package manifest
+- codex-code-permissions-hook.toml  Codex policy profile
+- config.toml.example               Codex config hook example
+- codex-hook-guide.md               Saved upstream Codex hook reference
`- README.md                         Project entry point
```

## Key subtrees

### [src/](../src/)

- `main.rs`: CLI entry point.
- `hook_io.rs`: lifecycle JSON protocol.
- `config.rs`: TOML loading and regex compilation.
- `decomposer.rs`: Bash leaf-command extraction.
- `matcher.rs`: rule evaluation.
- `path_check.rs`: Claude file-tool path validation.
- `auditing.rs`: JSON Lines audit output.
- `lib.rs`: shared processing API.

### [tests/](../tests/)

- Rust integration files exercise public APIs and protected branches.
- `command_decisions.tsv` stores end-to-end policy cases.
- `test_config.toml` and `test_protected_branch_config.toml` provide focused
  fixtures.
- Python tests verify repository hygiene, Markdown, TOML, and source quality.
- `playwright/` contains browser-test support.

### [tools/](../tools/)

- `run_command_decisions.py` runs the TSV corpus against the release binary.
- `check_plan_mode_enforcement.py` remains a Claude-specific compatibility
  diagnostic.

## Generated artifacts

- `target/` contains Cargo build output and is ignored.
- `.pytest_cache/` and Python bytecode caches are test artifacts and should not
  be committed.
- Audit JSON Lines files are written to paths selected by each TOML profile.

## Documentation map

- [docs/CODEX_HOOK_USAGE_GUIDE.md](CODEX_HOOK_USAGE_GUIDE.md): Codex lifecycle,
  trust and registration workflow.
- [docs/CONFIGURATION_GUIDE.md](CONFIGURATION_GUIDE.md): policy schema and rule
  authoring.
- [docs/INSTALL.md](INSTALL.md): build and hook setup.
- [docs/USAGE.md](USAGE.md): CLI examples.
- [docs/CODE_ARCHITECTURE.md](CODE_ARCHITECTURE.md): processing design.
- [docs/CHANGELOG.md](CHANGELOG.md): current change history.

## Where to add new work

- Add Rust implementation under `src/` and Rust integration coverage under
  `tests/*.rs`.
- Add policy behaviors to the appropriate root TOML and decision fixtures.
- Add user-facing operational guidance under `docs/`.
- Add maintenance commands under `devel/` and standalone diagnostics under
  `tools/`.
