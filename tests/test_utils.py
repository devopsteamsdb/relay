import io
import subprocess
import unittest
from unittest.mock import patch

from toolbox import utils


class UtilsExecuteCommandTests(unittest.TestCase):
    def test_execute_command_simulate_skips_subprocess(self):
        with patch("subprocess.run") as mock_run:
            ok = utils.execute_command("echo simulated", simulate=True)
        self.assertTrue(ok)
        mock_run.assert_not_called()

    def test_execute_command_success(self):
        fake_result = subprocess.CompletedProcess(args="cmd", returncode=0, stdout="ok\n", stderr="")
        with patch("subprocess.run", return_value=fake_result) as mock_run:
            ok = utils.execute_command("echo hi")
        self.assertTrue(ok)
        mock_run.assert_called_once()

    def test_execute_command_failure(self):
        with patch(
            "subprocess.run",
            side_effect=subprocess.CalledProcessError(returncode=1, cmd="bad", output="", stderr="error"),
        ):
            ok = utils.execute_command("bad cmd")
        self.assertFalse(ok)


if __name__ == "__main__":
    unittest.main()
