#![forbid(unsafe_code)]
#![warn(clippy::all)]

use anyhow::{Context, Result};
use serde::{Deserialize, Deserializer, Serialize};
use std::io::{self, Read, Write};

use crate::auditing::Decision;

#[derive(Debug, Deserialize)]
pub struct HookInput {
    pub session_id: String,
    #[serde(default, deserialize_with = "deserialize_nullable_string")]
    pub transcript_path: String,
    pub cwd: String,
    pub hook_event_name: String,
    pub tool_name: String,
    pub tool_input: serde_json::Value,
}

#[derive(Debug, Serialize)]
pub struct HookOutput {
    #[serde(rename = "hookSpecificOutput")]
    pub hook_specific_output: HookSpecificOutput,
}

#[derive(Debug, Serialize)]
pub struct HookSpecificOutput {
    #[serde(rename = "hookEventName")]
    pub hook_event_name: String,
    #[serde(rename = "permissionDecision")]
    pub permission_decision: String,
    #[serde(rename = "permissionDecisionReason")]
    pub permission_decision_reason: String,
}

impl HookInput {
    pub fn read_from_stdin() -> Result<Self> {
        let mut buffer = String::new();
        io::stdin()
            .read_to_string(&mut buffer)
            .context("Failed to read from stdin")?;

        let input: HookInput =
            serde_json::from_str(&buffer).context("Failed to parse JSON from stdin")?;

        Ok(input)
    }

    pub fn extract_field(&self, field_name: &str) -> Option<String> {
        self.tool_input
            .get(field_name)
            .and_then(|v| v.as_str())
            .map(|s| s.to_string())
    }

    /// Create a copy of this input with only the "command" field replaced.
    ///
    /// Used by the decomposer to create synthetic inputs for each
    /// sub-command extracted from a compound Bash command.
    pub fn with_command(&self, command: &str) -> Self {
        let mut tool_input = serde_json::Map::new();
        tool_input.insert(
            "command".to_string(),
            serde_json::Value::String(command.to_string()),
        );
        HookInput {
            session_id: self.session_id.clone(),
            transcript_path: self.transcript_path.clone(),
            cwd: self.cwd.clone(),
            hook_event_name: self.hook_event_name.clone(),
            tool_name: self.tool_name.clone(),
            tool_input: serde_json::Value::Object(tool_input),
        }
    }
}

fn deserialize_nullable_string<'de, D>(deserializer: D) -> Result<String, D::Error>
where
    D: Deserializer<'de>,
{
    Ok(Option::<String>::deserialize(deserializer)?.unwrap_or_default())
}

impl HookOutput {
    /// Convert an internal policy decision into supported Codex hook output.
    ///
    /// Codex accepts `permissionDecision: "allow"` only with `updatedInput`.
    /// This hook does not rewrite tool inputs, so allow and passthrough results
    /// produce no output and let Codex continue its normal permission flow.
    pub fn from_policy_decision(decision: Decision, reason: Option<String>) -> Option<Self> {
        match decision {
            Decision::Deny => Some(Self::deny(reason.unwrap_or_default())),
            Decision::Allow | Decision::Passthrough => None,
        }
    }

    pub fn deny(reason: String) -> Self {
        HookOutput {
            hook_specific_output: HookSpecificOutput {
                hook_event_name: "PreToolUse".to_string(),
                permission_decision: "deny".to_string(),
                permission_decision_reason: reason,
            },
        }
    }

    pub fn write_to_stdout(&self) -> Result<()> {
        let json = serde_json::to_string(self).context("Failed to serialize output to JSON")?;
        io::stdout()
            .write_all(json.as_bytes())
            .context("Failed to write to stdout")?;
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use pretty_assertions::assert_eq;

    #[test]
    fn test_extract_field() {
        let input = HookInput {
            session_id: "test".to_string(),
            transcript_path: "/tmp/test".to_string(),
            cwd: "/home/user".to_string(),
            hook_event_name: "PreToolUse".to_string(),
            tool_name: "Read".to_string(),
            tool_input: serde_json::json!({
                "file_path": "/home/user/test.txt"
            }),
        };

        assert_eq!(
            input.extract_field("file_path"),
            Some("/home/user/test.txt".to_string())
        );
        assert_eq!(input.extract_field("nonexistent"), None);
    }

    #[test]
    fn test_policy_allow_produces_no_hook_output() {
        let output = HookOutput::from_policy_decision(
            Decision::Allow,
            Some("Allowed by policy".to_string()),
        );

        assert!(output.is_none());
    }

    #[test]
    fn test_policy_passthrough_produces_no_hook_output() {
        let output = HookOutput::from_policy_decision(Decision::Passthrough, None);

        assert!(output.is_none());
    }

    #[test]
    fn test_deny_hook_output_serialization() -> Result<()> {
        let output =
            HookOutput::from_policy_decision(Decision::Deny, Some("Test reason".to_string()))
                .expect("deny decisions should produce hook output");
        let json = serde_json::to_value(&output)?;

        assert_eq!(json["hookSpecificOutput"]["permissionDecision"], "deny");
        assert_eq!(
            json["hookSpecificOutput"]["permissionDecisionReason"],
            "Test reason"
        );
        assert!(json.get("suppressOutput").is_none());

        Ok(())
    }

    #[test]
    fn test_null_transcript_path_deserializes() -> Result<()> {
        let input: HookInput = serde_json::from_value(serde_json::json!({
            "session_id": "session",
            "transcript_path": null,
            "cwd": "/tmp",
            "hook_event_name": "PreToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": "echo hello"},
            "turn_id": "turn",
            "tool_use_id": "tool",
            "model": "gpt-5",
            "permission_mode": "default"
        }))?;

        assert_eq!(input.transcript_path, "");
        Ok(())
    }
}
