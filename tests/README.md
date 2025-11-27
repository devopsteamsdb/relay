# Tests

This project uses Python's built-in `unittest`.

## How to run tests

From the repo root:

```bash
# If not already active, enable the virtualenv
source venv/bin/activate

# Run all tests (with friendly per-test status)
python -m unittest discover -s tests -v
```

On Windows PowerShell:

```powershell
venv\\Scripts\\activate

# Run all tests (with friendly per-test status)
python -m unittest discover -s tests -v
```

## Notes

- Tests are located in `tests/`.
- `test_config.py` (ConfigVersionTests): covers latest-version resolution for tools with `version_source` (GitHub and HashiCorp checkpoint; mocked network; per-test status lines).
- `test_cli.py` (CLIBatchSummaryTests): ensures batch Download/Install summaries report successes/failures correctly (tool actions mocked).
- `test_utils.py` (UtilsExecuteCommandTests): validates `execute_command` behavior for simulate/success/failure paths.
- `test_download_collections.py` (DownloadCollectionsTests): verifies download writes bytes and collection info is parsed (network mocked).
- Each test prints `[ RUN ] ...`, `[ PASS ] ...` (or `[ FAIL ] ...`) for readability.
