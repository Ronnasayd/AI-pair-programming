"""Integration tests for API endpoint fallback behaviour."""
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

import copilot_ollama

MOCK_COPILOT_RESPONSE = {"text": "Hello from Copilot"}

client = TestClient(copilot_ollama.app)


class TestListModels:
    def test_returns_all_configured_models(self):
        resp = client.get("/api/tags")
        assert resp.status_code == 200
        names = {m["name"] for m in resp.json()["models"]}
        assert names == copilot_ollama.ALLOWED_MODELS

    def test_response_count_matches_config(self):
        resp = client.get("/api/tags")
        assert len(resp.json()["models"]) == len(copilot_ollama.ALLOWED_MODELS)


class TestOpenAIListModels:
    def test_returns_all_configured_models(self):
        resp = client.get("/v1/models")
        assert resp.status_code == 200
        ids = {m["id"] for m in resp.json()["data"]}
        assert ids == copilot_ollama.ALLOWED_MODELS


class TestChatEndpoint:
    def _call(self, model=None):
        body = {"messages": [{"role": "user", "content": "Hi"}], "stream": False}
        if model is not None:
            body["model"] = model
        with patch("copilot_ollama.call_copilot", new=AsyncMock(return_value=MOCK_COPILOT_RESPONSE)):
            return client.post("/api/chat", json=body)

    def test_valid_model_succeeds(self):
        a_model = next(iter(copilot_ollama.ALLOWED_MODELS))
        resp = self._call(model=a_model)
        assert resp.status_code == 200
        assert resp.json()["message"]["content"] == "Hello from Copilot"

    def test_unknown_model_falls_back_silently(self):
        resp = self._call(model="does-not-exist")
        assert resp.status_code == 200

    def test_missing_model_uses_default(self):
        resp = self._call(model=None)
        assert resp.status_code == 200

    def test_response_model_field_equals_normalized_model(self):
        a_model = next(iter(copilot_ollama.ALLOWED_MODELS))
        resp = self._call(model=a_model)
        # The response model field is the normalized form (adds :latest when no tag present)
        assert resp.json()["model"] == copilot_ollama.normalize_model_name(a_model)


class TestGenerateEndpoint:
    def _call(self, model=None):
        body = {"prompt": "Say hi", "stream": False}
        if model is not None:
            body["model"] = model
        with patch("copilot_ollama.call_copilot", new=AsyncMock(return_value=MOCK_COPILOT_RESPONSE)):
            return client.post("/api/generate", json=body)

    def test_valid_model_succeeds(self):
        a_model = next(iter(copilot_ollama.ALLOWED_MODELS))
        resp = self._call(model=a_model)
        assert resp.status_code == 200

    def test_unknown_model_falls_back(self):
        resp = self._call(model="unknown-llm")
        assert resp.status_code == 200

    def test_missing_model_uses_default(self):
        resp = self._call(model=None)
        assert resp.status_code == 200


class TestOpenAIChatCompletions:
    def _call(self, model=None):
        body = {"messages": [{"role": "user", "content": "Hello"}], "stream": False}
        if model is not None:
            body["model"] = model
        with patch("copilot_ollama.call_copilot", new=AsyncMock(return_value=MOCK_COPILOT_RESPONSE)):
            return client.post("/v1/chat/completions", json=body)

    def test_valid_model_succeeds(self):
        a_model = next(iter(copilot_ollama.ALLOWED_MODELS))
        resp = self._call(model=a_model)
        assert resp.status_code == 200
        assert resp.json()["choices"][0]["message"]["content"] == "Hello from Copilot"

    def test_unknown_model_falls_back_silently(self):
        resp = self._call(model="not-a-model")
        assert resp.status_code == 200

    def test_missing_model_uses_default(self):
        resp = self._call(model=None)
        assert resp.status_code == 200
