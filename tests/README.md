# Tests

This project uses Python's built-in `unittest`.

## How to run tests

From the repo root:

```bash
# If not already active, enable the virtualenv
source venv/bin/activate

# Run all tests
python -m unittest discover -s tests
```

On Windows PowerShell:

```powershell
venv\\Scripts\\activate
python -m unittest discover -s tests
```

## Notes

- Tests are located in `tests/`.
- `test_config.py` mocks network calls to verify latest-version resolution.
