import json
import os
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch


class _DummyTqdm:
    def __init__(self, *args, **kwargs):
        self.total = kwargs.get("total", 0)

    def update(self, n):
        return None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False


sys.modules.setdefault("tqdm", type("tqdm", (), {"tqdm": _DummyTqdm}))

from toolbox import download_collections as dlc


class _FakeHTTPResponse:
    def __init__(self, data: bytes, headers=None, chunk_size=None):
        self._data = data
        self._headers = headers or {}
        self._pos = 0
        self._chunk_size = chunk_size or len(data)

    def info(self):
        return SimpleNamespace(get=self._headers.get)

    def read(self, size=-1):
        if self._pos >= len(self._data):
            return b""
        if size == -1:
            size = len(self._data) - self._pos
        chunk = self._data[self._pos : self._pos + size]
        self._pos += size
        return chunk

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False


class DownloadCollectionsTests(unittest.TestCase):
    def test_download_file_writes_content(self):
        payload = b"abc123"
        headers = {"Content-Length": str(len(payload))}
        with tempfile.TemporaryDirectory() as tmp:
            dest = os.path.join(tmp, "file.out")
            with patch("urllib.request.urlopen", return_value=_FakeHTTPResponse(payload, headers=headers)):
                ok = dlc.download_file("http://example.com/file", dest)
            self.assertTrue(ok)
            self.assertTrue(os.path.exists(dest))
            with open(dest, "rb") as f:
                self.assertEqual(f.read(), payload)

    def test_get_collection_info_returns_data(self):
        # Simulate v3 success
        response_data = {"name": "ns.name", "versions_url": "/v3/versions"}
        with patch(
            "urllib.request.urlopen",
            return_value=_FakeHTTPResponse(json.dumps(response_data).encode("utf-8")),
        ):
            info = dlc.get_collection_info("ns", "name")
        self.assertIsNotNone(info)
        self.assertEqual(info.get("name"), "ns.name")


if __name__ == "__main__":
    unittest.main()
