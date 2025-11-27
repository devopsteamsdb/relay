import os
import tempfile
import unittest
from unittest.mock import patch

from toolbox.cli import ToolboxCLI


class IntegrationFlowTests(unittest.TestCase):
    def setUp(self):
        # Temporary working directory to isolate downloads
        self.tmpdir = tempfile.TemporaryDirectory()
        self.getcwd_patch = patch("toolbox.cli.os.getcwd", return_value=self.tmpdir.name)
        self.getcwd_patch.start()

        # Minimal tool config for end-to-end download/install flow
        self.tools_patch = patch(
            "toolbox.cli.load_tool_configurations",
            return_value=[
                {
                    "name": "ToolX",
                    "description": "Test tool",
                    "download_steps": [{"type": "shell", "command": "echo download"}],
                    "install_steps": [{"type": "shell", "command": "echo install"}],
                }
            ],
        )
        self.tools_patch.start()

        # Skip expensive initial detection
        self.check_patch = patch.object(ToolboxCLI, "_check_initial_installed_tools", lambda self: None)
        self.check_patch.start()

        # Force command execution to succeed
        self.exec_patch = patch("toolbox.cli.execute_command", return_value=True)
        self.exec_patch.start()

        # Avoid blocking input calls during install
        self.input_patch = patch("toolbox.cli.input", return_value="")
        self.input_patch.start()

        self.cli = ToolboxCLI()

    def tearDown(self):
        self.input_patch.stop()
        self.exec_patch.stop()
        self.check_patch.stop()
        self.tools_patch.stop()
        self.getcwd_patch.stop()
        self.tmpdir.cleanup()

    def test_end_to_end_download_then_install(self):
        tool = self.cli.tools_config[0]

        # Download phase
        download_ok = self.cli.download_tool(tool)
        self.assertTrue(download_ok)
        self.assertIn(tool["name"], self.cli.downloaded_tools)

        # Verify files/directories are created in the sandboxed downloads dir
        expected_download_dir = os.path.join(self.tmpdir.name, "downloads", tool["name"])
        self.assertTrue(os.path.isdir(expected_download_dir))

        # Install phase
        install_ok = self.cli.install_tool(tool)
        self.assertTrue(install_ok)
        self.assertIn(tool["name"], self.cli.installed_tools)


if __name__ == "__main__":
    unittest.main()
