# maXerial-license-verification-python
A Python package for the communication interface between dockerized Python environments and the maXerial license activation server.

## Usage

```python
from maxerial_license_verifier import LicenseVerifier

# Initialize with license file path (Windows style for API calls)
verifier = LicenseVerifier(
    license_file_path="C:\\Users\\User\\Documents\\license.xml",
    server_ip="10.0.250.145",      # Optional, defaults to "127.0.0.1"
    server_port=61040,             # Optional, defaults to 61040
    server_endpoint="/api/verify_license"  # Optional, defaults to "/api/verify_license"
)

# Verify license via activation server
if verifier.verify_license():
    print("License verified successfully")
    
    # Check if a feature is enabled (uses Unix-style path internally)
    if verifier.check_feature("pro"):
        print("Pro feature is enabled")
else:
    print("License verification failed")
```

## Examples

The `examples/` folder contains small scripts you can run locally. These are not packaged or built with the library.

- `examples/mock_activation_server.py`: Minimal Flask server that accepts the GET request expected by the client for testing purposes.
- `examples/basic_usage.py`: Demonstrates calling `verify_license()` and `check_feature()`.

### Run the mock server

1. Install Flask:
   ```bash
   python -m pip install Flask
   ```
2. Start the server (defaults to port 61040; override with `MOCK_SERVER_PORT`):
   ```bash
   python examples/mock_activation_server.py
   ```

### Run the client example

1. Install the library in editable mode (or `pip install .`):
   ```bash
   python -m pip install -e .
   ```
2. Optionally set env vars and run:
   ```bash
   export EXAMPLE_LICENSE_PATH=C:\\Users\\User\\Documents\\license.xml
   export EXAMPLE_FEATURE=feature_name_enabled
   export EXAMPLE_SERVER_IP=127.0.0.1
   export EXAMPLE_SERVER_PORT=61040
   python examples/basic_usage.py
   ```

The example prints the result of `verify_license()` and whether a feature is present in the XML. Ensure your license XML contains a `<feature>` entry matching `EXAMPLE_FEATURE` for a `True` result.

## Build and publish to PyPI

1. Ensure version is updated in `pyproject.toml` under `[project] version`.
2. (Optional) Create and activate a clean virtual environment.
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
3. Install packaging tools.
   ```bash
   python -m pip install --upgrade pip build twine
   ```
4. Build the distribution (wheel + sdist).
   ```bash
   python -m build
   # Artifacts will be in ./dist/
   ls dist/
   ```
5. Check the distribution files.
   ```bash
   python -m twine check dist/*
   ```
6. (Recommended) Upload to TestPyPI first.
   ```bash
   # Create a token at https://test.pypi.org/manage/account/#api-tokens
   # Username: __token__
   # Password: pypi-AgENdGVzdC5weXBpLm9yZw... (your token)
   python -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*
   ```
7. Install from TestPyPI to validate.
   ```bash
   python -m pip install --index-url https://test.pypi.org/simple/ --no-deps maxerial-license-verifier
   ```
8. Upload to PyPI.
   ```bash
   # Create a token at https://pypi.org/manage/account/#api-tokens
   # Username: __token__
   # Password: pypi-AgENdHB5cGkub3Jn... (your token)
   python -m twine upload dist/*
   ```

Tips:
- Consider tagging the release: `git tag v0.1.0 && git push origin v0.1.0`.
- You can configure `~/.pypirc` for saved credentials and repository aliases.
- If re-uploading the same version, bump the version in `pyproject.toml` (PyPI does not allow overwriting files).
