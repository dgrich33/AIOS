use std::process::Command;

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct DelegateInfo {
    pub connected: bool,
    pub cli_version: String,
    pub plan: String,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum BridgeError {
    ResourceExhausted(String),
    Unavailable(String),
}

pub fn delegate_status(codex_bin: &str) -> DelegateInfo {
    match Command::new(codex_bin).arg("--version").output() {
        Ok(output) if output.status.success() => {
            let text = String::from_utf8_lossy(&output.stdout);
            DelegateInfo {
                connected: true,
                cli_version: text.trim().to_string(),
                plan: "codex_account_plan_uninspected".to_string(),
            }
        }
        Ok(output) => {
            let text = String::from_utf8_lossy(&output.stderr);
            DelegateInfo {
                connected: false,
                cli_version: text.trim().to_string(),
                plan: "unavailable".to_string(),
            }
        }
        Err(error) => DelegateInfo {
            connected: false,
            cli_version: error.to_string(),
            plan: "unavailable".to_string(),
        },
    }
}

pub fn map_codex_error(text: &str) -> BridgeError {
    let lowered = text.to_ascii_lowercase();
    if lowered.contains("usage limit") || lowered.contains("over quota") || lowered.contains("quota") {
        BridgeError::ResourceExhausted(text.to_string())
    } else {
        BridgeError::Unavailable(text.to_string())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn maps_usage_limit_to_resource_exhausted() {
        assert!(matches!(
            map_codex_error("You've hit your usage limit."),
            BridgeError::ResourceExhausted(_)
        ));
    }

    #[test]
    fn maps_generic_error_to_unavailable() {
        assert!(matches!(
            map_codex_error("socket missing"),
            BridgeError::Unavailable(_)
        ));
    }
}

