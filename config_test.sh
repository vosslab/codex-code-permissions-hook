#!/bin/sh
set -e

REPO_ROOT="$(git rev-parse --show-toplevel)"
BIN="$REPO_ROOT/target/release/codex-code-permissions-hook"

cargo build --release
cargo test

"$BIN" validate --config ~/.config/codex-code-permissions-hook.toml

echo ""
source "$REPO_ROOT/source_me.sh"
python3 "$REPO_ROOT/tools/run_command_decisions.py"
echo ""
readlink "$HOME/.config/codex-code-permissions-hook.toml"
echo ""

# Keep only the release binary; drop ~662M of build scratch.
rm -rf \
  "$REPO_ROOT/target/debug" \
  "$REPO_ROOT/target/release/deps" \
  "$REPO_ROOT/target/release/build" \
  "$REPO_ROOT/target/release/incremental" \
  "$REPO_ROOT/target/release/examples" \
  "$REPO_ROOT/target/release/libcodex_code_permissions_hook.rlib" \
  "$REPO_ROOT/target/release/libcodex_code_permissions_hook.d" \
  "$REPO_ROOT/target/release/codex-code-permissions-hook.d" \
  "$REPO_ROOT/target/tmp"

du -sh "$REPO_ROOT/target"
