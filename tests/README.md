# SecureDAL Tests

This directory contains the test suite to validate the tamper detection introduced by SecureDAL. The tests are designed to cover the scenarios defined in the [validation plan](./SCENARIOS.md).

You can run the tests using `pytest`:

```bash
# From the repository root directory
uv run pytest tests/test_tamper_detection_validation.py -v 
```