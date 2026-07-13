#!/usr/bin/env python3
"""
Run tests/command_decisions.tsv against the release hook binary.

Replaces the older tests/run_command_decisions.sh and the pytest-based
tests/test_hook.py. This runner is intentionally OUTSIDE pytest -- pytest
in this repo is reserved for Python source quality (pyflakes, ascii,
shebangs, imports, etc.).

TSV row formats accepted:
  expected<TAB>command                       -- Bash (Codex profile)
  expected<TAB>tool<TAB>json_input           -- non-Bash (Codex profile)
  expected<TAB>tool<TAB>config<TAB>json_in   -- explicit config path

  expected = allow | deny | passthrough
  tool     = Bash | Read | Write | Edit | Glob | Grep | WebFetch |
             WebSearch | Task | <any other tool name>
  config   = path relative to repo root (e.g. tests/test_config.toml).
             Use "default" for codex-code-permissions-hook.toml.

Lines starting with # and blank lines are skipped.

Exit code: 0 if all match, 1 if any FAIL, 2 on missing prerequisites.

Usage:
    python3 tests/run_command_decisions.py            # run all
    python3 tests/run_command_decisions.py ffprobe    # only rows whose
                                                      # command matches substring
"""

# Standard Library
import os
import sys
import json
import subprocess

_HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(_HERE)
HOOK = os.path.join(REPO_ROOT, "target", "release", "codex-code-permissions-hook")
CODEX_CFG = os.path.join(REPO_ROOT, "codex-code-permissions-hook.toml")
TSV = os.path.join(REPO_ROOT, "tests", "command_decisions.tsv")

# ANSI color helpers (only when stdout is a tty).
if sys.stdout.isatty():
	RED = "\033[1;31m"
	GREEN = "\033[1;32m"
	BG_RED = "\033[1;37;41m"
	RESET = "\033[0m"
else:
	RED = GREEN = BG_RED = RESET = ""


#============================================
def decide_with(cfg_path: str, tool_name: str, tool_input: dict) -> tuple:
	"""Send one HookInput to the binary and return (decision, reason).

	Returns:
		(decision, reason) where decision is allow|deny|passthrough.
	"""
	hook_input = {
		"session_id": "decision-runner",
		"transcript_path": "/tmp/transcript.jsonl",  # nosec B108
		"hook_event_name": "PreToolUse",
		"tool_name": tool_name,
		"tool_input": tool_input,
		"cwd": "/Users/<upstream-user>/Dropbox/prj/test",
	}
	json_input = json.dumps(hook_input)
	result = subprocess.run(
		[HOOK, "run", "--config", cfg_path],
		input=json_input,
		capture_output=True,
		text=True,
		timeout=10,
	)
	if result.returncode != 0:
		raise RuntimeError(
			f"hook exited {result.returncode} for {tool_name}: {result.stderr.strip()}"
		)
	stdout = result.stdout.strip()
	# Empty stdout = passthrough.
	if not stdout:
		return ("passthrough", "")
	parsed = json.loads(stdout)
	hook_out = parsed.get("hookSpecificOutput", {})
	decision = hook_out.get("permissionDecision", "passthrough")
	reason = hook_out.get("permissionDecisionReason", "")
	return (decision, reason)


#============================================
def parse_row(raw_line: str) -> dict:
	"""Parse one TSV row.

	Returns dict with keys: expected, tool, configs (list), tool_input.
	Returns None for comments/blanks.
	"""
	line = raw_line.rstrip("\n")
	if not line.strip() or line.lstrip().startswith("#"):
		return None
	fields = line.split("\t")
	if len(fields) < 2:
		raise ValueError(f"malformed (need at least expected<TAB>command): {raw_line!r}")
	expected = fields[0]
	# 2-column legacy: expected, command (Bash, default configs)
	if len(fields) == 2:
		row = {
			"expected": expected,
			"tool": "Bash",
			"configs": [CODEX_CFG],
			"tool_input": {"command": fields[1]},
		}
		return row
	# 3-column: expected, tool, json_input  (default configs)
	if len(fields) == 3:
		tool = fields[1]
		row = {
			"expected": expected,
			"tool": tool,
			"configs": [CODEX_CFG],
			"tool_input": _parse_input(tool, fields[2]),
		}
		return row
	# 4-column: expected, tool, config, json_input
	tool = fields[1]
	cfg = fields[2]
	if cfg == "default":
		configs = [CODEX_CFG]
	else:
		configs = [os.path.join(REPO_ROOT, cfg)]
	row = {
		"expected": expected,
		"tool": tool,
		"configs": configs,
		"tool_input": _parse_input(tool, fields[3]),
	}
	return row


#============================================
def _parse_input(tool: str, raw: str) -> dict:
	"""Parse the input field. Bash with bare command -> {command: raw}.
	Anything else (or Bash starting with '{') -> JSON.
	"""
	stripped = raw.strip()
	if tool == "Bash" and not stripped.startswith("{"):
		# Bash shorthand: bare command string.
		out = {"command": raw}
		return out
	# Otherwise interpret as JSON dict.
	parsed = json.loads(raw)
	return parsed


#============================================
def run_row(row: dict, filter_str: str) -> tuple[int, int, int, list[str]]:
	"""Run a single parsed TSV row against all of its configs.

	Returns (passes, fails, skipped, fail_lines). fail_lines is a list of
	human-readable mismatch summaries reprinted at the end of the run so the
	failures are visible without scrolling back through the OK output.
	"""
	# Filter: substring match against the JSON-rendered tool_input.
	display = row["tool"] + " " + json.dumps(row["tool_input"])
	if filter_str and filter_str not in display:
		return (0, 0, 1, [])
	passes = 0
	fails = 0
	fail_lines = []
	for cfg in row["configs"]:
		got, _reason = decide_with(cfg, row["tool"], row["tool_input"])
		label = os.path.basename(cfg)
		expected = row["expected"]
		if got == expected:
			print(f"OK   [{label:32s}] expect={expected:11s} got={got:11s} :: "
				f"{row['tool']} {json.dumps(row['tool_input'])[:80]}")
			passes += 1
		else:
			# Build the line once so the inline print and the end-of-run
			# summary stay identical.
			summary = (f"[{label:32s}] expect={expected:11s} got={got:11s} :: "
				f"{row['tool']} {json.dumps(row['tool_input'])[:80]}")
			print(f"{RED}FAIL {summary}{RESET}")
			fail_lines.append(summary)
			fails += 1
	return (passes, fails, 0, fail_lines)


#============================================
def setup_test_paths() -> None:
	"""Materialize the /tmp/cck-test/ tree referenced by TSV fixtures.

	The path-existence pre-check denies Read/Edit/Glob/Grep against missing
	paths, so TSV rows that expect 'allow' or 'passthrough' must reference
	files that exist. Idempotent: re-running is a no-op.
	"""
	# Directory layout used across TSV rows under tests/test_config.toml.
	# /tmp/cck-test/ is inside the NSH_PATH allow zone.
	# /tmp/cck-nomatch/ stays outside the allow zone so near-miss tests
	# (passthrough rows that verify deny regexes do not false-positive)
	# work without being captured by the broad path allow.
	root = "/tmp/cck-test"  # nosec B108 -- intentional /tmp fixture root for TSV runner
	nomatch = "/tmp/cck-nomatch"  # nosec B108 -- intentional /tmp non-allow-zone fixture root
	dirs = [
		root,
		os.path.join(root, "myproject"),
		os.path.join(root, "deep", "nested", "path"),
		os.path.join(root, "src"),
		nomatch,
	]
	for d in dirs:
		os.makedirs(d, exist_ok=True)
	# Files used by 'allow' Read/Edit/Grep rows and dotfile-near-miss rows.
	files = [
		os.path.join(root, "main.rs"),
		os.path.join(root, "test_safe_file.txt"),
		os.path.join(root, "myproject", "README.md"),
		os.path.join(root, "deep", "nested", "path", "file.txt"),
		os.path.join(nomatch, ".env.local"),
		os.path.join(nomatch, ".env.production"),
		os.path.join(nomatch, ".environment"),
		os.path.join(nomatch, ".secrets"),
		os.path.join(nomatch, "env"),
		os.path.join(nomatch, "secret_notes.txt"),
	]
	for f in files:
		if not os.path.exists(f):
			# touch
			open(f, "a").close()


#============================================
def main() -> int:
	"""Entry point."""
	setup_test_paths()
	# Preflight checks.
	if not os.access(HOOK, os.X_OK):
		print(f"FAIL: hook binary missing or not executable; "
			f"run 'cargo build --release' first: {HOOK}", file=sys.stderr)
		return 2
	if not os.path.isfile(CODEX_CFG):
		print(f"FAIL: Codex config not found: {CODEX_CFG}", file=sys.stderr)
		return 2
	if not os.path.isfile(TSV):
		print(f"FAIL: fixture not found: {TSV}", file=sys.stderr)
		return 2

	filter_str = sys.argv[1] if len(sys.argv) > 1 else ""

	total_pass = 0
	total_fail = 0
	total_skip = 0
	all_fail_lines = []
	with open(TSV, "r", encoding="utf-8") as handle:
		for raw in handle:
			row = parse_row(raw)
			if row is None:
				continue
			p, f, s, fail_lines = run_row(row, filter_str)
			total_pass += p
			total_fail += f
			total_skip += s
			all_fail_lines.extend(fail_lines)

	print()
	if total_fail == 0:
		print(f"{GREEN}OVERALL: ALL TESTS PASSED "
			f"(passed={total_pass}, skipped={total_skip}){RESET}")
		return 0
	print(f"{BG_RED} ============================================================ {RESET}")
	print(f"{BG_RED}   FAILURE: {total_fail} mismatches "
		f"(passed={total_pass}, skipped={total_skip})  {RESET}")
	print(f"{BG_RED} ============================================================ {RESET}")
	# Reprint every mismatch so failures are visible at the end of the run
	# without searching back through the OK lines.
	for line in all_fail_lines:
		print(f"{RED}FAIL {line}{RESET}")
	return 1


if __name__ == "__main__":
	sys.exit(main())
