"""Tests for load_model_config() in copilot_ollama.

Covers:
- Successful load of a valid config
- Startup abort on missing file
- Startup abort on malformed YAML
- Startup abort on missing 'models' key
- Startup abort on missing 'default_model' key
- Startup abort when default_model is not listed in models
- Startup abort on non-string model entry
- Empty models list is rejected
- Duplicate model entries are deduplicated (set behaviour)
"""
from unittest.mock import mock_open, patch

import pytest

import copilot_ollama


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load(yaml_content: str) -> None:
    """Call load_model_config() with the given YAML content mocked as file I/O."""
    with patch("builtins.open", mock_open(read_data=yaml_content)):
        copilot_ollama.load_model_config()


def _expect_exit(yaml_content: str | None = None, open_exc=None) -> "pytest.ExceptionInfo":
    """Assert that load_model_config raises SystemExit(1) for the given content."""
    if open_exc is not None:
        ctx = patch("builtins.open", side_effect=open_exc)
    else:
        ctx = patch("builtins.open", mock_open(read_data=yaml_content))
    with ctx:
        with pytest.raises(SystemExit) as exc_info:
            copilot_ollama.load_model_config()
    assert exc_info.value.code == 1
    return exc_info


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestValidConfig:
    def test_allowed_models_populated(self):
        _load("models:\n  - 'gpt-4'\n  - 'gpt-4-turbo'\ndefault_model: 'gpt-4'\n")
        assert "gpt-4" in copilot_ollama.ALLOWED_MODELS
        assert "gpt-4-turbo" in copilot_ollama.ALLOWED_MODELS

    def test_default_model_set(self):
        _load("models:\n  - 'gpt-4'\n  - 'gpt-4-turbo'\ndefault_model: 'gpt-4-turbo'\n")
        assert copilot_ollama.DEFAULT_MODEL == "gpt-4-turbo"

    def test_duplicate_models_deduplicated(self):
        _load("models:\n  - 'gpt-4'\n  - 'gpt-4'\ndefault_model: 'gpt-4'\n")
        assert len(copilot_ollama.ALLOWED_MODELS) == 1


class TestMissingFile:
    def test_exits_on_missing_config(self):
        _expect_exit(open_exc=FileNotFoundError())


class TestMalformedYaml:
    def test_exits_on_syntax_error(self):
        _expect_exit("models: [unclosed")

    def test_exits_on_non_mapping_root(self):
        _expect_exit("- just a list")


class TestMissingRequiredKeys:
    def test_exits_when_models_key_absent(self):
        _expect_exit("default_model: gpt-4\n")

    def test_exits_when_models_is_empty_list(self):
        _expect_exit("models: []\ndefault_model: gpt-4\n")

    def test_exits_when_default_model_absent(self):
        _expect_exit("models:\n  - gpt-4\n")

    def test_exits_when_default_not_in_models(self):
        _expect_exit("models:\n  - 'gpt-4'\ndefault_model: 'gpt-4-turbo'\n")

    def test_exits_on_non_string_model_entry(self):
        _expect_exit("models:\n  - 'gpt-4'\n  - 42\ndefault_model: 'gpt-4'\n")
