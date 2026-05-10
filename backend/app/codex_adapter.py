import httpx
from typing import Protocol


class CodexRuntimeAdapter(Protocol):
    name: str

    def info(self) -> dict:
        ...

    def run(self, objective: str, session_id: str | None = None) -> dict:
        ...

    def execute_skill(self, skill_name: str, input_payload: dict) -> dict:
        ...


class LocalQueueCodexAdapter:
    name = "LocalQueueCodexAdapter"

    def info(self) -> dict:
        return {
            "name": self.name,
            "mode": "local_demo",
            "replaceWith": "OfficialCodexRuntimeAdapter",
            "supportsStreaming": False,
            "supportsToolCalls": True,
            "supportsSkillExecution": True,
        }

    def run(self, objective: str, session_id: str | None = None) -> dict:
        return {
            "adapter": self.name,
            "status": "accepted",
            "sessionId": session_id,
            "objective": objective,
            "message": "Local adapter accepted the Codex run request. Official runtime integration belongs behind this interface.",
        }

    def execute_skill(self, skill_name: str, input_payload: dict) -> dict:
        return {
            "adapter": self.name,
            "status": "completed",
            "skillName": skill_name,
            "output": {
                "summary": "Local skill execution simulated for controlled demo.",
                "received": input_payload,
            },
        }


class OfficialCodexRuntimeAdapter:
    name = "OfficialCodexRuntimeAdapter"

    def __init__(
        self,
        endpoint: str = "",
        service_token: str = "",
        provider: str = "openai_codex",
        default_model: str = "gpt-5.2-codex",
        project_id: str = "",
        organization_id: str = "",
        max_output_tokens: int = 800,
        reasoning_effort: str = "medium",
    ):
        self.endpoint = endpoint.rstrip("/") if endpoint else ""
        self.service_token = service_token
        self.provider = provider
        self.default_model = default_model
        self.project_id = project_id
        self.organization_id = organization_id
        self.max_output_tokens = max_output_tokens
        self.reasoning_effort = reasoning_effort

    def info(self) -> dict:
        configured = bool(self.endpoint and self.service_token)
        return {
            "name": self.name,
            "mode": "official_ready" if configured else "contract_ready_waiting_for_credentials",
            "provider": self.provider,
            "endpointConfigured": bool(self.endpoint),
            "serviceTokenConfigured": bool(self.service_token),
            "defaultModel": self.default_model,
            "supportsStreaming": True,
            "supportsToolCalls": True,
            "supportsSkillExecution": True,
            "networkCallsEnabled": configured,
        }

    def contract(self) -> dict:
        return {
            "requestSchema": {
                "requestId": "string",
                "sessionId": "string",
                "modelId": "string",
                "objective": "string",
                "tools": "array",
                "metadata": "object",
            },
            "responseSchema": {
                "requestId": "string",
                "sessionId": "string",
                "status": "accepted|running|completed|failed",
                "output": "object",
                "usageInternal": "object redacted from user UX",
            },
            "streamEventSchema": {
                "event": "session.started|token.delta|tool.call|tool.result|snapshot.ready|handoff.ready|session.completed|error",
                "requestId": "string",
                "sessionId": "string",
                "payload": "object",
            },
            "toolCallSchema": {
                "toolName": "string",
                "arguments": "object",
                "risk": "low|medium|high",
                "requiresConfirmation": "boolean",
            },
            "errorSchema": {
                "code": "string",
                "message": "string",
                "retryable": "boolean",
                "requestId": "string",
                "sessionId": "string",
                "modelId": "string",
                "details": "object",
            },
            "timeouts": {"defaultSeconds": 120, "longSessionMode": "streaming_heartbeat_checkpoint"},
            "retry": {"maxAttempts": 3, "backoff": "exponential", "noDuplicateDestructiveToolCalls": True},
        }

    def dry_run(self, model_id: str, objective: str) -> dict:
        return {
            "adapter": self.name,
            "accepted": True,
            "modelId": model_id,
            "objective": objective,
            "networkCallPerformed": False,
            "message": "Dry run validated the official adapter contract without sending secrets or calling external runtime.",
        }

    def list_models(self) -> list[str]:
        if not self.endpoint or not self.service_token:
            raise RuntimeError("Official runtime endpoint and credential are required.")

        headers = {
            "Authorization": f"Bearer {self.service_token}",
            "Content-Type": "application/json",
        }
        if self.project_id:
            headers["OpenAI-Project"] = self.project_id
        if self.organization_id:
            headers["OpenAI-Organization"] = self.organization_id

        with httpx.Client(timeout=30) as client:
            response = client.get(f"{self.endpoint}/models", headers=headers)
            response.raise_for_status()
            payload = response.json()

        return [
            item.get("id")
            for item in payload.get("data", []) or []
            if isinstance(item, dict) and isinstance(item.get("id"), str)
        ]

    def invoke_responses(self, session_id: str, model_id: str, objective: str) -> dict:
        if not self.endpoint or not self.service_token:
            raise RuntimeError("Official runtime endpoint and credential are required.")

        runtime_model = model_id if model_id.startswith(("gpt-", "o")) else self.default_model
        body = {
            "model": runtime_model,
            "input": [
                {
                    "role": "developer",
                    "content": (
                        "You are running inside AIOS Codex Unlimited. "
                        "Treat Codex sessions as the product unit. "
                        "Do not expose API keys, service tokens, internal credentials, or hidden telemetry. "
                        "Return a concise engineering result for the current session."
                    ),
                },
                {"role": "user", "content": objective},
            ],
            "max_output_tokens": self.max_output_tokens,
            "metadata": {
                "aios_session_id": session_id,
                "aios_product": "aios_codex_unlimited",
                "product_unit": "codex_sessions",
            },
        }
        if self.reasoning_effort:
            body["reasoning"] = {"effort": self.reasoning_effort}

        headers = {
            "Authorization": f"Bearer {self.service_token}",
            "Content-Type": "application/json",
        }
        if self.project_id:
            headers["OpenAI-Project"] = self.project_id
        if self.organization_id:
            headers["OpenAI-Organization"] = self.organization_id

        with httpx.Client(timeout=120) as client:
            response = client.post(f"{self.endpoint}/responses", headers=headers, json=body)
            response.raise_for_status()
            payload = response.json()

        output_text = payload.get("output_text") or self._extract_output_text(payload)
        return {
            "adapter": self.name,
            "provider": self.provider,
            "status": payload.get("status", "completed"),
            "responseId": payload.get("id"),
            "requestedModelId": model_id,
            "runtimeModelId": runtime_model,
            "outputText": output_text,
            "usageCaptured": bool(payload.get("usage")),
            "networkCallPerformed": True,
        }

    def _extract_output_text(self, payload: dict) -> str:
        fragments: list[str] = []
        for item in payload.get("output", []) or []:
            for content in item.get("content", []) or []:
                text = content.get("text")
                if isinstance(text, str):
                    fragments.append(text)
        return "\n".join(fragments).strip()

    def run(self, objective: str, session_id: str | None = None) -> dict:
        return {
            "adapter": self.name,
            "status": "not_configured" if not self.service_token else "ready",
            "sessionId": session_id,
            "objective": objective,
        }

    def execute_skill(self, skill_name: str, input_payload: dict) -> dict:
        return {
            "adapter": self.name,
            "status": "not_configured" if not self.service_token else "ready",
            "skillName": skill_name,
            "output": {"received": input_payload},
        }


class OllamaRuntimeAdapter:
    name = "OllamaRuntimeAdapter"

    def __init__(self, base_url: str = "http://localhost:11434", default_model: str = "deepseek-v4-pro:cloud"):
        self.base_url = base_url.rstrip("/")
        self.default_model = default_model

    def info(self) -> dict:
        return {
            "name": self.name,
            "provider": "ollama_local_cloud",
            "baseUrl": self.base_url,
            "defaultModel": self.default_model,
            "requiresDeveloperApiKey": False,
            "supportsStreaming": True,
            "supportsToolCalls": False,
            "supportsSkillExecution": True,
            "networkCallsEnabled": True,
            "notes": "Uses local Ollama HTTP API. Cloud models use the user's local Ollama sign-in, not an OpenAI developer API key.",
        }

    def list_models(self) -> list[str]:
        with httpx.Client(timeout=10) as client:
            response = client.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            payload = response.json()
        return [
            item.get("name") or item.get("model")
            for item in payload.get("models", []) or []
            if isinstance(item, dict) and isinstance(item.get("name") or item.get("model"), str)
        ]

    def chat(self, messages: list[dict], model: str | None = None) -> dict:
        selected_model = model or self.default_model
        body = {"model": selected_model, "messages": messages, "stream": False}
        with httpx.Client(timeout=180) as client:
            response = client.post(f"{self.base_url}/api/chat", json=body)
            response.raise_for_status()
            payload = response.json()
        output_text = ""
        message = payload.get("message")
        if isinstance(message, dict) and isinstance(message.get("content"), str):
            output_text = message["content"]
        return {
            "adapter": self.name,
            "provider": "ollama_local_cloud",
            "model": payload.get("model") or selected_model,
            "outputText": output_text,
            "networkCallPerformed": True,
            "rawStatus": "completed" if payload.get("done", True) else "running",
        }


class AIOSCognitiveRuntimeMesh:
    name = "AIOSCognitiveRuntimeMesh"

    def build_messages(self, objective: str, session_id: str) -> list[dict]:
        system = (
            "Voce esta operando no AIOS Codex Unlimited. "
            "Use uma malha cognitiva de tres fases: planejar, executar e revisar. "
            "A unidade do produto e sessao Codex, nao token. "
            "Nao exponha credenciais, segredos, auth files ou telemetria interna. "
            "Entregue uma resposta pratica de engenharia com qualidade premium."
        )
        developer = (
            f"Session ID: {session_id}. "
            "Estruture a resposta em: Plano, Execucao, Revisao, Riscos e Proximo passo. "
            "Se faltar acesso real a algum runtime/modelo, declare o bloqueio com precisao em vez de simular sucesso."
        )
        return [
            {"role": "system", "content": system},
            {"role": "assistant", "content": developer},
            {"role": "user", "content": objective},
        ]

    def quality_gate(self, output_text: str) -> dict:
        checks = {
            "hasOutput": bool(output_text.strip()),
            "mentionsPlan": "plano" in output_text.lower() or "plan" in output_text.lower(),
            "mentionsReview": "revis" in output_text.lower() or "review" in output_text.lower(),
            "noSecretDisclosure": all(term not in output_text.lower() for term in ["sk-", "api_key", "authorization: bearer"]),
        }
        score = sum(1 for value in checks.values() if value)
        return {
            "runtimeClass": self.name,
            "score": score,
            "maxScore": len(checks),
            "status": "passed" if score >= 3 else "review",
            "checks": checks,
        }


adapter = LocalQueueCodexAdapter()
