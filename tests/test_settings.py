import os
import unittest
from unittest.mock import patch

from agentic_chaos_monkey.settings import GeminiSettings


class GeminiSettingsTests(unittest.TestCase):
    def test_gemini_api_key_is_supported(self) -> None:
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}, clear=True):
            settings = GeminiSettings.from_environment()

        self.assertEqual(settings.api_key, "test-key")
        self.assertEqual(settings.model, "gemini-flash-latest")

    def test_google_api_key_takes_precedence(self) -> None:
        with patch.dict(
            os.environ,
            {"GEMINI_API_KEY": "gemini", "GOOGLE_API_KEY": "google"},
            clear=True,
        ):
            settings = GeminiSettings.from_environment()

        self.assertEqual(settings.api_key, "google")

    def test_missing_key_fails_without_exposing_secrets(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "GEMINI_API_KEY"):
                GeminiSettings.from_environment()
