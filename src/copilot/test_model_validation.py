"""Tests for is_valid_model() and get_validated_model() in copilot_ollama."""
import logging


import copilot_ollama


class TestIsValidModel:
    def test_returns_true_for_allowed_model(self):
        a_model = next(iter(copilot_ollama.ALLOWED_MODELS))
        assert copilot_ollama.is_valid_model(a_model) is True

    def test_returns_false_for_unknown_model(self):
        assert copilot_ollama.is_valid_model("totally-unknown-llm") is False

    def test_returns_false_for_empty_string(self):
        assert copilot_ollama.is_valid_model("") is False

    def test_returns_false_for_none(self):
        assert copilot_ollama.is_valid_model(None) is False  # type: ignore[arg-type]

    def test_all_configured_models_are_valid(self):
        for model in copilot_ollama.ALLOWED_MODELS:
            assert copilot_ollama.is_valid_model(model) is True


class TestGetValidatedModel:
    def test_returns_valid_model_unchanged(self):
        a_model = next(iter(copilot_ollama.ALLOWED_MODELS))
        assert copilot_ollama.get_validated_model(a_model) == a_model

    def test_fallback_on_unknown_model(self):
        result = copilot_ollama.get_validated_model("bogus-llm")
        assert result == copilot_ollama.DEFAULT_MODEL

    def test_fallback_on_empty_string(self):
        assert copilot_ollama.get_validated_model("") == copilot_ollama.DEFAULT_MODEL

    def test_fallback_on_none(self):
        assert copilot_ollama.get_validated_model(None) == copilot_ollama.DEFAULT_MODEL

    def test_fallback_logs_correct_message(self, caplog):
        unknown = "my-unknown-model"
        with caplog.at_level(logging.INFO):
            copilot_ollama.get_validated_model(unknown)
        assert "Unknown model" in caplog.text
        assert unknown in caplog.text
        assert copilot_ollama.DEFAULT_MODEL in caplog.text
