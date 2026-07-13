#!/usr/bin/env python3
"""Compare Claude and Codex permission profiles by TOML meaning."""

# Standard Library
import os
import json
import argparse
import difflib
import tomllib


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CLAUDE_CONFIG = os.path.join(REPO_ROOT, "example.toml")
DEFAULT_CODEX_CONFIG = os.path.join(REPO_ROOT, "codex-code-permissions-hook.toml")
DEFAULT_PATCH = os.path.join(REPO_ROOT, "config", "codex_claude_policy_patch.json")


#============================================
def parse_args() -> argparse.Namespace:
	"""Parse command-line arguments."""
	parser = argparse.ArgumentParser(
		description="Show or verify the semantic diff between Claude and Codex TOML profiles."
	)
	parser.add_argument(
		"--claude", dest="claude_config", default=DEFAULT_CLAUDE_CONFIG,
		help="Claude TOML source profile",
	)
	parser.add_argument(
		"--codex", dest="codex_config", default=DEFAULT_CODEX_CONFIG,
		help="Codex TOML derived profile",
	)
	parser.add_argument(
		"--patch", dest="patch", default=DEFAULT_PATCH,
		help="Reviewed semantic policy patch",
	)
	parser.add_argument(
		"-c", "--check", dest="check", action="store_true",
		help="Fail when the current semantic diff differs from the policy patch",
	)
	return parser.parse_args()


#============================================
def load_toml(path: str) -> dict:
	"""Load one TOML configuration file."""
	with open(path, "rb") as file_handle:
		data = tomllib.load(file_handle)
	return data


#============================================
def rule_identity(rule: dict) -> str:
	"""Return a stable identity for one allow or deny rule."""
	identity_fields = {key: value for key, value in rule.items() if key != "reason"}
	identity = json.dumps(identity_fields, sort_keys=True, separators=(",", ":"))
	return identity


#============================================
def index_rules(rules: list[dict], section: str, profile: str) -> dict:
	"""Index rules by matching fields and reject ambiguous duplicates."""
	indexed = {}
	for rule in rules:
		identity = rule_identity(rule)
		if identity in indexed:
			raise ValueError(f"duplicate {section} rule in {profile}: {identity}")
		indexed[identity] = rule
	return indexed


#============================================
def profile_values(profile: dict) -> dict:
	"""Return non-rule configuration values."""
	values = {key: value for key, value in profile.items() if key not in ("allow", "deny")}
	return values


#============================================
def compare_rule_section(claude: dict, codex: dict, section: str) -> dict:
	"""Compare one repeated TOML rule section."""
	claude_rules = index_rules(claude.get(section, []), section, "Claude")
	codex_rules = index_rules(codex.get(section, []), section, "Codex")
	claude_ids = set(claude_rules)
	codex_ids = set(codex_rules)
	changed = []
	for identity in sorted(claude_ids & codex_ids):
		if claude_rules[identity] != codex_rules[identity]:
			changed.append({
				"identity": json.loads(identity),
				"claude": claude_rules[identity],
				"codex": codex_rules[identity],
			})
	difference = {
		"claude_only": [claude_rules[key] for key in sorted(claude_ids - codex_ids)],
		"codex_only": [codex_rules[key] for key in sorted(codex_ids - claude_ids)],
		"changed": changed,
	}
	return difference


#============================================
def compare_profiles(claude: dict, codex: dict) -> dict:
	"""Build a stable semantic difference between two profiles."""
	difference = {
		"values": {
			"claude": profile_values(claude),
			"codex": profile_values(codex),
		},
		"deny": compare_rule_section(claude, codex, "deny"),
		"allow": compare_rule_section(claude, codex, "allow"),
	}
	if difference["values"]["claude"] == difference["values"]["codex"]:
		difference["values"] = {}
	return difference


#============================================
def format_json(data: dict) -> str:
	"""Format stable JSON with one trailing newline."""
	formatted = json.dumps(data, indent=2, sort_keys=True) + "\n"
	return formatted


#============================================
def check_patch(current_text: str, patch_path: str) -> int:
	"""Compare current output with the reviewed policy patch."""
	with open(patch_path, "r", encoding="ascii") as file_handle:
		expected_text = file_handle.read()
	if current_text == expected_text:
		print("Codex/Claude semantic diff matches the reviewed policy patch.")
		return 0
	difference = difflib.unified_diff(
		expected_text.splitlines(),
		current_text.splitlines(),
		fromfile=patch_path,
		tofile="current semantic diff",
		lineterm="",
	)
	print("\n".join(difference))
	return 1


#============================================
def main() -> int:
	"""Show the semantic diff or verify it against the policy patch."""
	args = parse_args()
	claude = load_toml(args.claude_config)
	codex = load_toml(args.codex_config)
	difference = compare_profiles(claude, codex)
	current_text = format_json(difference)
	if args.check:
		result = check_patch(current_text, args.patch)
		return result
	print(current_text, end="")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
