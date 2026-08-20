"""Add src/copilot to sys.path so copilot_ollama can be imported in tests."""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
