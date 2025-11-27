import json
import os
import sys
import unittest
from unittest.mock import patch

# Ensure the project root is on sys.path for direct module imports
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from toolbox.config import _apply_latest_version, _fetch_latest_version


class _FakeResponse:
    def __init__(self, payload: str):
        self._payload = payload.encode("utf-8")

    def read(self):
        return self._payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False


class ConfigVersionTests(unittest.TestCase):
    def test_apply_latest_version_replaces_placeholder(self):
        tool = {
            "name": "Docker",
            "version": "{{latest_version}}",
            "version_source": {"type": "github_release", "repo": "moby/moby"},
        }

        with patch("toolbox.config._fetch_latest_version", return_value="1.2.3") as mock_fetch:
            updated = _apply_latest_version(tool.copy())

        self.assertEqual(updated["version"], "1.2.3")
        mock_fetch.assert_called_once_with(tool["version_source"])

    def test_apply_latest_version_without_source_keeps_placeholder(self):
        tool = {"name": "Docker", "version": "{{latest_version}}"}
        updated = _apply_latest_version(tool.copy())
        self.assertEqual(updated["version"], "{{latest_version}}")

    def test_fetch_latest_version_github_release_parses_tag(self):
        payload = json.dumps({"tag_name": "v9.8.7"})
        with patch("toolbox.config.urllib.request.urlopen", return_value=_FakeResponse(payload)) as mock_urlopen:
            version = _fetch_latest_version({"type": "github_release", "repo": "org/proj"})

        self.assertEqual(version, "9.8.7")
        mock_urlopen.assert_called_once()

    def test_fetch_latest_version_hashicorp_checkpoint(self):
        payload = json.dumps({"current_version": "2.1.0"})
        with patch("toolbox.config.urllib.request.urlopen", return_value=_FakeResponse(payload)) as mock_urlopen:
            version = _fetch_latest_version({"type": "hashicorp_checkpoint", "product": "terraform"})

        self.assertEqual(version, "2.1.0")
        mock_urlopen.assert_called_once()


if __name__ == "__main__":
    unittest.main()
