//! Integration tests for the codex-code-permissions-hook library.
//!
//! These tests use the library's public API directly to test rule matching
//! logic without spawning a subprocess.
//!
//! Decision-table coverage (Bash/Read/Write/Edit/Glob/Grep allow-deny-passthrough
//! cases) lives in `tests/command_decisions.tsv`, run by
//! `tools/run_command_decisions.py` against both the live and example configs.
//! This file keeps only the API-level tests that the decision table does not
//! cover: config validation, decomposer compound/loop behavior, and the
//! `HookResult` constructors.

use std::path::PathBuf;

use codex_code_permissions_hook::{
    Decision, HookInput, HookResult, process_hook_input, validate_config,
};

/// Helper to get the path to the test config
fn config_path() -> PathBuf {
    let mut path = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    path.push("tests");
    path.push("test_config.toml");
    path
}

/// Helper to get the path to the Codex policy.
fn codex_config_path() -> PathBuf {
    let mut path = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    path.push("codex-code-permissions-hook.toml");
    path
}

#[test]
fn test_validate_codex_config() {
    let result = validate_config(&codex_config_path());
    assert!(result.is_ok(), "Codex config should be valid");

    let (deny_count, allow_count) = result.unwrap();
    assert!(deny_count > 0, "Codex config should have deny rules");
    assert!(allow_count > 0, "Codex config should have allow rules");
}

#[test]
fn test_validate_test_config() {
    let result = validate_config(&config_path());
    assert!(result.is_ok(), "Test config should be valid");

    let (deny_count, allow_count) = result.unwrap();
    assert!(deny_count > 0, "Test config should have deny rules");
    assert!(allow_count > 0, "Test config should have allow rules");
}

#[test]
fn test_codex_apply_patch_secret_file_denied() {
    let input = HookInput {
        session_id: "test".to_string(),
        transcript_path: String::new(),
        cwd: "/home/user/project".to_string(),
        hook_event_name: "PreToolUse".to_string(),
        tool_name: "apply_patch".to_string(),
        tool_input: serde_json::json!({
            "command": "*** Begin Patch\n*** Update File: .env\n*** End Patch"
        }),
    };
    let result = process_hook_input(&codex_config_path(), &input)
        .expect("Codex apply_patch processing should succeed");
    assert_eq!(result.decision, Decision::Deny);
}

#[test]
fn test_codex_apply_patch_nested_secret_file_denied() {
    let input = HookInput {
        session_id: "test".to_string(),
        transcript_path: String::new(),
        cwd: "/home/user/project".to_string(),
        hook_event_name: "PreToolUse".to_string(),
        tool_name: "apply_patch".to_string(),
        tool_input: serde_json::json!({
            "command": "*** Begin Patch\n*** Add File: config/.secret\n*** End Patch"
        }),
    };
    let result = process_hook_input(&codex_config_path(), &input)
        .expect("Codex apply_patch processing should succeed");
    assert_eq!(result.decision, Decision::Deny);
}

#[test]
fn test_codex_apply_patch_regular_file_preserves_normal_flow() {
    let input = HookInput {
        session_id: "test".to_string(),
        transcript_path: String::new(),
        cwd: "/home/user/project".to_string(),
        hook_event_name: "PreToolUse".to_string(),
        tool_name: "apply_patch".to_string(),
        tool_input: serde_json::json!({
            "command": "*** Begin Patch\n*** Update File: src/main.rs\n*** End Patch"
        }),
    };
    let result = process_hook_input(&codex_config_path(), &input)
        .expect("Codex apply_patch processing should succeed");
    assert_eq!(result.decision, Decision::Passthrough);
}

// --- Decomposer integration tests ---

#[test]
fn test_decomposer_safe_compound_allowed() {
    // echo hi && echo bye: both sub-commands are safe utilities
    let input = HookInput {
        session_id: "test".to_string(),
        transcript_path: "/tmp/test".to_string(),
        cwd: "/home/user".to_string(),
        hook_event_name: "PreToolUse".to_string(),
        tool_name: "Bash".to_string(),
        tool_input: serde_json::json!({"command": "echo hi && echo bye"}),
    };
    let result = process_hook_input(&config_path(), &input).expect("Processing should succeed");
    assert_eq!(
        result.decision,
        Decision::Allow,
        "Safe compound should be allowed"
    );
}

#[test]
fn test_decomposer_dangerous_sub_command_denied() {
    // echo ok && rm file: rm sub-command triggers deny
    let input = HookInput {
        session_id: "test".to_string(),
        transcript_path: "/tmp/test".to_string(),
        cwd: "/home/user".to_string(),
        hook_event_name: "PreToolUse".to_string(),
        tool_name: "Bash".to_string(),
        tool_input: serde_json::json!({"command": "echo ok && rm -rf /tmp"}),
    };
    let result = process_hook_input(&config_path(), &input).expect("Processing should succeed");
    assert_eq!(
        result.decision,
        Decision::Deny,
        "rm in compound should be denied"
    );
}

#[test]
fn test_decomposer_mixed_passthrough() {
    // echo ok && python3 script: python3 is not in allow rules
    let input = HookInput {
        session_id: "test".to_string(),
        transcript_path: "/tmp/test".to_string(),
        cwd: "/home/user".to_string(),
        hook_event_name: "PreToolUse".to_string(),
        tool_name: "Bash".to_string(),
        tool_input: serde_json::json!({"command": "echo ok && python3 script.py"}),
    };
    let result = process_hook_input(&config_path(), &input).expect("Processing should succeed");
    assert_eq!(
        result.decision,
        Decision::Passthrough,
        "Mixed safe + unknown should passthrough"
    );
}

#[test]
fn test_decomposer_for_loop_safe_body() {
    // for loop with safe body commands
    let input = HookInput {
        session_id: "test".to_string(),
        transcript_path: "/tmp/test".to_string(),
        cwd: "/home/user".to_string(),
        hook_event_name: "PreToolUse".to_string(),
        tool_name: "Bash".to_string(),
        tool_input: serde_json::json!({"command": "for f in *.py; do echo $f; done"}),
    };
    let result = process_hook_input(&config_path(), &input).expect("Processing should succeed");
    assert_eq!(
        result.decision,
        Decision::Allow,
        "For loop with safe body should be allowed"
    );
}

#[test]
fn test_decomposer_for_loop_dangerous_body() {
    // for loop with rm in body
    let input = HookInput {
        session_id: "test".to_string(),
        transcript_path: "/tmp/test".to_string(),
        cwd: "/home/user".to_string(),
        hook_event_name: "PreToolUse".to_string(),
        tool_name: "Bash".to_string(),
        tool_input: serde_json::json!({"command": "for f in *.tmp; do rm $f; done"}),
    };
    let result = process_hook_input(&config_path(), &input).expect("Processing should succeed");
    assert_eq!(
        result.decision,
        Decision::Deny,
        "For loop with rm in body should be denied"
    );
}

#[test]
fn test_hook_result_constructors() {
    let allow = HookResult::allow("test reason".to_string());
    assert_eq!(allow.decision, Decision::Allow);
    assert_eq!(allow.reason, Some("test reason".to_string()));

    let deny = HookResult::deny("denied".to_string());
    assert_eq!(deny.decision, Decision::Deny);
    assert_eq!(deny.reason, Some("denied".to_string()));

    let passthrough = HookResult::passthrough();
    assert_eq!(passthrough.decision, Decision::Passthrough);
    assert_eq!(passthrough.reason, None);
}
