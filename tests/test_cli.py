import io
import unittest
import re
from contextlib import redirect_stdout
from unittest.mock import patch, MagicMock

from toolbox.cli import ToolboxCLI


class CLIBatchSummaryTests(unittest.TestCase):
    def setUp(self):
        self.load_patch = patch(
            "toolbox.cli.load_tool_configurations",
            return_value=[
                {"name": "ToolA", "description": "A tool", "download_steps": [], "install_steps": []},
                {"name": "ToolB", "description": "B tool", "download_steps": [], "install_steps": []},
            ],
        )
        self.load_patch.start()
        self.check_patch = patch.object(ToolboxCLI, "_check_initial_installed_tools", lambda self: None)
        self.check_patch.start()
        self.cli = ToolboxCLI()

    def tearDown(self):
        self.load_patch.stop()
        self.check_patch.stop()

    def test_process_all_tools_download_reports_success_and_failures(self):
        # First succeeds, second fails
        self.cli.download_tool = MagicMock(side_effect=[True, False])
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.cli._process_all_tools(action="Download")
        output = _strip_ansi(buf.getvalue())
        self.assertIn("Succeeded: ToolA", output)
        self.assertIn("Failed: ToolB", output)

    def test_process_all_tools_install_reports_success(self):
        self.cli.install_tool = MagicMock(return_value=True)
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.cli._process_all_tools(action="Install")
        output = _strip_ansi(buf.getvalue())
        self.assertIn("Succeeded: ToolA, ToolB", output)
        self.assertIn("Failed: None", output)


def _strip_ansi(text: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*m", "", text)


if __name__ == "__main__":
    unittest.main()
