use aios_codex_organ_bridge::{delegate_status, map_codex_error, BridgeError};
use std::env;

fn main() {
    let codex_bin = env::var("CODEX_BIN").unwrap_or_else(|_| "codex".to_string());
    let socket = env::var("CODEX_CLI_SOCKET").unwrap_or_else(|_| "/tmp/codex_cli.sock".to_string());
    let info = delegate_status(&codex_bin);
    println!(
        "{{\"cos\":\"1.1\",\"socket\":\"{}\",\"connected\":{},\"cli_version\":\"{}\",\"plan\":\"{}\"}}",
        socket.replace('\\', "\\\\").replace('"', "\\\""),
        info.connected,
        info.cli_version.replace('\\', "\\\\").replace('"', "\\\""),
        info.plan
    );

    if !info.connected {
        let error = map_codex_error(&info.cli_version);
        match error {
            BridgeError::ResourceExhausted(message) => {
                eprintln!("RESOURCE_EXHAUSTED: {}", message);
                std::process::exit(8);
            }
            BridgeError::Unavailable(message) => {
                eprintln!("UNAVAILABLE: {}", message);
                std::process::exit(7);
            }
        }
    }
}

