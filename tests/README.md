# Tests

This project uses Python's built-in `unittest`.

## How to run tests

From the repo root:

```bash
# If not already active, enable the virtualenv
source venv/bin/activate

# Run all tests (with friendly per-test status)
python -m unittest discover -s tests -v | tee /tmp/relay-tests.log

# Quick summary after run (passed/total and failures if any)
python - <<'PY'
import re
log = open('/tmp/relay-tests.log', 'r').read()
match = re.search(r"Ran (\\d+) tests? .*\\n\\n(OK|FAILED \\(failures?=.*\\))", log, re.MULTILINE)
if match:
    total = match.group(1)
    status = match.group(2)
    if status.startswith("OK"):
        print(f"Summary: {total}/{total} tests passed")
    else:
        print(f"Summary: {status}")
        fails = re.findall(r"FAIL: (.*?)\\n", log)
        for f in fails:
            print(f"- Failed: {f}")
else:
    print("Could not parse test summary")
PY
```

On Windows PowerShell:

```powershell
venv\\Scripts\\activate

# Run all tests (with friendly per-test status)
python -m unittest discover -s tests -v | Tee-Object -FilePath $env:TEMP\\relay-tests.log

# Quick summary after run (passed/total and failures if any)
python - <<'PY'
import re, os
log_path = os.path.join(os.environ.get('TEMP', '.'), 'relay-tests.log')
log = open(log_path, 'r').read()
match = re.search(r"Ran (\\d+) tests? .*\\n\\n(OK|FAILED \\(failures?=.*\\))", log, re.MULTILINE)
if match:
    total = match.group(1)
    status = match.group(2)
    if status.startswith("OK"):
        print(f"Summary: {total}/{total} tests passed")
    else:
        print(f"Summary: {status}")
        fails = re.findall(r"FAIL: (.*?)\\n", log)
        for f in fails:
            print(f"- Failed: {f}")
else:
    print("Could not parse test summary")
PY
```

## Notes

- Tests are located in `tests/`.
- `test_config.py` (ConfigVersionTests): covers latest-version resolution for tools with `version_source` (GitHub and HashiCorp checkpoint; mocked network; per-test status lines).
- `test_cli.py` (CLIBatchSummaryTests): ensures batch Download/Install summaries report successes/failures correctly (tool actions mocked).
- `test_utils.py` (UtilsExecuteCommandTests): validates `execute_command` behavior for simulate/success/failure paths.
- `test_download_collections.py` (DownloadCollectionsTests): verifies download writes bytes and collection info is parsed (network mocked).
- `test_integration.py` (IntegrationFlowTests): simulates an end-to-end download → install flow with a temporary downloads directory and mocked command execution.
- Each test prints `[ RUN ] ...`, `[ PASS ] ...` (or `[ FAIL ] ...`) for readability.
